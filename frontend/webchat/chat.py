from client import ChatClient

user_id = 33784
token = "secret123"
url = "http://0.0.0.0:8000"
chat = ChatClient(url, token)
chat.set_system_prompt(user_id, 'Ты философ любящий рассуждать.')
while 1:
    print('-' * 20)
    while 1:
        user = input("H:> ")
        if not user:
            chat.clear_context(user_id)
            print('B:> Контекст очищен!')
            break
        chat.add_user_message(user_id, user)
        answer = chat.process_user_message(user_id)
        chat.add_bot_message(user_id, answer)
        print('B:> ' + answer)
