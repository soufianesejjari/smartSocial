from app import create_app
from app.models import User

app = create_app()
with app.app_context():
    users = User.objects()
    for user in users:
        if 'is_admin' not in user:
            user.is_admin = False
            user.save()
    print("Updated all users to include the is_admin field.")
