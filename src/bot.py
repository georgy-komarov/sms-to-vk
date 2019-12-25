import json
import time

import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll
from vk_api.utils import get_random_id

from db import DBHelper

ADMIN_ID = 223712375

KEYB = {
    'main_inline':     [json.dumps({'inline': False, 'buttons': [[{'action': {'type': 'text', 'label': '📶Ping'}, 'color': 'positive'},
                                                                  {'action': {'type': 'text', 'label': '⏩Last'}, 'color': 'positive'},
                                                                  {'action': {'type': 'text', 'label': '🆕'}, 'color': 'positive'}]]}),
                        ['📶Ping', '⏩Last', '🆕']],
    'main_inline_old': [json.dumps({'inline': True, 'buttons': [[{'action': {'type': 'text', 'label': '📶Ping'}, 'color': 'positive'},
                                                                 {'action': {'type': 'text', 'label': '⏩Last'}, 'color': 'positive'},
                                                                 {'action': {'type': 'text', 'label': '🆕'}, 'color': 'positive'}]]}),
                        ['📶Ping', '⏩Last', '🆕']],
    'empty':           [json.dumps({'buttons': [], 'one_time': True}), '']
}

DB = DBHelper()


def main():
    bot_token = "b7ce240ea07d280d84f533c027cd533072529c7c3a02306aaaa678d79f019136a08e1af11ce4fc9f1c9fd"
    gid = 190228123

    vk_session = vk_api.VkApi(token=bot_token, api_version='5.103')

    vk = vk_session.get_api()

    longpoll = VkLongPoll(vk_session)

    # PC
    # vk.messages.send(
    #     user_id=ADMIN_ID,
    #     random_id=get_random_id(),
    #     message=f'Бот инициализирован от {time.strftime("%d.%m.%Y %H:%M:%S")}',
    #     keyboard=KEYB['main'][0]
    # )

    vk.messages.send(
        user_id=ADMIN_ID,
        random_id=get_random_id(),
        message=f'Бот инициализирован от {time.strftime("%d.%m.%Y %H:%M:%S")}',
        keyboard=KEYB['main_inline'][0]
    )

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            if event.peer_id == ADMIN_ID:
                if event.text == KEYB['main_inline'][1][0]:
                    vk.messages.send(
                        user_id=ADMIN_ID,
                        random_id=get_random_id(),
                        message="Онлайн",
                        keyboard=KEYB['main_inline'][0]
                    )
                elif event.text == KEYB['main_inline'][1][1]:
                    # Last
                    last_msg = DB.get_last_messages(3)

                    for msg in last_msg:
                        text = '🆕 ' if msg['read'] == '0' else '✉ '
                        text += f'Сообщение от {msg["address"]}:\n{msg["body"]}'
                        vk.messages.send(
                            user_id=ADMIN_ID,
                            random_id=get_random_id(),
                            message=text
                        )

                    vk.messages.send(
                        user_id=ADMIN_ID,
                        random_id=get_random_id(),
                        message="Пока ничего нового",
                        keyboard=KEYB['main_inline'][0]
                    )

                elif event.text == KEYB['main_inline'][1][2]:
                    # New
                    new_msg = DB.get_unread_messages()
                    if len(new_msg) == 0:
                        vk.messages.send(
                            user_id=ADMIN_ID,
                            random_id=get_random_id(),
                            message='Пока ничего нового',
                            keyboard=KEYB['main_inline'][0]
                        )
                    else:
                        for msg in new_msg:
                            vk.messages.send(
                                user_id=ADMIN_ID,
                                random_id=get_random_id(),
                                message=f'Сообщение от {msg["address"]}:\n{msg["body"]}'
                            )

                        DB.read_all_messages()

                        vk.messages.send(
                            user_id=ADMIN_ID,
                            random_id=get_random_id(),
                            message="Пока ничего нового",
                            keyboard=KEYB['main_inline'][0]
                        )


if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception as e:
            pass
        time.sleep(15)
