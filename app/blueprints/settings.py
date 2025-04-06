from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from ..models import PageProfile, AutoReplySettings
from ..services.llm_service import LLMService
from datetime import datetime  # Add this import

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')
llm_service = LLMService()

@settings_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    profile = PageProfile.objects(user=current_user).first()
    
    if request.method == 'POST':
        if not profile:
            profile = PageProfile(user=current_user)
        
        profile.page_name = request.form.get('page_name')
        profile.page_id = request.form.get('page_id')
        profile.category = request.form.get('category')
        profile.target_audience = request.form.get('target_audience')
        profile.content_language = request.form.get('content_language', 'en')
        profile.save()
        
        flash('Profile settings updated successfully!')
        return redirect(url_for('settings.profile'))
    
    return render_template('settings/profile.html', profile=profile)

@settings_bp.route('/templates', methods=['GET', 'POST'])
@login_required
def templates():
    profile = PageProfile.objects(user=current_user).first()
    
    if request.method == 'POST':
        template = request.form.get('template')
        if not profile:
            flash('Please set up your page profile first')
            return redirect(url_for('settings.profile'))
        
        if template:
            if not profile.response_templates:
                profile.response_templates = []
            profile.response_templates.append(template)
            profile.save()
            flash('Response template added successfully!')
    
    return render_template('settings/templates.html', 
                         templates=profile.response_templates if profile else [])

@settings_bp.route('/templates/generate', methods=['POST'])
@login_required
def generate_template():
    scenario = request.json.get('scenario')
    tone = request.json.get('tone', 'professional')
    profile = PageProfile.objects(user=current_user).first()
    
    if profile:
        context = f"Category: {profile.category}\nTarget Audience: {profile.target_audience}"
        template = llm_service.generate_response(scenario, context)
        return jsonify({'template': template})
    
    return jsonify({'error': 'Profile not found'}), 404

@settings_bp.route('/auto-reply', methods=['GET', 'POST'])
@login_required
def auto_reply_settings():
    settings = AutoReplySettings.objects(user=current_user).first()
    
    if not settings:
        settings = AutoReplySettings(user=current_user).save()
    
    if request.method == 'POST':
        settings.enabled = 'enabled' in request.form
        settings.reply_to_all = 'reply_to_all' in request.form
        settings.reply_to_negative = 'reply_to_negative' in request.form
        settings.reply_template = request.form.get('reply_template', '')
        settings.updated_at = datetime.utcnow()
        settings.save()
        
        flash('Auto-reply settings updated successfully')
        return redirect(url_for('settings.auto_reply_settings'))
    
    return render_template('settings/auto_reply.html', settings=settings)
