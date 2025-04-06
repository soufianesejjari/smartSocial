from ..models import ScheduledPost, User
from .facebook_service import FacebookService
from typing import List, Optional
from datetime import datetime

class SchedulingService:
    def __init__(self):
        self.fb_service = FacebookService()

    def schedule_post(self, user: User, content: str, scheduled_time: datetime) -> ScheduledPost:
        scheduled_post = ScheduledPost(
            user=user,
            content=content,
            scheduled_time=scheduled_time,
            status='pending'
        ).save()
        return scheduled_post

    def get_pending_posts(self) -> List[ScheduledPost]:
        return ScheduledPost.objects(
            status='pending',
            scheduled_time__lte=datetime.utcnow()
        )

    def process_scheduled_posts(self) -> None:
        pending_posts = self.get_pending_posts()
        for post in pending_posts:
            try:
                # Attempt to publish the post
                response = self.fb_service.create_post(post.content)
                if response.get('id'):
                    post.status = 'published'
                else:
                    post.status = 'failed'
            except Exception as e:
                post.status = 'failed'
            finally:
                post.save()

    def get_user_scheduled_posts(self, user: User) -> List[ScheduledPost]:
        return ScheduledPost.objects(user=user).order_by('scheduled_time')

    def cancel_scheduled_post(self, post_id: str, user: User) -> Optional[ScheduledPost]:
        post = ScheduledPost.objects(id=post_id, user=user, status='pending').first()
        if post:
            post.delete()
            return post
        return None
