from bot.postagger import POSTagger
import string


class ModalityDetector:
    def __init__(self):
        self.question_words = 'насколько где кто что почему откуда куда зачем чего кого кем чем кому чему ком чем как сколько ли когда докуда какой какая какое какие какого какую каких каким какими какому какой каков какова каковы'.split()
        self.postagger = POSTagger()

    def get_person(self, words):
        if any((word in ('ты', 'тебя', 'тебе')) for word in words):
            return 2

        if any((word in ('я', 'мне', 'меня')) for word in words):
            return 1

        return -1

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

    def is_question(self, word):
        return word in self.question_words

    def modality(self, text):
        tokens = self.tokenize(text)
        tags = self.postagger.tag(text)

        if len(text) == 0:
            return None
        elif text.endswith('?'):
            return 'question'

        if any(self.is_question(word) for word in tokens):
            return 'question'

        if len(tokens) > 1 and self.is_question(tokens[1]):
            return 'question'

        if text.endswith('!'):
            if any((u'VERB' in tag) for tag in tags):
                return 'imperative'

        if any((u'impr' in tag) for tag in tags):
            return 'imperative'

        return 'assertion'
