import re

class TextCleaner:
    @staticmethod
    def clean(text: str):
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"\n+", "\n", text)
        text = text.replace("\t", " ")
        return text.strip()
text_cleaner = TextCleaner()