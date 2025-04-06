from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User
import logging

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
logger = logging.getLogger(__name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            user = User.objects(email=email).first()
            
            # Debug logging
            logger.debug(f"Login attempt for {email}")
            logger.debug(f"User found: {user is not None}")
            
            if user and user.check_password(password):
                login_user(user)
                logger.info(f"User {email} logged in successfully")
                
                # Get the next page or default to dashboard
                next_page = request.args.get('next')
                if not next_page or not next_page.startswith('/'):
                    next_page = url_for('dashboard.index')
                    
                return redirect(next_page)
            else:
                logger.warning(f"Failed login attempt for {email}")
                flash('Invalid email or password', 'error')
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            flash('An error occurred during login', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            password = request.form.get('password')
            name = request.form.get('name')

            if User.objects(email=email).first():
                flash('Email address already registered', 'error')
                return render_template('auth/register.html')

            user = User.create_user(
                email=email,
                password=password,
                name=name,
                is_active=True
            )
            
            login_user(user)
            return redirect(url_for('dashboard.index'))
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            flash('An error occurred during registration', 'error')
            
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
