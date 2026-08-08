"""
Identra AI - CID Font Encoding Artifacts Cleanup Script
========================================================================
Cleans font encoding artifacts like (cid:415) -> 'ti', (cid:414) -> 'tt', (cid:413) -> 'fl',
(cid:412) -> 'fi', (cid:411) -> 'ff', and remaining (cid:\d+) patterns from the SQLite database.
"""

import re
import os
from app import create_app
from extensions import db
from database.models import User, Document, TimelineEvent, KnowledgeNode, KnowledgeEdge

CID_MAPPINGS = [
    (r'\(cid:415\)', 'ti'),
    (r'\(cid:414\)', 'tt'),
    (r'\(cid:413\)', 'fl'),
    (r'\(cid:412\)', 'fi'),
    (r'\(cid:411\)', 'ff'),
    (r'\(cid:410\)', 'fi'),
    (r'\(cid:409\)', 'fl'),
    (r'\(cid:\d+\)', ''),
    (r'[\uf0b7\uf0a7\uf020]', ' ')
]

def clean_str(val):
    if not val or not isinstance(val, str):
        return val
    cleaned = val
    for pattern, repl in CID_MAPPINGS:
        cleaned = re.sub(pattern, repl, cleaned)
    # Fix any double spaces caused by removing empty cids
    cleaned = re.sub(r' +', ' ', cleaned).strip()
    return cleaned

def run_cid_cleanup():
    app = create_app()
    with app.app_context():
        print("[CID Cleanup] Auditing & cleaning PDF font artifacts in database...")
        
        cleaned_count = 0

        # 1. Clean User records
        users = User.query.all()
        for u in users:
            old_degree = u.degree
            old_dept = u.department
            old_coll = u.college
            old_bio = u.bio

            u.degree = clean_str(u.degree)
            u.department = clean_str(u.department)
            u.college = clean_str(u.college)
            u.bio = clean_str(u.bio)

            if (old_degree != u.degree or old_dept != u.department or 
                old_coll != u.college or old_bio != u.bio):
                cleaned_count += 1
                print(f"[CID Cleanup] Cleaned User #{u.id}: Degree='{u.degree}', Dept='{u.department}'".encode('ascii', 'ignore').decode())

        # 2. Clean TimelineEvent records
        timeline_events = TimelineEvent.query.all()
        for te in timeline_events:
            old_title = te.title
            old_desc = te.description

            te.title = clean_str(te.title)
            te.description = clean_str(te.description)

            if old_title != te.title or old_desc != te.description:
                cleaned_count += 1
                print(f"[CID Cleanup] Cleaned TimelineEvent #{te.id}: Title='{te.title}'".encode('ascii', 'ignore').decode())

        # 3. Clean Document records
        docs = Document.query.all()
        for d in docs:
            old_orig = d.original_name
            old_text = d.extracted_text
            old_reason = d.classification_reason
            old_matched = d.matched_keywords

            d.original_name = clean_str(d.original_name)
            d.extracted_text = clean_str(d.extracted_text)
            d.classification_reason = clean_str(d.classification_reason)
            d.matched_keywords = clean_str(d.matched_keywords)

            if (old_orig != d.original_name or old_text != d.extracted_text or 
                old_reason != d.classification_reason or old_matched != d.matched_keywords):
                cleaned_count += 1
                print(f"[CID Cleanup] Cleaned Document #{d.id}: Name='{d.original_name}'".encode('ascii', 'ignore').decode())

        # 4. Clean KnowledgeNode records
        nodes = KnowledgeNode.query.all()
        for kn in nodes:
            old_label = kn.label
            old_prop = kn.properties

            kn.label = clean_str(kn.label)
            kn.properties = clean_str(kn.properties)

            if old_label != kn.label or old_prop != kn.properties:
                cleaned_count += 1
                print(f"[CID Cleanup] Cleaned KnowledgeNode #{kn.id}: Label='{kn.label}'".encode('ascii', 'ignore').decode())

        db.session.commit()
        print(f"[CID Cleanup] Completed! Total records sanitized: {cleaned_count}")

if __name__ == '__main__':
    run_cid_cleanup()
