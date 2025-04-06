from mongoengine import (
    Document, ReferenceField, BooleanField, 
    StringField, ListField, IntField
)
from .user import User

class AutoReplySettings(Document):
    user = ReferenceField(User, required=True)
    enabled = BooleanField(default=False)
    reply_to_all = BooleanField(default=False)
    reply_to_negative = BooleanField(default=True)
    reply_template = StringField()
    custom_responses = ListField(StringField())
    excluded_topics = ListField(StringField())
    max_replies_per_day = IntField(default=50)
    cooldown_minutes = IntField(default=5)  # Minutes between replies to same user

    meta = {
        'collection': 'auto_reply_settings',
        'indexes': ['user']
    }

    def __str__(self):
        return f"Auto Reply Settings for {self.user.email}"
