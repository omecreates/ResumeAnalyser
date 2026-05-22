# ============================================================
# app.py — Flask Backend (AI-Upgraded Version)
# ============================================================

import os
import re
import json
import nltk
import spacy
import pdfplumber
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Import our new AI analyzer module
from ai_analyzer import analyze_with_ai, rewrite_bullet_point

# Load .env file (reads GROQ_API_KEY into environment)
load_dotenv()

# ── NLTK Downloads ──
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('punkt_tab', quiet=True)

# ── spaCy Model ──
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("⚠️  Run: python -m spacy download en_core_web_sm")
    nlp = None

# ── Flask App ──
app = Flask(__name__)
CORS(app)

# ── File Upload Config ──
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ── Skills Database ──
SKILLS_DB = [
    "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go",
    "swift", "kotlin", "php", "scala", "rust", "matlab", "r",
    "html", "css", "react", "angular", "vue", "node.js", "express", "django",
    "flask", "fastapi", "bootstrap", "tailwind", "next.js", "nuxt",
    "machine learning", "deep learning", "neural networks", "nlp",
    "natural language processing", "computer vision", "data science",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras",
    "matplotlib", "seaborn", "jupyter",
    "sql", "mysql", "postgresql", "mongodb", "redis", "sqlite",
    "oracle", "cassandra", "firebase",
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes",
    "jenkins", "git", "github", "gitlab", "ci/cd", "linux", "bash",
    "rest api", "graphql", "microservices", "agile", "scrum",
    "object oriented programming", "data structures", "algorithms",
    "system design", "excel", "tableau", "power bi"
]

# ── Helpers ──
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
    return [skill for skill in SKILLS_DB if skill.lower() in text_lower]

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

    word_count = len(text.split())
    if word_count >= 400: content_score = 20
    elif word_count >= 200: content_score = 12
    elif word_count >= 100: content_score = 6
    else: content_score = 2
    breakdown['content_length'] = {'score': content_score, 'max': 20, 'word_count': word_count}
    score += content_score

    skills_count = len(skills_found)
    if skills_count >= 15: skills_score = 40
    elif skills_count >= 10: skills_score = 30
    elif skills_count >= 5: skills_score = 20
    elif skills_count >= 2: skills_score = 10
    else: skills_score = 0
    breakdown['skills_match'] = {'score': skills_score, 'max': 40, 'skills_found': skills_count}
    score += skills_score

    text_lower = text.lower()
    sections = {
        'education': ['education', 'academic', 'qualification', 'degree', 'university', 'college'],
        'experience': ['experience', 'work history', 'employment', 'internship', 'intern'],
        'skills': ['skills', 'technical skills', 'competencies', 'technologies'],
        'projects': ['projects', 'portfolio', 'work samples'],
        'contact': ['email', 'phone', 'linkedin', 'github', 'contact']
    }
    found_sections = []
    for section_name, keywords in sections.items():
        for keyword in keywords:
            if keyword in text_lower:
                found_sections.append(section_name)
                break
    section_score = min(25, len(found_sections) * 5)
    breakdown['sections'] = {'score': section_score, 'max': 25, 'found': found_sections}
    score += section_score

    action_verbs = ['developed', 'built', 'created', 'designed', 'implemented',
                    'managed', 'led', 'improved', 'achieved', 'delivered',
                    'optimized', 'analyzed', 'collaborated', 'mentored']
    verb_count = sum(1 for verb in action_verbs if verb in text_lower)
    has_numbers = bool(re.search(r'\d+%|\d+ years|\d+\+', text))
    format_score = min(10, verb_count * 2)
    if has_numbers: format_score += 5
    format_score = min(15, format_score)
    breakdown['formatting'] = {'score': format_score, 'max': 15, 'action_verbs_found': verb_count, 'has_quantified_results': has_numbers}
    score += format_score

    return min(100, score), breakdown

