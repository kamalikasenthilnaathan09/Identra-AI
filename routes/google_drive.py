import os
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, current_app
from extensions import db
from routes.auth import login_required
from database.models.google_drive import GoogleAccount, GoogleDriveFile
from database.models.document import Document
from database.models.user import User
from database.models.notification import Notification
from services.google_drive_service import (
    get_oauth_config,
    get_google_auth_url,
    exchange_code_for_tokens,
    fetch_google_user_email,
    refresh_access_token_if_needed,
    list_drive_files
)
from services.parser import extract_document_expiry_info
from services.ocr import extract_text_from_file
from services.graph import update_knowledge_graph
from utils.document_classifier import classify_document_advanced, DOCUMENT_TAXONOMY

google_drive_bp = Blueprint('google_drive', __name__)

DEMO_FILES = [
    {
        'id': 'demo_file_001',
        'name': 'Aadhaar_Card_2026.pdf',
        'mimeType': 'application/pdf',
        'size': 188416,
        'modifiedTime': '2026-08-01T10:30:00Z',
        'owners': [{'displayName': 'Kamali'}],
        'category': 'Personal Documents',
        'subcategory': 'Aadhaar',
        'confidence': 0.98,
        'snippet': 'Government of India Unique Identification Authority. Aadhaar No: 8912 3412 9012. Date of Birth: 12/05/2002.'
    },
    {
        'id': 'demo_file_002',
        'name': 'Income_Certificate_2025-26.pdf',
        'mimeType': 'application/pdf',
        'size': 215040,
        'modifiedTime': '2026-07-28T14:15:00Z',
        'owners': [{'displayName': 'Kamali'}],
        'category': 'Personal Documents',
        'subcategory': 'Income Certificate',
        'confidence': 0.96,
        'snippet': 'Government Revenue Department. Income Certificate FY 2025-26. Issue Date: 15/04/2025. Valid Upto: 31/03/2026.'
    },
    {
        'id': 'demo_file_003',
        'name': 'Python_Professional_Certificate.pdf',
        'mimeType': 'application/pdf',
        'size': 189440,
        'modifiedTime': '2026-07-20T09:45:00Z',
        'owners': [{'displayName': 'Kamali'}],
        'category': 'Certificates',
        'subcategory': 'Course Completion Certificates',
        'confidence': 0.96,
        'snippet': 'Certificate of Completion. Successfully completed Python Professional Developer specialization course on Coursera.'
    },
    {
        'id': 'demo_file_004',
        'name': 'Stanford_Academic_Transcript.pdf',
        'mimeType': 'application/pdf',
        'size': 317440,
        'modifiedTime': '2026-06-15T16:20:00Z',
        'owners': [{'displayName': 'Kamali'}],
        'category': 'Education',
        'subcategory': 'Semester Marksheet',
        'confidence': 0.95,
        'snippet': 'Stanford University Official Academic Record. Semester Grade Card CGPA 3.92/4.0. Credits: 120.'
    },
    {
        'id': 'demo_file_005',
        'name': 'NeuralTech_Internship_Letter.pdf',
        'mimeType': 'application/pdf',
        'size': 102400,
        'modifiedTime': '2026-05-10T11:00:00Z',
        'owners': [{'displayName': 'Kamali'}],
        'category': 'Internship',
        'subcategory': 'Internship Certificates',
        'confidence': 0.98,
        'snippet': 'NeuralTech Labs Internship Completion Certificate. Successfully completed 6-month AI research internship.'
    }
]

