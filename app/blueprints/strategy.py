from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from ..models import Strategy  # Updated import
from ..services.llm_service import LLMService

strategy_bp = Blueprint('strategy', __name__, url_prefix='/strategy')
llm_service = LLMService()

@strategy_bp.route('/')
@login_required
def index():
    """List all strategies."""
    strategies = Strategy.objects(user=current_user).order_by('-is_active')
    return render_template('strategy/index.html', strategies=strategies)

@strategy_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new strategy."""
    if request.method == 'POST':
        try:
            strategy = Strategy(
                user=current_user.id,  # Assuming current_user.id exists
                name=request.form.get('name'),
                description=request.form.get('description'),
                business_type=request.form.get('business_type'),
                target_audience=request.form.getlist('target_audience'),
                key_objectives=request.form.getlist('key_objectives'),
                tone_of_voice=request.form.get('tone_of_voice'),
                key_topics=request.form.getlist('key_topics'),
                content_pillars=request.form.getlist('content_pillars'),
                value_propositions=request.form.getlist('value_propositions')
            )
            strategy.save()
            
            if request.form.get('is_active'):
                Strategy.objects(user=current_user.id, id__ne=strategy.id).update(is_active=False)
                strategy.is_active = True
                strategy.save()
                
                llm_service.set_strategy(strategy)
            
            flash('Strategy created successfully!', 'success')
            return redirect(url_for('strategy.index'))
        except Exception as e:
            flash(f'Error creating strategy: {str(e)}', 'error')
            
    return render_template('strategy/create.html')

@strategy_bp.route('/<strategy_id>/activate', methods=['POST'])
@login_required
def activate(strategy_id):
    """Activate a specific strategy."""
    try:
        strategy = Strategy.objects.get(id=strategy_id, user=current_user.id)
        
        # Deactivate all other strategies
        Strategy.objects(user=current_user.id).update(is_active=False)
        
        # Activate selected strategy
        strategy.is_active = True
        strategy.save()
        
        # Update LLM service with new strategy
        llm_service.set_strategy(strategy)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
