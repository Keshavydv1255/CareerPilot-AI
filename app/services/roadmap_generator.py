class RoadmapGenerator:

    @staticmethod
    def generate(skill_gap):

        roadmap = []

        week = 1

        for skill in skill_gap["priority"]:

            roadmap.append({
                "week": week,
                "topic": skill
            })

            week += 1

        return roadmap