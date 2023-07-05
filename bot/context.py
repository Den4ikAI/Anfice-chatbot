class Dialog:
    def __init__(self):
        self.dialogs = {}  # словарь для хранения диалогов
        self.user_system_prompts = {} # словарь для хранения пользовательских системных промптов
    def add_message(self, dialog_id, sender, text):
        if dialog_id not in self.dialogs:
            self.dialogs[dialog_id] = []  # создаем новый диалог, если его еще нет
        self.dialogs[dialog_id].append((sender, text))  # добавление нового сообщения в список

    def add_dialog(self, dialog_id, messages):
        self.dialogs[dialog_id] = messages  # добавление нового диалога в словарь

    def get_dialog(self, dialog_id):
        if dialog_id in self.dialogs:
            return [(sender, text) for sender, text in self.dialogs[dialog_id] if sender != 'system']  # получение диалога по id
        else:
            return []

    def clear_dialog(self, dialog_id):
        self.dialogs.pop(dialog_id, None)  # удаление диалога из словаря

    def set_system_prompt(self, prompt_id, text):
        if prompt_id not in self.user_system_prompts:
            self.user_system_prompts[prompt_id] = ""  # создаем новую ячейку пользователя
        self.user_system_prompts[prompt_id] = text  # добавление нового промпта в список

    def get_system_prompt(self, prompt_id):
        if prompt_id in self.user_system_prompts:
            return self.user_system_prompts[prompt_id]
        else:
            return ''



# Testing
'''
dialog = Dialog()
dialog.add_message(1, 'system', 'Привет!', is_system_prompt=True)
dialog.add_message(1, 'user', 'Здравствуйте.')
dialog.add_message(1, 'bot', 'Как ваши дела?')
dialog.add_message(1, 'user', 'Хорошо, спасибо.')
dialog.add_message(1, 'bot', 'Чем я могу помочь?')

system_prompts = dialog.get_system_prompt(1)
print("System Prompts:")
for sender, text in system_prompts:
    print(f"{sender}: {text}")

dialog1 = dialog.get_dialog(1)
print("\nDialog without System Prompts:")
for sender, text in dialog1:
    print(f"{sender}: {text}")
'''