from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from ..services.facebook_service import FacebookService
from ..services.llm_service import LLMService
from ..services.dashboard_service import DashboardService
from ..models import PageProfile  # Updated import

comments_bp = Blueprint('comments', __name__, url_prefix='/comments')
facebook_service = FacebookService()
llm_service = LLMService()
dashboard_service = DashboardService()

@comments_bp.route('/monitor')
@login_required
def monitor():
    posts = facebook_service.get_page_posts()
    comments_data = []
    
    for post in posts.get('data', []):
        comments = facebook_service.get_post_comments(post['id'])
        for comment in comments.get('data', []):
            sentiment = llm_service.analyze_sentiment(comment['message'])
            comment['sentiment'] = sentiment
            comment['post_message'] = post.get('message', '')[:100] + '...'
            comments_data.append(comment)
    
    return render_template('comments/monitor.html', comments=comments_data)

@comments_bp.route('/list/<post_id>')
@login_required
def list_comments(post_id):
    """Display comments for a specific post."""
    post_comments = facebook_service.get_post_comments(post_id)
    return render_template('comments/list.html', comments=post_comments, post_id=post_id)

@comments_bp.route('/<comment_id>/reply', methods=['POST'])
@login_required
def reply(comment_id):
    message = request.json.get('message')
    response = facebook_service.reply_to_comment(comment_id, message)
    return jsonify(response)

@comments_bp.route('/auto-reply/<comment_id>', methods=['POST'])
@login_required
def auto_reply(comment_id):
    comment_text = request.json.get('comment')
    profile = PageProfile.objects(user=current_user).first()
    
    if not profile:
        return jsonify({'error': 'Page profile not found'}), 404
    
    context = f"""
    Page Category: {profile.category}
    Target Audience: {profile.target_audience}
    Language: {profile.content_language}
    """
    
    response = llm_service.generate_response(comment_text, context)
    result = facebook_service.reply_to_comment(comment_id, response)
    
    return jsonify({
        'reply': response,
        'result': result
    })

@comments_bp.route('/quick_reply', methods=['POST'])
@login_required
def quick_reply():
    """Handle quick reply to comments from the dashboard."""
    comment_id = request.form.get('comment_id')
    reply_message = request.form.get('reply_message')
    
    if not comment_id or not reply_message:
        flash('Comment ID and reply message are required.', 'error')
        return redirect(url_for('dashboard.index'))
    
    result = dashboard_service.quick_reply_to_comment(comment_id, reply_message)
    
    if 'error' in result:
        flash(f'Error replying to comment: {result["error"]}', 'error')
    else:
        flash('Reply sent successfully!', 'success')
    
    return redirect(url_for('dashboard.index'))

# Add API endpoint for comments
@comments_bp.route('/api/reply', methods=['POST'])
@login_required
def api_reply():
    """API endpoint for replying to comments."""
    data = request.json
    comment_id = data.get('comment_id')
    message = data.get('message')
    
    if not comment_id or not message:
        return jsonify({'success': False, 'error': 'Comment ID and message are required'})
    
    result = facebook_service.reply_to_comment(comment_id, message)
    
    if 'error' in result:
        return jsonify({'success': False, 'error': result['error']})
    
    return jsonify({'success': True, 'data': result})

@comments_bp.route('/negative')
@login_required
def negative_comments():
    posts = facebook_service.get_page_posts()
    negative_comments = []
    
    for post in posts.get('data', []):
        comments = facebook_service.get_post_comments(post['id'])
        for comment in comments.get('data', []):
            sentiment = llm_service.analyze_sentiment(comment['message'])
            if sentiment['sentiment'] == 'negative':
                comment['sentiment'] = sentiment
                comment['post_message'] = post.get('message', '')[:100] + '...'
                negative_comments.append(comment)
    
    return render_template('comments/negative.html', comments=negative_comments)
