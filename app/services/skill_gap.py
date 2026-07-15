class SkillGapAnalyzer:

    @staticmethod
    def analyze(found_skills):

        roadmap = [
            "Python",
            "C++",
            "SQL",
            "Git",
            "GitHub",
            "HTML",
            "CSS",
            "JavaScript",
            "React",
            "FastAPI",
            "Docker",
            "Linux",
            "AWS"
        ]

        missing = []

        found_lower = [skill.lower() for skill in found_skills]

        for skill in roadmap:
            if skill.lower() not in found_lower:
                missing.append(skill)

        priority = missing[:5]

        if len(priority) <= 2:
            duration = "2 Weeks"

        elif len(priority) <= 5:
            duration = "1 Month"

        elif len(priority) <= 8:
            duration = "2 Months"

        else:
            duration = "3 Months"

        return {
            "missing_skills": missing,
            "priority": priority,
            "duration": duration
        }