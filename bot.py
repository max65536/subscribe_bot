import logging
import os
from telethon import TelegramClient, events, Button
from telethon.tl.functions.contacts import SearchRequest
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.custom import Button as CustomButton
from telethon.errors import ChannelPrivateError, UsernameNotOccupiedError
from pymongo import MongoClient, ReturnDocument
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

@user_client.on(events.NewMessage())
async def message_handler(event):
    # logging.info(event.message)
    sender = await event.get_sender()
    # logging.info(sender)   
    channel = channel_collection.find_one({"channelid": sender.id}) 
    for user in channel['users']:
        for word in user['words']:
            if word in event.message.text:
                await bot_client.send_message(user['id'], "From %s:\n%s"%(sender.title, event.message.text))    
    
    # logging.info(str(sender)+":"+event.message.text)
#    await bot_client.send_message(28664002, event.message.text)
 

# 为机器人定义事件处理程序
@bot_client.on(events.NewMessage(pattern='/start'))
async def bot_handler(event):
    sender = await event.get_sender()
    # await event.reply('Hello from bot!')
    user = user_collection
    user_collection.update_one({"userid": sender.id}, 
                               {'$set':{"channels":[], "keywords":["ETH", "layer2", "BTC", "分片", "eip"]}},
                               upsert=True)
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
    await event.respond(msg, buttons = [[Button.inline('set channel', b'set_channel')]])

@bot_client.on(events.CallbackQuery(pattern=b'get_keywords'))
async def get_keywords(event):
    sender = await event.get_sender()
    user = user_collection.find_one({"userid": sender.id})
    msg = "keywords: " + ', '.join(user['keywords']) if user is not None else 'no keywords set yet'
    await event.respond(msg, buttons = [[Button.inline('set keywords', b'set_keywords')]])
    
@bot_client.on(events.NewMessage(pattern='/set_channel'))
async def set_channel(event):
    # sender = await event.get_sender()
    # user = user_collection.find_one({"userid": sender.id})
    # if user is None:
    #     post = {"userid": sender.id, "channels":["Odaily", "BlockBeats", "Foresight News", "messageloader"], "keywords":["ETH", "BTC"]}
    #     # "channelid":1919143832, "title":"messageloader"
    #     post_id = user_collection.insert_one(post).inserted_id    
    await event.respond('input a channel name or link:', reply_to=event.id, buttons=CustomButton.force_reply(selective=True, placeholder=r'"xxx" or "https://t.me/xxx"'))    
    # await event.respond('input a channel name or link:', reply_to=event.id, buttons=CustomButton.force_reply(selective=True, placeholder='test placeholder'))



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
#         await event.edit('You selected Option 1!')ReturnDocument
#     elif event.data == b'data_option2':
#         await event.edit('You selected Option 2!')

@bot_client.on(events.NewMessage(pattern='/test'))
async def start_handler(event):
    await event.respond('请回复这条消息：', reply_to=event.id, buttons=CustomButton.force_reply(selective=True, placeholder='test placeholder'))

def append_user_in_channel_db(channelid, channeltitle, userid):
    user = user_collection.find_one_and_update(
        {"userid":userid}, 
        {'$addToSet':{'channels':channeltitle}},
        return_document=ReturnDocument.AFTER)
    
    channel_collection.update_one(
        {"channelid":channelid}, 
        {'$addToSet':{'users':{'id':userid, 'words':user['keywords']}}, '$set':{"title":channeltitle}},
        upsert=True)
    return False

@bot_client.on(events.NewMessage(func=lambda e: e.is_reply))
async def reply_handler(event):
    replied_message = await event.get_reply_message()
    sender = await event.get_sender()
    if replied_message.text == '请回复这条消息：':
        await event.respond(f'你说: {event.text}')
    elif replied_message.text == 'input a channel name or link:':        
        channel_link = f"https://t.me/{event.text}" if '/' not in event.text else event.text
        try:
            newchannel = await user_client.get_entity(channel_link)
            channel_result = channel_collection.find_one({"channelid": newchannel.id})
            if channel_result is None:
                entity = await user_client(JoinChannelRequest(newchannel))
                channel_result = entity.chats[0]
                channel_collection.insert_one({"channelid":channel_result.id, "title":channel_result.title, 
                                               "users":[{"id":sender.id, "words":[]}]})
                append_user_in_channel_db(channel_result.id, channel_result.title, sender.id)
            else:
                append_user_in_channel_db(channel_result['channelid'], channel_result['title'], sender.id)

            logging.info("channel_result:"+str(channel_result))                
            await event.respond(f'成功加入频道{channel_link}')
        except UsernameNotOccupiedError:
            await event.respond("该用户名不存在。")        
        except ChannelPrivateError:
            await event.respond("你没有权限访问此频道，或者该频道是私有的。")            
        except Exception as e:
            logging.info(f"发生了错误：{str(e)}")                
            await event.respond(f"发生了错误：{str(e)}")



# 同时运行客户端和机器人
with user_client, bot_client:
    user_client.run_until_disconnected()
