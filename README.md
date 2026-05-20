# 🤖 AI-Powered Resume Analyzer

An intelligent AI-powered web application that analyzes PDF resumes using Natural Language Processing (NLP), extracts technical skills, calculates ATS compatibility scores, and provides actionable recommendations for improvement.

Built using React, Flask, spaCy, NLTK, and scikit-learn.

---

## 🚀 Live Demo

Frontend: https://your-app.vercel.app
Backend API: https://your-backend.onrender.com

---

## ✨ Features

* 📄 Upload PDF resumes
* 🧠 NLP-based skill extraction
* 📊 ATS compatibility score calculation
* 🔍 Resume section analysis
* 💡 Smart improvement recommendations
* 🌙 Modern dark-themed UI
* ⚡ Real-time frontend-backend communication
* 🔐 Secure file handling
* 📱 Responsive design

---

## 🛠️ Tech Stack

### Frontend

* React.js
* Vite
* Axios
* CSS3

### Backend

* Flask
* Flask-CORS
* Gunicorn

### AI / NLP

* spaCy
* NLTK
* scikit-learn

### PDF Processing

* pdfplumber

### Deployment

* Vercel (Frontend)
* Render (Backend)

---

## 📂 Project Structure

```bash
ResumeAnalyser/
│
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── uploads/
│   └── venv/
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── main.jsx
│   │   └── index.css
│   │
│   ├── public/
│   ├── package.json
│   ├── vite.config.js
│   └── .env
│
├── render.yaml
├── .gitignore
└── README.md
```

---

## ⚙️ Installation & Setup

### 1. Clone Repository

```bash
git clone https://github.com/omecreates/ResumeAnalyser.git
cd ResumeAnalyser
```

---

### 2. Backend Setup

```bash
cd backend

python -m venv venv

# Windows
.\venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt

python -m spacy download en_core_web_sm

python app.py
```

Backend runs on:

```bash
http://127.0.0.1:5000
```

---

### 3. Frontend Setup

Open a new terminal:

```bash
cd frontend

npm install

npm run dev
```

Frontend runs on:

```bash
http://localhost:5173
```

---

## 🔌 API Endpoints

### Health Check

```http
GET /health
```

Response:

```json
{
  "status": "ok",
  "message": "Resume Analyzer API is running!"
}
```

---

### Analyze Resume

```http
POST /analyze
```

Upload a PDF resume using multipart/form-data.

Response:

```json
{
  "success": true,
  "ats_score": 85,
  "skills_found": [
    "python",
    "react",
    "flask"
  ],
  "recommendations": [
    "Add more quantified achievements"
  ]
}
```

---

## 🌐 Deployment

### Frontend Deployment (Vercel)

1. Push code to GitHub
2. Import repository into Vercel
3. Set root directory to:

   ```bash
   frontend
   ```
4. Add environment variable:

   ```bash
   VITE_API_URL=https://your-backend.onrender.com
   ```
5. Deploy

---

### Backend Deployment (Render)

1. Connect GitHub repository to Render
2. Render automatically reads:

   ```bash
   render.yaml
   ```
3. Deploy backend service

---

## 🧠 AI Features

* NLP-based resume parsing
* Technical skill detection
* ATS scoring engine
* Resume formatting analysis
* Action verb detection
* Quantified achievement detection
* Smart recommendation generation

---

## 📈 Future Improvements

* AI-powered resume rewriting
* GPT integration
* Job description matching
* Resume ranking system
* User authentication
* Dashboard analytics
* Resume templates
* Export reports

---

## 👨‍💻 Author

Shahid Ali
B.Tech ECE — VIT Chennai

GitHub: https://github.com/omecreates
LinkedIn: https://www.linkedin.com/in/shahid-ali-433353320?utm_source=share_via&utm_content=profile&utm_medium=member_android

---

## 📄 License

This project is licensed under the MIT License.

Feel free to use, modify, and improve the project.
