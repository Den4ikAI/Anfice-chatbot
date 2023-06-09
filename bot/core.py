from bot.context import Dialog
from bot.rubert_phrase_classifier import RuBertPhraseClassifier
from bot.rubert_qa_selector import RuBertQASelector
from bot.instructor import Instructor
from bot.web_search import InternetSearch
from bot.rubert_qa_ranker import QARanker
from bot.text_retrieval.searcher import TextSearch
from bot.modality_detector import ModalityDetector
from bot.rut5_interpreter import RuT5Interpreter
from bot.postagger import POSTagger
from terminaltables import AsciiTable
from rapidfuzz import fuzz
from tqdm import tqdm
import config.config as config
import logging
import torch

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


class ContextPrepare:
    def __init__(self):
        pass

    def construct_chitchat3_dialog(self, context):
        last_user_message = context[-3] if len(context) > 2 else None
        last_robot_message = context[-2] if len(context) > 2 else None
        msg = context[-1].strip().lower().capitalize()

        dialog = []
        if last_user_message is not None and last_user_message != '':
            dialog.append('Собеседник: ' + last_user_message.strip().lower().capitalize() + '\n')
        if last_robot_message is not None and last_robot_message != '':
            dialog.append('Ты: ' + last_robot_message.strip().lower().capitalize() + '\n')
        dialog.append('Собеседник: ' + msg)

        return dialog

    def prepare_qa_context(self, context):
        return '<SC6>Человек: {}\nБот: <extra_id_0>'.format(context[-1])

    def construct_retriever_context(self, page, question):
        return '<SC6>Человек: Текст: {}\nВопрос: {}\nОтвет: <extra_id_0>'.format(page, question)


