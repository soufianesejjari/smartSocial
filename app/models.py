from . import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Document):
    email = db.StringField(required=True, unique=True)
    password = db.StringField(required=True)
    is_admin = db.BooleanField(default=False)
    created_at = db.DateTimeField(default=datetime.utcnow)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_id(self):
        return str(self.id)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @staticmethod
    def create_user(email: str, password: str, is_admin: bool = False) -> 'User':
        user = User(
            email=email,
            password=generate_password_hash(password),
            is_admin=is_admin
        )
        return user.save()

class PageProfile(db.Document):
    user = db.ReferenceField(User, required=True)
    page_id = db.StringField(required=True)
    page_name = db.StringField(required=True)
    category = db.StringField()
    target_audience = db.StringField()
    content_language = db.StringField(default='en')
    response_templates = db.ListField(db.StringField())
    created_at = db.DateTimeField(default=datetime.utcnow)

class ScheduledPost(db.Document):
    user = db.ReferenceField(User, required=True)
    content = db.StringField(required=True)
    scheduled_time = db.DateTimeField(required=True)
    status = db.StringField(choices=['pending', 'published', 'failed'])
    created_at = db.DateTimeField(default=datetime.utcnow)

class AutoReplySettings(db.Document):
    user = db.ReferenceField(User, required=True)
    enabled = db.BooleanField(default=False)
    reply_to_all = db.BooleanField(default=False)  # Reply to all comments
    reply_to_negative = db.BooleanField(default=True)  # Reply only to negative comments
    reply_template = db.StringField(default="Thank you for your feedback. We appreciate your comments and will address your concerns.")
    created_at = db.DateTimeField(default=datetime.utcnow)
    updated_at = db.DateTimeField(default=datetime.utcnow)