def generate_recommendations(breakdown, skills_found, text):
    recs = []
    if breakdown['content_length']['word_count'] < 400:
        recs.append("📝 Add more detail to your experience and project descriptions. Aim for 400+ words.")
    if breakdown['skills_match']['skills_found'] < 10:
        recs.append("🔧 Add more technical skills relevant to your target role.")
    if 'education' not in breakdown['sections']['found']:
        recs.append("🎓 Add an Education section with your degree, institution, and graduation year.")
    if 'experience' not in breakdown['sections']['found']:
        recs.append("💼 Add a Work Experience or Internships section.")
    if 'contact' not in breakdown['sections']['found']:
        recs.append("📧 Make sure your email, phone number, and LinkedIn/GitHub are clearly listed.")
    if not breakdown['formatting']['has_quantified_results']:
        recs.append("📊 Add numbers to your achievements (e.g., 'Improved performance by 30%').")
    if breakdown['formatting']['action_verbs_found'] < 3:
        recs.append("⚡ Start bullet points with strong action verbs like: Developed, Built, Designed, Led.")
    if not recs:
        recs.append("✅ Great resume! Consider tailoring skills to specific job descriptions.")
    return recs

# ============================================================
# ROUTE 1: Health Check
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
# ROUTE 2: Analyze Resume (Main Route — now with AI)
# ============================================================
@app.route('/analyze', methods=['POST'])
def analyze_resume():
    # ── Validate file ──
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded.'}), 400
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No file selected.'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'Only PDF files are allowed.'}), 400

    # ── Get optional parameters from frontend ──
    # The frontend can now send a target job role for personalized AI advice
    job_role = request.form.get('job_role', '')
    # ai_enabled lets the frontend choose whether to call AI
    # Default True — can be set to False for quick test runs
    ai_enabled = request.form.get('ai_enabled', 'true').lower() == 'true'

    # ── Save file ──
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # ── Extract text ──
    try:
        resume_text = extract_text_from_pdf(filepath)
    except Exception as e:
        return jsonify({'error': f'Could not read PDF: {str(e)}'}), 500

    if not resume_text or len(resume_text.strip()) < 50:
        return jsonify({'error': 'Could not extract text. Use a text-based PDF, not a scanned image.'}), 400

    # ── Traditional scoring (fast, always runs) ──
    skills_found = detect_skills(resume_text)
    ats_score, score_breakdown = calculate_ats_score(resume_text, skills_found)
    contact_info = extract_contact_info(resume_text)
    recommendations = generate_recommendations(score_breakdown, skills_found, resume_text)

    # ── AI Analysis (Groq — runs if enabled and API key exists) ──
    ai_analysis = None
    ai_error = None

    if ai_enabled and os.environ.get("GROQ_API_KEY"):
        ai_result = analyze_with_ai(resume_text, skills_found, ats_score, job_role)
        if "error" in ai_result and len(ai_result) == 1:
            ai_error = ai_result["error"]
        else:
            ai_analysis = ai_result
    elif not os.environ.get("GROQ_API_KEY"):
        ai_error = "GROQ_API_KEY not configured on server."

    # ── Cleanup uploaded file ──
    try:
        os.remove(filepath)
    except:
        pass

    # ── Build and return combined response ──
    return jsonify({
        # Traditional analysis (always present)
        'success': True,
        'ats_score': ats_score,
        'skills_found': skills_found,
        'skills_count': len(skills_found),
        'contact_info': contact_info,
        'score_breakdown': score_breakdown,
        'recommendations': recommendations,
        'word_count': len(resume_text.split()),
        'text_preview': resume_text[:500],

        # AI analysis (present if Groq call succeeded)
        'ai_analysis': ai_analysis,
        'ai_error': ai_error,
        'ai_enabled': ai_enabled and bool(os.environ.get("GROQ_API_KEY")),
        'job_role': job_role,
    })

# ============================================================
# ROUTE 3: Rewrite a single bullet point (NEW)
# ============================================================
@app.route('/rewrite', methods=['POST'])
def rewrite_bullet():
    """
    Accepts a single bullet point and returns an AI-improved version.
    Frontend sends: { "text": "worked on projects", "context": "backend developer" }
    """
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Send JSON with "text" field.'}), 400

    bullet_text = data.get('text', '').strip()
    context = data.get('context', '')

    if len(bullet_text) < 5:
        return jsonify({'error': 'Text too short.'}), 400
    if len(bullet_text) > 500:
        return jsonify({'error': 'Text too long (max 500 chars).'}), 400

    if not os.environ.get("GROQ_API_KEY"):
        return jsonify({'error': 'AI not configured on server.'}), 503

    result = rewrite_bullet_point(bullet_text, context)
    return jsonify(result)

# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')