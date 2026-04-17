class ResumeScorer:
    def __init__(self, skill_weight=0.8, project_weight=0.2, max_projects=5):
        self.skill_weight = skill_weight
        self.project_weight = project_weight
        self.max_projects = max_projects

    def calculate_score(self, match_percentage, project_count):
        skill_score = self._calculate_skill_score(match_percentage)
        project_score = self._calculate_project_score(project_count)
        total_score = skill_score + project_score
        return round(min(total_score, 100), 2)

    def _calculate_skill_score(self, match_percentage):
        return max(0, min(match_percentage, 100)) * self.skill_weight

    def _calculate_project_score(self, project_count):
        if self.max_projects <= 0:
            return 0.0

        normalized_projects = min(max(project_count, 0), self.max_projects) / self.max_projects
        return normalized_projects * (self.project_weight * 100)
