import constants
from datetime import datetime
import json
import logging

class Settings():
    def __init__(self, settings_file):
        self.settings_file = settings_file
        self.channel_reminder = None
        self.admin = None
        self.token = None
        self.announcement_channel = None
        self.prefix = constants.DEFAULT_PREFIX
    
    def parse_settings(self):
        try:
            with open(self.settings_file, 'r') as f:
                data = json.loads(f.read())
            self.token = data.get("token")
            self.admin = data.get("admin")
            self.prefix = data.get("prefix")
            self.announcement_channel = data.get("announcement_channel")
            return True
        except Exception as e:
            logging.critical(f'Failed to parse_settings: {e}')
            return False
    
    def string_to_datetime(self, string):
        return datetime.strptime(string, "%B %d %Y, %H:%M:%S")