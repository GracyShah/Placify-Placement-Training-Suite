import re

from data.skills_db import TECHNICAL_SKILLS


class SkillExtractor:
    def __init__(self, skills=None, nlp=None):
        self.skills = skills or TECHNICAL_SKILLS

    def extract_skills(self, text):
        normalized_text = self._normalize_text(text)
        matched_skills = []
        for skill in self.skills:
            normalized_skill = self._normalize_text(skill)
            if normalized_skill and self._contains_skill(normalized_text, normalized_skill):
                matched_skills.append(skill)
        return matched_skills

    def _normalize_text(self, text):
        normalized = re.sub(r"[^a-z0-9\s]", " ", (text or "").lower())
        normalized = re.sub(r"\s+", " ", normalized)
        return normalized.strip()

    @staticmethod
    def _contains_skill(text, skill):
        pattern = rf"(?<!\w){re.escape(skill)}(?!\w)"
        return re.search(pattern, text) is not None
