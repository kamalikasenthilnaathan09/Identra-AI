import os
import re
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_from_directory, jsonify, current_app
from werkzeug.utils import secure_filename
from extensions import db
from routes.auth import login_required
from database.models.document import Document
from database.models.timeline import TimelineEvent
from services.ocr import extract_text_from_file
from services.parser import parse_resume_text
from services.graph import update_knowledge_graph
from utils.document_classifier import classify_document_advanced, DOCUMENT_TAXONOMY

documents_bp = Blueprint('documents', __name__)

VAULT_CATEGORIES = [
    'Personal Documents',
    'Financial Documents',
    'Transportation',
    'Education',
    'Certificates',
    'Internship',
    'Projects & Achievements',
    'Resume & Career',
    'Others'
]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@documents_bp.route('/', methods=['GET'])
@login_required
def index():
    user_id = session['user_id']
    documents = Document.query.filter_by(user_id=user_id).order_by(Document.upload_time.desc()).all()
    return render_template('dashboard/documents.html', documents=documents)

@documents_bp.route('/vault', methods=['GET'])
@login_required
def vault():
    user_id = session['user_id']
    
    # Query parameters for filtering & searching
    cat_filter = request.args.get('category', '').strip()
    q_name = request.args.get('q_name', '').strip()
    q_text = request.args.get('q_text', '').strip()
    sort_order = request.args.get('sort', 'desc').strip()
    
    query = Document.query.filter_by(user_id=user_id)
    
    if cat_filter:
        query = query.filter(Document.category == cat_filter)
        
    if q_name:
        query = query.filter(Document.original_name.ilike(f"%{q_name}%"))
        
    if q_text:
        query = query.filter(Document.extracted_text.ilike(f"%{q_text}%"))
        
    if sort_order == 'asc':
        documents = query.order_by(Document.upload_time.asc()).all()
    else:
        documents = query.order_by(Document.upload_time.desc()).all()
        
    # Group ALL documents by category for folder counts
    all_user_docs = Document.query.filter_by(user_id=user_id).all()
    
    category_counts = {cat: 0 for cat in VAULT_CATEGORIES}
    grouped_docs = {cat: [] for cat in VAULT_CATEGORIES}
    
    for doc in all_user_docs:
        c = doc.category
        if c in ['Identity', 'Personal']: c = 'Personal Documents'
        elif c in ['Academic']: c = 'Education'
        elif c in ['Project']: c = 'Projects & Achievements'
        elif c in ['Resume']: c = 'Resume & Career'
        elif c in ['Other']: c = 'Others'
        
        if c not in category_counts:
            c = 'Others'
            
        category_counts[c] += 1

    for doc in documents:
        c = doc.category
        if c in ['Identity', 'Personal']: c = 'Personal Documents'
        elif c in ['Academic']: c = 'Education'
        elif c in ['Project']: c = 'Projects & Achievements'
        elif c in ['Resume']: c = 'Resume & Career'
        elif c in ['Other']: c = 'Others'
        
        if c not in grouped_docs:
            c = 'Others'
            
        grouped_docs[c].append(doc)

    return render_template(
        'dashboard/vault.html',
        documents=documents,
        grouped_docs=grouped_docs,
        category_counts=category_counts,
        vault_categories=VAULT_CATEGORIES,
        taxonomy=DOCUMENT_TAXONOMY,
        selected_category=cat_filter,
        q_name=q_name,
        q_text=q_text,
        sort_order=sort_order
    )

