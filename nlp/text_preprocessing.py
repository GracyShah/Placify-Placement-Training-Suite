import re


class TextPreprocessor:
    def __init__(self, nlp=None):
        self.nlp = nlp

    def preprocess(self, text):
        text = self._lowercase(text)
        return self._clean_with_regex(text)

    @staticmethod
    def _lowercase(text):
        return (text or "").lower().strip()

    @staticmethod
    def _clean_with_regex(text):
        text = re.sub(r"\S+@\S+", " ", text)
        text = re.sub(r"https?://\S+|www\.\S+", " ", text)
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()
