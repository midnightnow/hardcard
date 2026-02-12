#!/usr/bin/env python3
"""
HardCard Notification System
Sends alerts via Slack and Email for critical events and daily summaries
"""

import json
import logging
import os
import smtplib
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class NotificationSystem:
    def __init__(self):
        self.base_path = Path("/Users/studio/hardcard")
        
        # Load configuration from environment or config file
        self.config = self.load_config()
        
        # Notification thresholds
        self.thresholds = {
            "code_completion_critical": 50,
            "code_completion_warning": 70,
            "test_coverage_critical": 50,
            "test_coverage_warning": 70,
            "security_score_critical": 80,
            "typescript_errors_critical": 10,
            "typescript_errors_warning": 5
        }
        
        # Track sent notifications to avoid spam
        self.sent_notifications = {}
        
    def load_config(self) -> Dict:
        """Load notification configuration"""
        config_file = self.base_path / "notification-config.json"
        
        # Default configuration
        default_config = {
            "slack": {
                "enabled": False,
                "webhook_url": os.getenv("SLACK_WEBHOOK_URL", ""),
                "channel": "#hardcard-alerts",
                "daily_summary_hour": 9  # 9 AM
            },
            "email": {
                "enabled": False,
                "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
                "smtp_port": 587,
                "smtp_user": os.getenv("SMTP_USER", ""),
                "smtp_password": os.getenv("SMTP_PASSWORD", ""),
                "from_email": os.getenv("FROM_EMAIL", "hardcard@example.com"),
                "to_emails": os.getenv("TO_EMAILS", "").split(","),
                "daily_summary_hour": 9
            },
            "alerts": {
                "critical_only": False,
                "include_improvements": True,
                "include_metrics": True
            }
        }
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                loaded_config = json.load(f)
                # Merge with defaults
                for key in default_config:
                    if key in loaded_config:
                        default_config[key].update(loaded_config[key])
        
        return default_config
    
    def send_slack_message(self, message: str, color: str = "good") -> bool:
        """Send message to Slack"""
        if not self.config["slack"]["enabled"] or not self.config["slack"]["webhook_url"]:
            return False
            
        try:
            # Prepare the Slack message
            slack_data = {
                "channel": self.config["slack"]["channel"],
                "username": "HardCard Bot",
                "icon_emoji": ":robot_face:",
                "attachments": [
                    {
                        "color": color,  # good, warning, danger
                        "text": message,
                        "footer": "HardCard Continuous Improvement System",
                        "ts": int(datetime.now().timestamp())
                    }
                ]
            }
            
            # Send to Slack
            req = urllib.request.Request(
                self.config["slack"]["webhook_url"],
                data=json.dumps(slack_data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            response = urllib.request.urlopen(req)
            return response.status == 200
            
        except Exception as e:
            logger.error(f"Failed to send Slack message: {e}")
            return False
    
    def send_email(self, subject: str, body: str, is_html: bool = False) -> bool:
        """Send email notification"""
        if not self.config["email"]["enabled"] or not self.config["email"]["smtp_user"]:
            return False
            
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[HardCard] {subject}"
            msg['From'] = self.config["email"]["from_email"]
            msg['To'] = ", ".join(self.config["email"]["to_emails"])
            
            # Add body
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.config["email"]["smtp_server"], self.config["email"]["smtp_port"]) as server:
                server.starttls()
                server.login(self.config["email"]["smtp_user"], self.config["email"]["smtp_password"])
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def check_thresholds(self, system_status: Dict) -> List[Dict]:
        """Check if any metrics exceed thresholds"""
        alerts = []
        
        if "goals" in system_status and "code_quality" in system_status["goals"]:
            goals = system_status["goals"]["code_quality"]
            
            # Check code completion
            completion = goals.get("current_completion", 0)
            if completion < self.thresholds["code_completion_critical"]:
                alerts.append({
                    "level": "critical",
                    "metric": "Code Completion",
                    "value": f"{completion:.1f}%",
                    "threshold": f"{self.thresholds['code_completion_critical']}%",
                    "message": f"🚨 Code completion critically low: {completion:.1f}%"
                })
            elif completion < self.thresholds["code_completion_warning"]:
                alerts.append({
                    "level": "warning",
                    "metric": "Code Completion",
                    "value": f"{completion:.1f}%",
                    "threshold": f"{self.thresholds['code_completion_warning']}%",
                    "message": f"⚠️ Code completion below target: {completion:.1f}%"
                })
            
            # Check test coverage
            coverage = goals.get("current_test_coverage", 0)
            if coverage < self.thresholds["test_coverage_critical"]:
                alerts.append({
                    "level": "critical",
                    "metric": "Test Coverage",
                    "value": f"{coverage}%",
                    "threshold": f"{self.thresholds['test_coverage_critical']}%",
                    "message": f"🚨 Test coverage critically low: {coverage}%"
                })
            
            # Check security score
            security = goals.get("current_security_score", 0)
            if security < self.thresholds["security_score_critical"]:
                alerts.append({
                    "level": "critical",
                    "metric": "Security Score",
                    "value": f"{security}%",
                    "threshold": f"{self.thresholds['security_score_critical']}%",
                    "message": f"🚨 Security score below critical threshold: {security}%"
                })
        
        # Check TypeScript errors from agents
        if "agents" in system_status:
            for agent_name, agent_data in system_status["agents"].items():
                if agent_name == "code_quality_agent" and "results" in agent_data:
                    metrics = agent_data["results"].get("metrics", {})
                    ts_errors = metrics.get("typescript_errors", 0)
                    
                    if ts_errors > self.thresholds["typescript_errors_critical"]:
                        alerts.append({
                            "level": "critical",
                            "metric": "TypeScript Errors",
                            "value": str(ts_errors),
                            "threshold": str(self.thresholds["typescript_errors_critical"]),
                            "message": f"🚨 High TypeScript error count: {ts_errors} errors"
                        })
        
        return alerts
    
    def generate_daily_summary(self, system_status: Dict) -> str:
        """Generate daily summary report"""
        summary = ["# 📊 HardCard Daily Summary\n"]
        summary.append(f"**Date**: {datetime.now().strftime('%Y-%m-%d')}\n")
        
        # Overall health
        summary.append("## 🏥 System Health\n")
        if "agents" in system_status:
            active_agents = sum(1 for agent in system_status["agents"].values() 
                              if agent.get("status") in ["running", "idle"])
            total_agents = len(system_status["agents"])
            summary.append(f"- **Active Agents**: {active_agents}/{total_agents}")
            
            # Agent details
            summary.append("\n### Agent Activity\n")
            for agent_name, agent_data in system_status["agents"].items():
                status = agent_data.get("status", "unknown")
                last_run = agent_data.get("last_run", "Never")
                
                status_emoji = {
                    "running": "🟢",
                    "idle": "🟡",
                    "error": "🔴"
                }.get(status, "⚪")
                
                summary.append(f"- {status_emoji} **{agent_name.replace('_', ' ').title()}**: {status}")
                
                if "results" in agent_data and "improvements" in agent_data["results"]:
                    for improvement in agent_data["results"]["improvements"][:2]:  # Top 2
                        summary.append(f"  - {improvement}")
        
        # Goals progress
        summary.append("\n## 🎯 Goal Progress\n")
        if "goals" in system_status and "code_quality" in system_status["goals"]:
            goals = system_status["goals"]["code_quality"]
            
            metrics = [
                ("Code Completion", goals.get("current_completion", 0), goals.get("target_completion", 95)),
                ("Test Coverage", goals.get("current_test_coverage", 0), goals.get("target_test_coverage", 90)),
                ("Security Score", goals.get("current_security_score", 0), goals.get("target_security_score", 95))
            ]
            
            for metric_name, current, target in metrics:
                progress = (current / target) * 100 if target > 0 else 0
                progress_bar = self.create_progress_bar(progress)
                summary.append(f"- **{metric_name}**: {current}% / {target}% {progress_bar}")
        
        # Strategic objectives
        if "goals" in system_status and "strategic_objectives" in system_status["goals"]:
            summary.append("\n## 🎯 Strategic Objectives\n")
            for obj_name, obj_data in system_status["goals"]["strategic_objectives"].items():
                current = obj_data.get("current", 0)
                target = obj_data.get("target", 100)
                deadline = obj_data.get("deadline", "TBD")
                
                summary.append(f"- **{obj_name.replace('_', ' ').title()}**: {current}% / {target}% (Due: {deadline})")
        
        # Recommendations
        summary.append("\n## 💡 Today's Recommendations\n")
        alerts = self.check_thresholds(system_status)
        if alerts:
            for alert in alerts[:3]:  # Top 3 alerts
                summary.append(f"- {alert['message']}")
        else:
            summary.append("- ✅ All systems operating within normal parameters")
        
        return "\n".join(summary)
    
    def create_progress_bar(self, percentage: float, width: int = 20) -> str:
        """Create text progress bar"""
        filled = int(width * percentage / 100)
        empty = width - filled
        return f"[{'█' * filled}{'░' * empty}]"
    
    def should_send_notification(self, notification_key: str, cooldown_hours: int = 1) -> bool:
        """Check if notification should be sent (cooldown period)"""
        now = datetime.now()
        
        if notification_key in self.sent_notifications:
            last_sent = self.sent_notifications[notification_key]
            if now - last_sent < timedelta(hours=cooldown_hours):
                return False
        
        self.sent_notifications[notification_key] = now
        return True
    
    def process_alerts(self, system_status: Dict):
        """Process and send alerts based on system status"""
        alerts = self.check_thresholds(system_status)
        
        for alert in alerts:
            notification_key = f"{alert['metric']}_{alert['level']}"
            
            # Only send critical alerts or if not in cooldown
            if alert["level"] == "critical" or self.should_send_notification(notification_key):
                # Determine color for Slack
                color = {
                    "critical": "danger",
                    "warning": "warning",
                    "info": "good"
                }.get(alert["level"], "good")
                
                # Send notifications
                self.send_slack_message(alert["message"], color)
                
                if alert["level"] == "critical":
                    self.send_email(
                        f"Critical Alert: {alert['metric']}",
                        alert["message"]
                    )
    
    def send_daily_summary(self, system_status: Dict):
        """Send daily summary report"""
        summary = self.generate_daily_summary(system_status)
        
        # Send via Slack
        self.send_slack_message(summary, "good")
        
        # Send via Email (HTML formatted)
        html_summary = summary.replace("\n", "<br>").replace("# ", "<h2>").replace("## ", "<h3>")
        self.send_email("Daily Summary Report", html_summary, is_html=True)


def setup_notification_config():
    """Create default notification configuration file"""
    config = {
        "slack": {
            "enabled": True,
            "webhook_url": "",  # User needs to add their webhook URL
            "channel": "#hardcard-alerts",
            "daily_summary_hour": 9
        },
        "email": {
            "enabled": False,
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_user": "",  # User needs to add email
            "smtp_password": "",  # User needs to add app password
            "from_email": "hardcard@example.com",
            "to_emails": ["your-email@example.com"],
            "daily_summary_hour": 9
        },
        "alerts": {
            "critical_only": False,
            "include_improvements": True,
            "include_metrics": True
        }
    }
    
    config_file = Path("/Users/studio/hardcard/notification-config.json")
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Created notification config at: {config_file}")
    print("⚠️  Please edit this file to add your Slack webhook URL and/or email credentials")


if __name__ == "__main__":
    # Create config file if it doesn't exist
    if not Path("/Users/studio/hardcard/notification-config.json").exists():
        setup_notification_config()
    else:
        # Test the notification system
        notifier = NotificationSystem()
        
        # Load current status
        status_file = Path("/Users/studio/hardcard/system-status.json")
        if status_file.exists():
            with open(status_file, 'r') as f:
                system_status = json.load(f)
            
            # Send test notifications
            print("📧 Sending test notifications...")
            notifier.process_alerts(system_status)
            
            # Generate and print daily summary
            summary = notifier.generate_daily_summary(system_status)
            print("\n📊 Daily Summary Preview:")
            print(summary)