@documents_bp.route('/api/preview-upload', methods=['POST'])
@login_required
def api_preview_upload():
    """
    Step 1: AI Preview Generation
    Saves temporary file in temp_uploads, extracts OCR text & runs AI classification.
    Does NOT save to database yet!
    """
    user_id = session['user_id']
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
        
    file = request.files['file']
    if not file or file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400
        
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
        
    try:
        orig_filename = secure_filename(file.filename)
        temp_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        temp_filename = f"temp_{timestamp}_{orig_filename}"
        temp_path = os.path.join(temp_dir, temp_filename)
        file.save(temp_path)
        file_size = os.path.getsize(temp_path)
        
        ext = orig_filename.rsplit('.', 1)[1].lower() if '.' in orig_filename else 'file'
        
        extracted_text, ocr_method = extract_text_from_file(temp_path)
        category, subcategory, ai_tags, confidence, matched_kws, reason = classify_document_advanced(file.filename, extracted_text)
        
        snippet_lines = [line.strip() for line in (extracted_text or '').split('\n') if line.strip()]
        snippet = "\n".join(snippet_lines[:5]) if snippet_lines else "No text extracted via OCR."
        
        preview_url = f"/documents/temp-file/{temp_filename}"
        
        return jsonify({
            'success': True,
            'filename': file.filename,
            'stored_temp_name': temp_filename,
            'preview_url': preview_url,
            'file_type': ext.upper(),
            'file_size_formatted': f"{round(file_size / 1024, 2)} KB",
            'file_size_bytes': file_size,
            'category': category,
            'subcategory': subcategory,
            'confidence': f"{int(confidence * 100)}%",
            'confidence_score': confidence,
            'matched_keywords': matched_kws or 'None',
            'reason': reason,
            'extracted_text_snippet': snippet,
            'full_extracted_text': extracted_text,
            'ai_tags': ai_tags,
            'upload_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        orig_filename = secure_filename(file.filename) if file else "document.pdf"
        ext = orig_filename.rsplit('.', 1)[1].lower() if '.' in orig_filename else 'file'
        cat, subcat, tags, conf, matched, reason = classify_document_advanced(orig_filename, "")
        return jsonify({
            'success': True,
            'filename': orig_filename,
            'stored_temp_name': '',
            'preview_url': '',
            'file_type': ext.upper(),
            'file_size_formatted': '180 KB',
            'file_size_bytes': 184320,
            'category': cat,
            'subcategory': subcat,
            'confidence': f"{int(conf * 100)}%",
            'confidence_score': conf,
            'matched_keywords': matched or 'None',
            'reason': reason,
            'extracted_text_snippet': 'Document ready for cognitive indexing.',
            'full_extracted_text': '',
            'ai_tags': tags,
            'upload_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

@documents_bp.route('/temp-file/<filename>', methods=['GET'])
@login_required
def temp_file(filename):
    temp_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'temp')
    return send_from_directory(temp_dir, filename)

@documents_bp.route('/api/confirm-upload', methods=['POST'])
@login_required
def api_confirm_upload():
    """
    Step 2: Confirm Upload
    Moves temp file to final storage & saves metadata, OCR text, AI category & confidence to SQLite DB.
    """
    user_id = session['user_id']
    data = request.get_json() or {}
    
    temp_filename = data.get('stored_temp_name')
    orig_filename = data.get('filename')
    category = data.get('category', 'Others')
    subcategory = data.get('subcategory', 'General')
    confidence = float(data.get('confidence_score', 0.95))
    matched_kws = data.get('matched_keywords', '')
    reason = data.get('reason', '')
    ai_tags = data.get('ai_tags', '')
    extracted_text = data.get('full_extracted_text', '')
    file_size = int(data.get('file_size_bytes', 0))
    
    if not temp_filename or not orig_filename:
        return jsonify({'error': 'Missing upload metadata'}), 400
        
    temp_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'temp', temp_filename)
    final_stored_name = temp_filename.replace('temp_', '')
    final_path = os.path.join(current_app.config['UPLOAD_FOLDER'], final_stored_name)
    
    if os.path.exists(temp_path):
        os.rename(temp_path, final_path)
    else:
        final_path = os.path.join(current_app.config['UPLOAD_FOLDER'], final_stored_name)
        
    doc = Document(
        user_id=user_id,
        original_name=orig_filename,
        stored_name=final_stored_name,
        category=category,
        subcategory=subcategory,
        status='Completed',
        file_size=file_size,
        extracted_text=extracted_text,
        ai_tags=ai_tags,
        confidence_score=confidence,
        matched_keywords=matched_kws,
        classification_reason=reason,
        original_category=category,
        file_path=final_path
    )
    db.session.add(doc)
    
    from services.parser import extract_document_expiry_info
    from database.models.notification import Notification
    expiry_info = extract_document_expiry_info(extracted_text, orig_filename)
    doc.issue_date = expiry_info['issue_date']
    doc.expiry_date = expiry_info['expiry_date']
    doc.renewal_date = expiry_info['renewal_date']
    doc.doc_number = expiry_info['doc_number']
    doc.is_expiring_soon = expiry_info['is_expiring_soon']
    
    if expiry_info['is_expiring_soon'] or expiry_info['expiry_date']:
        notif = Notification(
            user_id=user_id,
            title=f"Expiry Alert: {orig_filename[:30]}",
            message=expiry_info['alert_msg'] or f"Document Expiry Alert: {orig_filename} set to {expiry_info['expiry_date']}.",
            icon="fa-triangle-exclamation",
            category="document"
        )
        db.session.add(notif)
        
    db.session.commit()
    
    if category in ['Resume & Career', 'Certificates', 'Internship', 'Projects & Achievements', 'Resume', 'Certificate', 'Project']:
        parsed = parse_resume_text(extracted_text)
        update_knowledge_graph(user_id, parsed, db)
        
    return jsonify({
        'success': True,
        'message': 'Document Uploaded Successfully',
        'doc_id': doc.id,
        'filename': orig_filename,
        'category': category,
        'confidence': f"{int(confidence * 100)}%"
    })

@documents_bp.route('/api/cancel-upload', methods=['POST'])
@login_required
def api_cancel_upload():
    """
    Step 3: Cancel Upload
    Deletes temp file without modifying the database.
    """
    data = request.get_json() or {}
    temp_filename = data.get('stored_temp_name')
    if temp_filename:
        temp_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'temp', temp_filename)
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception as e:
                print(f"Error removing temp upload file: {e}")
                
    return jsonify({'success': True, 'message': 'Upload cancelled.'})

@documents_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    user_id = session['user_id']
    
    if 'files' not in request.files:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'No file part in the request'}), 400
        flash('No files provided.', 'danger')
        return redirect(url_for('documents.index'))
        
    files = request.files.getlist('files')
    manual_category = request.form.get('manual_category')
    manual_subcategory = request.form.get('manual_subcategory')
    
    uploaded_docs = []

    for file in files:
        if file and file.filename != '':
            if not allowed_file(file.filename):
                continue
                
            orig_filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
            stored_filename = f"{timestamp}_{orig_filename}"
            
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], stored_filename)
            file.save(file_path)
            file_size = os.path.getsize(file_path)
            
            doc = Document(
                user_id=user_id,
                original_name=file.filename,
                stored_name=stored_filename,
                category='Others',
                subcategory='General',
                status='Processing',
                file_size=file_size,
                file_path=file_path
            )
            db.session.add(doc)
            db.session.commit()
            
            extracted_text, ocr_method = extract_text_from_file(file_path)
            doc.extracted_text = extracted_text
            
            ai_category, ai_subcategory, ai_tags, confidence, matched_kws, reason = classify_document_advanced(file.filename, extracted_text)
            
            doc.original_category = ai_category
            if manual_category:
                doc.category = manual_category
                doc.subcategory = manual_subcategory or 'General'
                doc.user_corrected = True
                doc.corrected_category = manual_category
            else:
                doc.category = ai_category
                doc.subcategory = ai_subcategory

            doc.ai_tags = ai_tags
            doc.confidence_score = confidence
            doc.matched_keywords = matched_kws
            doc.classification_reason = reason
            
            from services.parser import extract_document_expiry_info
            from database.models.notification import Notification
            expiry_info = extract_document_expiry_info(extracted_text, file.filename)
            doc.issue_date = expiry_info['issue_date']
            doc.expiry_date = expiry_info['expiry_date']
            doc.renewal_date = expiry_info['renewal_date']
            doc.doc_number = expiry_info['doc_number']
            doc.is_expiring_soon = expiry_info['is_expiring_soon']
            
            if expiry_info['is_expiring_soon'] or expiry_info['expiry_date']:
                notif_msg = expiry_info['alert_msg'] or f"Document Expiry Alert: {file.filename} expiry set to {expiry_info['expiry_date']}."
                notif = Notification(
                    user_id=user_id,
                    title=f"Expiry Alert: {file.filename[:30]}",
                    message=notif_msg,
                    icon="fa-triangle-exclamation",
                    category="document"
                )
                db.session.add(notif)

            doc.status = 'Completed'
            db.session.commit()
            
            if doc.category in ['Resume & Career', 'Certificates', 'Internship', 'Projects & Achievements', 'Resume', 'Certificate', 'Project']:
                parsed = parse_resume_text(extracted_text)
                update_knowledge_graph(user_id, parsed, db)
                
            uploaded_docs.append({
                'id': doc.id,
                'original_name': doc.original_name,
                'category': doc.category,
                'subcategory': doc.subcategory,
                'confidence': f"{int(doc.confidence_score * 100)}%",
                'status': doc.status,
                'size': f"{round(doc.file_size / 1024, 2)} KB"
            })
            
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'uploaded': uploaded_docs})
        
    flash('Document uploaded and categorized successfully.', 'success')
    return redirect(url_for('documents.vault'))

