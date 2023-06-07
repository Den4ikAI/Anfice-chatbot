class Dialog:
    def __init__(self):
        self.dialogs = {}  # словарь для хранения диалогов

    def add_message(self, dialog_id, sender, text):
        if dialog_id not in self.dialogs:
            self.dialogs[dialog_id] = []  # создаем новый диалог, если его еще нет
        self.dialogs[dialog_id].append((sender, text))  # добавление нового сообщения в список

    def add_dialog(self, dialog_id, messages):
        self.dialogs[dialog_id] = messages  # добавление нового диалога в словарь

    def get_dialog(self, dialog_id):
        if dialog_id in self.dialogs:
            return self.dialogs[dialog_id]  # получение диалога по id
        else:
            return []

    def clear_dialog(self, dialog_id):
        self.dialogs.pop(dialog_id, None)  # удаление диалога из словаря


# Testing
'''
if True:
    dialog = Dialog()
    dialog.add_message(1, 'bot', 'Привет!')
    dialog.add_message(1, 'user', 'Здравствуйте.')
    dialog.add_message(1, 'bot', 'Как ваши дела?')
    # dialog.clear_dialog(1)
    dialog1 = dialog.get_dialog(1)
    print(dialog1)
'''
