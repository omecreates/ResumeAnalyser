# ============================================================
# ai_analyzer.py — AI-Powered Resume Analysis using Groq
# ============================================================
#
# This file handles ALL communication with the Groq AI API.
# We keep it separate from app.py so the code stays clean
# and you can easily swap to OpenAI/Gemini later.
#
# GROQ runs Llama 3.1 (Meta's best open-source model) for FREE.
# It's extremely fast — responses come back in 1-2 seconds.
# ============================================================

import os
import json
from groq import Groq
from dotenv import load_dotenv

# load_dotenv() reads your .env file and makes the variables
# available via os.environ. Without this, GROQ_API_KEY would
# return None and the API call would fail.
load_dotenv()

# Initialize the Groq client with your API key
# The client automatically reads GROQ_API_KEY from environment
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ============================================================
# MODEL SELECTION
# ============================================================
# llama-3.1-8b-instant  → faster, good quality, higher rate limits
# llama-3.1-70b-versatile → slower, better quality, lower rate limits
#
# For a student project, start with 8b-instant (faster + more free calls)
# Upgrade to 70b when you want better analysis quality
MODEL = "llama-3.1-8b-instant"

# ============================================================
# MASTER PROMPT BUILDER
# ============================================================
# This is the most important function — it builds the prompt
# that tells the AI exactly what to analyze and how to respond.
#
# PROMPT ENGINEERING PRINCIPLES USED HERE:
# 1. Role assignment: "You are a senior HR expert..." (sets context)
# 2. Structured output: Ask for JSON so we can parse it
# 3. Specificity: Tell it exactly what sections to include
# 4. Constraints: Tell it what NOT to do (no generic advice)
# 5. Examples embedded in instructions: guides the quality
# ============================================================

def build_analysis_prompt(resume_text, skills_found, ats_score, job_role=""):
    """
    Builds a detailed prompt for the AI to analyze a resume.
    
    Args:
        resume_text (str): The extracted text from the resume PDF
        skills_found (list): Skills already detected by our scorer
        ats_score (int): The ATS score we already calculated
        job_role (str): Optional target job role from the user
    
    Returns:
        str: The complete prompt to send to Groq
    """
    
    role_context = f"The candidate is targeting a role as: {job_role}." if job_role else ""
    skills_list = ", ".join(skills_found) if skills_found else "none detected"
    
    prompt = f"""You are a world-class resume coach and senior HR professional with 15+ years of experience 
hiring for top tech companies. You have reviewed thousands of resumes and know exactly what ATS systems 
and hiring managers look for.

Analyze this resume thoroughly and provide actionable, personalized feedback.

{role_context}

--- RESUME TEXT START ---
{resume_text[:3000]}
--- RESUME TEXT END ---

Context:
- Pre-calculated ATS Score: {ats_score}/100
- Skills already detected: {skills_list}

Your task: Provide a DEEP, PERSONALIZED analysis in the following JSON format.
Be specific to THIS resume — do not give generic advice.
Reference actual content from the resume in your feedback.

Respond ONLY with valid JSON, no markdown, no explanation outside the JSON:

{{
  "overall_assessment": "2-3 sentence honest overall assessment of this specific resume",
  
  "strengths": [
    "Specific strength 1 with reference to actual resume content",
    "Specific strength 2",
    "Specific strength 3"
  ],
  
  "critical_weaknesses": [
    "Most critical weakness that is hurting this resume",
    "Second weakness",
    "Third weakness"
  ],
  
  "missing_skills": [
    "Important skill missing from this resume for modern tech roles",
    "Another missing skill",
    "Another missing skill",
    "Another missing skill",
    "Another missing skill"
  ],
  
  "improved_bullet_points": [
    {{
      "original": "Exact bullet point or sentence from the resume that is weak",
      "improved": "Professionally rewritten version with action verb, metrics, and impact",
      "why": "Brief explanation of what made it better"
    }},
    {{
      "original": "Another weak line from the resume",
      "improved": "Rewritten version",
      "why": "Explanation"
    }},
    {{
      "original": "Third weak line",
      "improved": "Rewritten version", 
      "why": "Explanation"
    }}
  ],
  
  "section_feedback": {{
    "summary": "Specific feedback on the summary/objective section, or note if missing",
    "experience": "Specific feedback on work experience section",
    "education": "Specific feedback on education section",
    "skills": "Specific feedback on skills section",
    "projects": "Specific feedback on projects section, or note if missing"
  }},
  
  "ats_optimization_tips": [
    "Specific ATS tip 1 based on what you see in this resume",
    "Specific ATS tip 2",
    "Specific ATS tip 3"
  ],
  
  "career_advice": [
    "Personalized career advice based on their background and skills",
    "Second piece of career advice",
    "Third piece of advice"
  ],
  
  "score_justification": "Explain in 2 sentences why this resume scored {ats_score}/100 and what the top 2 changes would be to improve it",
  
  "priority_actions": [
    {{
      "action": "The single most impactful change to make",
      "impact": "high",
      "effort": "low",
      "description": "Detailed instruction on how to make this change"
    }},
    {{
      "action": "Second priority action",
      "impact": "high", 
      "effort": "medium",
      "description": "How to do it"
    }},
    {{
      "action": "Third priority action",
      "impact": "medium",
      "effort": "low",
      "description": "How to do it"
    }}
  ],
  
  "estimated_score_after_fixes": 0
}}

IMPORTANT RULES:
- Be specific to THIS resume. Quote actual text from it.
- For improved_bullet_points, only use lines that actually appear in the resume
- estimated_score_after_fixes should be a realistic number between {ats_score} and 95
- impact values: "high", "medium", "low"
- effort values: "high", "medium", "low"
- All arrays must have the specified number of items minimum
- Return ONLY the JSON object, nothing else"""

    return prompt


