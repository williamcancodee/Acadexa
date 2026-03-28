from flask import Flask, after_this_request, jsonify, render_template, request, send_file, flash, redirect, url_for, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
import tempfile
from time import time
from uuid import uuid4
from datetime import datetime, timedelta
from sqlalchemy import event

# Local imports
from search import STEM_SUBJECTS
from utils import parse_grade, collect_resources
from pdf_generator import generate_pdf
from models_fixed import db, User, CachedSearch, SearchHistory, Download, Resource, ResourceRating, query_hash

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-prod')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', r'sqlite:///c:/Users/USER/Desktop/PYTHON PROJECTS/AcaDexa/instance/acadexa.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init extensions
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
migrate = Migrate(app, db)

BRAND_MOTTO = 'Academia Reimagined'
CACHE_TTL_HOURS = 24

login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def _subject_catalog():
    return [
        'Math', 'Science', 'English', 'History', 'Geography', 'Art', 'Music',
        'Physical Education', 'Computer Science', 'Physics', 'Chemistry', 'Biology',
        'Economics', 'Psychology', 'Sociology', 'Philosophy', 'Literature', 'Languages',
        'Engineering', 'Medicine', 'Law', 'Business', 'Statistics', 'Accounting',
        'Political Science', 'Anthropology', 'Environmental Science', 'Astronomy',
        'Data Science', 'Robotics', 'Architecture', 'Journalism', 'Media Studies',
        'Religious Studies', 'Civics', 'Public Speaking', 'Other'
    ]

def _display_names():
    return {
        'books': 'Books',
        'videos': 'Videos',
        'articles': 'Articles',
        'libraries': 'Open Source Libraries / PDFs'
    }

def _cleanup_expired_cache():
    CachedSearch.query.filter(CachedSearch.expires_at < datetime.utcnow()).delete()
    db.session.commit()

@app.context_processor
def inject_branding():
    return {'brand_motto': BRAND_MOTTO}

@app.route('/')
def index():
    subjects_catalog = _subject_catalog()
    return render_template(
        'index.html',
        subjects_catalog=subjects_catalog,
        subject_count=len(subjects_catalog)
    )

@app.route('/about')
def about():
    return render_template('about.html', subject_count=len(_subject_catalog()))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return render_template('register.html')
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('register.html')

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password.', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/results', methods=['POST'])
def results():
    grade = request.form.get('grade')
    subjects = request.form.getlist('subjects')
    resource_types = request.form.getlist('resource_types')

    if not grade or not grade.strip() or not subjects or not resource_types:
        flash('Please fill in all required fields.', 'error')
        return redirect(url_for('index'))

    level = parse_grade(grade)
    qhash = query_hash(grade, subjects, resource_types)

    # Check cache first
    _cleanup_expired_cache()
    cached = CachedSearch.query.filter_by(query_hash=qhash).first()
    if cached and not cached.is_expired():
        resources = cached.results
        token = str(cached.id)
    else:
        # Compute new
        try:
            resources = collect_resources(subjects, resource_types, level, STEM_SUBJECTS)
            if not any(resources.values()):
                flash('No resources found. Please try different selections.', 'warning')
                return redirect(url_for('index'))

            # Save individual resources
            cached_resources = []
            for rtype, items in resources.items():
                for item in items:
                    existing = Resource.query.filter_by(link=item['link']).first()
                    if not existing:
                        resource = Resource(
                            title=item.get('title', 'Unknown'),
                            resource_type=rtype,
                            link=item['link'],
                            description=item.get('description') or item.get('summary', ''),
                            source_api=item.get('source', 'unknown')
                        )
                        db.session.add(resource)
                        cached_resources.append(resource)
                    else:
                        cached_resources.append(existing)
            db.session.commit()

            # Save cache
            cache_entry = CachedSearch(
                query_hash=qhash,
                grade=grade,
                subjects=subjects,
                resource_types=resource_types,
                results=resources,
                expires_at=datetime.utcnow() + timedelta(hours=CACHE_TTL_HOURS)
            )
            db.session.add(cache_entry)
            db.session.commit()

            # Track search
            if current_user.is_authenticated:
                search_hist = SearchHistory(
                    user_id=current_user.id,
                    grade=grade,
                    subjects=subjects,
                    resource_types=resource_types
                )
                db.session.add(search_hist)
                db.session.commit()
                token = str(cache_entry.id)
            else:
                token = uuid4().hex  # Fallback for anon

            resources = resources
        except Exception as e:
            print(f"Error generating resources: {e}")
            flash('An error occurred while generating resources. Please try again.', 'error')
            return redirect(url_for('index'))

    return render_template(
        'results.html',
        token=token,
        grade=grade,
        subjects=subjects,
        resource_types=resource_types,
        resources=resources,
        has_results=any(resources.values()),
        display_names=_display_names()
    )

@app.route('/download/<token>', methods=['GET'])
def download_pdf(token):
    _cleanup_expired_cache()
    try:
        cached_id = int(token)
        payload = CachedSearch.query.get(cached_id)
    except ValueError:
        payload = None

    if not payload or payload.is_expired():
        flash('Session expired. Please search again.', 'warning')
        return redirect(url_for('index'))

    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_pdf.close()

    generate_pdf(
        payload.results,
        payload.grade,
        payload.subjects,
        payload.resource_types,
        output_path=temp_pdf.name
    )

    # Track download
    if current_user.is_authenticated:
        download = Download(
            user_id=current_user.id,
            search_history_id=payload.id,  # Link to search if cached
            resources_count=sum(len(lst) for lst in payload.results.values()),
            file_size=os.path.getsize(temp_pdf.name)
        )
        db.session.add(download)
        db.session.commit()

    @after_this_request
    def _remove_temp_file(response):
        try:
            os.remove(temp_pdf.name)
        except OSError:
            pass
        return response

    return send_file(
        temp_pdf.name,
        as_attachment=True,
        download_name=f"acadexa_resources_{token}.pdf"
    )

@app.route('/review/<token>', methods=['POST'])
def submit_review(token):
    try:
        cached_id = int(token)
        payload = CachedSearch.query.get(cached_id)
    except ValueError:
        payload = None

    if not payload or payload.is_expired():
        return jsonify({'ok': False, 'message': 'Review session expired. Please curate again.'}), 404

    data = request.get_json(silent=True) or {}
    rating_val = data.get('rating')
    comment = (data.get('comment') or '').strip()[:500]

    try:
        rating = int(rating_val)
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'message': 'Rating must be a number between 1 and 5.'}), 400

    if rating < 1 or rating > 5:
        return jsonify({'ok': False, 'message': 'Rating must be between 1 and 5.'}), 400

    # Save rating (aggregate over resources for simplicity; could loop over resources)
    if current_user.is_authenticated:
        rating_entry = ResourceRating(
            user_id=current_user.id,
            resource_id=payload.id,  # Use cached search as 'resource' proxy
            rating=rating,
            comment=comment
        )
        db.session.add(rating_entry)
        db.session.commit()

    return jsonify({'ok': True, 'message': 'Thanks for rating Acadexa. Your feedback helps improve!'})


@app.cli.command('init-db')
def init_db():
    """Initialize the database."""
    db.create_all()
    print('Database initialized!')

@app.cli.command('create-superuser')
def create_superuser():
    """Create a superuser."""
    username = input('Username: ')
    email = input('Email: ')
    password = input('Password: ')
    hashed = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(username=username, email=email, password_hash=hashed)
    db.session.add(user)
    db.session.commit()
    print('Superuser created!')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Quick dev init
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)

