import telegram
import requests
import json
import os

from constants import GET_ALL_GROUP_CHAT_ID
from db_connection import db
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
bearer_token = os.getenv('BEARER_TOKEN')

def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2FilteredStreamPython"
    return r

def get_stream():
    params = {'tweet.fields': 'author_id'}
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream", auth=bearer_oauth, stream=True, params=params
    )
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(f"Cannot get stream (HTTP {response.status_code}): {response.text}")

    for response_line in response.iter_lines():
        if response_line:
            json_response = json.loads(response_line)
            json_object = json.dumps(json_response, indent=4, sort_keys=True)
            if json_object:
                dict_response = json.loads(json_object)
                author_id = dict_response['data']['author_id']
                msg_body = dict_response['data']['text']
                user_chat_id = db.fetchall(GET_ALL_GROUP_CHAT_ID.format(author_id=author_id))
                for each_chat in set(user_chat_id):
                    each_chat_id = each_chat[0]
                    bot = telegram.Bot(token=BOT_TOKEN)
                    bot.sendMessage(chat_id=each_chat_id,text=str(msg_body),parse_mode="HTML",disable_web_page_preview=False)

get_stream()