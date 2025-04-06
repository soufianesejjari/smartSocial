from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from ..services.facebook_service import FacebookService
from ..services.llm_service import LLMService

posts_bp = Blueprint('posts', __name__, url_prefix='/posts')  # Added url_prefix
facebook_service = FacebookService()
llm_service = LLMService()

@posts_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    """Create a new post."""
    if request.method == 'POST':
        message = request.form.get('message')
        if not message:
            flash('Post message is required', 'error')
            return redirect(url_for('posts.create_post'))
        
        result = facebook_service.create_post(message)
        if 'error' in result:
            flash(f'Error creating post: {result["error"]["message"]}', 'error')
        else:
            flash('Post created successfully!', 'success')
            return redirect(url_for('dashboard.index'))
    
    return render_template('posts/create.html')

# API endpoint for creating posts (used by the suggestion feature)
@posts_bp.route('/api/posts', methods=['POST'])
@login_required
def api_create_post():
    """API endpoint for creating posts."""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'success': False, 'error': 'Message is required'}), 400
        
        message = data['message']
        result = facebook_service.create_post(message)
        
        if isinstance(result, dict) and 'error' in result:
            return jsonify({'success': False, 'error': str(result['error'])}), 400
        
        return jsonify({'success': True, 'data': result}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
