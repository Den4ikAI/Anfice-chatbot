import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer
import config.config as config



class RuT5Interpreter:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.load(config.interpreter_path)

    def load(self, models_dir):
        self.tokenizer = T5Tokenizer.from_pretrained(models_dir)
        self.model = T5ForConditionalGeneration.from_pretrained(models_dir)
        self.model.to(self.device)
        self.model.eval()

    def interpret(self, phrases, num_return_sequences=1):
        t5_input = '\n'.join(('- ' + f) for f in phrases)
        input_ids = self.tokenizer(t5_input, return_tensors='pt').input_ids.to(self.device)
        out_ids = self.model.generate(input_ids=input_ids,
                                      max_length=60,
                                      eos_token_id=self.tokenizer.eos_token_id,
                                      do_sample=True,
                                      temperature=1.0,
                                      num_return_sequences=num_return_sequences,
                                      )

        outputs = set()
        for i in range(len(out_ids)):
            o = self.tokenizer.decode(out_ids[i][1:])
            o = o.replace('</s>', '')
            outputs.add(o)

        return list(outputs)[0]
