import json
import re

from app.services.gemini_service import ask_gemini, gemini_failed


KNOWN_SKILLS = [
    "C", "C++", "Python", "Java", "JavaScript", "HTML", "HTML5", "CSS", "CSS3",
    "SQL", "MySQL", "FastAPI", "Flask", "Django", "React", "Git", "GitHub",
    "Docker", "AWS", "Linux", "Data Structures", "Algorithms", "DSA", "DBMS",
    "Operating Systems", "Computer Networks", "Generative AI", "LLM", "Cloud Computing",
]


class ResumeAnalyzer:
    @staticmethod
    def _local_fallback(resume_text: str) -> dict:
        text = resume_text or ""
        lower = text.lower()

        skills = []
        for skill in KNOWN_SKILLS:
            pattern = re.escape(skill.lower())
            if re.search(rf"(?<!\w){pattern}(?!\w)", lower):
                normalized = "HTML" if skill == "HTML5" else "CSS" if skill == "CSS3" else skill
                if normalized not in skills:
                    skills.append(normalized)

        sections = {
            "education": "education" in lower,
            "experience": any(word in lower for word in ("experience", "internship", "intern")),
            "projects": "project" in lower,
            "skills": "skill" in lower,
            "contact": bool(re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", text)) and bool(re.search(r"\b\d{10}\b", re.sub(r"\D", "", text))),
            "links": "github" in lower or "linkedin" in lower,
        }

        score = 35
        score += min(len(skills) * 2, 20)
        score += sum(7 for present in sections.values() if present)
        score += 5 if len(text) > 1200 else 0
        score = max(35, min(score, 88))

        strengths = []
        if skills:
            strengths.append(f"Shows a broad technical foundation with {len(skills)} identifiable skills.")
        if sections["projects"]:
            strengths.append("Includes project work that can support technical interview discussions.")
        if sections["experience"]:
            strengths.append("Includes internship or practical experience.")
        if sections["links"]:
            strengths.append("Provides professional profile or portfolio links.")
        if not strengths:
            strengths.append("The resume contains enough text for a basic structural review.")

        weaknesses = []
        if not sections["projects"]:
            weaknesses.append("A clearly labelled projects section was not detected.")
        if not sections["experience"]:
            weaknesses.append("Practical experience or internships are not clearly highlighted.")
        if not sections["links"]:
            weaknesses.append("GitHub or LinkedIn links are not clearly visible.")
        if len(skills) < 5:
            weaknesses.append("The technical skills section could be more specific and keyword-rich.")
        if not weaknesses:
            weaknesses.append("Some bullet points may still benefit from stronger metrics and outcomes.")

        suggestions = [
            "Use concise action-led bullet points and quantify impact wherever the source resume supports it.",
            "Keep section headings ATS-friendly: Summary, Education, Skills, Experience and Projects.",
            "Tailor technical keywords to each target job description without adding skills you do not possess.",
        ]

        return {
            "score": score,
            "summary": (
                "A structured local ATS review was generated because the external AI service was temporarily unavailable. "
                "The resume demonstrates a student/fresher profile with technical skills, education and practical project or internship exposure."
            ),
            "skills": skills,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "suggestions": suggestions,
            "analysis_source": "local_fallback",
        }

    @staticmethod
    def analyze(resume_text: str) -> dict:
        prompt = f"""
You are an expert ATS Resume Reviewer.
Analyze the resume and return ONLY valid JSON with this exact structure:
{{
  "score": 0,
  "summary": "",
  "skills": [],
  "strengths": [],
  "weaknesses": [],
  "suggestions": []
}}
Rules:
- score must be an integer from 0 to 100.
- Do not invent facts.
- Keep each list concise and practical.

Resume:
{resume_text}
"""

        response = ask_gemini(prompt)
        if gemini_failed(response):
            return ResumeAnalyzer._local_fallback(resume_text)

        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start < 0 or end <= start:
                raise ValueError("No JSON returned")
            data = json.loads(response[start:end])
            data["score"] = max(0, min(int(data.get("score", 0)), 100))
            for key in ("skills", "strengths", "weaknesses", "suggestions"):
                if not isinstance(data.get(key), list):
                    data[key] = []
            data["summary"] = str(data.get("summary", ""))
            data["analysis_source"] = "gemini"
            return data
        except (ValueError, TypeError, json.JSONDecodeError):
            return ResumeAnalyzer._local_fallback(resume_text)
