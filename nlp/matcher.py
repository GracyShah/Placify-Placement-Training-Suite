class SkillMatcher:
    @staticmethod
    def match(resume_skills, job_skills):
        normalized_resume_skills = SkillMatcher._normalize_skills(resume_skills)
        normalized_job_skills = SkillMatcher._normalize_skills(job_skills)

        matched = sorted(normalized_resume_skills & normalized_job_skills)
        match_percentage = SkillMatcher._calculate_match_percentage(matched, normalized_job_skills)

        return {
            "matched_skills": matched,
            "match_percentage": match_percentage,
        }

    @staticmethod
    def _normalize_skills(skills):
        return {skill.strip().lower() for skill in skills if skill and skill.strip()}

    @staticmethod
    def _calculate_match_percentage(matched_skills, job_skills):
        if not job_skills:
            return 0.0

        return round((len(matched_skills) / len(job_skills)) * 100, 2)
