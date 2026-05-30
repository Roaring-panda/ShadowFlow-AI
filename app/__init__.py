from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Configuration
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['JSON_SORT_KEYS'] = False
    
    # Register blueprints
    from app.routes import auth, payment, workflow, dashboard
    
    app.register_blueprint(auth.bp)
    app.register_blueprint(payment.bp)
    app.register_blueprint(workflow.bp)
    app.register_blueprint(dashboard.bp)
    
    return app
