from sentence_transformers import SentenceTransformer, util
import torch
from nltk.tokenize import sent_tokenize
from rapidfuzz import process, fuzz
from bot.text_retrieval.text_processor import TextProcessor
from bot.text_retrieval.synonimizer import Synonymizer
import config.config as config

class TextSearch:
    def __init__(self) -> None:
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.embedder = SentenceTransformer(config.embedding_model_path).to(self.device)
        self.text_processor = TextProcessor()
        self.synonymizer = Synonymizer()

    def get_texts_similarity(self, query, mylist, num_return_sequences=10, threshold=10):
        corpus_embeddings2 = self.embedder.encode(mylist, convert_to_tensor=True)
        outputs = []
        query = query.strip().lower()
        top_k = min(num_return_sequences, len(mylist))
        query_embedding = self.embedder.encode(query, convert_to_tensor=True)
        cos_scores = util.cos_sim(query_embedding, corpus_embeddings2)[0]
        top_results = torch.topk(cos_scores, k=top_k)
        for score, idx in zip(top_results[0], top_results[1]):
            score = int(float(score) * 100)
            if score > threshold:
                outputs.append(mylist[idx])
        return outputs

    def del_empty_paragraphs(self, text):
        abzacs = []
        mas = text.split('\n')
        for x in mas:
            x = x.strip()
            if len(x) > 100:
                abzacs.append(x)
        return abzacs

    def paragraph_locator(self, paragraphs):
        phr_abz = {}
        z = 0
        for paragraph in paragraphs:
            phrases = sent_tokenize(paragraph)
            for phrase in phrases:
                if phrase.strip() != paragraph.strip():
                    phr_abz[phrase.lower()] = z
                else:
                    phr_abz[phrase.lower()] = -1
            z += 1
        return phr_abz

    def get_relevant_paragraphs(self, query, text, max_paragraphs=3):
        relevant_paragraphs = []
        paragraphs = self.del_empty_paragraphs(text)
        facts = self.paragraph_locator(paragraphs)
        similar_phrases = self.get_texts_similarity(query, list(facts.keys()), num_return_sequences=max_paragraphs)
        similar_phrases2 = process.extract(query, facts.keys(), scorer=fuzz.token_set_ratio, limit=max_paragraphs)

        for phrase in similar_phrases2:
            found_text = phrase[0]
            if not found_text in similar_phrases:
                similar_phrases.append(found_text)

        for phrase in similar_phrases:
            if facts[phrase] != -1:
                most_similar_paragraph = paragraphs[facts[phrase]]
                next_paragraph = ''
                if facts[phrase] < (len(paragraphs) - 1):
                    next_paragraph = paragraphs[facts[phrase] + 1]
            else:
                next_paragraph = ''
                most_similar_paragraph = phrase
                if facts[phrase] < (len(paragraphs) - 1):
                    next_paragraph = paragraphs[facts[phrase] + 1]

            if not most_similar_paragraph.strip().endswith(
                    '?') and not query.lower() in most_similar_paragraph.lower() and not '?' in most_similar_paragraph[
                                                                                                len(most_similar_paragraph) // 2:]:
                if not (
                        'о том' in most_similar_paragraph or 'узнаем' in most_similar_paragraph or 'расскажем' in most_similar_paragraph or 'обзоре' in most_similar_paragraph or 'речь пойдет' in most_similar_paragraph or 'статье ниже' in most_similar_paragraph or 'текущей статье' in most_similar_paragraph or 'данной статье' in most_similar_paragraph or 'этой статье' in most_similar_paragraph or 'рассмотрим' in most_similar_paragraph or 'расскажем' in most_similar_paragraph):
                    relevant_paragraphs.append(most_similar_paragraph)

            if next_paragraph.strip() != '':
                if not next_paragraph.strip().endswith(
                        '?') and not query.lower() in next_paragraph.lower() and not '?' in next_paragraph[
                                                                                            len(next_paragraph) // 2:]:
                    if not (
                            'о том' in next_paragraph or 'узнаем' in next_paragraph or 'расскажем' in next_paragraph or 'обзоре' in next_paragraph or 'речь пойдет' in next_paragraph or 'статье ниже' in next_paragraph or 'текущей статье' in next_paragraph or 'данной статье' in next_paragraph or 'этой статье' in next_paragraph or 'рассмотрим' in next_paragraph or 'расскажем' in next_paragraph):
                        relevant_paragraphs.append(next_paragraph)

        return relevant_paragraphs

    def get_right_answer(self, mas, q):
        # Собираем массив ключевых слов из вопроса
        keywords_q = self.text_processor.extract_nouns(q.lower()) + self.text_processor.extract_verbs(
            q.lower()) + self.text_processor.extract_adjectives(q.lower())
        # Добавляем синонимы к ключевым словам из вопроса
        synonyms_q = self.synonymizer.extract_synonyms(keywords_q)
        keywords_q = list(set(keywords_q + synonyms_q))
        # Будет использоваться для хранения наиболее подходящих ответов на вопрос
        result = []
        # Будет использоваться для хранения количества совпадающих ключевых слов в ответах на вопрос
        old_count = 1
        for answer in mas:
            # Собираем массив ключевых слов из ответа
            keywords_answer = self.text_processor.extract_nouns(answer.lower()) + self.text_processor.extract_verbs(
                answer.lower()) + self.text_processor.extract_adjectives(answer.lower())
            keywords_answer = list(set(keywords_answer))
            # Считаем количество совпадающих ключевых слов между вопросом и ответом
            count = len(list(set(keywords_q) & set(keywords_answer)))
            # Если количество совпадающих ключевых слов больше или равно предыдущей наибольшей,
            # то добавляем данный ответ в массив наиболее подходящих ответов
            if count >= old_count:
                if old_count < count:
                    result = []
                    old_count = count
                if not answer in result:
                    result.append(answer)
        if result != [] and result is not None:
            most_similar_answer = self.get_texts_similarity(q, result, num_return_sequences=2)
            if most_similar_answer:
                return most_similar_answer[0]
            else:
                return None
        else:
            return None


'''
test = InternetSearch()
q = 'Когда родился Пушкин?'
paragraphs = list(set(test.get_relevant_paragraphs(q, '[TEXT]', 3)))
print(test.get_right_answer(paragraphs, q))
'''
