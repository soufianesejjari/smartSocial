import os
import logging
from logging.handlers import RotatingFileHandler
import click
from app import create_app
from app.models import User, PageProfile, Strategy, ScheduledPost, AutoReplySettings
import colorama
from colorama import Fore, Style
from mongoengine import connect, disconnect
from pymongo import MongoClient

# Initialize colorama for Windows support
colorama.init()

def setup_logging(app):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler('logs/smartsocial.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(message)s'))
    
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('SmartSocial startup')

def check_mongodb():
    try:
        client = MongoClient('mongodb://localhost:27017/')
        client.server_info()
        click.echo(f"{Fore.GREEN}✓ MongoDB connection successful{Style.RESET_ALL}")
        return True
    except Exception as e:
        click.echo(f"{Fore.RED}✗ MongoDB connection failed: {str(e)}{Style.RESET_ALL}")
        return False

def check_environment():
    required_vars = ['FACEBOOK_PAGE_ACCESS_TOKEN', 'FACEBOOK_PAGE_ID', 'GROQ_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        click.echo(f"{Fore.RED}✗ Missing environment variables: {', '.join(missing_vars)}{Style.RESET_ALL}")
        return False
    click.echo(f"{Fore.GREEN}✓ Environment variables verified{Style.RESET_ALL}")
    return True

@click.group()
def cli():
    """SmartSocial Management CLI"""
    pass

@cli.command()
@click.option('--debug', is_flag=True, help='Enable debug mode')
def run(debug):
    """Run the SmartSocial application"""
    click.echo(f"{Fore.CYAN}Starting SmartSocial...{Style.RESET_ALL}")
    
    # Startup checks
    click.echo("\nPerforming startup checks:")
    checks_passed = True
    
    if not check_mongodb():
        checks_passed = False
    if not check_environment():
        checks_passed = False
    
    if not checks_passed:
        click.echo(f"\n{Fore.RED}Startup checks failed. Please fix the issues and try again.{Style.RESET_ALL}")
        return
    
    click.echo(f"\n{Fore.GREEN}All checks passed! Starting server...{Style.RESET_ALL}\n")
    
    try:
        # Clean any existing connections
        disconnect()
        
        # Create and configure the application
        app = create_app()
        setup_logging(app)
        
        click.echo(f"{Fore.YELLOW}Server running on http://localhost:5000{Style.RESET_ALL}")
        app.run(debug=debug)
    except Exception as e:
        click.echo(f"{Fore.RED}Error starting server: {str(e)}{Style.RESET_ALL}")
        raise
    finally:
        disconnect()

@cli.command()
def init_db():
    """Initialize the database"""
    click.echo(f"{Fore.CYAN}Initializing database...{Style.RESET_ALL}")
    
    if not check_mongodb():
        return
    
    try:
        # Ensure clean connection state
        disconnect()
        
        app = create_app()
        with app.app_context():
            # Clear collections in reverse dependency order
            AutoReplySettings.objects.delete()
            ScheduledPost.objects.delete()
            PageProfile.objects.delete()
            Strategy.objects.delete()
            User.objects.delete()
            
            click.echo(f"{Fore.GREEN}✓ Database initialized successfully{Style.RESET_ALL}")
    except Exception as e:
        click.echo(f"{Fore.RED}✗ Database initialization failed: {str(e)}{Style.RESET_ALL}")
        raise  # Add raise to see full traceback during development
    finally:
        disconnect()

@cli.command()
@click.option('--email', prompt=True, help='Admin user email')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Admin user password')
def create_admin(email, password):
    """Create an admin user"""
    if not check_mongodb():
        return
        
    try:
        disconnect()
        app = create_app()
        
        with app.app_context():
            if User.objects(email=email).first():
                click.echo(f"{Fore.RED}✗ User with email {email} already exists{Style.RESET_ALL}")
                return
            
            # Use the create_user static method
            User.create_user(
                email=email,
                password=password,
                name='Admin',
                is_active=True
            )
            
            click.echo(f"{Fore.GREEN}✓ Admin user created successfully{Style.RESET_ALL}")
    except Exception as e:
        click.echo(f"{Fore.RED}✗ Failed to create admin user: {str(e)}{Style.RESET_ALL}")
    finally:
        disconnect()

@cli.command()
def health_check():
    """Check system health"""
    click.echo(f"{Fore.CYAN}Performing health check...{Style.RESET_ALL}\n")
    
    checks = [
        ("MongoDB Connection", check_mongodb),
        ("Environment Variables", check_environment),
    ]
    
    all_passed = True
    for name, check in checks:
        click.echo(f"Checking {name}...")
        try:
            result = check()
            if not result:
                all_passed = False
        except Exception as e:
            click.echo(f"{Fore.RED}✗ {name} check failed: {str(e)}{Style.RESET_ALL}")
            all_passed = False
    
    if all_passed:
        click.echo(f"\n{Fore.GREEN}All health checks passed!{Style.RESET_ALL}")
    else:
        click.echo(f"\n{Fore.RED}Some health checks failed.{Style.RESET_ALL}")

if __name__ == '__main__':
    cli()
