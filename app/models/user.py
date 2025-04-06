from mongoengine import Document, StringField, EmailField, BooleanField
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(Document, UserMixin):
    email = EmailField(required=True, unique=True)
    password_hash = StringField(required=True)
    name = StringField(required=True)
    is_active = BooleanField(default=True)

    meta = {
        'collection': 'users',
        'indexes': ['email']
    }

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def create_user(email, password, **kwargs):
        user = User(email=email, **kwargs)
        user.set_password(password)
        user.save()
        return user

    def __str__(self):
        return self.email
