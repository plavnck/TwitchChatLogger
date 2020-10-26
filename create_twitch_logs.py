import requests
import datetime
import time
import pandas as pd
from tabulate import tabulate

from helper import TwitchChannel, return_current_time, write_table_to_html_file, headers, process_api_response

# Create new variable of class TwitchChannel taking info from the conf file
channel = TwitchChannel("checker.conf")

# Create list of logs and add the header to it; it is going to be transformed to HTML table
list_of_logs = list()
list_of_logs.append(["time", "user", "log"])

# Infinite loop for requesting to the twitch API
while True:
    # store current time in the begining of the iteration
    current_time = return_current_time()
    now = datetime.datetime.now()
    print(current_time + " Processing the code")

    # Send requests to the twitch API
    chat_information_response = requests.get(f"https://tmi.twitch.tv/group/user/{channel.name}/chatters", auth=('user', 'pass'))
    channel_information_response = requests.get(f"https://api.twitch.tv/helix/channels?broadcaster_id={channel.id}",
                                                headers=headers)
    # Process the api response and save it to the HTML file
    write_table_to_html_file(tabulate(process_api_response(channel, channel_information_response.json(),
                                                           chat_information_response.json(),
                                                           list_of_logs, current_time),
                                      tablefmt='html', headers="firstrow", stralign="center"))

    # Wait for the iteration time if it is needed
    while datetime.datetime.now() - now < pd.to_timedelta(int(channel.refresh_interval), unit='S'):
        time.sleep(1)
