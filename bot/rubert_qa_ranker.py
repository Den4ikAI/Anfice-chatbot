import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import config.config as config


class QARanker:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(config.qa_ranker_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(config.qa_ranker_path)
        self.device = torch.device("cpu")
        self.model.to(self.device)

    def rank_responses(self, user, answer):
        inputs = self.tokenizer('[CLS]{}[RESPONSE_TOKEN]{}'.format(user, answer),
                                max_length=512, add_special_tokens=False, return_tensors='pt')
        with torch.inference_mode():
            logits = self.model(**inputs).logits
            probas = torch.sigmoid(logits)[0].cpu().detach().numpy()
        relevance, no_relevance = probas
        return relevance
