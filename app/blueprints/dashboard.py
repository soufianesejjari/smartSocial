from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from ..services.dashboard_service import DashboardService
from ..services.facebook_service import FacebookService
from ..services.llm_service import LLMService
from ..models import Strategy
dashboard_bp = Blueprint('dashboard', __name__)
dashboard_service = DashboardService()
facebook_service = FacebookService()
llm_service = LLMService()
@dashboard_bp.route('/')
@login_required
def index():
    """Display the main dashboard."""
    try:
        # Get all dashboard data
        dashboard_data = dashboard_service.get_dashboard_data()
        
        # Get active strategy
        active_strategy = Strategy.objects(user=current_user.id, is_active=True).first()
        
        # Extract required data
        posts = dashboard_data.get('posts', {})
        recent_comments = dashboard_data.get('recent_comments', {"data": []})
        post_suggestions = dashboard_data.get('post_suggestions', [])
        activity_summary = dashboard_data.get('activity_summary', "No recent activity to summarize.")
        feedback_summary = dashboard_data.get('feedback_summary', {"summary": "No feedback to analyze.", "topics": []})
        
        # Add suggested replies to each comment
        for comment in recent_comments.get('data', []):
            try:
                comment['suggested_replies'] = llm_service.generate_quick_replies(
                    comment['message'], 
                    active_strategy if active_strategy else None
                )
            except Exception as e:
                logger.error(f"Error generating quick replies for comment {comment['id']}: {str(e)}")
                comment['suggested_replies'] = ["Thank you for your feedback!", "We appreciate your input!"]
        
        # Prepare stats for the template
        stats = {
            'total_posts': dashboard_data['posts_summary'].get('total_posts', 0),
            'total_comments': dashboard_data['engagement_metrics'].get('total_comments', 0),
            'sentiment_summary': dashboard_data['sentiment_analysis']
        }
        
        return render_template(
            'dashboard/index.html', 
            active_strategy=active_strategy,
            posts=posts, 
            stats=stats,
            recent_comments=recent_comments,
            post_suggestions=post_suggestions,
            activity_summary=activity_summary,
            feedback_summary=feedback_summary
        )
    except Exception as e:
        logger.error(f"Error loading dashboard: {str(e)}")
        return render_template(
            'dashboard/index.html', 
            posts={"data": []}, 
            stats={
                'total_posts': 0,
                'total_comments': 0,
                'sentiment_summary': {'positive': 0, 'negative': 0, 'neutral': 0}
            },
            recent_comments={"data": []},
            post_suggestions=[],
            activity_summary="Unable to load activity summary.",
            feedback_summary={"summary": "Unable to load feedback analysis.", "topics": []}
        )

# Add other routes as needed...
