import logging
import os
from telethon import TelegramClient, events, Button
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv()
# 客户端配置
user_api_id = int(os.getenv('USER_API_ID', 0))
user_api_hash = os.getenv('USER_API_HASH', '')
user_client = TelegramClient('malybot', user_api_id, user_api_hash).start()

# 机器人配置
bot_token = os.getenv('BOT_TOKEN', '')
bot_client = TelegramClient('bot', user_api_id, user_api_hash).start(bot_token=bot_token)

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.INFO)

# database
client = MongoClient()
db = client['tgbot']
user_collection = db['users']
channel_collection = db['channels']

channels = ["Odaily", "BlockBeats", "Foresight News"]
keywords = ["ETH", "layer2", "BTC", "分片", "eip"]

# 为用户定义事件处理程序
 # @user_client.on(events.NewMessage(pattern='hello'))
 # async def user_handler(event):
 #     await event.reply('Hello from user!')
 # 
 # @user_client.on(events.NewMessage(pattern='H'))
 # async def message_handler(event):
 #     sender = await event.get_input_sender()
 #     await user_client.send_message(sender, 'Hi')
 #     await bot_client.send_message(sender, str(sender))
 #     logging.info(str(sender)+":"+event.message.text)
 # #    await bot_client.send_message(28664002, event.message.text)
 # 
 # @user_client.on(events.NewMessage(pattern='push'))
 # async def push_handler(event):
 #     sender = await event.get_input_sender()
 # #    await user_client.send_message(sender, 'Hi')
 #     await bot_client.send_message(6653848637, event.message.text)
 #     logging.info(str(sender)+":"+event.message.text)
 # #    await bot_client.send_message(28664002, event.message.text)

@user_client.on(events.NewMessage())
async def message_handler(event):
    logging.info(event.message.text)
    sender = await event.get_sender()
    for word in keywords:
        if word in event.message.text:
            await bot_client.send_message(6653848637, "%s:\n%s"%(sender.username, event.message.text))
    logging.info(str(sender)+":"+event.message.text)
#    await bot_client.send_message(28664002, event.message.text)
 

# 为机器人定义事件处理程序
@bot_client.on(events.NewMessage(pattern='/start'))
async def bot_handler(event):
    # await event.reply('Hello from bot!')
    await event.respond(
        'Welcome!',
        buttons=[
            [Button.inline('check channels', b'get_channels')],
            [Button.inline('check keywords', b'get_keywords')]
        ]
    )

@bot_client.on(events.NewMessage(pattern='/channels'))
async def edit_channels(event):
    sender = await event.get_sender()
    user = user_collection.find_one({"userid": sender.id})
    msg = "channels: " + ', '.join(user['channels']) if user is not None else 'no channels set yet'
    await event.respond(msg, buttons = [[Button.inline('set channels', b'set_channels')]])

@bot_client.on(events.NewMessage(pattern='/keywords'))
async def edit_keywords(event):
    sender = await event.get_sender()
    user = user_collection.find_one({"userid": sender.id})
    msg = "keywords: " + ', '.join(user['keywords']) if user is not None else 'no keywords set yet'
    buttons = [[Button.inline("X "+word, b'set_%s' % word)] for word in user['keywords']]
    buttons.append([Button.inline("+", b'append')])
    await event.respond(msg, buttons = buttons)

@bot_client.on(events.CallbackQuery(pattern=b'get_channels'))
async def get_channels(event):
    sender = await event.get_sender()
    user = user_collection.find_one({"userid": sender.id})
    msg = "channels: " + ', '.join(user['channels']) if user is not None else 'no channels set yet'
    await event.respond(msg, buttons = [[Button.inline('set channels', b'set_channels')]])

@bot_client.on(events.CallbackQuery(pattern=b'get_keywords'))
async def get_keywords(event):
    sender = await event.get_sender()
    user = user_collection.find_one({"userid": sender.id})
    msg = "keywords: " + ', '.join(user['keywords']) if user is not None else 'no keywords set yet'
    await event.respond(msg, buttons = [[Button.inline('set keywords', b'set_keywords')]])
    
@bot_client.on(events.CallbackQuery(pattern=b'set_keywords'))
async def set_keywords(event):
    sender = await event.get_sender()
    user = user_collection.find_one({"userid": sender.id})
    if user is None:
        post = {"userid": sender.id, "channels":["Odaily", "BlockBeats", "Foresight News"], "keywords":["ETH", "BTC"]}
        post_id = user_collection.insert_one(post).inserted_id
    else:
        words = event.message.text.split(',')
        words = [w.strip() for w in words]
        updates = {"keywords": words}
        user_collection.update_one({"userid":sender.id},{"keywords": keywords})
    await bot_client.send_message(6653848637, ','.join(keywords))

# @bot_client.on(events.CallbackQuery())
# async def callback_handler(event):
#     if event.data == b'data_option1':
#         await event.edit('You selected Option 1!')
#     elif event.data == b'data_option2':
#         await event.edit('You selected Option 2!')

# 同时运行客户端和机器人
with user_client, bot_client:
    user_client.run_until_disconnected()
