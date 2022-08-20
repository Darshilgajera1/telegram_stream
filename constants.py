INSERT_TWITTER_USERNAME = """INSERT INTO innit.twitter_stream_user (group_chat_id,user_name,author_id) VALUES ('{group_chat_id}','{user_name}','{author_id}')"""
CHECK_TWITTER_USERNAME = """SELECT user_name 
                            FROM innit.twitter_stream_user WHERE
                             group_chat_id='{group_chat_id}' 
                             AND user_name = '{user_name}'
                             AND author_id = '{author_id}'"""
GET_ALL_USER = """SELECT user_name FROM innit.twitter_stream_user"""
GET_ALL_GROUP_CHAT_ID = """SELECT group_chat_id FROM innit.twitter_stream_user WHERE author_id='{author_id}' """
