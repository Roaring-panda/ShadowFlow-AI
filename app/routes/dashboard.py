from flask import Blueprint, jsonify
from datetime import datetime, timedelta

bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@bp.route('/stats', methods=['GET'])
def get_stats():
    """Get dashboard statistics"""
    stats = {
        'total_workflows': 0,
        'active_workflows': 0,
        'api_calls_used': 0,
        'api_calls_limit': 1000,
        'uptime': '99.9%',
        'last_execution': None,
        'total_executions': 0
    }
    
    return jsonify(stats), 200

@bp.route('/recent-activities', methods=['GET'])
def get_recent_activities():
    """Get recent activities"""
    activities = [
        {
            'id': 1,
            'type': 'workflow_executed',
            'description': 'Workflow "Data Processing" executed successfully',
            'timestamp': (datetime.utcnow() - timedelta(hours=1)).isoformat()
        },
        {
            'id': 2,
            'type': 'plan_upgraded',
            'description': 'Plan upgraded from Free to Pro',
            'timestamp': (datetime.utcnow() - timedelta(days=1)).isoformat()
        }
    ]
    
    return jsonify({'activities': activities}), 200

@bp.route('/usage', methods=['GET'])
def get_usage():
    """Get API usage statistics"""
    usage = {
        'current_month': {
            'api_calls': 450,
            'limit': 1000,
            'percentage': 45
        },
        'workflows_executed': 12,
        'avg_execution_time': '2.3s'
    }
    
    return jsonify(usage), 200
