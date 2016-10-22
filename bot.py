# -*- coding: utf-8 -*-

__author__ = 'ufian'

import time
from collections import defaultdict, deque

import config
import telepot


# import pymongo
#
# class MongoActions(object):
#     def __init__(self):
#         self.conn = pymongo.MongoClient(config.MONGO['host'], config.MONGO['port'])
#         self.db = self.conn.get_database(config.MONGO['db'])
#
#     def init_db(self):
#         pass
#
#     def check_chat(self, chat_id):
#         pass


class Limiter(object):
    def __init__(self, size=2, min_diff=60):
        self.size = size
        self.min_diff = min_diff
        self.queues = defaultdict(lambda: deque(size*[-1], size))
        
    def push(self, key, value):
        self.queues[key].append(value)
        
        if self.queues[key][0] == -1 or (value - self.queues[key][0] > self.min_diff):
            return True

        for i in range(1, self.size):
            self.queues[key].append(-1)

        self.queues[key].append(value)
        
        return False
        

class AddmetoBot(telepot.Bot):
    def __init__(self, token):
        super(AddmetoBot, self).__init__(token)
        self.messages = Limiter(4, 60)
        self.stickers = Limiter(3, 60)
        self.metas = Limiter(3, 60)
        self.photo = Limiter(3, 60)
                
    def on_chat_message(self, msg):
        chat_id = msg.get('chat', {'id': None}).get('id')
        from_id = msg.get('from', {'id': None}).get('id')
        ts = msg.get('date')
        
        if chat_id is None or from_id is None or ts is None:
            return

        if not self.messages.push((chat_id, from_id), ts):
            self.reply(msg, 'Слишком много сообщений')
        
        if 'sticker' in msg:
            if not self.stickers.push((chat_id, from_id), ts):
                self.reply(msg, 'Стикероспам')
                
        if any(key in msg for key in (
                'audio', 'game', 'document', 'voice', 'contact', 'location','venue', 'video', 'photo'
            )):
            
            if not self.metas.push((chat_id, from_id), ts):
                self.reply(msg, 'Слишком много не того')
        
    def reply(self, msg, text):
        self.sendMessage(msg['chat']['id'], text, reply_to_message_id=msg['message_id'])
        
if __name__ == '__main__':
    bot = AddmetoBot(config.BOT_TOKEN)
    bot.message_loop()
    print ('Listening ...')

    # Keep the program running.
    while 1:
        time.sleep(10)