# Конфигурационный файл системы

VERSION = 4.2

instructor_path = 'SiberiaSoft/SiberianFRED-T5-XL' # Инструкционная модель
phrase_classifier_path = 'Den4ikAI/ruBert-tiny-replicas-classifier' # Классификатор фраз пользователя
question_classifier_path = 'Den4ikAI/ruBert-tiny-questions-classifier' # Классификатор вопросов
embedding_model_path = 'sentence-transformers/distiluse-base-multilingual-cased-v1' # Эмбеддинг модель
qa_ranker_path = 'Den4ikAI/ruBert-base-qa-ranker' # Ранжировщик ответов
interpreter_path = 'Den4ikAI/ruT5-small-interpreter' # Интерпретатор реплик
tgbot_token = '' # Токен полученный от @botfather
database_path = 'database/dialogues.db' # Путь к бд хранящей диалоги
access_tokens = ['secret123'] # Токены доступа через FastAPI
default_system_prompt = 'Ты девушка Анфиса, разговаривающая с незнакомым тебе человеком.' # Системный промпт по умолчанию
logdir = "logs/chatbot.log"
