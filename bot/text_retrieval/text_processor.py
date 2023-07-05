import pymorphy2
import re
import string
import nltk
from nltk.stem.wordnet import WordNetLemmatizer


class TextProcessor:
    def __init__(self):
        self.morph = pymorphy2.MorphAnalyzer()
        self.en_morph = WordNetLemmatizer()

    def clear_text(self, text):
        # удаляем все символы из текста, кроме тех, которые точно разберет парсер
        text = re.sub(r'[^\w\d\s\-\n\r\.\(\)\{\}\[\]\"\'«»`%,:_]', " ", text, flags=re.M | re.U | re.I)
        return text

    def infinitive(self, text):
        p = self.morph.parse(text)[0]
        return p.normal_form

    def pos_tag(self, text):
        p = self.morph.parse(text)[0]
        return p.tag.POS, p.tag.number, p.tag.gender, p.tag.person, p.tag.case, p.tag.voice, p.tag.tense

    def en_pos_tag(self, text):
        p = nltk.pos_tag(nltk.word_tokenize(text.lower()))
        return [p[0][1]]

    def split_by_words(self, text):
        # разбиваем текст на слова
        text = text.lower()
        spec_chars = string.punctuation + '\r\n\xa0«»\t—…'
        for char in spec_chars:
            text = text.replace(char, ' ')
        text = text.replace('   ', ' ')
        text = text.replace('  ', ' ')
        output = text.split()
        return output

    def extract_verbs(self, text):
        # извлекаем все глаголы из текста
        outputs = []
        words = self.split_by_words(text)
        for word in words:
            if word.isalpha() and all(ord(c) < 128 for c in word):
                tagged = self.en_pos_tag(word)
                if 'VB' in tagged[0]:
                    infinitive = self.en_morph.lemmatize(word, 'v')
                    outputs.append(infinitive.lower())
            else:
                infinitive = self.infinitive(word)
                tagged = self.pos_tag(infinitive)
                if tagged[0] == 'VERB' or tagged[0] == 'INFN':
                    outputs.append(infinitive.lower())
        return list(set(outputs))

    def extract_nouns(self, text):
        # извлекаем все существительные из текста
        outputs = []
        words = self.split_by_words(text)
        for word in words:
            if word.isalpha() and all(ord(c) < 128 for c in word):
                tagged = self.en_pos_tag(word)
                if 'NN' in tagged[0]:
                    infinitive = self.en_morph.lemmatize(word, 'n')
                    outputs.append(infinitive.lower())
            else:
                infinitive = self.infinitive(word)
                tagged = self.pos_tag(infinitive)
                if tagged[0] == 'NOUN':
                    outputs.append(infinitive.lower())
        return list(set(outputs))

    def extract_adjectives(self, text):
        # извлекаем все прилагательные из текста
        outputs = []
        words = self.split_by_words(text)
        for word in words:
            if word.isalpha() and all(ord(c) < 128 for c in word):
                tagged = self.en_pos_tag(word)
                if 'JJ' in tagged[0]:
                    infinitive = self.en_morph.lemmatize(word, 'a')
                    outputs.append(infinitive.lower())
            else:
                infinitive = self.infinitive(word)
                tagged = self.pos_tag(infinitive)
                if tagged[0] == 'ADJF' or tagged[0] == 'ADJS':
                    outputs.append(infinitive.lower())
        return list(set(outputs))
