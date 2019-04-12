class User:
    def __init__(self, id, display_name, chat_id, first_name = None, last_name = None, admin = False, events = [], **kwargs):
        self.id = id
        self.display_name = display_name
        self.first_name = first_name
        self.last_name = last_name
        self.chat_id = chat_id
        self.events = events
        self.admin  = admin

        self.fields = {}

        # Allow for arbitrary fields
        for key, value in kwargs.items():
            self.fields[key] = value
    
    def to_json(self):
        obj = {
            'id': self.id,
            'display_name': self.display_name,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'chat_id': self.chat_id,
            'admin': self.admin,
            'events': self.events
        }
        obj.update(self.fields)
        return obj