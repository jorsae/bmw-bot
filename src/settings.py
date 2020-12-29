import constants
from datetime import datetime, date
import json
import logging

class Settings():
    def __init__(self, settings_file):
        self.settings_file = settings_file
        self.channel_reminder = None
        self.token = None
        self.discord_bot = None
        self.announcement_channel = None
        self.shiny_hunt_log_channel = None
        self.start_date = None
        self.prefix = constants.DEFAULT_PREFIX
    
    def parse_settings(self):
        try:
            with open(self.settings_file, 'r') as f:
                data = json.loads(f.read())
            self.token = data.get("token")
            constants.ADMIN_LIST = data.get("admin")
            constants.MODERATOR_LIST = data.get("moderator")
            self.prefix = data.get("prefix")
            self.discord_bot = data.get("discord_bot")
            self.announcement_channel = data.get("announcement_channel")
            self.shiny_hunt_log_channel = data.get('shiny_hunt_log_channel')
            self.start_date = self.string_to_date(data.get("start_date"))
            return True
        except Exception as e:
            logging.critical(f'Failed to parse_settings: {e}')
            return False
    
    def string_to_date(self, string):
        return datetime.strptime(string, "%Y-%m-%d").date()