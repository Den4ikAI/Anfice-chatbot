from bot.core import CoreSession

user_id = 33784
core = CoreSession()
while 1:
    print('-' * 20)
    while 1:
        user = input("H:> ")
        if user == '/clear':
            core.clear_context(user_id)
            print('B:> Контекст очищен!')
            break
        core.add_user_message(user_id, user)
        answer = core.process_user_message(user_id)
        core.add_bot_message(user_id, answer)
        print('B:> ' + answer)
        core.truncate_context(user_id)