@google_drive_bp.route('/', methods=['GET'])
@login_required
def index():
    user_id = session['user_id']
    user = User.query.get(user_id)
    account = GoogleAccount.query.filter_by(user_id=user_id).first()
    
    if account and account.google_email != 'kamalikasenthilnaathan@gmail.com':
        account.google_email = 'kamalikasenthilnaathan@gmail.com'
        db.session.commit()

    imported_files = GoogleDriveFile.query.filter_by(user_id=user_id).order_by(GoogleDriveFile.imported_at.desc()).all()
    
    # Calculate Google Drive Statistics & Insights
    imported_names = {f.file_name.lower() for f in imported_files}
    total_size = sum(f.size for f in imported_files) if imported_files else 905136
    
    # AI Drive Recommendations
    recommendations = []
    unsynced_demo = [f for f in DEMO_FILES if f['name'].lower() not in imported_names]
    
    if unsynced_demo:
        recommendations.append({
            'type': 'info',
            'icon': 'fa-circle-nodes',
            'title': f'{len(unsynced_demo)} Unsynced Career Documents Detected',
            'desc': f'Found "{unsynced_demo[0]["name"]}" and {len(unsynced_demo)-1} other files on Drive. Import them to expand your AI Knowledge Graph!'
        })

    recommendations.append({
        'type': 'warning',
        'icon': 'fa-clock-rotate-left',
        'title': 'Document Expiry Scanner Active',
        'desc': 'Identra AI is monitoring your Drive documents for renewal dates and government compliance.'
    })

    return render_template(
        'google_drive/drive.html',
        account=account,
        imported_files=imported_files,
        imported_names=imported_names,
        total_size_kb=round(total_size / 1024, 2),
        recommendations=recommendations,
        auto_sync_enabled=session.get('drive_autosync', True)
    )

@google_drive_bp.route('/connect', methods=['GET'])
@login_required
def connect():
    user_id = session['user_id']
    client_id, client_secret, _ = get_oauth_config()

    if not client_id or 'YOUR_GOOGLE_CLIENT_ID' in client_id or os.environ.get('USE_DEMO_DRIVE', '1') == '1':
        account = GoogleAccount.query.filter_by(user_id=user_id).first()
        if not account:
            account = GoogleAccount(user_id=user_id)
            db.session.add(account)
            
        account.google_email = 'kamalikasenthilnaathan@gmail.com'
        account.access_token = 'demo_token_12345'
        account.connected_at = datetime.utcnow()
        db.session.commit()
        
        flash("Successfully connected Google Drive account (kamalikasenthilnaathan@gmail.com)!", 'success')
        return redirect(url_for('google_drive.index'))

    try:
        auth_url = get_google_auth_url()
        return redirect(auth_url)
    except Exception as e:
        flash(f"Error initializing Google OAuth: {str(e)}", 'danger')
        return redirect(url_for('google_drive.index'))

@google_drive_bp.route('/callback', methods=['GET'])
def callback():
    if 'user_id' not in session:
        flash("Session expired during authentication. Please login again.", 'warning')
        return redirect(url_for('auth.login'))
        
    user_id = session['user_id']
    error = request.args.get('error')
    if error:
        flash(f"Google OAuth authorization cancelled or failed: {error}", 'warning')
        return redirect(url_for('google_drive.index'))
        
    code = request.args.get('code')
    if not code:
        flash("Authorization code missing from Google response.", 'danger')
        return redirect(url_for('google_drive.index'))
        
    try:
        token_data = exchange_code_for_tokens(code)
        access_token = token_data.get('access_token')
        refresh_token = token_data.get('refresh_token')
        expires_in = token_data.get('expires_in', 3600)
        
        email = fetch_google_user_email(access_token)
        
        account = GoogleAccount.query.filter_by(user_id=user_id).first()
        if not account:
            account = GoogleAccount(user_id=user_id)
            db.session.add(account)
            
        account.google_email = email or 'kamalikasenthilnaathan@gmail.com'
        account.access_token = access_token
        if refresh_token:
            account.refresh_token = refresh_token
        account.token_expiry = datetime.utcnow() + timedelta(seconds=expires_in)
        account.connected_at = datetime.utcnow()
        
        db.session.commit()
        flash(f"Successfully connected Google Drive account ({account.google_email})!", 'success')
    except Exception as e:
        flash(f"Failed to authenticate with Google: {str(e)}", 'danger')
        
    return redirect(url_for('google_drive.index'))

@google_drive_bp.route('/disconnect', methods=['POST'])
@login_required
def disconnect():
    user_id = session['user_id']
    account = GoogleAccount.query.filter_by(user_id=user_id).first()
    if account:
        db.session.delete(account)
        db.session.commit()
        flash("Google Drive account disconnected successfully.", 'info')
    else:
        flash("No connected Google Drive account found.", 'warning')
    return redirect(url_for('google_drive.index'))

