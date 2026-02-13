from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON
import json

db = SQLAlchemy()

class Job(db.Model):
    """Transcription job model"""
    __tablename__ = 'jobs'
    
    id = db.Column(db.String(36), primary_key=True)  # UUID
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    callback_url = db.Column(db.String(500))
    error_message = db.Column(db.Text)
    
    # Relationships
    transcripts = db.relationship('Transcript', backref='job', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert job to dictionary"""
        return {
            'id': self.id,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'callback_url': self.callback_url,
            'error_message': self.error_message,
            'transcripts': [t.to_dict() for t in self.transcripts]
        }

class Transcript(db.Model):
    """Individual transcript model"""
    __tablename__ = 'transcripts'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String(36), db.ForeignKey('jobs.id'), nullable=False)
    url = db.Column(db.String(500))
    video_id = db.Column(db.String(20))
    transcript_data = db.Column(db.Text)  # JSON string of transcript
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_transcript(self, data):
        """Store transcript as JSON string"""
        self.transcript_data = json.dumps(data)
    
    def get_transcript(self):
        """Retrieve transcript from JSON string"""
        if self.transcript_data:
            return json.loads(self.transcript_data)
        return None
    
    def to_dict(self):
        """Convert transcript to dictionary"""
        return {
            'id': self.id,
            'url': self.url,
            'video_id': self.video_id,
            'status': self.status,
            'error_message': self.error_message,
            'transcript': self.get_transcript(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
