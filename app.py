import requests, json, re, subprocess
from bs4 import BeautifulSoup, SoupStrainer
from html import escape
import codecs
from flask import Flask, requests
import telegram
import os
import json

from dotenv import dotenv_values

config = dotenv_values(".env")

from stellar_sdk import Keypair, Network, Server, TransactionBuilder
from stellar_sdk.keypair import Keypair
import requests
from stellar_sdk import Keypair
#from stellar_base.address import Address

server = Server(horizon_url="https://horizon-testnet.stellar.org")
secret = os.environ['SECRET']
source = Keypair.from_secret("secret")
destination = Keypair.random()


class BoilerPlate:
    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    def get_updates(self, offset=0, timeout=10000):                 #FOR GETTING UPDATES
        function = 'getUpdates'
        fieldss = {'timeout' : timeout, 'offset': offset}
        send = requests.get(self.api_url + function, fieldss)
        result_json = send.json()['result']
        return result_json

    def send_message(self, chat_id, text):                          #FOR SENDING MESSAGES
        fieldss = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
        function = 'sendMessage'
        send = requests.post(self.api_url + function, fieldss)
        return send
    def send_message_two(self, chat_id, text, reply_markup, one_time_keyboard=False, resize_keyboard=True):     #FOR SENDING MESSAGES WITH A BOT KEYBOARD. PASS [['KEYBOARD BUTTON NAME']]
        reply_markup = json.dumps({'keyboard': reply_markup, 'one_time_keyboard': one_time_keyboard, 'resize_keyboard': resize_keyboard})
        fieldss = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML', 'reply_markup': reply_markup}
        function = 'sendMessage'
        send = requests.post(self.api_url + function, fieldss).json()
        return send
    
    def delete_message(self, group_id, message_id):         #FOR DELETING MESSAGES FROM GROUP
        fieldss = {'chat_id': group_id, 'message_id': message_id}
        function = 'deleteMessage'
        send = requests.post(self.api_url + function, fieldss)
        return send
    
    def deleteWebhook(self):                #CALL THIS AFTER CURRENT_UPDATE IF THERE IS A WEBHOOK ERROR
        function = 'deleteWebhook'
        send = requests.post(self.api_url + function)
        return send

#token = '.env.token'
offset = 0                  #MODIFY TO -1 TO READ ONLY THE LAST MESSAGE AND IGNORE ALL PREVIOUS MESSAGE. OTHERWISE DO NOT CHANGE
bot = BoilerPlate(token)    #bot.get_updates(offset = update_id+1) IS USED TO PREVENT THE BOT FROM READING THE SAME MESSAGE

TOKEN = os.environ['TOKEN']
bot = telegram.Bot(token=TOKEN)

def starter():
    global offset
    while True:
        all_updates = bot.get_updates(offset)
        for current_updates in all_updates:
           # print(current_updates)
            update_id = current_updates['update_id']
            if 'edited_message' in current_updates:
                bot.get_updates(offset = update_id+1)
                pass
            if 'poll' in current_updates:
                bot.get_updates(offset = update_id+1)
                pass
            if 'mention' in current_updates:
                bot.get_updates(offset = update_id+1)
                pass
            elif 'text' not in current_updates['message']:
                bot.get_updates(offset = update_id+1)
                pass
            else:
                dict_checker = []
                for keys in current_updates.get('message'):
                    dict_checker.append(keys)
                update_id = current_updates['update_id']
                group_id = current_updates['message']['chat']['id']
                sender_id = current_updates['message']['from']['id']
                if 'new_chat_members' in dict_checker or 'left_chat_member' in dict_checker or 'photo' in dict_checker:
                    group_message_handler(current_updates, update_id, sender_id, group_id, dict_checker)
                else:
                    bot_message_handler(current_updates, update_id, sender_id, group_id, dict_checker)