class CoreSession:
    def __init__(self):
        self.dialog = Dialog(config.database_path)
        self.logger = logging.getLogger('Core')
        self.file = logging.FileHandler(config.logdir)
        self.logger.addHandler(self.file)
        self.max_context_length = 6
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.logger.info('Version = [{}]'.format(config.VERSION))
        self.logger.info('Device = [{}]'.format(self.device))
        self.context_prepare = ContextPrepare()
        self.internet_search = InternetSearch()
        self.text_search = TextSearch()
        self.modality_detector = ModalityDetector()
        self.postagger = POSTagger()
        self.initialize_models()

    def initialize_models(self):
        self.instructor = Instructor()
        self.phrase_classifier = RuBertPhraseClassifier()
        self.qa_classifier = RuBertQASelector()
        self.qa_ranker = QARanker()
        self.interpreter = RuT5Interpreter()

    def draw_dialog(self, dialog, answer, user_id):
        table_data = [["User ID", "Turn", "Text"]]
        dialog.append(['bot', answer])
        for message in dialog:
            sender, text = message
            table_data.append([user_id, sender, text])

        table_instance = AsciiTable(table_data)
        table_instance.inner_row_border = True
        self.logger.info(table_instance.table)

    def add_user_message(self, user_id, message):
        if len(message.split(' ')) > 3:
            tags = self.postagger.tag(message)
            self.logger.info("Message tags = [{}]".format(tags))
            if any((u'NPRO' in tag) for tag in tags) or "это" in message.split(' '):
                self.logger.info('Anaphora detected! Interpreting...')
                context = self.dialog.get_dialog(user_id)
                context = [dialogue[1] for dialogue in context]
                context.append(message)
                message = self.interpreter.interpret(context)
        self.dialog.add_message(user_id, 'user', message)
        return None

    def add_bot_message(self, user_id, message):
        self.dialog.add_message(user_id, 'bot', message)
        self.truncate_context(user_id)
        return None

    def get_dialog(self, user_id):
        dialog = self.dialog.get_dialog(user_id)
        return dialog

    def get_last_user_message(self, user_id):
        dialog = self.dialog.get_dialog(user_id)
        if dialog:
            return dialog[-2][1]
        else:
            return None

    def get_last_bot_message(self, user_id):
        dialog = self.dialog.get_dialog(user_id)
        if dialog:
            return dialog[-1][1]
        else:
            return None

    def set_system_prompt(self, user_id, prompt):
        self.dialog.set_system_prompt(user_id, prompt)
        return None

    def clear_context(self, user_id):
        self.dialog.clear_dialog(user_id)
        return None

    def truncate_context(self, user_id):
        dialog = self.dialog.get_dialog(user_id)
        if len(dialog) > self.max_context_length:
            dialog = dialog[-self.max_context_length:]
        self.dialog.add_dialog(user_id, dialog)
        return None

    def get_best_qa_response(self, context, answers):
        ranked_answers = []
        for answer in answers:
            score = self.qa_ranker.rank_responses(context[-1], answer)
            ranked_answers.append([answer, score])
        return sorted(ranked_answers, key=lambda x: x[1], reverse=True)[0][0]

    def process_user_message(self, user_id):
        replicas = self.dialog.get_dialog(user_id)
        context = [dialogue[1] for dialogue in replicas]
        system_prompt = self.dialog.get_system_prompt(user_id)
        mode = self.phrase_classifier.get_sentence_type(context[-1])
        modality = self.modality_detector.modality(context[-1])
        chitchat_answers = []
        qa_answers = []
        self.logger.info('Started processing messages user_id=[{}]'.format(user_id))
        self.logger.info('Message = [{}]'.format(context[-1]))
        self.logger.info('UserID = [{}]'.format(user_id))
        self.logger.info('Persona = [{}]'.format(system_prompt))
        self.logger.info('Mode = [{}]'.format(mode))
        self.logger.info('Modality = [{}]'.format(modality))

        if mode == 'dialogue':
            message = context[-1]
            if len(context) > 2:
                last_bot_message = context[-2]
            else:
                last_bot_message = None
            t5_output = self.instructor.generate2(self.context_prepare.construct_chitchat3_dialog(context),
                                                  system_prompt)

            if fuzz.ratio(str(t5_output), last_bot_message) > 75:
                self.logger.warning('Repetition detected! Clearing context and restarting generation')
                self.clear_context(user_id)
                self.add_user_message(user_id, message)
                replicas = self.dialog.get_dialog(user_id)
                context = [dialogue[1] for dialogue in replicas]
                t5_output = self.instructor.generate2(self.context_prepare.construct_chitchat3_dialog(context),
                                                      system_prompt)
            chitchat_answers.extend(t5_output)

        elif mode == 'about_user':
            message = context[-1]
            if len(context) > 2:
                last_bot_message = context[-2]
            else:
                last_bot_message = None
            t5_output = self.instructor.generate2(self.context_prepare.construct_chitchat3_dialog(context),
                                                  system_prompt)

            if fuzz.ratio(str(t5_output), last_bot_message) > 75:
                self.logger.warning('Repetition detected! Clearing context and restarting generation')
                self.clear_context(user_id)
                self.add_user_message(user_id, message)
                replicas = self.dialog.get_dialog(user_id)
                context = [dialogue[1] for dialogue in replicas]
                t5_output = self.instructor.generate2(self.context_prepare.construct_chitchat3_dialog(context),
                                                      system_prompt)
            chitchat_answers.extend(t5_output)

        elif mode == 'about_system' and modality == 'question':
            message = context[-1]
            if len(context) > 2:
                last_bot_message = context[-2]
            else:
                last_bot_message = None
            t5_output = self.instructor.generate2(self.context_prepare.construct_chitchat3_dialog(context),
                                                  system_prompt)

            if fuzz.ratio(str(t5_output), last_bot_message) > 75:
                self.logger.warning('Repetition detected! Clearing context and restarting generation')
                self.clear_context(user_id)
                self.add_user_message(user_id, message)
                replicas = self.dialog.get_dialog(user_id)
                context = [dialogue[1] for dialogue in replicas]
                t5_output = self.instructor.generate2(self.context_prepare.construct_chitchat3_dialog(context),
                                                      system_prompt)
            chitchat_answers.extend(t5_output)

        elif mode == 'question' and modality == 'question' and len(
                context[-1].split(' ')) > 2:
            cls = self.qa_classifier.get_question_type(context[-1])
            self.logger.info('Mode = [{}]'.format(cls))
            if cls == 'exact_question':
                message = context[-1]
                web_outputs = self.internet_search.web_search(message, num_return_sequences=5)
                if web_outputs:
                    for page in tqdm(web_outputs):
                        try:
                            paragraphs = list(set(self.text_search.get_relevant_paragraphs(message, page)))
                            paragraph = self.text_search.get_right_answer(paragraphs, message)
                        except:
                            paragraph = None
                        if paragraph is not None:
                            qa_answers.extend(
                                self.instructor.generate(
                                    self.context_prepare.construct_retriever_context(paragraph, message)))
                        else:
                            t5_output = self.instructor.generate(self.context_prepare.prepare_qa_context(context))
                            t5_output = [t5_output[0].split('Собеседник сказал:')[0]]
                            qa_answers.extend(t5_output)
                else:
                    t5_output = self.instructor.generate(self.context_prepare.prepare_qa_context(context))
                    t5_output = [t5_output[0].split('Собеседник сказал:')[0]]
                    qa_answers.extend(t5_output)
            elif cls == 'inaccurate_question':
                self.logger.warning('Internet search did not give results. The generation may be inaccurate')
                t5_output = self.instructor.generate(self.context_prepare.prepare_qa_context(context))
                t5_output = [t5_output[0].split('Собеседник сказал:')[0]]
                qa_answers.extend(t5_output)

        elif mode == 'instruct':
            message = context[-1]
            web_outputs = self.internet_search.web_search(message, num_return_sequences=5)

            if web_outputs:
                for page in tqdm(web_outputs):
                    try:
                        paragraphs = list(set(self.text_search.get_relevant_paragraphs(message, page)))
                        paragraph = self.text_search.get_right_answer(paragraphs, message)
                    except:
                        paragraph = None
                    if paragraph is not None:
                        qa_answers.extend(
                            self.instructor.generate(
                                self.context_prepare.construct_retriever_context(paragraph, message)))
                    else:
                        t5_output = self.instructor.generate(self.context_prepare.prepare_qa_context(context))
                        t5_output = [t5_output[0].split('Собеседник сказал:')[0]]
                        qa_answers.extend(t5_output)
            else:
                self.logger.warning('Internet search did not give results. The generation may be inaccurate')
                t5_output = self.instructor.generate(self.context_prepare.prepare_qa_context(context))
                t5_output = [t5_output[0].split('Собеседник сказал:')[0]]
                qa_answers.extend(t5_output)
        elif mode == 'problem':
            message = context[-1]
            if len(context) > 2:
                last_bot_message = context[-2]
            else:
                last_bot_message = None
            t5_output = self.instructor.generate2(self.context_prepare.construct_chitchat3_dialog(context),
                                                  system_prompt)
            if fuzz.ratio(str(t5_output), last_bot_message) > 75:
                self.logger.warning('Repetition detected! Clearing context and restarting generation')
                self.clear_context(user_id)
                self.add_user_message(user_id, message)
                replicas = self.dialog.get_dialog(user_id)
                context = [dialogue[1] for dialogue in replicas]
                t5_output = self.instructor.generate2(self.context_prepare.construct_chitchat3_dialog(context),
                                                      system_prompt)
            chitchat_answers.extend(t5_output)
        else:
            message = context[-1]
            if len(context) > 2:
                last_bot_message = context[-2]
            else:
                last_bot_message = None
            t5_output = self.instructor.generate2(self.context_prepare.construct_chitchat3_dialog(context),
                                                  system_prompt)

            if fuzz.ratio(str(t5_output), last_bot_message) > 75:
                self.logger.warning('Repetition detected! Clearing context and restarting generation')
                self.clear_context(user_id)
                self.add_user_message(user_id, message)
                replicas = self.dialog.get_dialog(user_id)
                context = [dialogue[1] for dialogue in replicas]
                t5_output = self.instructor.generate2(self.context_prepare.construct_chitchat3_dialog(context),
                                                      system_prompt)
            chitchat_answers.extend(t5_output)

        if chitchat_answers:
            self.draw_dialog(replicas, chitchat_answers[0], user_id)
            self.logger.info('Answer = [{}]'.format(chitchat_answers[0]))
            return chitchat_answers[0]
        elif qa_answers:
            best_response = self.get_best_qa_response(context, qa_answers)
            self.draw_dialog(replicas, best_response, user_id)
            self.logger.info('Answer = [{}]'.format(best_response))
            return best_response
        else:
            self.draw_dialog(replicas, None, user_id)
            self.logger.info('Answer = [{}]'.format(None))
            return None
