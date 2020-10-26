import unittest

from helper import TwitchChannel, return_current_time, process_api_response


class TestStringMethods(unittest.TestCase):
    def test_fake_new_game_name_and_title(self):
        """
        Test that adds fake new name and title to the broadcast
        """
        # Create new TwitchChannel
        channel = TwitchChannel("checker.conf")
        channel.game_name = "previous_fake_name"
        channel.title = "previous_game_title"

        # Fake API responses
        chat_information_response = {'_links': {}, 'chatter_count': 123, 'chatters': {'broadcaster': [], 'vips': [],
                                                                                      'moderators': [], 'staff': [],
                                                                                      'admins': [], 'global_mods': [],
                                                                                      'viewers': []}}

        fake = {'data': [
            {'broadcaster_id': '43899589', 'broadcaster_name': 'C_a_k_e', 'broadcaster_language': 'ru',
             'game_id': '27471',
             'game_name': 'fake_game_name', 'title': 'fake_title'}]}

        # Get needed parameters for the unit
        current_time = return_current_time()
        list_of_logs = list()
        dict_of_user_logs = dict()

        self.assertEqual(process_api_response(channel, fake, chat_information_response,
                                              list_of_logs, current_time, dict_of_user_logs)[1],
                         [current_time, '<Channel Moderator>',
                          'Channel game changed to fake_game_name', ''])
        self.assertEqual(process_api_response(channel, fake, chat_information_response,
                                              list_of_logs, current_time, dict_of_user_logs)[0],
                         [current_time, '<Channel Moderator>',
                          'Channel title changed to fake_title', ''])

    def test_fake_viewer_left(self):
        """
        Test, faking a user leaving a chat
        """

        # Create TwitchChannel with users "a" and "b" on the broadcast
        channel = TwitchChannel("checker.conf")
        channel.viewers = {"a", "b"}
        channel.game_name = "fake_game_name"
        channel.title = "fake_title"

        # Get the response where only user "a" is in the chat
        chat_information_response = {'_links': {}, 'chatter_count': 123, 'chatters': {'broadcaster': [], 'vips': [],
                                                                                      'moderators': [], 'staff': [],
                                                                                      'admins': [], 'global_mods': [],
                                                                                      'viewers': ["a"]}}

        # Fake all other needed parameters for the unit
        fake = {'data': [
            {'broadcaster_id': '43899589', 'broadcaster_name': 'C_a_k_e', 'broadcaster_language': 'ru',
             'game_id': '27471',
             'game_name': 'fake_game_name', 'title': 'fake_title'}]}
        current_time = return_current_time()
        dict_of_user_logs = dict()
        list_of_logs = list()
        self.assertEqual(process_api_response(channel, fake, chat_information_response,
                                              list_of_logs, current_time, dict_of_user_logs)[0],
                         [current_time, 'b', 'left the chat', '<a href="htmls/b.html">b log</a>'])

    def test_fake_viewer_entered(self):
        """
        test, faking a viewer entering a chat
        """

        # Create a channel with only user "b" in the chat room
        channel = TwitchChannel("checker.conf")
        channel.viewers = {"b"}
        channel.game_name = "fake_game_name"
        channel.title = "fake_title"

        # Fake the response where user "a" enters the chat
        chat_information_response = {'_links': {}, 'chatter_count': 123, 'chatters': {'broadcaster': [], 'vips': [],
                                                                                      'moderators': [], 'staff': [],
                                                                                      'admins': [], 'global_mods': [],
                                                                                      'viewers': ["a", "b"]}}
        # Fake all other needed info for the unit
        fake = {'data': [
            {'broadcaster_id': '43899589', 'broadcaster_name': 'C_a_k_e', 'broadcaster_language': 'ru',
             'game_id': '27471',
             'game_name': 'fake_game_name', 'title': 'fake_title'}]}
        current_time = return_current_time()
        list_of_logs = list()
        dict_of_user_logs = dict()
        self.assertEqual(process_api_response(channel, fake, chat_information_response,
                                              list_of_logs, current_time, dict_of_user_logs)[0],
                         [current_time, 'a', 'entered the chat', '<a href="htmls/a.html">a log</a>'])


if __name__ == '__main__':
    unittest.main()
