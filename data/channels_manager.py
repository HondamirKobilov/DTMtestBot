import json
class ChannelsManager:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ChannelsManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, filename="data/files/channels.json"):
        if not self._initialized:
            self.filename = filename
            self.channels = self.load_channels()
            self._initialized = True

    def load_channels(self):
        with open(self.filename, "r", encoding="utf-8") as f:
            return json.load(f).get("channels", [])

    def get_channels(self):
        return self.channels

    def get_channel_by_id(self, channel_id):
        for channel in self.channels:
            if channel['id'] == channel_id:
                return channel
        return None

    def modify_channel(self, old_channel_id, new_channel_id, new_channel_title):
        for channel in self.channels:
            if channel['id'] == old_channel_id:
                channel['id'] = new_channel_id
                channel['title'] = new_channel_title
                self.save_channels()
                return True
        return False

    def add_channel(self, channel_id, channel_title):
        self.channels.append({"id": channel_id, "title": channel_title})
        self.save_channels()

    def save_channels(self):
        with open(self.filename, "w+", encoding="utf-8") as f:
            json.dump({"channels": self.channels}, f, indent=4)

    def remove_channel(self, channel_id):
        self.channels = [channel for channel in self.channels if channel['id'] != channel_id]
        self.save_channels()
