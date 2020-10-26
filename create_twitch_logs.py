import json
import requests
import datetime
import time
import pandas as pd
from helper import TwitchChannel, return_current_time, write_table_to_html_file, headers, process_api_response, \
    convert_set_to_html

# Create new variable of class TwitchChannel taking info from the conf file
channel = TwitchChannel("checker.conf")

# Create list of logs and add the header to it; it is going to be transformed to HTML table
list_of_logs = list()
list_of_logs.append(["time", "user", "log", "link"])

# If something went wrong - user can load previous version of dict_of_user_logs from archieve.json
answer = input("Do you wish to load previous run results? (y/n) ")
while answer != "y" and answer != "n":
    answer = input("Wrong input. Do you wish to load previous run results? (y/n) ")
if answer == "y":
    with open('archive.json') as json_file:
        dict_of_user_logs = json.load(json_file)
        for user in dict_of_user_logs:
            channel.viewers.add(user)
else:
    dict_of_user_logs = dict()

# Infinite loop for requesting to the twitch API
while True:
    # store current time in the begining of the iteration
    current_time = return_current_time()
    now = datetime.datetime.now()
    print(current_time + " Processing the code")

    # Send requests to the twitch API
    chat_information_response = requests.get(f"https://tmi.twitch.tv/group/user/{channel.name}/chatters",
                                             auth=('user', 'pass'))
    channel_information_response = requests.get(f"https://api.twitch.tv/helix/channels?broadcaster_id={channel.id}",
                                                headers=headers)
    # Process the api response and save it to the HTML file

    write_table_to_html_file(convert_set_to_html(process_api_response(channel, channel_information_response.json(),
                                                                      chat_information_response.json(),
                                                                      list_of_logs, current_time, dict_of_user_logs)),
                             "chatlog.html")

    # Wait for the iteration time if it is needed
    with open('archive.json', 'w') as fp:
        json.dump(dict_of_user_logs, fp)
    while datetime.datetime.now() - now < pd.to_timedelta(int(channel.refresh_interval), unit='S'):
        time.sleep(0.5)
