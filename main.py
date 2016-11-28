#-*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2

import urllib
import urllib2
import json
import logging

from bball import Baseball

TOKEN           = [TELEGRAM-TOKEN]
BASE_URL        = 'https://api.telegram.org/bot' + TOKEN + '/'

CMD_START       = '/start'
CMD_STOP        = '/stop'
CMD_HELP        = '/help'

MSG_START       = """Number Baseball Game Start.
Guess %d digit Number!
Nuber range is 1 ~ 9.
You can challenge %d times."""
MSG_STOP        = "Baseball Game Stop"
MSG_HELP = """ Command List
/start - (Game Start)
/stop  - (Game Stop)
/help  - (Show this help message)
"""

CUSTOM_KEYBOARD = [
        [CMD_START],
        [CMD_STOP],
        [CMD_HELP],
        ]

class GameStatus(ndb.Model):
    enabled = ndb.BooleanProperty(required=True, indexed=True, default=False,)
    baseball = ndb.StringProperty()

def set_game(chat_id, enabled):
    gs = GameStatus.get_or_insert(str(chat_id))
    gs.enabled = enabled
    if enabled == True:
        number = Baseball.make_game()
        bb = Baseball(number)
        gs.baseball = str(bb)
    gs.put()

def get_game(chat_id):
    return GameStatus.get_by_id(str(chat_id))

def send_msg(chat_id, text, reply_to=None, no_preview=True, keyboard=None):
    params = {
        'chat_id': str(chat_id),
        'text': text.encode('utf-8'),
        }
    if reply_to:
        params['reply_to_message_id'] = reply_to
    if no_preview:
        params['disable_web_page_preview'] = no_preview
    if keyboard:
        reply_markup = json.dumps({
            'keyboard': keyboard,
            'resize_keyboard': True,
            'one_time_keyboard': False,
            'selective': (reply_to != None),
            })
        params['reply_markup'] = reply_markup
    try:
        urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode(params)).read()
    except Exception as e: 
        logging.exception(e)

def cmd_start(chat_id):
    set_game(chat_id, True)
    send_msg(chat_id, MSG_START % (Baseball.DEFAULT_NUMBER_LENGTH, Baseball.DEFAULT_GAME_COUNT))

def cmd_stop(chat_id):
    set_game(chat_id, False)
    send_msg(chat_id, MSG_STOP)

def cmd_help(chat_id):
    send_msg(chat_id, MSG_HELP, keyboard=CUSTOM_KEYBOARD)

def cmd_game(chat_id, gs, text):
    if gs.baseball is None:
        return

    bb = Baseball.loads(gs.baseball)
    res = bb.validate(text)
    if not res is None:
        send_msg(chat_id, res)
        return

    result = bb.run(text)
    s = bb.get_strike(result)
    b = bb.get_ball(result)

    if bb.is_out(result):
        send_msg(chat_id, "Great! You did it! If you want a new game, plz /start.")
        gs.baseball = str(bb)
        gs.put()
        return

    if  bb.decrease() <= 0:
        send_msg(chat_id, "Number is %s. plz /start to play again." % bb.number())
        gs.baseball = str(bb)
        gs.put()
        return

    send_msg(chat_id, "%d Strike(s), %d Ball(s). You left %d time(s)." % (s, b, bb.left_count()))
    gs.baseball = str(bb)
    gs.put()

def process_cmds(msg):
    msg_id = msg['message_id']
    chat_id = msg['chat']['id']
    text = msg.get('text')

    if (not text):
        return

    if CMD_START == text:
        cmd_start(chat_id)
        return

    gs = get_game(chat_id)
    if (not gs):
        return

    if CMD_STOP == text:
        cmd_stop(chat_id)
        return
    if CMD_HELP == text:
        cmd_help(chat_id)
        return

    cmd_game(chat_id, gs, text)
    return

class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))

class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getUpdates'))))

class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))

class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        self.response.write(json.dumps(body))
        process_cmds(body['message'])

app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set-webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
], debug=True)
