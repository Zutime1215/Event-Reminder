from json import loads, dump
import requests
from datetime import datetime
from time import sleep, time
from pathlib import Path

file_path = Path.home() / '.imp.json'
with file_path.open("r") as f:
    bot_token = loads(f.read())['reminderBot']

def file(file_name, mode, text=None):
    try:
        if mode == 'write':
            with open(file_name, 'w') as fl:
                fl.write(str(text))
        else:
            with open(file_name, 'r') as fl:
                return fl.read()
    except Exception as e:
        print(f"File operation failed: {e}")


def requesting(url):
    while True:
        try:
            return requests.get(url).text
        except Exception as e:
            print(e)
            sleep(3)

def sendMessage(text, chat_id=2048432908, thread_id=""):
    snd_url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&message_thread_id={thread_id}&text={text}&parse_mode=Markdown"
    try:
        res = requesting(snd_url)
        return res
    except Exception as e:
        print(e)
        sleep(3)
        sendMessage(text, chat_id, thread_id)

def getUpdates():
    get_url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    while True:
        try:
            res = loads(requesting(get_url))
            return res
        except Exception as e:
            print(e)
            sleep(3)


msg_format = "The message format is: MM.DD.hh.mm:Reminder Message(Like 09.09.20.30:JC's Birthday)(which is Sep 09, 8:30PM JC's Birthday)"
start_msg = "Hi! I'm a reminder bot. Send me a message with a date and I'll remind you of it. " + msg_format
outdated_msg = "Hey there! The date you picked is already history."
only_text_msg = "Please only send me text message. " + msg_format
success_msg = "Success. I am gonna remind you of it."
remin_msg = "Hey there! It's time to remind you of "

last_update_id = 0
current_year = datetime.now().year
db = []

def main():
    global last_update_id, current_year, db
    while True:
        present_time_stamp = time()
        if db:
            last_reminder = db[-1]
            if last_reminder[0] < present_time_stamp:
                sendMessage(remin_msg + '\n```' + last_reminder[1] + "```", last_reminder[2])
                db.pop()
        else:
            # Database is empty
            pass

        result = getUpdates()["result"]
        if len(result) > 0:
            for res in result:
                if res["update_id"] > last_update_id:
                    last_update_id = res["update_id"]
                    file("last_update_id.txt", "write", last_update_id)
                    user_id = res["message"]["from"]["id"]
                    try:
                        msg = res["message"]["text"]
                        if res["message"]["text"] == "/start":
                            sendMessage(start_msg, user_id)
                        else:
                            try:
                                parts = msg.split(':')
                                timeOfReminder = int(datetime.strptime(str(current_year)+'.'+parts[0], "%Y.%m.%d.%H.%M").timestamp())
                                reminder = parts[1]

                                if present_time_stamp > timeOfReminder:
                                    sendMessage(outdated_msg, user_id)
                                else:
                                    db.append([timeOfReminder, reminder, user_id])
                                    db = sorted(db, key=lambda x: x[0], reverse=True)
                                    with open("./db.json", "w") as fl:
                                        dump(db, fl)

                                    sendMessage(success_msg, user_id)

                            except:
                                sendMessage(only_text_msg, user_id)
                    except:
                        sendMessage(only_text_msg, user_id)

        sleep(3)

if __name__ == "__main__":
    last_update_id = int(file("last_update_id.txt", "read"))
    db = loads(file("db.json", "read"))
    main()