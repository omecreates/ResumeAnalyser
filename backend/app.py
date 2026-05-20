import os
import re
import json
import nltk
import pdfplumber

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('punkt_tab', quiet=True)

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    found_skills = []

    for skill in SKILLS_DB:

        if skill.lower() in text_lower:
            found_skills.append(skill)

    return found_skills

def calculate_ats_score(text, skills_found):

    score = 0
    breakdown = {}

    word_count = len(text.split())

    if word_count >= 400:
        content_score = 20

    elif word_count >= 200:
        content_score = 12

    elif word_count >= 100:
        content_score = 6

    else:
        content_score = 2

    breakdown['content_length'] = {
        'score': content_score,
        'max': 20,
        'word_count': word_count
    }

    score += content_score

    skills_count = len(skills_found)

    if skills_count >= 15:
        skills_score = 40

    elif skills_count >= 10:
        skills_score = 30

    elif skills_count >= 5:
        skills_score = 20

    elif skills_count >= 2:
        skills_score = 10

    else:
        skills_score = 0

    breakdown['skills_match'] = {
        'score': skills_score,
        'max': 40,
        'skills_found': skills_count
    }

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

    breakdown['sections'] = {
        'score': section_score,
        'max': 25,
        'found': found_sections
    }

    score += section_score

    action_verbs = [
        'developed', 'built', 'created', 'designed', 'implemented',
        'managed', 'led', 'improved', 'achieved', 'delivered',
        'optimized', 'analyzed', 'collaborated', 'mentored'
    ]

    verb_count = sum(1 for verb in action_verbs if verb in text_lower)

    has_numbers = bool(re.search(r'\d+%|\d+ years|\d+\+', text))

    format_score = min(10, verb_count * 2)

    if has_numbers:
        format_score += 5

    format_score = min(15, format_score)

    breakdown['formatting'] = {
        'score': format_score,
        'max': 15,
        'action_verbs_found': verb_count,
        'has_quantified_results': has_numbers
    }

    score += format_score

    return min(100, score), breakdown

def extract_contact_info(text):

    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'

    emails = re.findall(email_pattern, text)
    phones = re.findall(phone_pattern, text)

    return {
        'email': emails[0] if emails else None,
        'phone': phones[0] if phones else None
    }

def generate_recommendations(breakdown, skills_found, text):

    recs = []

    if breakdown['content_length']['word_count'] < 400:
        recs.append("📝 Add more detail to your experience and project descriptions. Aim for 400+ words.")

    if breakdown['skills_match']['skills_found'] < 10:
        recs.append("🔧 Add more technical skills relevant to your target role. Include tools, languages, and frameworks.")

    if 'education' not in breakdown['sections']['found']:
        recs.append("🎓 Add an Education section with your degree, institution, and graduation year.")

    if 'experience' not in breakdown['sections']['found']:
        recs.append("💼 Add a Work Experience or Internships section.")

    if 'contact' not in breakdown['sections']['found']:
        recs.append("📧 Make sure your email, phone number, and LinkedIn/GitHub are clearly listed.")

    if not breakdown['formatting']['has_quantified_results']:
        recs.append("📊 Add numbers to your achievements (e.g., 'Improved performance by 30%', 'Built app used by 500+ users').")

    if breakdown['formatting']['action_verbs_found'] < 3:
        recs.append("⚡ Start bullet points with strong action verbs like: Developed, Built, Designed, Led, Optimized.")

    if not recs:
        recs.append("✅ Great resume! Consider tailoring skills to specific job descriptions for even better ATS scores.")

    return recs

@app.route('/health', methods=['GET'])
def health_check():

    return jsonify({
        'status': 'ok',
        'message': 'Resume Analyzer API is running! 🚀'
    })

@app.route('/analyze', methods=['POST'])
def analyze_resume():

    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded. Please upload a resume PDF.'}), 400

    file = request.files['resume']

    if file.filename == '':
        return jsonify({'error': 'No file selected.'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Only PDF files are allowed.'}), 400

    filename = secure_filename(file.filename)

    filepath = os.path.join(
        app.config['UPLOAD_FOLDER'],
        filename
    )

    file.save(filepath)

    try:
        resume_text = extract_text_from_pdf(filepath)

    except Exception as e:
        return jsonify({'error': f'Could not read PDF: {str(e)}'}), 500

    if not resume_text or len(resume_text.strip()) < 50:

        return jsonify({
            'error': 'Could not extract text from this PDF. It may be a scanned image. Please use a text-based PDF.'
        }), 400

    skills_found = detect_skills(resume_text)

    ats_score, score_breakdown = calculate_ats_score(
        resume_text,
        skills_found
    )

    contact_info = extract_contact_info(resume_text)

    recommendations = generate_recommendations(
        score_breakdown,
        skills_found,
        resume_text
    )

    try:
        os.remove(filepath)

    except:
        pass

    return jsonify({
        'success': True,
        'ats_score': ats_score,
        'skills_found': skills_found,
        'skills_count': len(skills_found),
        'contact_info': contact_info,
        'score_breakdown': score_breakdown,
        'recommendations': recommendations,
        'word_count': len(resume_text.split()),
        'text_preview': resume_text[:500]
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')