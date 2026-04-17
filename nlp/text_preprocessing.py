import re

import spacy


class TextPreprocessor:
    def __init__(self, nlp=None):
        self.nlp = nlp or spacy.blank("en")

    def preprocess(self, text):
        text = self._lowercase(text)
        text = self._clean_with_regex(text)
        return self._normalize_with_spacy(text)

    @staticmethod
    def _lowercase(text):
        return text.lower().strip()

    @staticmethod
    def _clean_with_regex(text):
        text = re.sub(r"\S+@\S+", " ", text)
        text = re.sub(r"https?://\S+|www\.\S+", " ", text)
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _normalize_with_spacy(self, text):
        doc = self.nlp(text)
        tokens = [token.text for token in doc if not token.is_space]
        return " ".join(tokens).strip()