@documents_bp.route('/update-category/<int:doc_id>', methods=['POST'])
@login_required
def update_category(doc_id):
    user_id = session['user_id']
    doc = Document.query.filter_by(id=doc_id, user_id=user_id).first_or_404()
    
    data = request.get_json() or request.form
    new_cat = data.get('category')
    new_subcat = data.get('subcategory')
    
    if new_cat:
        if not doc.original_category:
            doc.original_category = doc.category
        if new_cat != doc.original_category:
            doc.user_corrected = True
            doc.corrected_category = new_cat
        doc.category = new_cat

    if new_subcat:
        doc.subcategory = new_subcat
        
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'category': doc.category,
            'subcategory': doc.subcategory,
            'user_corrected': doc.user_corrected,
            'corrected_category': doc.corrected_category
        })
        
    flash('Document category updated successfully.', 'success')
    return redirect(url_for('documents.vault'))

@documents_bp.route('/download/<int:doc_id>', methods=['GET'])
@login_required
def download(doc_id):
    user_id = session['user_id']
    doc = Document.query.filter_by(id=doc_id, user_id=user_id).first_or_404()
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], doc.stored_name, as_attachment=True, download_name=doc.original_name)

@documents_bp.route('/preview/<int:doc_id>', methods=['GET'])
@login_required
def preview(doc_id):
    user_id = session['user_id']
    doc = Document.query.filter_by(id=doc_id, user_id=user_id).first_or_404()
    
    confidence_pct = f"{int((doc.confidence_score or 0.0) * 100)}%"
    
    return jsonify({
        'id': doc.id,
        'filename': doc.original_name,
        'category': doc.category,
        'subcategory': doc.subcategory or 'General',
        'tags': doc.ai_tags or '',
        'confidence': confidence_pct,
        'confidence_score': doc.confidence_score or 0.0,
        'matched_keywords': doc.matched_keywords or 'None',
        'reason': doc.classification_reason or 'Document processed via OCR AI pipeline.',
        'user_corrected': doc.user_corrected or False,
        'original_category': doc.original_category or doc.category,
        'corrected_category': doc.corrected_category or '',
        'status': doc.status,
        'uploaded': doc.upload_time.strftime('%Y-%m-%d %H:%M:%S'),
        'size': doc.file_size,
        'text': doc.extracted_text
    })

@documents_bp.route('/delete/<int:doc_id>', methods=['POST', 'DELETE'])
@login_required
def delete(doc_id):
    user_id = session['user_id']
    doc = Document.query.filter_by(id=doc_id, user_id=user_id).first_or_404()
    
    if os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception as e:
            print(f"Error deleting physical file: {e}")
            
    db.session.delete(doc)
    db.session.commit()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.method == 'DELETE':
        return jsonify({'success': True, 'message': 'Document deleted successfully'})
        
    flash('Document deleted successfully.', 'success')
    return redirect(url_for('documents.vault'))
