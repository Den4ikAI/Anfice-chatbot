from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from transformers import GenerationConfig
import config.config as config


class Instructor:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(config.instructor_path)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(config.instructor_path, torch_dtype=torch.float16).to(
            self.device)
        self.model.eval()
        self.generation_config = GenerationConfig.from_pretrained(config.instructor_path)

    def generate(self, prompt):
        inputs = [prompt]
        for sample in inputs:
            data = self.tokenizer(sample, max_length=1024, truncation=True, return_tensors="pt")
            data = {k: v.to(self.model.device) for k, v in data.items()}
            output_ids = self.model.generate(
                **data,generation_config=self.generation_config)[0]

        out = self.tokenizer.decode(output_ids.tolist())
        out = out.replace("<s>", "").replace("</s>", "").replace('<extra_id_0>', '').replace('Ответ:','')
        return [out]

    def generate2(self, dialog, system_prompt):
        prompt = f'<SC1>{system_prompt} Продолжи диалог:' + '\n'.join(dialog) + '\nТы: <extra_id_0>'.format(system_prompt)
        input_ids = self.tokenizer(prompt, return_tensors='pt').input_ids.to(self.device)
        out_ids = self.model.generate(input_ids, do_sample=True, temperature=0.9, max_new_tokens=512, top_p=0.85, top_k=2)
        t5_output = self.tokenizer.decode(out_ids[0], skip_special_tokens=True).replace('<extra_id_0>', '').strip()
        if 'Собеседник' in t5_output:
            t5_output = t5_output.split('Собеседник')[0].strip()
        elif 'Ты ответ' in t5_output:
            t5_output = t5_output.split('Ты ответ')[0].strip()
        return [t5_output]
