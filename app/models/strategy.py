from mongoengine import Document, StringField, ListField, ReferenceField, BooleanField
from .user import User

class Strategy(Document):
    user = ReferenceField(User, required=True)
    name = StringField(required=True)
    description = StringField(required=True)
    business_type = StringField(required=True)  # e.g., "SaaS", "E-commerce", etc.
    target_audience = ListField(StringField())
    key_objectives = ListField(StringField())
    tone_of_voice = StringField()  # e.g., "professional", "casual", "technical"
    key_topics = ListField(StringField())
    content_pillars = ListField(StringField())
    value_propositions = ListField(StringField())
    is_active = BooleanField(default=True)

    meta = {
        'collection': 'strategies',
        'indexes': ['user', 'is_active']
    }

    def __str__(self):
        return f"{self.name} ({self.business_type})"
