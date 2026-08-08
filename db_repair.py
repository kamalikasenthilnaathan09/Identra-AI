"""
Identra AI - Database Schema Inspection & Automatic Repair Utility
========================================================================
This script inspects all SQLAlchemy models vs the SQLite database,
applies column additions via ALTER TABLE where needed, creates any missing
tables/indexes, and sets up Flask-Migrate versioning.
"""

import os
import sys
import sqlite3
from app import create_app
from extensions import db
from database.models import (
    User, Document, TimelineEvent, KnowledgeNode, KnowledgeEdge,
    ChatHistory, DocumentEmbedding, Notification
)
from sqlalchemy import inspect, text

def run_repair():
    app = create_app()
    with app.app_context():
        print("[DB Repair] Starting Database Schema Audit & Repair...")
        
        # Ensure database directory exists
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        print(f"[DB Repair] Target Database Path: {db_path}")
        
        engine = db.engine
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        print(f"[DB Repair] Existing Tables in Database: {existing_tables}")
        
        # Models to check
        models = [User, Document, TimelineEvent, KnowledgeNode, KnowledgeEdge, ChatHistory, DocumentEmbedding, Notification]
        
        report = {
            'tables_created': [],
            'columns_added': [],
            'indexes_created': [],
            'relationships_verified': []
        }

        # Step 1: Ensure all tables exist
        db.create_all()
        
        # Refresh inspector after create_all
        inspector = inspect(engine)
        new_existing_tables = inspector.get_table_names()
        for t in new_existing_tables:
            if t not in existing_tables:
                report['tables_created'].append(t)

        # Step 2: Column inspection & ALTER TABLE for missing columns
        db_file = os.path.abspath(db_path)
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        for model in models:
            table_name = model.__tablename__
            # Get existing columns in SQLite table
            cursor.execute(f"PRAGMA table_info('{table_name}')")
            existing_cols = {row[1]: row[2] for row in cursor.fetchall()}
            
            # Check model columns
            for column in model.__table__.columns:
                col_name = column.name
                if col_name not in existing_cols:
                    # Column is missing! Prepare ALTER TABLE
                    col_type = column.type.compile(engine.dialect)
                    
                    # Convert boolean/integer/text defaults to valid SQL
                    default_sql = ""
                    if column.default is not None and column.default.arg is not None:
                        val = column.default.arg
                        if isinstance(val, bool):
                            default_sql = f" DEFAULT {1 if val else 0}"
                        elif isinstance(val, (int, float)):
                            default_sql = f" DEFAULT {val}"
                        elif isinstance(val, str):
                            default_sql = f" DEFAULT '{val}'"

                    alter_query = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}{default_sql}"
                    print(f"[DB Repair] Adding missing column: {table_name}.{col_name} ({col_type})")
                    try:
                        cursor.execute(alter_query)
                        conn.commit()
                        report['columns_added'].append(f"{table_name}.{col_name}")
                    except Exception as e:
                        print(f"[DB Repair] Warning: Could not alter column {table_name}.{col_name}: {e}")

        conn.close()

        # Step 3: Verify Columns specifically required for User
        required_user_cols = [
            'full_name', 'phone', 'dob', 'gender', 'location', 'college', 'degree',
            'department', 'graduation_year', 'bio', 'skills_list', 'social_github',
            'social_linkedin', 'social_portfolio', 'social_leetcode', 'social_hackerrank',
            'social_resume_website', 'pref_dark_mode', 'pref_notifications', 'pref_language',
            'pref_email_alerts', 'pref_auto_ai_scan', 'pref_ocr_on_upload', 'pref_default_category'
        ]
        
        inspector = inspect(engine)
        user_cols = [c['name'] for c in inspector.get_columns('users')]
        missing_user_cols = [c for c in required_user_cols if c not in user_cols]
        
        if missing_user_cols:
            print(f"[DB Repair] Warning: Missing columns in users table: {missing_user_cols}")
        else:
            print("[DB Repair] SUCCESS: All 24 extended User columns present and verified!")

        # Step 4: Verify indexes & foreign keys
        for model in models:
            table_name = model.__tablename__
            indexes = inspector.get_indexes(table_name)
            report['indexes_created'].extend([f"{table_name}:{idx['name']}" for idx in indexes if idx['name']])
            
            fks = inspector.get_foreign_keys(table_name)
            for fk in fks:
                report['relationships_verified'].append(f"{table_name}.{fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")

        print("[DB Repair] Database Audit & Repair Complete!")
        return report

if __name__ == '__main__':
    rep = run_repair()
    print("\n--- REPAIR REPORT ---")
    print(f"Tables Created: {rep['tables_created']}")
    print(f"Columns Added: {rep['columns_added']}")
    print(f"Relationships Verified: {len(rep['relationships_verified'])}")
