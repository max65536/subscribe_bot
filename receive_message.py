from telethon import TelegramClient, events, sync
from dotenv import load_dotenv
import os
import logging
from IPython import embed

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
# These example values won't work. You must get your own api_id and
# api_hash from https://my.telegram.org, under API Development.
load_dotenv()
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')

client = TelegramClient('malybot', api_id, api_hash)

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
@client.on(events.NewMessage)
async def message_handler(event):
    # 如果消息是从一个频道发来的
    if event.is_channel and not event.is_group:
        print(event.message.text)  # 打印消息内容

# 运行客户端
with client:
    client.run_until_disconnected()

#with client:
    # This remembers the events.NewMessage we registered before
#    client.add_event_handler(handler)


#    print('(Press Ctrl+C to stop this)')
#    client.run_until_disconnected()
