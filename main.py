import requests
import json
import time


# Telegram Bot URL
TOKEN = "AAGWCtS8NMnUquWkY9yiTIcMIEv1y12u8IE"   # TODO - is the token always the same
CHAT_ID = "-263054020"                          # TODO - Get the chat ID and pass it as a variable
BASE_URL = "https://api.telegram.org/bot455477447:{token}/sendMessage?chat_id={chat}".format(token=TOKEN, chat=CHAT_ID)

# Customized Keyboards
cuisines_kboard = [["We're Done Choosing!"], ["American", "Burgers"], ["Fast Food", "Japanese"], ["Pizza", "Sushi"],
                       ["Asian Fusion", "Cafes"], ["Indian", "Korean"], ["Sandwiches", "Thai"],
                       ["Breakfast", "Chinese"], ["Italian", "Noodles"], ["Seafood", "Vietnamese"]]
dietary_kboard = [["We're Done Choosing!"], ["Other (Please specify)", "None"], ["Vegetarian", "Vegan"],
                  ["Peanut", "Lactose"], ["Egg", "Wheat"], ["Soy", "Shellfish"]]
price_kboard = [["We're Done Choosing!"], ["$", "$$"], ["$$$", "$$$$"]]
location_kboard = [["We're Done Choosing!"], ["Downtown Vancouver", "West End"], ["Kitsilano", "Olympic Village"],
                  ["Burnaby", "Richmond"], ["North Vancouver", "East Vancouver"]]
more_options_kboard = [["More Restaurant Recommendations!", "Thanks, we're done!"]]
eval_kboard = [["Rate Me"], ["Help us with new restaurant suggestions"]]
rate_kboard = [["1", "2", "3", "4", "5"]]


script_flow = [
    [False, "Hello, I’m Yelp4Groups. Tell me what you guys feel like eating tonight"],
    [True, "Please choose one or more of the following:", cuisines_kboard],
    [False, "OK, that'll give me a better of idea of what kind of cuisines you guys want."],
    [True, "Does anyone have any particular dietary restrictions?", dietary_kboard],
    [True, "What price range are you guys thinking?", price_kboard],
    [True, "What location should I search in?", location_kboard],
    [False, "Got it. Let me think…"],
    [False, "I have found these places so far…"],
    [False, "https://www.yelp.com/biz/mercante-vancouver-2"],
    [False, "https://www.yelp.com/biz/my-home-cuisine-vancouver"],
    [False, "https://www.yelp.com/biz/school-of-fish-vancouver"],
    [True, "Let me know if you want more options", more_options_kboard],
    [False, "Here are more recommendations based on your preferences"],
    [False, "https://www.yelp.com/biz/burgoo-bistro-vancouver"],
    [False, "https://www.yelp.com/biz/the-wolf-and-hound-vancouver"],
    [False, "https://www.yelp.com/biz/the-diner-vancouver"],
    [False, "Have a great dinner!"],
    [True, "Feel free to let me know how I did :)", eval_kboard],
    [True, "Rate 1-5, how intuitive was the bot?", rate_kboard],
    [None]
]


"""HTTP Requests to chat: GET for text messages, POST for customized keyboards """


def _get_request(msg_text):
    return requests.get(url=BASE_URL + "&text=" + msg_text)


def _post_request(data):
    return requests.post(url=BASE_URL, data=data)


def check_response(response):
    if response.status_code == 200:
        print("Message sent: {code}\n".format(code=response.status_code))
    else:
        print("Message failed: {code}\n{content}".format(code=response.status_code, content=response.content))


"""Functions for the keyboard buttons"""


def build_keyboard(description, custom_keyboard):
    data = {
        'text': description,
        'reply_markup': json.dumps(to_dict(custom_keyboard))
    }

    return data


def to_dict(keyboard):
    keyboard_data = {'keyboard': []}
    for row in keyboard:
        keyboard_data['keyboard'].append([button.to_dict() if hasattr(button, 'to_dict') else button for button in row])

    return keyboard_data


"""Script entry"""


def run_bot():
    """
        Main function which runs the script
            * Script content dictionary
                                                                            Type
            msgs[0] = Text vs Customized Keyboard                           {Boolean}
            msgs[1] = Text                                                  {String}
            msgs[2] = Keyboard values                                       {List}
    """
    chat_updates = GetChatUpdates()                         # creates queue of latest chat ids

    queue_len = len(script_flow)
    for i, msgs in enumerate(script_flow):
        print("Message in queue: (" + str(i + 1) + "/" + str(queue_len) + ")")

        if msgs[0] is None:
            exit("\n*****\nScript is complete\n*****\n")
        elif msgs[0]:
            keyboard = build_keyboard(description=msgs[1], custom_keyboard=msgs[2])
            res = _post_request(data=keyboard)
            chat_updates.wait_till_done()
        else:
            res = _get_request(msg_text=msgs[1])
        check_response(response=res)


class GetChatUpdates:
    """
    Polls chat server until user completion has been selected
    """
    latest_id = 0

    def __init__(self):
        self.set_chat_id()

    def _get_chat_history(self):
        updates_url = "https://api.telegram.org/bot455477447:{token}/getUpdates?offset={last_id}".format(
            token=TOKEN,
            last_id=self.latest_id
        )
        data = {'timeout': 0, 'limit': 100}

        return requests.post(updates_url, data=data, timeout=float(30.) + float(0))

    def set_chat_id(self):
        res = self._get_chat_history()

        if res.status_code == 200:
            last_id = [res['update_id'] for res in res.json()['result']][-1]
            self.latest_id = last_id
            print("Latest chat ID has been set to: {last_id}".format(last_id=last_id))

        else:
            print("Error in request: {code}\n{content}".format(code=res.status_code, content=res.json()))
            self.latest_id = 0

    def poll_chat_history(self):
        res = self._get_chat_history()

        if res.status_code == 200:
            last_msg = [[res['update_id'], res['message']['text']] for res in res.json()['result']][-1]

            if self.is_done_trigger(msg=last_msg[1]) and self.latest_id != last_msg[0]:
                self.latest_id = last_msg[0]
                return True

            return False

        else:
            print("Error in request: {code}\n{content}".format(code=res.status_code, content=res.json()))
            return False

    def wait_till_done(self):
        is_done = self.poll_chat_history()
        if is_done:
            return
        else:
            print("Polling chat till finished")
            time.sleep(0.5)
            self.wait_till_done()

    @staticmethod
    def is_done_trigger(msg):
        done_msgs = ["We're Done Choosing!", "Thanks, we're done!", "More Restaurant Recommendations!", "Rate Me"]
        evaluation_ratings = ["1", "2", "3", "4", "5"]
        if msg in done_msgs or msg in evaluation_ratings:
            return True

        return False


if __name__ == "__main__":
    run_bot()
