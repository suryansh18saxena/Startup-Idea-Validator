import os
from dotenv import load_dotenv
import google.generativeai as genai
from .models import Ideas
import requests

load_dotenv()  # Load environment variables from .env file

def _extract_gemini_response(response):
    """Safely extract text from a Gemini API response, with proper error handling."""
    response_data = response.json()

    # Check if the API returned an error
    if "error" in response_data:
        error_msg = response_data["error"].get("message", "Unknown API error")
        raise Exception(f"Gemini API error: {error_msg}")

    # Check if the response was blocked by safety filters
    if "promptFeedback" in response_data:
        block_reason = response_data["promptFeedback"].get("blockReason", "")
        if block_reason:
            raise Exception(f"Request blocked by Gemini safety filters: {block_reason}")

    # Check if candidates exist
    if "candidates" not in response_data or not response_data["candidates"]:
        raise Exception(f"No candidates in Gemini response. Full response: {response_data}")

    candidate = response_data["candidates"][0]

    # Check if the candidate was blocked
    finish_reason = candidate.get("finishReason", "")
    if finish_reason == "SAFETY":
        raise Exception("Response blocked by Gemini safety filters (finish reason: SAFETY)")

    if "content" not in candidate or "parts" not in candidate["content"]:
        raise Exception(f"Unexpected candidate structure: {candidate}")

    return candidate["content"]["parts"][0]["text"]


def get_swot_analysis(idea: Ideas):
    try:

        idea_details = f"""
        Problem Statement: {idea.problem_statement}
        Solution: {idea.solution}
        Target Market: {idea.market}
        Unique Value Proposition: {idea.unique_value}
        Revenue Model: {idea.revenue_model}
        Known Competitors: {idea.known_competitors}
        """

        prompt = f"""You are an expert Startup Analyst and Business Strategist.
Analyze the following startup idea and provide a detailed SWOT analysis. Be thorough, honest, and critical in your assessment. Cover all aspects of the idea comprehensively.

Respond ONLY with a Python list in this exact format:
["strength details", "weakness details", "opportunities details", "threats details", score_strength, score_weakness, score_opportunities, score_threats, overall_score]

Where:
- The first 4 items are detailed text descriptions (strings)
- The next 4 items are numerical scores for each SWOT category (integers 0-100)
- The last item is the overall viability score out of 100 (integer)

Do NOT include any introductory text, explanation, or markdown. Return ONLY the Python list.

Startup Idea:
{idea_details}
"""
        api = "https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key=" + os.getenv("GEMINI_API_KEY")
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(api, json=payload, headers=headers)
        response_text = _extract_gemini_response(response)

        # Clean the response to ensure it's valid Python list
        import ast
        cleaned = response_text.strip().replace('```python', '').replace('```', '').strip()
        result = ast.literal_eval(cleaned)
        print(result)
        return result

    except Exception as e:
        print(f"Error fetching SWOT analysis: {e}")
        # Return a default error message if the API call fails
        error_message = f"Could not generate analysis due to an error: {e}"
        return {
            "strengths": error_message,
            "weaknesses": error_message,
            "opportunities": error_message,
            "threats": error_message,
            "score_strengths": 0,
            "score_weaknesses": 0,
            "score_opportunities": 0,
            "score_threats": 0,
            "score": 0
        }


def generate_prd_content(idea):
    """Generate a Product Requirements Document (PRD) using Gemini AI."""
    try:
        idea_details = f"""
        Problem Statement: {idea.problem_statement}
        Solution: {idea.solution}
        Target Market: {idea.market}
        Unique Value Proposition: {idea.unique_value}
        Revenue Model: {idea.revenue_model}
        """

        prompt = f"""
You are a World-Class Product Manager with 15+ years of experience at top tech companies.
Based on the following startup idea, generate a comprehensive and professional Product Requirements Document (PRD).

{idea_details}

The PRD must include the following sections:
1. Executive Summary
2. Product Vision & Objectives
3. Target Audience & User Personas
4. Problem Statement & Opportunity
5. Proposed Solution & Key Features
6. User Stories & Use Cases
7. Functional Requirements
8. Non-Functional Requirements (Performance, Security, Scalability)
9. Tech Stack Recommendations
10. MVP Scope & Phased Rollout Plan
11. Success Metrics & KPIs
12. Risks & Mitigation Strategies
13. Timeline & Milestones

IMPORTANT FORMATTING RULES:
- Return the response in clean HTML format using tags like <h1>, <h2>, <h3>, <p>, <ul>, <li>, <ol>, <table>, <tr>, <th>, <td>, <strong>, <em>.
- Do NOT wrap the response in markdown code blocks like ```html or ```.
- Do NOT use any markdown formatting whatsoever.
- Start directly with the HTML content.
- Make the content detailed, actionable, and professional.
"""

        api = "https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key=" + os.getenv("GEMINI_API_KEY")
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(api, json=payload, headers=headers)
        prd_html = _extract_gemini_response(response)

        # Clean up any accidental markdown code block wrappers
        prd_html = prd_html.strip()
        if prd_html.startswith("```html"):
            prd_html = prd_html[7:]
        if prd_html.startswith("```"):
            prd_html = prd_html[3:]
        if prd_html.endswith("```"):
            prd_html = prd_html[:-3]
        prd_html = prd_html.strip()

        return prd_html

    except Exception as e:
        print(f"Error generating PRD: {e}")
        return f"<h2>Error</h2><p>Could not generate PRD due to an error: {e}</p>"


