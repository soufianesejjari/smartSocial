from werkzeug.security import generate_password_hash, check_password_hash
from ..models import User
from typing import Optional

class AuthService:
    @staticmethod
    def create_user(email: str, password: str) -> User:
        hashed_password = generate_password_hash(password)
        user = User(email=email, password=hashed_password)
        return user.save()

    @staticmethod
    def verify_user(email: str, password: str) -> Optional[User]:
        user = User.objects(email=email).first()
        if user and check_password_hash(user.password, password):
            return user
        return None

    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[User]:
        return User.objects(id=user_id).first()
