import datetime
import json
import requests

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

        # set of the viewers from the channel chat
        self.viewers = set()
        self.refresh_interval = interval
        # titile of the broadcast and name of the streamed game
        self.title = str()
        self.game_name = str()

    def update_viewers(self, viewers_set: set):
        """
        Method to update the viewers list

        :param viewers_set: new set of the viewers
        """
        self.viewers = viewers_set


def return_current_time():
    """
    Method, returning current time in the [hh:mm:ss] format
    :return:
    """
    now = datetime.datetime.now()

    return f"[{'%.2d' % now.hour}:{'%.2d' % now.minute}:{'%.2d' % now.second}]"


def convert_set_to_html(list_of_logs: list):
    """
    method to convert list of logs to the html-table
    :return: html code to output afterwards
    """
    output = "<Tbody><Table>"
    for log in list_of_logs:
        output = output + "<tr><th Style=\"Text-Align: Center;\">" + log[0] \
                 + "</th><th Style=\"Text-Align: Center;\">" + log[1] \
                 + "</th><th Style=\"Text-Align: Center;\">" + log[2] \
                 + "</th><th Style=\"Text-Align: Center;\">" + log[3] + "</th></tr>"
    return output


def write_table_to_html_file(line: str, path: str):
    """
    Method, writing html table lines to the html file
    :param path: path to the html file
    :param line: line with the html table code
    """
    file = open(path, 'w')

    message = f"""<html><head><style>

table {{
  font-family: arial, sans-serif;
  border-collapse: collapse;
  width: 100%;
}}

td, th {{
  border: 1px solid #dddddd;
  text-align: left;
  padding: 8px;
}}

tr:nth-child(even) {{
  background-color: #dddddd;
}}
</style></head><body><tr>{line}</tr></body></html>"""
    file.write(message)
    file.close()


def process_api_response(channel: TwitchChannel, channel_information_response: json,
                         chat_information_response: json, list_of_logs: list, current_time: str,
                         dict_of_user_logs: dict):
    """
    Method to process the responses from the API
    
    :param dict_of_user_logs: dictionary, storing each user's logs
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
        list_of_logs.append([current_time, "<Channel Moderator>", f"Channel title changed to {new_title}", ""])

    # If the game name has been changed - record it
    if channel.game_name != channel_information_response['data'][0]['game_name']:
        new_game_name = channel_information_response['data'][0]['game_name']
        channel.game_name = new_game_name
        list_of_logs.append([current_time, "<Channel Moderator>", f"Channel game changed to {new_game_name}", ""])

    # convert response to set
    new_viewers_set = set(chat_information_response['chatters']['viewers'])
    # Loop through the list of users and check, if any of them are new - else, remove them from the previous data
    for user in new_viewers_set:
        if user not in channel.viewers:
            # save the user information to the dictionary of user logs
            if user not in dict_of_user_logs:
                dict_of_user_logs[user] = [[current_time, user, "entered the chat",
                                            f"<a href=\"../chatlog.html\">previous page</a>"]]
            else:
                dict_of_user_logs[user].append([current_time, user, "entered the chat",
                                                f"<a href=\"../chatlog.html\">previous page</a>"])
            # write new information about the user in the user's html file
            write_table_to_html_file(convert_set_to_html(dict_of_user_logs[user]), f"htmls/{user}.html")
            # save changes in the logs list
            list_of_logs.append([current_time, user, "entered the chat",
                                 f"<a href=\"htmls/{user}.html\">{user} log</a>"])
        else:
            channel.viewers.discard(user)

    # Every user left in the list - are the users, that have left the chat - record this data
    for user in channel.viewers:
        # save changes in the user's logs dict
        if user not in dict_of_user_logs:
            dict_of_user_logs[user] = [[current_time, user, "left the chat",
                                        f"<a href=\"../chatlog.html\">previous page</a>"]]
        else:
            dict_of_user_logs[user].append([current_time, user, "left the chat",
                                            f"<a href=\"../chatlog.html\">previous page</a>"])
        # write changes to the user's html page and append the list of the logs
        write_table_to_html_file(convert_set_to_html(dict_of_user_logs[user]), f"htmls/{user}.html")
        list_of_logs.append([current_time, user, "left the chat", f"<a href=\"htmls/{user}.html\">{user} log</a>"])
    # Change the channel.viewers to the new list
    channel.update_viewers(new_viewers_set)
    return list_of_logs