# ============================================================
# MAIN ANALYSIS FUNCTION
# ============================================================

def analyze_with_ai(resume_text, skills_found, ats_score, job_role=""):
    """
    Sends the resume to Groq AI and returns structured analysis.
    
    This is the main function called by app.py.
    
    Returns:
        dict: Parsed AI analysis, or error dict if something fails
    """
    
    # Safety check: don't send empty resumes
    if not resume_text or len(resume_text.strip()) < 100:
        return {"error": "Resume text too short for AI analysis"}
    
    # Build our carefully crafted prompt
    prompt = build_analysis_prompt(resume_text, skills_found, ats_score, job_role)
    
    try:
        # ── API CALL TO GROQ ──
        # This sends our prompt to Llama 3.1 and waits for response
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    # System message sets the AI's behavior globally
                    "role": "system",
                    "content": "You are an expert resume coach. Always respond with valid JSON only. No markdown formatting, no code blocks, no explanation. Just the raw JSON object."
                },
                {
                    # User message is the actual request
                    "role": "user", 
                    "content": prompt
                }
            ],
            temperature=0.7,
            # temperature: 0 = very consistent/deterministic
            #              1 = more creative/varied
            # 0.7 gives us good, varied advice without being too random
            
            max_tokens=2000,
            # max_tokens limits response length and cost
            # 2000 tokens ≈ 1500 words, enough for our full analysis
        )
        
        # Extract the text response from the API result
        response_text = completion.choices[0].message.content.strip()
        
        # Clean up: sometimes models add markdown code blocks
        # even when told not to. We strip those here.
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            # Remove first line (```json) and last line (```)
            response_text = "\n".join(lines[1:-1])
        
        # Parse the JSON string into a Python dictionary
        analysis = json.loads(response_text)
        
        # Add metadata about the AI used
        analysis["ai_model"] = MODEL
        analysis["ai_provider"] = "Groq (Llama 3.1)"
        
        return analysis
        
    except json.JSONDecodeError as e:
        # AI didn't return valid JSON — this can happen occasionally
        # We return a safe fallback instead of crashing
        print(f"JSON parse error: {e}")
        print(f"Raw response: {response_text[:200]}")
        return {
            "error": "AI returned invalid format. Please try again.",
            "overall_assessment": "Analysis failed to parse. Please retry.",
            "strengths": [],
            "critical_weaknesses": [],
            "missing_skills": [],
            "improved_bullet_points": [],
            "section_feedback": {},
            "ats_optimization_tips": [],
            "career_advice": [],
            "score_justification": "",
            "priority_actions": [],
            "estimated_score_after_fixes": ats_score + 10
        }
        
    except Exception as e:
        # Network error, rate limit, invalid API key, etc.
        error_msg = str(e)
        print(f"Groq API error: {error_msg}")
        
        # Give user a helpful message based on error type
        if "rate_limit" in error_msg.lower():
            user_msg = "AI rate limit reached. Please wait 1 minute and try again."
        elif "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
            user_msg = "AI API key is invalid or missing. Check your .env file."
        elif "timeout" in error_msg.lower():
            user_msg = "AI request timed out. Please try again."
        else:
            user_msg = f"AI analysis unavailable: {error_msg}"
        
        return {"error": user_msg}


# ============================================================
# QUICK REWRITE FUNCTION (Bonus Feature)
# ============================================================
# This lets users paste a single bullet point and get it rewritten.
# Called from a separate API endpoint: POST /rewrite

def rewrite_bullet_point(bullet_text, context=""):
    """
    Rewrites a single resume bullet point to be more impactful.
    
    Args:
        bullet_text (str): The original bullet point text
        context (str): Optional context about their role/industry
    
    Returns:
        dict: { original, rewritten, explanation }
    """
    prompt = f"""Rewrite this resume bullet point to be more impactful.
Use: strong action verb + specific task + measurable result/impact.

Original: {bullet_text}
Context: {context if context else "software/tech role"}

Respond in JSON only:
{{
  "rewritten": "The improved bullet point",
  "explanation": "What you changed and why",
  "action_verb_used": "The strong action verb you chose",
  "alternative": "A second version with different emphasis"
}}"""

    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a professional resume writer. Return JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=400,
        )
        response_text = completion.choices[0].message.content.strip()
        if response_text.startswith("```"):
            response_text = "\n".join(response_text.split("\n")[1:-1])
        return json.loads(response_text)
    except Exception as e:
        return {"error": str(e), "rewritten": bullet_text}