from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    """User model for authentication."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    preference = db.relationship('UserPreference', backref='user', uselist=False, cascade='all, delete-orphan')
    search_history = db.relationship('SearchHistory', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    downloads = db.relationship('Download', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    ratings = db.relationship('ResourceRating', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class UserPreference(db.Model):
    """User preferences for default search values."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    default_grade = db.Column(db.String(50), nullable=True)
    default_subjects = db.Column(db.JSON, nullable=True)
    default_resource_types = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserPreference user_id={self.user_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'default_grade': self.default_grade,
            'default_subjects': self.default_subjects,
            'default_resource_types': self.default_resource_types
        }


class SearchHistory(db.Model):
    """Search history to track user searches."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    grade = db.Column(db.String(50), nullable=False)
    subjects = db.Column(db.JSON, nullable=False)
    resource_types = db.Column(db.JSON, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    downloads = db.relationship('Download', backref='search_history', lazy='dynamic')
    
    def __repr__(self):
        return f'<SearchHistory id={self.id} user_id={self.user_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'grade': self.grade,
            'subjects': self.subjects,
            'resource_types': self.resource_types,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class Download(db.Model):
    """Download tracking for PDF files."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    search_history_id = db.Column(db.Integer, db.ForeignKey('search_history.id'), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    resources_count = db.Column(db.Integer, default=0)
    file_size = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<Download id={self.id} user_id={self.user_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'search_history_id': self.search_history_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'resources_count': self.resources_count,
            'file_size': self.file_size
        }


class Resource(db.Model):
    """Cached resources for rating and caching."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)  # book, video, article, library
    link = db.Column(db.String(1000), nullable=False)
    description = db.Column(db.Text, nullable=True)
    source_api = db.Column(db.String(50), nullable=True)  # openlibrary, youtube, wikipedia, github
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    ratings = db.relationship('ResourceRating', backref='resource', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Resource {self.title[:30]}...>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'resource_type': self.resource_type,
            'link': self.link,
            'description': self.description,
            'source_api': self.source_api,
            'average_rating': self.get_average_rating()
        }
    
    def get_average_rating(self):
        """Calculate average rating for this resource."""
        ratings = self.ratings.all()
        if not ratings:
            return 0
        return sum(r.rating for r in ratings) / len(ratings)


class ResourceRating(db.Model):
    """User ratings and comments on resources."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('resource.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ResourceRating user_id={self.user_id} resource_id={self.resource_id} rating={self.rating}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'resource_id': self.resource_id,
            'rating': self.rating,
            'comment': self.comment,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class CachedSearch(db.Model):
    """Cached search results for performance."""
    id = db.Column(db.Integer, primary_key=True)
    query_hash = db.Column(db.String(64), unique=True, nullable=False)
    grade = db.Column(db.String(50), nullable=False)
    subjects = db.Column(db.JSON, nullable=False)
    resource_types = db.Column(db.JSON, nullable=False)
    results = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<CachedSearch query_hash={self.query_hash[:8]}...>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'query_hash': self.query_hash,
            'grade': self.grade,
            'subjects': self.subjects,
            'resource_types': self.resource_types,
            'results': self.results,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def is_expired(self):
        """Check if cache is expired."""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False
