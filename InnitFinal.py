import telegram
from telegram import Bot
from telegram.ext import Updater,MessageHandler,Filters
from telegram.utils.request import Request
import requests
import json
import os

from constants import INSERT_TWITTER_USERNAME, CHECK_TWITTER_USERNAME, GET_ALL_USER
from db_connection import db
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
bearer_token = os.getenv('BEARER_TOKEN')


def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2FilteredStreamPython"
    return r

def get_rules():
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream/rules", auth=bearer_oauth
    )
    if response.status_code != 200:
        raise Exception(f"Cannot get rules (HTTP {response.status_code}): {response.text}")
    return response.json()


def delete_all_rules(rules):
    if rules is None or "data" not in rules:
        return None

    ids = list(map(lambda rule: rule["id"], rules["data"]))
    payload = {"delete": {"ids": ids}}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload
    )
    if response.status_code != 200:
        raise Exception(f"Cannot delete rules (HTTP {response.status_code}): {response.text}")

def set_rules(author_handle):
    sample_rules = [
        {
            "value": f"from:{author_handle}",
            "tag": "test"
        }
    ]
    payload = {"add": sample_rules}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload,
    )
    if response.status_code != 201:
        raise Exception(f"Cannot add rules (HTTP {response.status_code}): {response.text}")


def message_handler(update,context):
    user_messages = update.message.text
    if update.message.chat['type'] in ['group','supergroup']:
        get_owner = []
        bot = telegram.Bot(token=BOT_TOKEN)
        sh = bot.getChatAdministrators(chat_id=update.message['chat']['id'])
        for r in sh:
            get_owner.append(r['user']['id'])
        if (user_messages.lower() == "/start"):
            if update.message.from_user['id'] not in get_owner:
                update.message.reply_text("Sorry, only admins and creators can issue this command")
            else:
                update.message.reply_text(f"Hey! Welcome to innit bot. Innitbot helps you to track all the tweets that you want. Enter Your account id or account username to go further!")
        elif (user_messages.isdigit() or user_messages.startswith('@')):
            if user_messages.isdigit():
                if update.message.from_user['id'] not in get_owner:
                    update.message.reply_text("Sorry, only admins and creators can issue this command")
                else:
                    rules = get_rules()
                    get_all_user = db.fetchall(GET_ALL_USER)
                    for username in get_all_user:
                        user = username[0].split('@')[1]
                        set_rules(author_handle=user)
                    rules = get_rules()
                    url = "https://api.twitter.com/2/users/{}".format(user_messages)
                    response = requests.get(url, auth=bearer_oauth)
                    json_data = json.loads(response.text)
                    group_chat_id = update.message['chat']['id']
                    author_id = user_messages
                    user_name = "@" + json_data['data']['username']
                    exist_data = db.fetchall(CHECK_TWITTER_USERNAME.format(group_chat_id=group_chat_id,user_name=user_name,author_id=author_id))
                    if not exist_data:
                        data = db.fetchall(INSERT_TWITTER_USERNAME.format(group_chat_id=group_chat_id,user_name=user_name,author_id=author_id))
                        update.message.reply_text(f"Now you can track all the tweets of this user{user_messages}.")
                    else:
                        update.message.reply_text("Sorry, You already configure this Twitter handle")
            else:
                if update.message.from_user['id'] not in get_owner:
                    update.message.reply_text("Sorry, only admins and creators can issue this command")
                else:
                    rules = get_rules()
                    get_all_user = db.fetchall(GET_ALL_USER)
                    for username in get_all_user:
                        user = username[0].split('@')[1]
                        set_rules(author_handle=user)
                    rules = get_rules()
                    group_chat_id = update.message['chat']['id']
                    user_name = user_messages
                    url = "https://api.twitter.com/2/users/by/username/{}".format(user_messages.split('@')[1])
                    response = requests.get(url, auth=bearer_oauth)
                    json_data = json.loads(response.text)
                    author_id = json_data['data']['id']
                    exist_data = db.fetchall(CHECK_TWITTER_USERNAME.format(group_chat_id=group_chat_id,user_name=user_name,author_id=author_id))
                    if not exist_data:
                        data = db.fetchall(INSERT_TWITTER_USERNAME.format(group_chat_id=group_chat_id,user_name=user_name,author_id=author_id))
                        update.message.reply_text(f"Now you can track all the tweets of this user{user_messages}.")
                    else:
                        update.message.reply_text("Sorry, You already configure this Twitter handle")
        else:
            update.message.reply_text("Sorry! you can start with /start command.")


def main():
    req = Request(connect_timeout=0.5)
    t_bot = Bot(request=req,token=BOT_TOKEN)
    updater = Updater(bot=t_bot,use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(filters=Filters.all,callback=message_handler))
    updater.start_polling(timeout=123)
    updater.idle()

main()

