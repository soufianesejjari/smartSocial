from mongoengine import Document, StringField, ReferenceField, ListField
from .user import User

class PageProfile(Document):
    user = ReferenceField(User, required=True)
    category = StringField(required=True)
    target_audience = ListField(StringField())
    content_language = StringField(default='en')
    business_description = StringField()
    brand_voice = StringField()

    meta = {
        'collection': 'page_profiles',
        'indexes': ['user']
    }

    def __str__(self):
        return f"{self.user.name}'s Page Profile"
