#!/usr/bin/env python3
"""
Hardcard Governance Analytics API
REST API for accessing governance analytics data
"""

import json
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import pandas as pd
from dataclasses import asdict

# Import the analytics engine
import sys
sys.path.append('..')
from governance_analytics import GovernanceAnalytics, ProposalMetrics, VotingMetrics, GuardianMetrics, SystemMetrics

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Global analytics instance
analytics = None

def init_analytics():
    """Initialize analytics engine"""
    global analytics
    if analytics is None:
        analytics = GovernanceAnalytics(
            database_path=os.getenv('ANALYTICS_DB_PATH', 'governance_analytics.db'),
            web3_url=os.getenv('WEB3_URL')
        )

@app.before_request
def before_request():
    """Initialize analytics before each request"""
    init_analytics()

@app.route('/health', methods=['GET'])
def health_check():
    """API health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'database_connected': True  # Add actual DB check
    })

@app.route('/api/v1/metrics/overview', methods=['GET'])
def get_overview_metrics():
    """Get high-level governance metrics"""
    try:
        proposal_metrics = analytics.calculate_proposal_metrics()
        voting_metrics = analytics.calculate_voting_metrics()
        guardian_metrics = analytics.calculate_guardian_metrics()
        system_metrics = analytics.calculate_system_metrics()
        
        # Calculate health score
        health_score = (
            proposal_metrics.quorum_achievement_rate * 0.3 +
            guardian_metrics.availability_rate * 0.3 +
            system_metrics.uptime_percentage / 100 * 0.2 +
            system_metrics.transaction_success_rate / 100 * 0.2
        ) * 100
        
        return jsonify({
            'timestamp': datetime.utcnow().isoformat(),
            'health_score': round(health_score, 2),
            'metrics': {
                'proposals': asdict(proposal_metrics),
                'voting': asdict(voting_metrics),
                'guardians': asdict(guardian_metrics),
                'system': asdict(system_metrics)
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/proposals', methods=['GET'])
def get_proposals():
    """Get proposals with optional filtering"""
    try:
        # Parse query parameters
        state = request.args.get('state')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Build query
        query = "SELECT * FROM proposals WHERE 1=1"
        params = []
        
        if state:
            query += " AND state = ?"
            params.append(state)
        
        if start_date:
            query += " AND created_at >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND created_at <= ?"
            params.append(end_date)
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        # Execute query
        df = pd.read_sql_query(query, analytics.conn, params=params)
        
        # Convert to JSON-serializable format
        proposals = df.to_dict('records')
        
        # Get total count for pagination
        count_query = "SELECT COUNT(*) FROM proposals WHERE 1=1"
        count_params = []
        
        if state:
            count_query += " AND state = ?"
            count_params.append(state)
        
        if start_date:
            count_query += " AND created_at >= ?"
            count_params.append(start_date)
        
        if end_date:
            count_query += " AND created_at <= ?"
            count_params.append(end_date)
        
        total_count = analytics.cursor.execute(count_query, count_params).fetchone()[0]
        
        return jsonify({
            'proposals': proposals,
            'pagination': {
                'total': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total_count
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/proposals/<proposal_id>', methods=['GET'])
def get_proposal_details(proposal_id):
    """Get detailed proposal information"""
    try:
        # Get proposal
        proposal_query = "SELECT * FROM proposals WHERE id = ?"
        proposal_df = pd.read_sql_query(proposal_query, analytics.conn, params=[proposal_id])
        
        if proposal_df.empty:
            return jsonify({'error': 'Proposal not found'}), 404
        
        proposal = proposal_df.iloc[0].to_dict()
        
        # Get votes for this proposal
        votes_query = "SELECT * FROM votes WHERE proposal_id = ? ORDER BY timestamp DESC"
        votes_df = pd.read_sql_query(votes_query, analytics.conn, params=[proposal_id])
        votes = votes_df.to_dict('records') if not votes_df.empty else []
        
        # Calculate additional metrics
        total_votes = proposal['votes_for'] + proposal['votes_against'] + proposal['votes_abstain']
        
        return jsonify({
            'proposal': proposal,
            'votes': votes,
            'analytics': {
                'total_participation': total_votes,
                'support_percentage': (proposal['votes_for'] / max(total_votes, 1)) * 100,
                'opposition_percentage': (proposal['votes_against'] / max(total_votes, 1)) * 100,
                'abstain_percentage': (proposal['votes_abstain'] / max(total_votes, 1)) * 100,
                'unique_voters': len(votes)
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/guardians', methods=['GET'])
def get_guardian_metrics():
    """Get guardian performance metrics"""
    try:
        guardian_metrics = analytics.calculate_guardian_metrics()
        
        # Get recent guardian actions
        actions_query = """
            SELECT * FROM guardian_actions 
            ORDER BY timestamp DESC 
            LIMIT 20
        """
        actions_df = pd.read_sql_query(actions_query, analytics.conn)
        actions = actions_df.to_dict('records') if not actions_df.empty else []
        
        return jsonify({
            'metrics': asdict(guardian_metrics),
            'recent_actions': actions
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/analytics/participation', methods=['GET'])
def get_participation_analytics():
    """Get detailed participation analytics"""
    try:
        # Parse time range
        days = int(request.args.get('days', 30))
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get participation trend
        trend_query = """
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as proposals,
                AVG(votes_for + votes_against + votes_abstain) as avg_participation,
                AVG(CASE WHEN quorum_reached THEN 1.0 ELSE 0.0 END) as quorum_rate
            FROM proposals 
            WHERE created_at >= ?
            GROUP BY DATE(created_at)
            ORDER BY date
        """
        
        trend_df = pd.read_sql_query(trend_query, analytics.conn, params=[start_date])
        trend_data = trend_df.to_dict('records') if not trend_df.empty else []
        
        # Get voter distribution
        voter_dist_query = """
            SELECT 
                state,
                AVG(votes_for + votes_against + votes_abstain) as avg_participation
            FROM proposals 
            WHERE created_at >= ?
            GROUP BY state
        """
        
        dist_df = pd.read_sql_query(voter_dist_query, analytics.conn, params=[start_date])
        distribution = dist_df.to_dict('records') if not dist_df.empty else []
        
        return jsonify({
            'period_days': days,
            'participation_trend': trend_data,
            'state_distribution': distribution
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/analytics/charts/participation', methods=['GET'])
def get_participation_chart():
    """Generate participation chart data"""
    try:
        # This would return chart configuration for frontend
        # For now, return sample chart data
        chart_data = {
            'type': 'line',
            'data': {
                'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                'datasets': [{
                    'label': 'Average Participation',
                    'data': [450000, 520000, 480000, 610000, 580000, 630000],
                    'borderColor': 'rgb(75, 192, 192)',
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)'
                }]
            },
            'options': {
                'responsive': True,
                'scales': {
                    'y': {
                        'beginAtZero': True,
                        'title': {
                            'display': True,
                            'text': 'Total Votes'
                        }
                    }
                }
            }
        }
        
        return jsonify(chart_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/reports/generate', methods=['POST'])
def generate_report():
    """Generate a new governance report"""
    try:
        data = request.get_json() or {}
        output_dir = data.get('output_dir', './reports_api')
        
        # Generate report
        report_path = analytics.generate_comprehensive_report(output_dir)
        
        # Return report metadata
        return jsonify({
            'status': 'success',
            'report_path': report_path,
            'generated_at': datetime.utcnow().isoformat(),
            'download_url': f"/api/v1/reports/download/{os.path.basename(report_path)}"
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/reports/download/<filename>', methods=['GET'])
def download_report(filename):
    """Download a generated report"""
    try:
        file_path = f"./reports_api/{filename}"
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'Report not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/export/<table_name>', methods=['GET'])
def export_table_data(table_name):
    """Export table data in various formats"""
    try:
        # Validate table name
        allowed_tables = ['proposals', 'votes', 'guardian_actions', 'system_events']
        if table_name not in allowed_tables:
            return jsonify({'error': 'Invalid table name'}), 400
        
        # Get format
        format_type = request.args.get('format', 'json').lower()
        
        # Query data
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", analytics.conn)
        
        if format_type == 'csv':
            output_path = f"/tmp/{table_name}_export.csv"
            df.to_csv(output_path, index=False)
            return send_file(output_path, as_attachment=True, download_name=f"{table_name}.csv")
        
        elif format_type == 'excel':
            output_path = f"/tmp/{table_name}_export.xlsx"
            df.to_excel(output_path, index=False)
            return send_file(output_path, as_attachment=True, download_name=f"{table_name}.xlsx")
        
        else:  # JSON
            return jsonify({
                'table': table_name,
                'data': df.to_dict('records'),
                'record_count': len(df)
            })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/system/status', methods=['GET'])
def get_system_status():
    """Get system status and performance metrics"""
    try:
        system_metrics = analytics.calculate_system_metrics()
        
        # Get recent events
        events_query = """
            SELECT event_type, COUNT(*) as count
            FROM system_events 
            WHERE timestamp >= datetime('now', '-24 hours')
            GROUP BY event_type
        """
        events_df = pd.read_sql_query(events_query, analytics.conn)
        recent_events = events_df.to_dict('records') if not events_df.empty else []
        
        return jsonify({
            'system_metrics': asdict(system_metrics),
            'recent_events_24h': recent_events,
            'database_stats': {
                'proposals': analytics.cursor.execute("SELECT COUNT(*) FROM proposals").fetchone()[0],
                'votes': analytics.cursor.execute("SELECT COUNT(*) FROM votes").fetchone()[0],
                'guardian_actions': analytics.cursor.execute("SELECT COUNT(*) FROM guardian_actions").fetchone()[0]
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/search', methods=['GET'])
def search_governance_data():
    """Search across governance data"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'error': 'Search query required'}), 400
        
        # Search proposals by title
        proposal_results = pd.read_sql_query(
            "SELECT id, title, state, created_at FROM proposals WHERE title LIKE ? LIMIT 10",
            analytics.conn,
            params=[f"%{query}%"]
        ).to_dict('records')
        
        # Search by proposer address
        proposer_results = pd.read_sql_query(
            "SELECT id, title, proposer, created_at FROM proposals WHERE proposer LIKE ? LIMIT 5",
            analytics.conn,
            params=[f"%{query}%"]
        ).to_dict('records')
        
        return jsonify({
            'query': query,
            'results': {
                'proposals': proposal_results,
                'proposers': proposer_results
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Configuration
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 5000))
    debug = os.getenv('API_DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 Starting Hardcard Governance Analytics API")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Debug: {debug}")
    print(f"   Database: {os.getenv('ANALYTICS_DB_PATH', 'governance_analytics.db')}")
    
    app.run(host=host, port=port, debug=debug)