from datetime import datetime
from extensions import db

class GoogleAccount(db.Model):
    __tablename__ = 'google_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    google_email = db.Column(db.String(120), nullable=True)
    google_id = db.Column(db.String(120), nullable=True)
    access_token = db.Column(db.Text, nullable=True)
    refresh_token = db.Column(db.Text, nullable=True)
    token_expiry = db.Column(db.DateTime, nullable=True)
    connected_at = db.Column(db.DateTime, default=datetime.utcnow)

    def is_token_expired(self):
        if not self.token_expiry:
            return True
        return datetime.utcnow() >= self.token_expiry

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'google_email': self.google_email,
            'connected': bool(self.access_token),
            'connected_at': self.connected_at.strftime('%b %d, %Y') if self.connected_at else None
        }


class GoogleDriveFile(db.Model):
    __tablename__ = 'google_drive_files'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    drive_file_id = db.Column(db.String(150), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(100), nullable=True)
    size = db.Column(db.BigInteger, default=0)
    file_path = db.Column(db.String(500), nullable=True)
    last_modified = db.Column(db.String(100), nullable=True)
    imported_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='Imported')

    def to_dict(self):
        return {
            'id': self.id,
            'drive_file_id': self.drive_file_id,
            'file_name': self.file_name,
            'mime_type': self.mime_type,
            'size': self.size,
            'file_path': self.file_path,
            'last_modified': self.last_modified,
            'imported_at': self.imported_at.strftime('%b %d, %Y %H:%M') if self.imported_at else None,
            'status': self.status
        }