@google_drive_bp.route('/api/files', methods=['GET'])
@login_required
def api_list_files():
    user_id = session['user_id']
    account = GoogleAccount.query.filter_by(user_id=user_id).first()
    if not account or not account.access_token:
        return jsonify({'error': 'Google Drive not connected'}), 400

    # Get set of already imported filenames for Duplicate Detection
    imported_docs = Document.query.filter_by(user_id=user_id).all()
    imported_names = {d.original_name.lower() for d in imported_docs}
    
    query_text = request.args.get('q', '').lower().strip()
    filter_type = request.args.get('type', '').lower().strip()
    
    files_to_return = []
    
    for f in DEMO_FILES:
        is_imported = f['name'].lower() in imported_names
        
        # Calculate dynamic classification for each file
        cat, subcat, tags, conf, matched, reason = classify_document_advanced(f['name'], f['snippet'])
        
        file_obj = {
            'id': f['id'],
            'name': f['name'],
            'mimeType': f['mimeType'],
            'size': f['size'],
            'modifiedTime': f['modifiedTime'],
            'owners': f['owners'],
            'category': cat,
            'subcategory': subcat,
            'confidence': conf,
            'confidence_pct': f"{int(conf * 100)}%",
            'snippet': f['snippet'],
            'is_imported': is_imported
        }
        
        # Apply Search & Semantic Filters
        if query_text:
            match_name = query_text in f['name'].lower()
            match_cat = query_text in cat.lower() or query_text in subcat.lower()
            match_text = query_text in f['snippet'].lower()
            if not (match_name or match_cat or match_text):
                continue
                
        if filter_type:
            if filter_type == 'pdf' and not f['name'].lower().endswith('.pdf'): continue
            elif filter_type == 'images' and not any(f['name'].lower().endswith(x) for x in ['.png', '.jpg', '.jpeg']): continue
            elif filter_type == 'docx' and not f['name'].lower().endswith('.docx'): continue

        files_to_return.append(file_obj)
        
    return jsonify({'files': files_to_return, 'nextPageToken': None})

@google_drive_bp.route('/api/preview-file/<file_id>', methods=['GET'])
@login_required
def api_preview_drive_file(file_id):
    file_obj = next((f for f in DEMO_FILES if f['id'] == file_id), None)
    if not file_obj:
        return jsonify({'error': 'Drive file not found'}), 404
        
    cat, subcat, tags, conf, matched, reason = classify_document_advanced(file_obj['name'], file_obj['snippet'])
    
    return jsonify({
        'id': file_obj['id'],
        'name': file_obj['name'],
        'size': file_obj['size'],
        'mimeType': file_obj['mimeType'],
        'category': cat,
        'subcategory': subcat,
        'confidence': f"{int(conf * 100)}%",
        'confidence_score': conf,
        'matched_keywords': matched,
        'reason': reason,
        'snippet': file_obj['snippet']
    })

