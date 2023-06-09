import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import logging
import config.config as config


class RuBertQASelector:
    def __init__(self):
        self.logger = logging.getLogger('Replica selector')
        self.use_cuda = torch.cuda.is_available()
        self.device = torch.device("cpu")
        self.logger.debug("Started loading QA selector")
        self.tokenizer = AutoTokenizer.from_pretrained(config.question_classifier_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(config.question_classifier_path).to(
            self.device).eval()
        self.classes = ['exact_question', 'inaccurate_question']

    def get_question_type(self, text):
        text = text.lower().replace(',', '').replace('?', '')
        inputs = self.tokenizer(text, max_length=512, add_special_tokens=False, truncation=True,
                                return_tensors='pt').to(self.device)
        with torch.no_grad():
            logits = self.model(**inputs).logits
            probas = list(torch.sigmoid(logits)[0].cpu().detach().numpy())
        out = self.classes[probas.index(max(probas))]
        self.logger.debug('Mode: {}'.format(out))
        return out
