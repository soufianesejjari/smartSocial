from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from ..services import FacebookService, LLMService, SchedulingService
from datetime import datetime

content_bp = Blueprint('content', __name__, url_prefix='/content')
fb_service = FacebookService()
llm_service = LLMService()
scheduling_service = SchedulingService()

@content_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        content = request.form.get('content')
        schedule_time = request.form.get('schedule_time')
        
        if schedule_time:
            scheduled_time = datetime.strptime(schedule_time, '%Y-%m-%dT%H:%M')
            scheduling_service.schedule_post(current_user, content, scheduled_time)
            flash('Post scheduled successfully!')
        else:
            fb_service.create_post(content)
            flash('Post created successfully!')
        
        return redirect(url_for('dashboard.index'))
    
    return render_template('content/create.html')

@content_bp.route('/schedule', methods=['GET'])
@login_required
def schedule():
    scheduled_posts = scheduling_service.get_user_scheduled_posts(current_user)
    return render_template('content/schedule.html', posts=scheduled_posts)

@content_bp.route('/suggest', methods=['POST'])
@login_required
def suggest_content():
    # Check if request is AJAX or form submit
    if request.is_json:
        topic = request.json.get('topic')
    else:
        topic = request.form.get('topic')
        
    if not topic:
        if request.is_json:
            return jsonify({'error': 'Topic is required'}), 400
        flash('Please provide a topic', 'error')
        return redirect(url_for('content.create'))
    
    suggestion = llm_service.generate_content_suggestion(topic)
    
    if request.is_json:
        return jsonify({'suggestion': suggestion})
    
    # For form submissions, store in session and redirect
    flash('Content suggestion generated!')
    return render_template('content/create.html', suggestion=suggestion, topic=topic)
