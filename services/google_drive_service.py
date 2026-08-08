import os
import requests
import json
from datetime import datetime, timedelta
from urllib.parse import urlencode
from werkzeug.utils import secure_filename
from flask import current_app
from extensions import db
from database.models.google_drive import GoogleAccount, GoogleDriveFile
from database.models.document import Document
from services.ocr import extract_text_from_file
from services.parser import parse_resume_text
from services.ai import classify_document
from services.graph import update_knowledge_graph
from services.embeddings import generate_embedding

# MIME Type mappings for filtering
MIME_TYPES = {
    'pdf': "mimeType = 'application/pdf'",
    'docx': "mimeType = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' or mimeType = 'application/msword'",
    'images': "mimeType = 'image/png' or mimeType = 'image/jpeg' or mimeType = 'image/jpg'",
    'txt': "mimeType = 'text/plain'",
    'ppt': "mimeType = 'application/vnd.openxmlformats-officedocument.presentationml.presentation' or mimeType = 'application/vnd.ms-powerpoint'",
    'excel': "mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' or mimeType = 'application/vnd.ms-excel'"
}

def get_oauth_config():
    client_id = current_app.config.get('GOOGLE_CLIENT_ID') or os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = current_app.config.get('GOOGLE_CLIENT_SECRET') or os.environ.get('GOOGLE_CLIENT_SECRET')
    redirect_uri = current_app.config.get('GOOGLE_REDIRECT_URI') or os.environ.get('GOOGLE_REDIRECT_URI', 'http://127.0.0.1:5000/auth/google/callback')
    return client_id, client_secret, redirect_uri

def get_google_auth_url():
    client_id, _, redirect_uri = get_oauth_config()
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'https://www.googleapis.com/auth/drive.readonly https://www.googleapis.com/auth/userinfo.email openid',
        'access_type': 'offline',
        'prompt': 'consent',
        'include_granted_scopes': 'true'
    }
    return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

def exchange_code_for_tokens(code):
    client_id, client_secret, redirect_uri = get_oauth_config()
    data = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    res = requests.post('https://oauth2.googleapis.com/token', data=data, timeout=10)
    if res.status_code != 200:
        raise Exception(f"Failed to exchange token with Google: {res.text}")
    return res.json()

def fetch_google_user_email(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    res = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', headers=headers, timeout=10)
    if res.status_code == 200:
        return res.json().get('email')
    return None

def refresh_access_token_if_needed(account):
    if not account or not account.refresh_token:
        return account.access_token if account else None

    # Check if token is expired or expires in < 5 minutes
    if account.token_expiry and datetime.utcnow() < (account.token_expiry - timedelta(minutes=5)):
        return account.access_token

    # Token expired, request new access token
    client_id, client_secret, _ = get_oauth_config()
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': account.refresh_token,
        'grant_type': 'refresh_token'
    }
    res = requests.post('https://oauth2.googleapis.com/token', data=data, timeout=10)
    if res.status_code == 200:
        token_data = res.json()
        account.access_token = token_data.get('access_token')
        expires_in = token_data.get('expires_in', 3600)
        account.token_expiry = datetime.utcnow() + timedelta(seconds=expires_in)
        db.session.commit()
        return account.access_token
    else:
        print(f"Error refreshing Google token: {res.text}")
        return account.access_token

def list_drive_files(access_token, query_text='', filter_type='', page_token=None, page_size=20):
    headers = {'Authorization': f'Bearer {access_token}'}
    
    # Construct Google Drive API query 'q'
    q_clauses = ["trashed = false", "'me' in owners or sharedWithMe = true"]
    
    if query_text:
        safe_query = query_text.replace("'", "\\'")
        q_clauses.append(f"name contains '{safe_query}'")
        
    if filter_type and filter_type in MIME_TYPES:
        q_clauses.append(f"({MIME_TYPES[filter_type]})")
        
    q_str = " and ".join(q_clauses)
    
    params = {
        'q': q_str,
        'pageSize': page_size,
        'fields': 'nextPageToken, files(id, name, mimeType, size, modifiedTime, iconLink, webViewLink, thumbnailLink, owners)',
        'orderBy': 'modifiedTime desc'
    }
    if page_token:
        params['pageToken'] = page_token

    res = requests.get('https://www.googleapis.com/drive/v3/files', headers=headers, params=params, timeout=12)
    if res.status_code != 200:
        raise Exception(f"Google Drive API error ({res.status_code}): {res.text}")
        
    return res.json()

def download_and_import_drive_file(user_id, account, drive_file_id, file_name, mime_type, file_size):
    access_token = refresh_access_token_if_needed(account)
    headers = {'Authorization': f'Bearer {access_token}'}
    
    # 1. Download file content from Google Drive API v3 alt=media
    url = f"https://www.googleapis.com/drive/v3/files/{drive_file_id}?alt=media"
    res = requests.get(url, headers=headers, stream=True, timeout=30)
    
    if res.status_code != 200:
        raise Exception(f"Failed to download file from Google Drive ({res.status_code})")

    # 2. Sanitize filename and create storage directory
    safe_name = secure_filename(file_name) or f"drive_{drive_file_id}.pdf"
    user_drive_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], str(user_id), 'google_drive')
    os.makedirs(user_drive_dir, exist_ok=True)
    
    saved_path = os.path.join(user_drive_dir, safe_name)
    
    # Write file content
    with open(saved_path, 'wb') as f:
        for chunk in res.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                
    actual_size = os.path.getsize(saved_path)

    # 3. Store metadata in google_drive_files table
    drive_record = GoogleDriveFile(
        user_id=user_id,
        drive_file_id=drive_file_id,
        file_name=safe_name,
        mime_type=mime_type,
        size=actual_size,
        file_path=saved_path,
        last_modified=datetime.utcnow().strftime('%Y-%m-%d %H:%M'),
        status='Imported'
    )
    db.session.add(drive_record)

    # 4. Seamlessly trigger AI Pipeline (OCR, Resume Parser, Categorization, Embedding, Knowledge Graph)
    extracted_text, ocr_engine = extract_text_from_file(saved_path)
    predicted_category = classify_document(safe_name, extracted_text)

    # Calculate embedding vector
    embedding_vec = generate_embedding(f"{safe_name} {extracted_text}")

    # Add to main Document model
    doc_record = Document(
        user_id=user_id,
        original_name=safe_name,
        stored_name=safe_name,
        category=predicted_category,
        file_size=actual_size,
        extracted_text=extracted_text,
        embedding=embedding_vec,
        status='Completed'
    )
    db.session.add(doc_record)
    db.session.flush()

    # Parse resume if applicable
    if predicted_category == 'Resume':
        parsed_data = parse_resume_text(extracted_text)
        update_knowledge_graph(user_id, parsed_data, db)

    db.session.commit()
    return drive_record, doc_record
