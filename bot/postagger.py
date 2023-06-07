import pymorphy2
import string

class POSTagger:
    def __init__(self):
        self.postagger = pymorphy2.MorphAnalyzer()

    def tokenize(self, text):
        # разбиваем текст на слова
        text = text.lower()
        spec_chars = string.punctuation + '\r\n\xa0«»\t—…'
        for char in spec_chars:
            text = text.replace(char, ' ')
        text = text.replace('   ', ' ')
        text = text.replace('  ', ' ')
        output = text.split()
        return output

    def tag(self, text):
        tags = []
        tokens = self.tokenize(text)
        for token in tokens:
            tags.append(self.postagger.parse(token)[0].tag)
        return tags


