from flask import (
    Flask,
    render_template,
    request,
    jsonify
)

import google.generativeai as genai
import os
import re

from dotenv import load_dotenv
from PyPDF2 import PdfReader
from werkzeug.utils import secure_filename

import markdown


# ====================================
# LOAD ENVIRONMENT VARIABLES
# ====================================

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)


# ====================================
# FLASK APP
# ====================================

app = Flask(__name__)

app.secret_key = "ats_ai_secret"

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


# ====================================
# UPLOAD FOLDER
# ====================================

UPLOAD_FOLDER = "static/uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# ====================================
# ALLOWED FILE TYPES
# ====================================

ALLOWED_EXTENSIONS = {
    "pdf",
    "txt"
}


def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# ====================================
# EXTRACT RESUME TEXT
# ====================================

def extract_resume_text(filepath):

    text = ""

    try:

        if filepath.endswith(".pdf"):

            pdf = PdfReader(filepath)

            for page in pdf.pages:

                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

        elif filepath.endswith(".txt"):

            with open(
                filepath,
                "r",
                encoding="utf-8"
            ) as file:

                text = file.read()

    except Exception as e:

        text = f"Error reading file: {str(e)}"

    return text


# ====================================
# GEMINI RESUME ANALYSIS
# ====================================

def analyze_resume_with_ai(text):

    prompt = f"""
You are an expert ATS Resume Analyzer.

Analyze the following resume professionally.

Provide:

# ATS Score
Give ATS score out of 100.

# Technical Skills

# Strengths

# Weaknesses

# Missing Keywords

# Resume Formatting Review

# Improvement Suggestions

# Final Verdict

Return response in clean markdown.

Resume Content:

{text}
"""

    try:

        response = model.generate_content(
            prompt
        )

        return response.text

    except Exception as e:

        return f"""
# Error

Gemini API Error:

{str(e)}
"""


# ====================================
# HOME PAGE
# ====================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ====================================
# LOGIN PAGE
# ====================================

@app.route("/login")
def login():

    return render_template(
        "login.html"
    )


# ====================================
# ABOUT PAGE
# ====================================

@app.route("/about")
def about():

    return render_template(
        "about.html"
    )


# ====================================
# DASHBOARD PAGE
# ====================================

@app.route("/dashboard")
def dashboard():

    return render_template(
        "dashboard.html"
    )


# ====================================
# RESUME SCAN PAGE
# ====================================

@app.route(
    "/resume_scan",
    methods=["GET", "POST"]
)
def resume_scan():

    analysis = ""
    ats_score = 0

    if request.method == "POST":

        uploaded_file = request.files.get(
            "resume_file"
        )

        if (
            uploaded_file
            and uploaded_file.filename != ""
            and allowed_file(
                uploaded_file.filename
            )
        ):

            filename = secure_filename(
                uploaded_file.filename
            )

            filepath = os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )

            uploaded_file.save(
                filepath
            )

            resume_text = extract_resume_text(
                filepath
            )

            raw_analysis = analyze_resume_with_ai(
                resume_text
            )

            score_match = re.search(
                r'ATS Score.*?(\d+)',
                raw_analysis,
                re.IGNORECASE | re.DOTALL
            )

            if score_match:

                ats_score = int(
                    score_match.group(1)
                )

            else:

                ats_score = 75

            analysis = markdown.markdown(
                raw_analysis
            )

    return render_template(
        "resume_scan.html",
        analysis=analysis,
        ats_score=ats_score
    )


# ====================================
# AI ASSISTANT PAGE
# ====================================

@app.route("/assistant")
def assistant():

    return render_template(
        "assistant.html"
    )


# ====================================
# CHAT API
# ====================================

@app.route(
    "/chat",
    methods=["POST"]
)
def chat():

    data = request.get_json()

    if not data:

        return jsonify({
            "reply": "No message received."
        })

    user_message = data.get(
        "message",
        ""
    )

    prompt = f"""
You are a professional AI Career Assistant.

Help users with:

- Resume Improvement
- ATS Optimization
- Interview Preparation
- Career Guidance
- DSA Roadmap
- AI/ML Roadmap
- Web Development
- Skill Development

User Question:

{user_message}
"""

    try:

        response = model.generate_content(
            prompt
        )

        reply = response.text

    except Exception as e:

        reply = f"Error communicating with Gemini: {str(e)}"

    return jsonify({
        "reply": reply
    })


# ====================================
# MAIN
# ====================================

if __name__ == "__main__":

    app.run(
        debug=True
    )