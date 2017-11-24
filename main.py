import requests
import json


# Telegram Bot URL
TOKEN = "AAGWCtS8NMnUquWkY9yiTIcMIEv1y12u8IE"
CHAT_ID = "-263054020"
BASE_URL = "https://api.telegram.org/bot455477447:" + TOKEN + "/sendMessage?chat_id=" + CHAT_ID + "&"

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
    [True, "Let me know if you want more options", more_options_kboard],
    [False, "https://www.yelp.com/biz/mercante-vancouver-2"],
    [False, "https://www.yelp.com/biz/my-home-cuisine-vancouver"],
    [False, "https://www.yelp.com/biz/school-of-fish-vancouver"],
    [False, "Here are more recommendations based on your preferences"],
    [False, "https://www.yelp.com/biz/burgoo-bistro-vancouver"],
    [False, "https://www.yelp.com/biz/the-wolf-and-hound-vancouver"],
    [False, "https://www.yelp.com/biz/the-diner-vancouver"],
    [False, "Have a great dinner!"],
    [True, "Feel free to let me know how I did :)", eval_kboard],
    [True, "Rate 1-5, how intuitive was the bot?", rate_kboard]
]


def _get_request(msg_text):
    return requests.get(url=BASE_URL + "&text=" + msg_text)


def _post_request(data):
    return requests.post(BASE_URL, data=data)


def check_response(response):
    if response.status_code == 200:
        print("Message sent: " + str(response.status_code) + "\n")
    else:
        print("Message failed: " + str(response.status_code))
        print(response.content)


"""Functions for the keyboard buttons"""


def build_keyboard(description, custom_keyboard):
    data = format_message(text=description, reply_markup=custom_keyboard)

    return data


def format_message(text, reply_markup):
    return {
        'text': text,
        'reply_markup': json.dumps(to_dict(reply_markup))
    }


def to_dict(keyboard):
    data = {'keyboard': []}

    for row in keyboard:
        data['keyboard'].append([button.to_dict() if hasattr(button, 'to_dict') else button for button in row])

    return data


def run_bot():
    """
        Main function which runs the script
            * Script content dictionary
                                                                            Type
            msgs[0] = Text vs Customized Keyboard                           {Boolean}
            msgs[1] = Text                                                  {String}
            msgs[2] = Keyboard values                                       {List}
    """
    queue_len = len(script_flow)
    for i, msgs in enumerate(script_flow):
        input("ENTER for next message in the queue (" + str(i + 1) + "/" + str(queue_len) + ")\n")
        if msgs[0]:
            keyboard = build_keyboard(description=msgs[1], custom_keyboard=msgs[2])
            res = _post_request(data=keyboard)
        else:
            res = _get_request(msg_text=msgs[1])
        check_response(response=res)

    print("*****\nScript is complete\n*****\n")


if __name__ == "__main__":
    run_bot()
