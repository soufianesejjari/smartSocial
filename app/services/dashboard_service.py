from .facebook_service import FacebookService
from .llm_service import LLMService
from typing import Dict, Any
from datetime import datetime, timedelta
from ..models import Strategy
import logging

logger = logging.getLogger(__name__)

class DashboardService:
    def __init__(self):
        self.fb_service = FacebookService()
        self.llm_service = LLMService()
        self.current_strategy = None

    def get_dashboard_data(self) -> Dict[str, Any]:
        try:
            # Get active strategy
            active_strategy = Strategy.objects(is_active=True).first()
            if active_strategy:
                self.llm_service.set_strategy(active_strategy)
            
            posts = self.fb_service.get_page_posts()
            recent_comments = self.fb_service.get_recent_comments(limit=5)
            profile_settings = self._get_profile_settings()
            location = self._get_user_location()
            
            # Get recent activity data
            recent_activity = self._get_recent_activity(posts)
            
            # Generate AI summaries
            activity_summary = self.llm_service.summarize_recent_activity(recent_activity)
            feedback_summary = self.llm_service.summarize_audience_feedback(recent_comments.get('data', []))
            
            post_suggestions = self.fb_service.generate_post_suggestions(
                self.llm_service, 
                profile_settings=profile_settings,
                location=location
            )
            
            # Add fallback for missing methods
            if not hasattr(self.llm_service, 'generate_quick_replies'):
                logger.warning("LLMService missing generate_quick_replies method")
                self.llm_service.generate_quick_replies = lambda comment, strategy: [
                    "Thank you for your feedback!",
                    "We appreciate your comment!",
                    "Thanks for sharing!"
                ]
            
            if not hasattr(self.llm_service, '_parse_post_suggestions'):
                logger.warning("LLMService missing _parse_post_suggestions method")
                self.llm_service._parse_post_suggestions = lambda result: []
            
            return {
                'posts': posts,
                'posts_summary': self._get_posts_summary(posts),
                'sentiment_analysis': self._analyze_comments_sentiment(posts),
                'engagement_metrics': self._calculate_engagement_metrics(posts),
                'recent_activity': recent_activity,
                'recent_comments': recent_comments,
                'post_suggestions': post_suggestions.get('suggestions', []),
                'activity_summary': activity_summary,
                'feedback_summary': feedback_summary
            }
            
        except Exception as e:
            logger.error(f"Error in dashboard data retrieval: {str(e)}")
            return self._get_empty_dashboard_data()

    def _get_empty_dashboard_data(self) -> Dict[str, Any]:
        """Return empty dashboard data structure."""
        return {
            'posts': {'data': []},
            'posts_summary': {'total_posts': 0, 'posts_this_week': 0},
            'sentiment_analysis': {'positive': 0, 'negative': 0, 'neutral': 0},
            'engagement_metrics': {'total_comments': 0, 'avg_comments_per_post': 0},
            'recent_activity': [],
            'recent_comments': {'data': []},
            'post_suggestions': [],
            'activity_summary': "No recent activity to summarize.",
            'feedback_summary': {'summary': "No feedback to analyze.", 'topics': []}
        }

    def _get_posts_summary(self, posts: Dict[str, Any]) -> Dict[str, Any]:
        data = posts.get('data', [])
        return {
            'total_posts': len(data),
            'posts_this_week': sum(1 for post in data if 
                self._is_within_days(post.get('created_time', ''), 7))
        }

    def _analyze_comments_sentiment(self, posts: Dict[str, Any]) -> Dict[str, int]:
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        for post in posts.get('data', []):
            comments = self.fb_service.get_post_comments(post['id'])
            for comment in comments.get('data', []):
                sentiment = self.llm_service.analyze_sentiment(comment['message'])
                sentiment_counts[sentiment['sentiment']] += 1
        return sentiment_counts

    def _calculate_engagement_metrics(self, posts: Dict[str, Any]) -> Dict[str, Any]:
        total_likes = 0
        total_comments = 0
        for post in posts.get('data', []):
            post_id = post['id']
            comments = self.fb_service.get_post_comments(post_id)
            total_comments += len(comments.get('data', []))
        
        return {
            'total_comments': total_comments,
            'avg_comments_per_post': total_comments / len(posts.get('data', [])) if posts.get('data') else 0
        }

    def _get_recent_activity(self, posts: Dict[str, Any]) -> list:
        recent_activities = []
        for post in posts.get('data', [])[:5]:  # Last 5 posts
            comments = self.fb_service.get_post_comments(post['id'])
            recent_activities.append({
                'post_id': post['id'],
                'message': post.get('message', ''),
                'created_time': post.get('created_time'),
                'comment_count': len(comments.get('data', []))
            })
        return recent_activities

    @staticmethod
    def _is_within_days(date_str: str, days: int = 7) -> bool:
        """Check if a date string is within the specified number of days from now."""
        try:
            post_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S+0000')
            return post_date > datetime.utcnow() - timedelta(days=days)
        except Exception:
            # If there's any error parsing the date, return False
            return False

    def _get_profile_settings(self) -> Dict[str, Any]:
        # This would normally come from a database
        # For now, let's return a sample profile
        return {
            'tone': 'friendly and professional',
            'topics': ['product updates', 'industry news', 'customer success stories'],
            'industry': 'technology',
            'posting_frequency': 'daily'
        }
        
    def _get_user_location(self) -> str:
        # This would normally be determined from user settings or analytics
        # For now, return a default location
        return "United States"
        
    def quick_reply_to_comment(self, comment_id: str, message: str) -> Dict[str, Any]:
        """Allow quick replies to comments from the dashboard."""
        return self.fb_service.reply_to_comment(comment_id, message)
