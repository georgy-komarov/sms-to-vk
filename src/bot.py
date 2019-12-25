import json
import threading
import time
from datetime import datetime

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

# DB = DBHelper('../examples/mmssms.db')
DB = DBHelper()


def on_new_messages(vk, new_msg, send_after=True):
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
                message=f'{msg["address"]} от {datetime.fromtimestamp(int(msg["date"]) // 1000).strftime("%d.%m %H:%M")}\n{msg["body"]}'
            )

        DB.read_all_messages()

        if send_after:
            vk.messages.send(
                user_id=ADMIN_ID,
                random_id=get_random_id(),
                message="Пока ничего нового",
                keyboard=KEYB['main_inline'][0]
            )


def checker_thread(vk):
    while True:
        new_msg = DB.get_unread_messages()
        if len(new_msg) != 0:
            on_new_messages(vk, new_msg, send_after=False)
        else:
            time.sleep(10)


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

    thread_checker = threading.Thread(target=checker_thread, args=(vk,), daemon=True)
    thread_checker.start()

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
                        text += f'{msg["address"]} от {datetime.fromtimestamp(int(msg["date"]) // 1000).strftime("%d.%m %H:%M")}\n{msg["body"]}'
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
                    on_new_messages(vk, new_msg)


if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception as e:
            print(repr(e))
        time.sleep(5)
