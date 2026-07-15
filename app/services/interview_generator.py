class InterviewGenerator:

    @staticmethod
    def generate(text: str):

        text = text.lower()

        technical = []

        hr = []

        project = []

        if "python" in text:
            technical.append("Explain Python's advantages over other programming languages.")

        if "c++" in text:
            technical.append("What is the difference between C and C++?")

        if "sql" in text:
            technical.append("Explain INNER JOIN and LEFT JOIN.")

        if "html" in text:
            technical.append("Difference between HTML and HTML5?")

        if "css" in text:
            technical.append("Explain Flexbox and Grid.")

        if "javascript" in text:
            technical.append("Difference between var, let and const.")

        if "fastapi" in text:
            technical.append("Why did you choose FastAPI for your project?")

        if "project" in text:
            project.append("Explain your project from start to finish.")
            project.append("What was the biggest challenge in your project?")
            project.append("How would you improve your project?")

        hr.extend([
            "Tell me about yourself.",
            "Why should we hire you?",
            "Where do you see yourself in 5 years?",
            "What are your strengths and weaknesses?"
        ])

        return {
            "technical": technical,
            "project": project,
            "hr": hr
        }