import datetime
import json
import requests
from tabulate import tabulate

# global variable for request's header
headers = {'Authorization': 'Bearer q3x3hfavdmzvfzm196ve128xd20ex6',
           'Client-Id': 'gp762nuuoqcoxypju8c569th9wz7q5'}


# class to store information about the channel
class TwitchChannel:
    def __init__(self, path_to_conf_file: str):
        """
        :param path_to_conf_file: pathway to the checker.conf file
        """

        # open JSON conf file and take needed information
        with open(path_to_conf_file) as json_file:
            data = json.load(json_file)
            channel_name = data['channel_name']
            interval = data['refresh_interval']
        # Save channel name
        self.name = channel_name
        # Send request for the channel information and get the channel id
        answer = requests.get(f"https://api.twitch.tv/helix/users?login={channel_name}", headers=headers)
        self.id = int(answer.json()['data'][0]['id'])

        # list of the viewers from the channel chat
        self.viewers = list()
        self.refresh_interval = interval
        # titile of the broadcast and name of the streamed game
        self.title = str()
        self.game_name = str()

    def update_viewers(self, viewers_set: list):
        """
        Method to update the viewers list

        :param viewers_list: new list of the viewers
        """
        self.viewers = viewers_set


def return_current_time():
    """
    Method, returning current time in the [hh:mm:ss] format
    :return:
    """
    now = datetime.datetime.now()
    return f"[{now.hour}:{now.minute}:{now.second}]"


def write_table_to_html_file(line):
    """
    Method, writing html table lines to the html file
    :param line: line with the html table code
    """
    file = open('chatlog.html', 'w')

    message = f"""<html>
    <head></head>
    <body><tr>{line}</tr></body>
    </html>"""
    file.write(message)
    file.close()


def process_api_response(channel: TwitchChannel, channel_information_response: json,
                         chat_information_response: json, list_of_logs: list, current_time: str):
    """
    Method to process the responses from the API
    
    :param channel: TwitchChannel class object, storing information about the analyzed channel
    :param channel_information_response: json of the response from the request to the twitch channel API
    :param chat_information_response: json of the response from the reqyest to the twitch broadcast API
    :param list_of_logs: list of the current updates about the broadcast
    :param current_time: string in the format[hh:mm:ss]
    :return: updated version of list_of_logs
    """
    # If the title has been changed - record it
    if channel.title != channel_information_response['data'][0]['title']:
        new_title = channel_information_response['data'][0]['title']
        channel.title = new_title
        list_of_logs.append([current_time, "<Channel Moderator>", f"Channel title changed to {new_title}"])

    # If the game name has been changed - record it
    if channel.game_name != channel_information_response['data'][0]['game_name']:
        new_game_name = channel_information_response['data'][0]['game_name']
        channel.game_name = new_game_name
        list_of_logs.append([current_time, "<Channel Moderator>", f"Channel game changed to {new_game_name}"])

    # Loop through the list of users and check, if any of them are new - else, remove them from the previous data
    for user in chat_information_response['chatters']['viewers']:
        if user not in channel.viewers:
            list_of_logs.append([current_time, user, "entered the chat"])
        else:
            channel.viewers.remove(user)

    # Every user left in the list - are the users, that have left the chat - record this data
    for user in channel.viewers:
        list_of_logs.append([current_time, user, "left the chat"])
    # Change the channel.viewers to the new list
    channel.update_viewers(chat_information_response['chatters']['viewers'])
    return list_of_logs

