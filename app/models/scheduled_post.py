from mongoengine import Document, StringField, ReferenceField, DateTimeField, BooleanField
from .user import User
from .strategy import Strategy

class ScheduledPost(Document):
    user = ReferenceField(User, required=True)
    strategy = ReferenceField(Strategy)
    message = StringField(required=True)
    scheduled_time = DateTimeField(required=True)
    is_published = BooleanField(default=False)
    publish_status = StringField(default='pending', choices=['pending', 'published', 'failed'])
    fb_post_id = StringField()  # Stores the Facebook post ID after publishing
    error_message = StringField()  # Stores any error that occurred during publishing

    meta = {
        'collection': 'scheduled_posts',
        'indexes': [
            'user',
            'scheduled_time',
            'is_published',
            'publish_status'
        ],
        'ordering': ['-scheduled_time']
    }

    def __str__(self):
        return f"Post scheduled for {self.scheduled_time}"
