# ============================================================
# app.py — Flask Backend (FINAL FIXED AI VERSION)
# ============================================================

import os
import re
import nltk
import pdfplumber

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# AI functions
from ai_analyzer import analyze_with_ai, rewrite_bullet_point

# ============================================================
# LOAD ENV VARIABLES
# ============================================================

load_dotenv()

# ============================================================
# NLTK SETUP
# ============================================================

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)
CORS(app)

# ============================================================
# FILE CONFIG
# ============================================================

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ============================================================
# SKILLS DATABASE
# ============================================================

SKILLS_DB = [
    "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go",
    "swift", "kotlin", "php", "scala", "rust", "matlab", "r",
    "html", "css", "react", "angular", "vue", "node.js", "express", "django",
    "flask", "fastapi", "bootstrap", "tailwind", "next.js",
    "machine learning", "deep learning", "nlp",
    "data science", "pandas", "numpy", "scikit-learn",
    "tensorflow", "pytorch", "keras",
    "sql", "mysql", "postgresql", "mongodb",
    "aws", "azure", "docker", "kubernetes",
    "git", "github", "linux",
    "rest api", "graphql",
    "data structures", "algorithms",
    "excel", "tableau", "power bi"
]

# ============================================================
# HELPERS
# ============================================================

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_pdf(filepath):

    text = ""

    with pdfplumber.open(filepath) as pdf:

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text.strip()


def detect_skills(text):

    text_lower = text.lower()

    return [
        skill for skill in SKILLS_DB
        if skill.lower() in text_lower
    ]


def extract_contact_info(text):

    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'

    emails = re.findall(email_pattern, text)
    phones = re.findall(phone_pattern, text)

    return {
        'email': emails[0] if emails else None,
        'phone': phones[0] if phones else None
    }


def calculate_ats_score(text, skills_found):

    score = 0
    breakdown = {}

    # CONTENT SCORE
    word_count = len(text.split())

    if word_count >= 400:
        content_score = 20
    elif word_count >= 200:
        content_score = 12
    else:
        content_score = 5

    breakdown['content_length'] = {
        'score': content_score,
        'max': 20,
        'word_count': word_count
    }

    score += content_score

    # SKILLS SCORE
    skills_count = len(skills_found)

    if skills_count >= 15:
        skills_score = 40
    elif skills_count >= 10:
        skills_score = 30
    elif skills_count >= 5:
        skills_score = 20
    else:
        skills_score = 10

    breakdown['skills_match'] = {
        'score': skills_score,
        'max': 40,
        'skills_found': skills_count
    }

    score += skills_score

    return min(100, score), breakdown


def generate_recommendations(skills_found):

    recommendations = []

    if len(skills_found) < 5:
        recommendations.append(
            "Add more technical skills related to your target role."
        )

    recommendations.append(
        "Use strong action verbs and measurable achievements."
    )

    recommendations.append(
        "Tailor your resume for each job description."
    )

    return recommendations

# ============================================================
# ROUTE 1 — HEALTH CHECK
# ============================================================

@app.route('/health', methods=['GET'])
def health_check():

    groq_key_set = bool(os.environ.get("GROQ_API_KEY"))

    return jsonify({
        'status': 'ok',
        'message': 'Resume Analyzer API is running! 🚀',
        'ai_enabled': groq_key_set,
        'ai_provider': 'Groq (Llama 3.1)' if groq_key_set else 'Not configured'
    })

# ============================================================
# ROUTE 2 — ANALYZE RESUME
# ============================================================

@app.route('/analyze', methods=['POST'])
def analyze_resume():

    try:

        # FILE VALIDATION
        if 'resume' not in request.files:
            return jsonify({'error': 'No file uploaded.'}), 400

        file = request.files['resume']

        if file.filename == '':
            return jsonify({'error': 'No file selected.'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Only PDF files allowed.'}), 400

        # SAVE FILE
        filename = secure_filename(file.filename)

        filepath = os.path.join(
            app.config['UPLOAD_FOLDER'],
            filename
        )

        file.save(filepath)

        # EXTRACT TEXT
        resume_text = extract_text_from_pdf(filepath)

        if len(resume_text.strip()) < 50:
            return jsonify({
                'error': 'Could not extract enough text from PDF.'
            }), 400

        # ANALYSIS
        skills_found = detect_skills(resume_text)

        ats_score, breakdown = calculate_ats_score(
            resume_text,
            skills_found
        )

        contact_info = extract_contact_info(resume_text)

        recommendations = generate_recommendations(skills_found)

        # AI ANALYSIS
        ai_analysis = None
        ai_error = None

        if os.environ.get("GROQ_API_KEY"):

            try:

                ai_analysis = analyze_with_ai(
                    resume_text,
                    skills_found,
                    ats_score
                )

            except Exception as ai_exception:

                ai_error = str(ai_exception)

        # CLEANUP
        try:
            os.remove(filepath)
        except:
            pass

        # RESPONSE
        return jsonify({
            'success': True,
            'ats_score': ats_score,
            'skills_found': skills_found,
            'skills_count': len(skills_found),
            'contact_info': contact_info,
            'recommendations': recommendations,
            'score_breakdown': breakdown,
            'word_count': len(resume_text.split()),
            'ai_analysis': ai_analysis,
            'ai_error': ai_error
        })

    except Exception as e:

        print("ANALYZE ERROR:", str(e))

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================
# ROUTE 3 — AI BULLET REWRITER
# ============================================================

@app.route('/rewrite', methods=['POST'])
def rewrite_bullet():

    try:

        data = request.get_json()

        if not data or 'text' not in data:

            return jsonify({
                'success': False,
                'error': 'Missing text field.'
            }), 400

        bullet_text = data.get('text', '').strip()
        context = data.get('context', '')

        if len(bullet_text) < 5:

            return jsonify({
                'success': False,
                'error': 'Text too short.'
            }), 400

        if not os.environ.get("GROQ_API_KEY"):

            return jsonify({
                'success': False,
                'error': 'GROQ_API_KEY missing.'
            }), 503

        print("✅ Rewrite endpoint hit")

        result = rewrite_bullet_point(
            bullet_text,
            context
        )

        print("✅ Rewrite success")

        return jsonify({
            'success': True,
            'result': result
        })

    except Exception as e:

        print("❌ REWRITE ERROR:", str(e))

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000
    )