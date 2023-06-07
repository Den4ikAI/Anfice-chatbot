from wiki_ru_wordnet import WikiWordnet


class Synonymizer:
    def __init__(self):
        self.wikiwordnet = WikiWordnet()

    def extract_synonym(self, text):
        # извлекаем все синонимы из текста
        try:
            outputs = []
            synonymy_set = self.wikiwordnet.get_synsets(text)[0]
            for word in synonymy_set.get_words():
                outputs.append(word.lemma())
            return outputs
        except IndexError:
            return []

    def extract_synonyms(self, inputs):
        outputs = []
        for chunk in inputs:
            outputs.append(chunk)
        for chunk in inputs:
            synonyms = self.extract_synonym(
                chunk.lower().strip())
            if synonyms is not None:
                for synonym in synonyms:
                    if not synonym in outputs:
                        outputs.append(synonym.lower())
            else:
                outputs = None
        return outputs