def check_idea_similarity(problem, solution, market, existing_ideas_text=""):
    """Check if a startup idea already exists using AI analysis."""
    try:
        prompt = f"""You are an expert Silicon Valley Startup Analyst and Tech Evaluator.
A founder has submitted the following startup idea:
Problem: {problem}
Solution: {solution}
Target Market: {market}

Here are some ideas already submitted on this platform for internal comparison:
{existing_ideas_text if existing_ideas_text else "No previous ideas found."}

Your job is to search your knowledge base (Internet, GitHub, Startup Databases like Crunchbase/YC) and determine if this idea already exists.

Analyze the idea and respond ONLY in valid JSON format with the following keys:
1. "similarity_percentage": A number between 0 to 100 representing how close this is to existing projects.
2. "existing_competitors": A list of 2-3 real companies, tools, or GitHub repositories already doing this. (If none, put ["None found"]).
3. "unique_angle": Identify one specific thing the founder mentioned that makes their approach unique.
4. "improvement_suggestion": Suggest one killer, highly specific feature they can add to make this idea completely unique and hard to copy.

Do not include any markdown formatting, backticks, or extra text. Output strict JSON only."""

        api = "https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key=" + os.getenv("GEMINI_API_KEY")
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(api, json=payload, headers=headers)
        raw_text = _extract_gemini_response(response)

        # Clean up any accidental markdown wrappers
        raw_text = raw_text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()

        import json
        result = json.loads(raw_text)
        print(f"Similarity Check Result: {result}")
        return result

    except Exception as e:
        print(f"Error checking idea similarity: {e}")
        return {
            "similarity_percentage": 0,
            "existing_competitors": ["Could not fetch data"],
            "unique_angle": "Analysis unavailable due to an error.",
            "improvement_suggestion": "Please try again later."
        }


def edit_prd_with_ai(current_prd_content, user_instruction):
    """Use Gemini AI to apply user-requested changes to a PRD document."""
    try:
        prompt = f"""You are a World-Class Product Manager and Document Editor.
You are given an existing Product Requirements Document (PRD) in HTML format, and a user instruction describing what changes to make.

CURRENT PRD CONTENT:
{current_prd_content}

USER INSTRUCTION:
{user_instruction}

YOUR TASK:
- Apply the user's requested changes to the PRD document.
- Keep all existing content that the user did NOT ask to change.
- Maintain the same HTML formatting style (h1, h2, h3, p, ul, li, ol, table, tr, th, td, strong, em).
- If the user asks to add a new section, integrate it logically into the existing structure.
- If the user asks to modify or rewrite a section, update only that section.
- If the user asks to remove something, remove it cleanly.

IMPORTANT FORMATTING RULES:
- Return the COMPLETE updated PRD in clean HTML format.
- Do NOT wrap the response in markdown code blocks like ```html or ```.
- Do NOT use any markdown formatting whatsoever.
- Start directly with the HTML content.
- Return the FULL document, not just the changed parts.
"""

        api = "https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key=" + os.getenv("GEMINI_API_KEY")
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(api, json=payload, headers=headers)
        updated_html = _extract_gemini_response(response)

        # Clean up any accidental markdown code block wrappers
        updated_html = updated_html.strip()
        if updated_html.startswith("```html"):
            updated_html = updated_html[7:]
        if updated_html.startswith("```"):
            updated_html = updated_html[3:]
        if updated_html.endswith("```"):
            updated_html = updated_html[:-3]
        updated_html = updated_html.strip()

        return {"success": True, "updated_content": updated_html}

    except Exception as e:
        print(f"Error editing PRD with AI: {e}")
        return {"success": False, "error": str(e)}