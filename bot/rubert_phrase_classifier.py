import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import logging


class RuBertPhraseClassifier:
    def __init__(self):
        self.logger = logging.getLogger('Replica selector')
        self.use_cuda = torch.cuda.is_available()
        self.device = torch.device("cpu")
        self.logger.debug("Started loading Replica selector")
        self.tokenizer = AutoTokenizer.from_pretrained('models/selector')
        self.model = AutoModelForSequenceClassification.from_pretrained('models/selector').to(self.device).eval()
        self.logger.debug('Start loading replica selector')
        self.classes = ['about_user', 'inaccurate_question', 'exact_question', 'instruct', 'about_system', 'problem',
                        'dialogue']

    def get_sentence_type(self, text):
        text = text.lower().replace(',', '').replace('?', '')
        inputs = self.tokenizer(text, max_length=512, add_special_tokens=False, truncation=True,
                                return_tensors='pt').to(self.device)
        with torch.no_grad():
            logits = self.model(**inputs).logits
            probas = list(torch.sigmoid(logits)[0].cpu().detach().numpy())
        out = self.classes[probas.index(max(probas))]
        self.logger.debug('Mode: {}'.format(out))
        return out
