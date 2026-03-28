from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import hashlib

db = SQLAlchemy()

class User(db.Model, UserMixin):
    """User model for authentication."""
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    preference = relationship('UserPreference', backref='user', uselist=False, cascade='all, delete-orphan')
    search_history = relationship('SearchHistory', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    downloads = relationship('Download', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    ratings = relationship('ResourceRating', backref='user', lazy='dynamic', cascade='all, delete-orphan')

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
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), unique=True, nullable=False)
    default_grade = Column(String(50), nullable=True)
    default_subjects = Column(JSON, nullable=True)
    default_resource_types = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    grade = Column(String(50), nullable=False, index=True)
    subjects = Column(JSON, nullable=False)
    resource_types = Column(JSON, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    downloads = relationship('Download', backref='search_history', lazy='dynamic')

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
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    search_history_id = Column(Integer, ForeignKey('search_history.id'), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    resources_count = Column(Integer, default=0)
    file_size = Column(Integer, default=0)

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
    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False)  # book, video, article, library
    link = Column(String(1000), nullable=False)
    description = Column(Text, nullable=True)
    source_api = Column(String(50), nullable=True)  # openlibrary, youtube, wikipedia, github
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    ratings = relationship('ResourceRating', backref='resource', lazy='dynamic', cascade='all, delete-orphan')

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
            return 0.0
        return sum(r.rating for r in ratings) / len(ratings)


class ResourceRating(db.Model):
    """User ratings and comments on resources."""
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    resource_id = Column(Integer, ForeignKey('resource.id'), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'resource_id', name='unique_user_resource_rating'),)

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
    id = Column(Integer, primary_key=True)
    query_hash = Column(String(64), unique=True, nullable=False, index=True)
    grade = Column(String(50), nullable=False)
    subjects = Column(JSON, nullable=False)
    resource_types = Column(JSON, nullable=False)
    results = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

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

def query_hash(grade, subjects, resource_types):
    """Generate SHA256 hash for cache key."""
    input_str = f"{grade}:{':'.join(sorted(subjects))}:{':'.join(sorted(resource_types))}"
    return hashlib.sha256(input_str.encode()).hexdigest()

