from telethon import TelegramClient, events
from dotenv import load_dotenv
import os
import plugins
load_dotenv()
# 客户端配置
user_api_id = int(os.getenv('USER_API_ID', 0))
user_api_hash = os.getenv('USER_API_HASH', '')
user_client = TelegramClient('malybot', user_api_id, user_api_hash)

# 机器人配置
bot_token = os.getenv('BOT_TOKEN', '')
bot_client = TelegramClient('bot', user_api_id, user_api_hash).start(bot_token=bot_token)

# 为用户定义事件处理程序
@user_client.on(events.NewMessage(pattern='hello'))
async def user_handler(event):
    await event.reply('Hello from user!')

# 为机器人定义事件处理程序
@bot_client.on(events.NewMessage(pattern='/start'))
async def bot_handler(event):
    await event.reply('Hello from bot!')

# 同时运行客户端和机器人
with user_client, bot_client:
    user_client.run_until_disconnected()
#    bot_client.run_until_disconnected()

