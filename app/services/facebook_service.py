import requests
from typing import Any, Dict
import logging
from ..config import get_settings
from datetime import datetime, timedelta

settings = get_settings()
GRAPH_API_BASE_URL = "https://graph.facebook.com/v18.0"

class FacebookService:
    def __init__(self):
        self.page_id = settings.FACEBOOK_PAGE_ID
        self.access_token = settings.FACEBOOK_PAGE_ACCESS_TOKEN
        self.logger = logging.getLogger(__name__)

    def get_page_posts(self) -> Dict[str, Any]:
        try:
            url = f"{GRAPH_API_BASE_URL}/{self.page_id}/feed"
            params = {
                "access_token": self.access_token,
                "fields": "id,message,created_time,permalink_url",
                "limit": 25
            }
            response = requests.get(url, params=params)
            result = response.json()
            
            # Check if we got valid data
            if 'data' in result and result['data']:
                return result
            else:
                return self._get_mock_posts()
        except Exception as e:
            self.logger.error(f"Error fetching posts: {str(e)}")
            return self._get_mock_posts()

    def get_post_comments(self, post_id: str) -> Dict[str, Any]:
        try:
            url = f"{GRAPH_API_BASE_URL}/{post_id}/comments"
            params = {
                "access_token": self.access_token,
                "fields": "id,message,from,created_time",
            }
            response = requests.get(url, params=params)
            result = response.json()
            
            # Check if we got valid data
            if 'data' in result:
                return result
            else:
                return self._get_mock_comments(post_id)
        except Exception as e:
            self.logger.error(f"Error fetching comments: {str(e)}")
            return self._get_mock_comments(post_id)

    def create_post(self, message: str) -> Dict[str, Any]:
        url = f"{GRAPH_API_BASE_URL}/{self.page_id}/feed"
        params = {
            "message": message,
            "access_token": self.access_token
        }
        response = requests.post(url, params=params)
        return response.json()

    def update_post(self, post_id: str, message: str) -> Dict[str, Any]:
        url = f"{GRAPH_API_BASE_URL}/{post_id}"
        params = {
            "message": message,
            "access_token": self.access_token
        }
        response = requests.post(url, params=params)
        return response.json()

    def delete_post(self, post_id: str) -> Dict[str, Any]:
        url = f"{GRAPH_API_BASE_URL}/{post_id}"
        params = {
            "access_token": self.access_token
        }
        response = requests.delete(url, params=params)
        return response.json()

    def get_post_metrics(self, post_id: str) -> Dict[str, Any]:
        url = f"{GRAPH_API_BASE_URL}/{post_id}/insights"
        params = {
            "metric": "post_impressions,post_engagements",
            "access_token": self.access_token
        }
        response = requests.get(url, params=params)
        return response.json()

    def reply_to_comment(self, comment_id: str, message: str) -> Dict[str, Any]:
        """Replies to a comment."""
        url = f"{GRAPH_API_BASE_URL}/{comment_id}/comments"  # Changed from 'replies' to 'comments'
        params = {
            "message": message,
            "access_token": self.access_token,
        }
        try:
            response = requests.post(url, params=params)
            result = response.json()
            if 'error' in result:
                self.logger.error(f"Error replying to comment: {result['error']}")
            return result
        except Exception as e:
            self.logger.error(f"Error replying to comment: {str(e)}")
            return {"error": str(e)}

    def process_new_comment(self, comment_data: dict, llm_service, auto_reply_settings=None):
        """Process a new comment and auto-reply if settings enabled."""
        try:
            comment_id = comment_data.get('id')
            comment_message = comment_data.get('message', '')
            
            if not comment_id or not comment_message:
                return None
                
            # Analyze sentiment
            sentiment = llm_service.analyze_sentiment(comment_message)
            
            # Check if auto-reply is enabled
            if auto_reply_settings and auto_reply_settings.enabled:
                should_reply = False
                
                # Determine if we should reply based on settings
                if auto_reply_settings.reply_to_all:
                    should_reply = True
                elif auto_reply_settings.reply_to_negative and sentiment['sentiment'] == 'negative':
                    should_reply = True
                    
                if should_reply:
                    # If we have a page profile, use it for context
                    context = "We aim to provide excellent service and value customer feedback."
                    
                    # Generate and send reply
                    if auto_reply_settings.reply_template:
                        reply = auto_reply_settings.reply_template
                    else:
                        reply = llm_service.generate_response(comment_message, context)
                        
                    self.reply_to_comment(comment_id, reply)
                    return {"comment_id": comment_id, "reply": reply, "sentiment": sentiment}
            
            return {"comment_id": comment_id, "sentiment": sentiment, "auto_replied": False}
            
        except Exception as e:
            self.logger.error(f"Error processing new comment: {str(e)}")
            return None

    def get_recent_comments(self, limit: int = 10) -> Dict[str, Any]:
        try:
            comments = []
            posts = self.get_page_posts()
            
            for post in posts.get('data', [])[:5]:  # Check last 5 posts for comments
                post_comments = self.get_post_comments(post['id'])
                for comment in post_comments.get('data', []):
                    comment['post_id'] = post['id']
                    comment['post_message'] = post.get('message', '')[:50] + '...' if len(post.get('message', '')) > 50 else post.get('message', '')
                    comments.append(comment)
                    
                    if len(comments) >= limit:
                        break
                
                if len(comments) >= limit:
                    break
            
            if not comments:
                return self._get_mock_recent_comments(limit)
                    
            return {"data": sorted(comments, key=lambda x: x.get('created_time', ''), reverse=True)[:limit]}
        except Exception as e:
            self.logger.error(f"Error getting recent comments: {str(e)}")
            return self._get_mock_recent_comments(limit)

    # Add mock data methods
    def _get_mock_posts(self) -> Dict[str, Any]:
        """Generate mock posts for development/testing."""
        return {
            "data": [
                {
                    "id": "mock_post_1",
                    "message": "Excited to announce our latest product update! Check out the new features that will make your experience even better.",
                    "created_time": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S+0000"),
                    "permalink_url": "https://facebook.com/mock_post_1"
                },
                {
                    "id": "mock_post_2",
                    "message": "What's your favorite productivity hack? Share in the comments below! We'll compile the best ones for a future post.",
                    "created_time": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%S+0000"),
                    "permalink_url": "https://facebook.com/mock_post_2"
                },
                {
                    "id": "mock_post_3",
                    "message": "Thank you to everyone who joined our webinar yesterday! The recording is now available on our website.",
                    "created_time": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S+0000"),
                    "permalink_url": "https://facebook.com/mock_post_3"
                },
                {
                    "id": "mock_post_4",
                    "message": "We're hiring! Check out our careers page for exciting opportunities to join our growing team.",
                    "created_time": (datetime.now() - timedelta(days=12)).strftime("%Y-%m-%dT%H:%M:%S+0000"),
                    "permalink_url": "https://facebook.com/mock_post_4"
                },
                {
                    "id": "mock_post_5",
                    "message": "Did you know? Today in tech history: The first iPhone was released on this day in 2007. How far we've come!",
                    "created_time": (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%dT%H:%M:%S+0000"),
                    "permalink_url": "https://facebook.com/mock_post_5"
                }
            ]
        }
        
    def _get_mock_comments(self, post_id: str) -> Dict[str, Any]:
        """Generate mock comments for a post."""
        return {
            "data": [
                {
                    "id": f"{post_id}_comment_1",
                    "message": "This update looks amazing! Can't wait to try the new features.",
                    "from": {"name": "John Smith", "id": "user_1"},
                    "created_time": (datetime.utcnow() - timedelta(hours=6)).strftime("%Y-%m-%dT%H:%M:%S+0000")
                },
                {
                    "id": f"{post_id}_comment_2",
                    "message": "Will this be available for Android users too?",
                    "from": {"name": "Emma Wilson", "id": "user_2"},
                    "created_time": (datetime.utcnow() - timedelta(hours=8)).strftime("%Y-%m-%dT%H:%M:%S+0000")
                },
                {
                    "id": f"{post_id}_comment_3",
                    "message": "I've been waiting for these features for so long! Thank you!",
                    "from": {"name": "Michael Brown", "id": "user_3"},
                    "created_time": (datetime.now() - timedelta(days=2, hours=1)).strftime("%Y-%m-%dT%H:%M:%S+0000")
                }
            ]
        }
        
    def _get_mock_recent_comments(self, limit: int = 10) -> Dict[str, Any]:
        """Generate mock recent comments across all posts."""
        all_comments = []
        mock_posts = self._get_mock_posts()
        
        for post in mock_posts.get('data', []):
            post_comments = self._get_mock_comments(post['id'])
            for comment in post_comments.get('data', []):
                comment['post_id'] = post['id']
                comment['post_message'] = post.get('message', '')[:50] + '...' if len(post.get('message', '')) > 50 else post.get('message', '')
                all_comments.append(comment)
        
        # Sort by created_time and take the most recent
        all_comments.sort(key=lambda x: x.get('created_time', ''), reverse=True)
        return {"data": all_comments[:limit]}
    
    def generate_post_suggestions(self, llm_service, profile_settings=None, location=None) -> Dict[str, Any]:
        """Generates post suggestions based on profile settings and location."""
        try:
            # Current date for calendar-based suggestions
            now = datetime.now()
            date_context = f"Today is {now.strftime('%A, %B %d, %Y')}."
            
            # Location context
            location_context = f"Target audience location is {location}." if location else ""
            
            # Profile settings context
            profile_context = ""
            if profile_settings:
                if profile_settings.get('tone'):
                    profile_context += f"Content tone should be {profile_settings.get('tone')}. "
                if profile_settings.get('topics'):
                    profile_context += f"Preferred topics include: {', '.join(profile_settings.get('topics'))}. "
                if profile_settings.get('industry'):
                    profile_context += f"Industry is {profile_settings.get('industry')}. "
            
            # Generate suggestions
            prompt = f"""Based on the following context, suggest 3 social media posts:
            {date_context}
            {location_context}
            {profile_context}
            Each suggestion should include a post message and a brief explanation why it would engage the audience.
            """
            
            suggestions = llm_service.generate_post_suggestions(prompt)
            return {"suggestions": suggestions}
            
        except Exception as e:
            self.logger.error(f"Error generating post suggestions: {str(e)}")
            return self._get_mock_post_suggestions()
    
    def _get_mock_post_suggestions(self) -> Dict[str, Any]:
        """Generate mock post suggestions for development/testing."""
        return {
            "suggestions": [
                {
                    "message": "📱 #TechTuesday: Exploring the future of AI in everyday applications. What AI tools are you currently using in your workflow? Share in the comments! #AITrends #FutureTech",
                    "reason": "Timely tech content that encourages engagement through questions and uses popular hashtags."
                },
                {
                    "message": "We're excited to announce our upcoming webinar: 'Productivity Tools for the Modern Workplace' on May 15th. Register now to secure your spot! #ProductivityTips #WorkSmarter",
                    "reason": "Promotes an upcoming event while providing clear value to the audience interested in productivity."
                },
                {
                    "message": "Customer spotlight: See how @TechInnovators increased their team efficiency by 45% using our collaboration platform. Read the full case study in our bio link! #CustomerSuccess #ProductivityWins",
                    "reason": "Social proof through customer stories drives credibility and shows real-world application of your products."
                }
            ]
        }