def bot_message_handler(current_updates, update_id, sender_id, group_id, dict_checker):
    global offset
    text = current_updates['message']['text']
    try:
        if text == '/start' or text == '/help' or text == '/help@stellarbot':
            bot.send_message(group_id, ("The following commands are at your disposal:\n/hi\n/moon\n/help\n/commands\n/price\n/marketcap\n/balance\n/deposit\n/withdraw\n/tip"))
            bot.get_updates(offset = update_id+1)

        if  text == '/hi' or text == '/hi@stellarbot':
            first = current_updates['message']['from']['first_name']
            bot.send_message(group_id, f'Hello {first}, How are you doing today?')
            bot.get_updates(offset = update_id+1)
        
        # stellar create account

        if  text == '/payment' or text == '/payment@stellarbot':
            keypair = Keypair.random()
            url = "https://friendbot.stellar.org"
            _response = requests.get(url, params={"addr": keypair.public_key})
            bot.send_message(group_id, f'1 XLM_NGN is valued at : {_response}')
            bot.get_updates(offset = update_id+1)


            # get stellar price
        if  text == '/price' or text == '/price@stellarbot':
            r = requests.get('https://ticker.stellar.org/markets.json')
            json_obj = r.json()
            # Parse through market data for XLM_USD pair - has most volume
            def get_price(json_obj, name):
                for dict in json_obj['pairs']:
                    if dict['name'] == name:
                        return dict['price']
            # Parse through market data for XLM_USD pair - has most volume
            def get_price(json_obj, name):
                for dict in json_obj['pairs']:
                    if dict['name'] == name:
                        return dict['price']
            # Set XLM price in NGN ( #1 / # XLM ) 
            xlm_price =  1 / get_price(json_obj, 'XLM_NGN')
            bot.send_message(group_id, f'1 XLM_NGN is valued at : {xlm_price}')
            bot.get_updates(offset = update_id+1)

            

  

        if text == '/moon1' or text == '/moon1@stellarbot':
            print("create a random keypair")
            kp = Keypair.random(1)
            bot.send_message(group_id, f'Secret: {kp.secret}')
            bot.send_message(group_id, f'Public Key: {kp.public_key}')
            bot.send_message(group_id, f'-' * 1)

        if text == '/moon2' or text == '/moon2@stellarbot':
            print("create a random keypair from secret")
            secret = "SD6VN4JA23HGE2SMBIQO4IRRSJKZKZ2TZ7XAJXAXH4BKCO356VGZ5XQE"
            kp = Keypair.from_secret(secret)
            bot.send_message(group_id, f'Secret: {kp.secret}')
            bot.send_message(group_id, f'Public Key: {kp.public_key}')
            bot.send_message(group_id, f'-' * 68)
            bot.get_updates(offset = update_id+1)

            
        
        if text == '/balance1' or text == '/balance1@stellarbot':
            print("create a random keypair")
            #kp = Keypair.random()
            bot.send_message(group_id, f'Secret: {kp.secret}')
            bot.send_message(group_id, f'Public Key: {kp.public_key}')
            bot.send_message(group_id, f'-' * 1)
        

            

        if  text == '/marketcap' or text == '/marketcap@stellarbot':
            quote_page = requests.get('https://www.worldcoinindex.com/coin/stellarlumens')
            strainer = SoupStrainer('div', attrs={'class': 'row mob-coin-table'})
            soup = BeautifulSoup(quote_page.content, 'html.parser', parse_only=strainer)
            name_box = soup.find('div', attrs={'class':'col-md-6 col-xs-6 coin-marketcap'})
            name = name_box.text.replace("\n","")
            mc = re.sub(r'\n\s*\n', r'\n\n', name.strip(), flags=re.M)
            bot.send_message(group_id, f"The current market cap of Stellar is valued at {mc}")
            bot.get_updates(offset = update_id+1)




def group_message_handler(current_updates, update_id, sender_id, group_id, dict_checker):
    message_id = current_updates['message']['message_id']

    if 'text' not in dict_checker and sender_id != group_id:
        if 'photo' in dict_checker:
            pass
        else:
            print('new member joined or left')
            bot.delete_message(group_id, message_id)
            bot.get_updates(offset = update_id+1)
    

if __name__ == "__main__":
    starter()


'''FOR BOT FATHER -> SELECT BOT -> EDIT BOT -> EDIT COMMAND 

balance - shows balance
moon - to the moon
help - available commands
deposit - get deposit address
price - shows ILCoin price
marketcap - shows ILCoin marketcap
hi - welcome message
commands - shows how to use commands

EDIT DESCRIPTION AS NEEDED
'''
