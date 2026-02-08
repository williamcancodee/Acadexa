from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import os
from search import STEM_SUBJECTS
from utils import parse_grade, collect_resources
from pdf_generator import generate_pdf

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')  # For flash messages

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results', methods=['POST'])
def results():
    grade = request.form.get('grade')
    subjects = request.form.getlist('subjects')
    resource_types = request.form.getlist('resource_types')

    if not grade.strip() or not subjects or not resource_types:
        flash('Please fill in all required fields.', 'error')
        return redirect(url_for('index'))

    level = parse_grade(grade)
    try:
        resources = collect_resources(subjects, resource_types, level, STEM_SUBJECTS)
        if not any(resources.values()):
            flash('No resources found. Please try different selections.', 'warning')
            return redirect(url_for('index'))
        generate_pdf(resources, grade, subjects, resource_types)
        return send_file("resources.pdf", as_attachment=True)
    except Exception as e:
        print(f"Error generating resources: {e}")
        flash('An error occurred while generating resources. Please try again.', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