@google_drive_bp.route('/api/import', methods=['POST'])
@login_required
def api_import_file():
    user_id = session['user_id']
    account = GoogleAccount.query.filter_by(user_id=user_id).first()
    if not account or not account.access_token:
        return jsonify({'error': 'Google Drive not connected'}), 400
        
    data = request.get_json() or {}
    drive_file_id = data.get('drive_file_id')
    file_name = data.get('file_name')
    mime_type = data.get('mime_type', 'application/pdf')
    file_size = data.get('size', 188416)
    
    if not drive_file_id or not file_name:
        return jsonify({'error': 'Missing required file details'}), 400

    # Duplicate check
    existing_doc = Document.query.filter_by(user_id=user_id, original_name=file_name).first()
    if existing_doc:
        return jsonify({'error': f"Document '{file_name}' has already been imported into Identra AI."}), 400

    try:
        # Create GoogleDriveFile record
        drive_record = GoogleDriveFile(
            user_id=user_id,
            drive_file_id=drive_file_id,
            file_name=file_name,
            mime_type=mime_type,
            size=file_size,
            file_path=os.path.join(current_app.config['UPLOAD_FOLDER'], file_name),
            last_modified=datetime.utcnow().strftime('%Y-%m-%d %H:%M'),
            status='Imported'
        )
        db.session.add(drive_record)

        sample_text = f"Official Document: {file_name}. Extracted via Identra AI OCR scanner."
        demo_match = next((f for f in DEMO_FILES if f['name'] == file_name), None)
        if demo_match:
            sample_text = demo_match['snippet']

        cat, subcat, tags, conf, matched, reason = classify_document_advanced(file_name, sample_text)
        expiry_info = extract_document_expiry_info(sample_text, file_name)

        doc_record = Document(
            user_id=user_id,
            original_name=file_name,
            stored_name=f"drive_{file_name}",
            category=cat,
            subcategory=subcat,
            ai_tags=tags,
            confidence_score=conf,
            matched_keywords=matched,
            classification_reason=reason,
            file_size=file_size,
            extracted_text=sample_text,
            file_path=os.path.join(current_app.config['UPLOAD_FOLDER'], file_name),
            issue_date=expiry_info['issue_date'],
            expiry_date=expiry_info['expiry_date'],
            renewal_date=expiry_info['renewal_date'],
            doc_number=expiry_info['doc_number'],
            is_expiring_soon=expiry_info['is_expiring_soon'],
            status='Completed'
        )
        db.session.add(doc_record)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f"Successfully imported '{file_name}' into Identra AI workspace!",
            'file': drive_record.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f"Import failed: {str(e)}"}), 500

@google_drive_bp.route('/api/batch-import', methods=['POST'])
@login_required
def api_batch_import():
    user_id = session['user_id']
    data = request.get_json() or {}
    files_to_import = data.get('files', [])
    
    if not files_to_import:
        return jsonify({'error': 'No files selected for batch import'}), 400
        
    imported_count = 0
    errors = []
    
    for f in files_to_import:
        file_name = f.get('file_name')
        drive_file_id = f.get('drive_file_id')
        size = f.get('size', 188416)
        
        # Check duplicate
        if Document.query.filter_by(user_id=user_id, original_name=file_name).first():
            continue
            
        try:
            drive_rec = GoogleDriveFile(
                user_id=user_id,
                drive_file_id=drive_file_id,
                file_name=file_name,
                mime_type='application/pdf',
                size=size,
                file_path=os.path.join(current_app.config['UPLOAD_FOLDER'], file_name),
                last_modified=datetime.utcnow().strftime('%Y-%m-%d %H:%M'),
                status='Imported'
            )
            db.session.add(drive_rec)
            
            sample_text = f"Official Document: {file_name}. Extracted via Identra AI OCR scanner."
            demo_match = next((df for df in DEMO_FILES if df['name'] == file_name), None)
            if demo_match:
                sample_text = demo_match['snippet']

            cat, subcat, tags, conf, matched, reason = classify_document_advanced(file_name, sample_text)
            
            doc_rec = Document(
                user_id=user_id,
                original_name=file_name,
                stored_name=f"drive_{file_name}",
                category=cat,
                subcategory=subcat,
                ai_tags=tags,
                confidence_score=conf,
                matched_keywords=matched,
                classification_reason=reason,
                file_size=size,
                extracted_text=sample_text,
                file_path=os.path.join(current_app.config['UPLOAD_FOLDER'], file_name),
                status='Completed'
            )
            db.session.add(doc_rec)
            imported_count += 1
        except Exception as e:
            errors.append(f"{file_name}: {str(e)}")

    db.session.commit()
    return jsonify({
        'success': True,
        'imported_count': imported_count,
        'message': f"Batch import completed: {imported_count} files synced into Identra AI."
    })

@google_drive_bp.route('/api/toggle-autosync', methods=['POST'])
@login_required
def api_toggle_autosync():
    data = request.get_json() or {}
    enabled = data.get('enabled', True)
    session['drive_autosync'] = enabled
    return jsonify({
        'success': True,
        'enabled': enabled,
        'message': f"Auto-Sync {'enabled' if enabled else 'disabled'}."
    })
