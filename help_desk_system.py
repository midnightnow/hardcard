#!/usr/bin/env python3
"""
HardCard Help Desk & Ticketing System
=====================================
Complete customer support platform with AI-powered ticket routing
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import uuid


class TicketPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketStatus(Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_CUSTOMER = "waiting_customer"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketCategory(Enum):
    TECHNICAL = "technical"
    BILLING = "billing"
    FEATURE_REQUEST = "feature_request"
    BUG_REPORT = "bug_report"
    PHONE_AGENT = "phone_agent"
    API_SUPPORT = "api_support"
    TRAINING = "training"
    GENERAL = "general"


class HelpDeskSystem:
    """Comprehensive help desk and ticketing system"""
    
    def __init__(self):
        self.base_dir = Path("/Users/studio/hardcard/help_desk")
        self.tickets_db = self.base_dir / "tickets.json"
        self.knowledge_base = self.base_dir / "knowledge_base.json"
        self.agents_db = self.base_dir / "agents.json"
        
        # Initialize directories and databases
        self.setup_system()
    
    def setup_system(self):
        """Initialize help desk system"""
        
        self.base_dir.mkdir(exist_ok=True)
        
        # Initialize tickets database
        if not self.tickets_db.exists():
            self.tickets_db.write_text(json.dumps({"tickets": {}}, indent=2))
        
        # Initialize knowledge base
        if not self.knowledge_base.exists():
            self.knowledge_base.write_text(json.dumps(self.create_knowledge_base(), indent=2))
        
        # Initialize agents database
        if not self.agents_db.exists():
            self.agents_db.write_text(json.dumps(self.create_agents_db(), indent=2))
    
    def create_knowledge_base(self) -> Dict[str, Any]:
        """Create comprehensive knowledge base"""
        
        return {
            "categories": {
                "getting_started": {
                    "title": "Getting Started",
                    "description": "Initial setup and onboarding",
                    "articles": [
                        {
                            "id": "setup_guide",
                            "title": "HardCard Setup Guide",
                            "content": """# HardCard Setup Guide

## Quick Start

1. **Account Creation**
   - Visit https://app.hardcard.com/signup
   - Choose your plan (Basic/Professional/Enterprise)
   - Complete clinic information

2. **Initial Configuration**
   - Import existing client data (CSV/Excel)
   - Configure clinic settings
   - Set up staff accounts

3. **Phone Agent Setup**
   - Record custom greeting message
   - Configure business hours
   - Test phone number routing

4. **Integration Setup**
   - Generate API tokens
   - Connect existing systems
   - Configure webhooks

## Need Help?

Contact support at support@hardcard.com or use the chat widget.""",
                            "tags": ["setup", "onboarding", "quick-start"],
                            "difficulty": "beginner",
                            "estimated_time": "30 minutes"
                        }
                    ]
                },
                "phone_agent": {
                    "title": "AI Phone Agent",
                    "description": "Phone agent configuration and troubleshooting",
                    "articles": [
                        {
                            "id": "phone_agent_setup",
                            "title": "Setting Up Your AI Phone Agent",
                            "content": """# AI Phone Agent Setup

## Configuration Steps

1. **Phone Number Setup**
   - Purchase phone number through HardCard
   - Or port existing number (takes 3-5 business days)
   - Verify number ownership

2. **Voice Personality**
   - Choose from pre-built personalities
   - Record custom greeting messages
   - Set speaking pace and tone

3. **Business Rules**
   - Configure appointment types and durations
   - Set availability windows
   - Define emergency handling procedures

4. **Testing**
   - Use test mode for safe testing
   - Make test calls to verify functionality
   - Review call recordings and transcripts

## Common Issues

### "Calls not connecting"
- Check phone number configuration
- Verify Twilio webhook settings
- Contact support for routing issues

### "Poor call quality"
- Check internet connection stability
- Verify microphone settings
- Report issues to support team

### "Appointments not booking"
- Verify calendar integration
- Check availability rules
- Review appointment type settings""",
                            "tags": ["phone-agent", "setup", "troubleshooting"],
                            "difficulty": "intermediate",
                            "estimated_time": "45 minutes"
                        }
                    ]
                },
                "api": {
                    "title": "API Integration",
                    "description": "Developer resources and API support",
                    "articles": [
                        {
                            "id": "api_authentication",
                            "title": "API Authentication Guide",
                            "content": """# API Authentication

## Bearer Token Authentication

All HardCard API requests require Bearer token authentication.

### Getting Your API Token

1. Log in to HardCard dashboard
2. Navigate to **Settings** → **API Access**
3. Click **Generate New Token**
4. Copy and securely store your token

### Using Your Token

```bash
curl -H "Authorization: Bearer YOUR_API_TOKEN" \\
     https://api.hardcard.com/health
```

### Token Security

- Store tokens securely (environment variables)
- Rotate tokens regularly
- Never commit tokens to version control
- Use different tokens for different environments

### Rate Limits

- Standard requests: 1000/hour
- Phone agent calls: 50/hour
- Bulk operations: 10/minute

### Troubleshooting

**401 Unauthorized**
- Token expired or invalid
- Generate new token

**429 Rate Limited**
- Wait for rate limit reset
- Implement exponential backoff""",
                            "tags": ["api", "authentication", "security"],
                            "difficulty": "intermediate",
                            "estimated_time": "15 minutes"
                        }
                    ]
                },
                "billing": {
                    "title": "Billing & Subscriptions",
                    "description": "Payment, billing, and subscription management",
                    "articles": [
                        {
                            "id": "billing_overview",
                            "title": "Understanding HardCard Billing",
                            "content": """# HardCard Billing Overview

## Subscription Plans

### Basic Plan - $99/month
- Up to 50 clients
- Basic phone agent (100 minutes/month)
- Email support
- Standard integrations

### Professional Plan - $199/month
- Up to 200 clients
- Advanced phone agent (500 minutes/month)
- Priority support
- Advanced analytics
- Custom integrations

### Enterprise Plan - $399/month
- Unlimited clients
- Unlimited phone agent usage
- 24/7 dedicated support
- Custom features
- White-label options

## Usage-Based Billing

### Phone Agent Minutes
- Billing per minute of AI phone usage
- Includes inbound and outbound calls
- Monthly allowances included in plans

### API Requests
- Generous free tier included
- Overage charges for high-volume usage
- Contact sales for enterprise pricing

## Billing Cycle

- Monthly billing on signup date
- Automatic payment via credit card
- Invoices available in dashboard
- Failed payments result in service suspension

## Need Help?

Contact billing@hardcard.com for billing questions.""",
                            "tags": ["billing", "pricing", "subscription"],
                            "difficulty": "beginner",
                            "estimated_time": "10 minutes"
                        }
                    ]
                }
            },
            "faqs": [
                {
                    "question": "How quickly can I get started with HardCard?",
                    "answer": "Most clinics are up and running within 30 minutes. Sign up, import your client data, and start using AI phone agents immediately.",
                    "category": "getting_started"
                },
                {
                    "question": "Can the AI phone agent handle emergency calls?",
                    "answer": "Yes! The AI agent can triage emergency calls and immediately route urgent cases to your emergency contact or on-call veterinarian.",
                    "category": "phone_agent"
                },
                {
                    "question": "Do you integrate with existing practice management software?",
                    "answer": "Yes, we integrate with most major practice management systems including IDEXX, VetBlue, and others via our API.",
                    "category": "integrations"
                },
                {
                    "question": "What happens if the phone agent can't help a caller?",
                    "answer": "The AI agent will gracefully escalate to your staff or take a detailed message. It's designed to never leave callers frustrated.",
                    "category": "phone_agent"
                },
                {
                    "question": "Is my clinic data secure?",
                    "answer": "Absolutely. We use bank-level encryption, HIPAA-compliant infrastructure, and regular security audits to protect your data.",
                    "category": "security"
                }
            ],
            "troubleshooting": {
                "common_issues": [
                    {
                        "issue": "Phone calls not connecting",
                        "solutions": [
                            "Check phone number configuration",
                            "Verify webhook URLs are correct",
                            "Test with different phone numbers",
                            "Contact support if issue persists"
                        ],
                        "category": "phone_agent"
                    },
                    {
                        "issue": "API returning 401 errors",
                        "solutions": [
                            "Verify API token is correct",
                            "Check token hasn't expired",
                            "Ensure Bearer prefix in Authorization header",
                            "Generate new token if needed"
                        ],
                        "category": "api"
                    },
                    {
                        "issue": "Clients not syncing",
                        "solutions": [
                            "Check internet connection",
                            "Verify integration credentials",
                            "Review sync logs in dashboard",
                            "Force manual sync if available"
                        ],
                        "category": "integrations"
                    }
                ]
            }
        }
    
    def create_agents_db(self) -> Dict[str, Any]:
        """Create support agents database"""
        
        return {
            "agents": {
                "agent_001": {
                    "id": "agent_001",
                    "name": "Sarah Chen",
                    "email": "sarah@hardcard.com",
                    "role": "Senior Support Engineer",
                    "specialties": ["phone_agent", "api_support", "technical"],
                    "availability": {
                        "timezone": "PST",
                        "hours": "9:00-17:00",
                        "days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
                    },
                    "current_load": 3,
                    "max_tickets": 8,
                    "response_time_avg": "15 minutes",
                    "satisfaction_rating": 4.9
                },
                "agent_002": {
                    "id": "agent_002", 
                    "name": "Dr. Marcus Webb",
                    "email": "marcus@hardcard.com",
                    "role": "Veterinary Success Manager",
                    "specialties": ["training", "best_practices", "feature_request"],
                    "availability": {
                        "timezone": "EST",
                        "hours": "8:00-16:00",
                        "days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
                    },
                    "current_load": 2,
                    "max_tickets": 6,
                    "response_time_avg": "20 minutes",
                    "satisfaction_rating": 4.8
                },
                "agent_003": {
                    "id": "agent_003",
                    "name": "Jessica Rodriguez",
                    "email": "jessica@hardcard.com",
                    "role": "Billing Specialist",
                    "specialties": ["billing", "subscriptions", "general"],
                    "availability": {
                        "timezone": "MST",
                        "hours": "10:00-18:00",
                        "days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
                    },
                    "current_load": 4,
                    "max_tickets": 10,
                    "response_time_avg": "10 minutes",
                    "satisfaction_rating": 4.7
                }
            },
            "escalation_rules": {
                "critical_tickets": {
                    "immediate_notification": True,
                    "notify_agents": ["agent_001"],
                    "max_response_time": "5 minutes"
                },
                "billing_issues": {
                    "assign_to": "agent_003",
                    "max_response_time": "30 minutes"
                },
                "technical_issues": {
                    "assign_to": "agent_001",
                    "max_response_time": "1 hour"
                }
            }
        }
    
    def create_ticket(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new support ticket with AI routing"""
        
        ticket_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()
        
        # AI-powered category and priority detection
        category = self.detect_category(ticket_data["subject"], ticket_data["description"])
        priority = self.detect_priority(ticket_data["description"])
        
        # Auto-assign to best agent
        assigned_agent = self.auto_assign_agent(category, priority)
        
        ticket = {
            "id": ticket_id,
            "subject": ticket_data["subject"],
            "description": ticket_data["description"],
            "customer": {
                "name": ticket_data["customer_name"],
                "email": ticket_data["customer_email"],
                "clinic_id": ticket_data.get("clinic_id"),
                "phone": ticket_data.get("customer_phone")
            },
            "category": category.value,
            "priority": priority.value,
            "status": TicketStatus.OPEN.value,
            "assigned_agent": assigned_agent,
            "created_at": timestamp,
            "updated_at": timestamp,
            "messages": [
                {
                    "id": str(uuid.uuid4())[:8],
                    "author": ticket_data["customer_name"],
                    "author_type": "customer",
                    "content": ticket_data["description"],
                    "timestamp": timestamp,
                    "attachments": ticket_data.get("attachments", [])
                }
            ],
            "tags": self.extract_tags(ticket_data["description"]),
            "sla": self.calculate_sla(priority, category),
            "estimated_resolution": self.estimate_resolution_time(category, priority)
        }
        
        # Save ticket
        tickets_data = json.loads(self.tickets_db.read_text())
        tickets_data["tickets"][ticket_id] = ticket
        self.tickets_db.write_text(json.dumps(tickets_data, indent=2))
        
        # Send notifications
        self.notify_assignment(ticket)
        
        return ticket
    
    def detect_category(self, subject: str, description: str) -> TicketCategory:
        """AI-powered category detection"""
        
        text = (subject + " " + description).lower()
        
        # Simple keyword-based detection (in production, use ML model)
        if any(word in text for word in ["phone", "call", "agent", "voice", "dial"]):
            return TicketCategory.PHONE_AGENT
        elif any(word in text for word in ["api", "integration", "webhook", "token"]):
            return TicketCategory.API_SUPPORT
        elif any(word in text for word in ["bill", "payment", "charge", "invoice", "subscription"]):
            return TicketCategory.BILLING
        elif any(word in text for word in ["bug", "error", "broken", "crash", "issue"]):
            return TicketCategory.BUG_REPORT
        elif any(word in text for word in ["feature", "enhancement", "request", "suggestion"]):
            return TicketCategory.FEATURE_REQUEST
        elif any(word in text for word in ["training", "help", "how to", "tutorial"]):
            return TicketCategory.TRAINING
        elif any(word in text for word in ["server", "down", "slow", "technical"]):
            return TicketCategory.TECHNICAL
        else:
            return TicketCategory.GENERAL
    
    def detect_priority(self, description: str) -> TicketPriority:
        """AI-powered priority detection"""
        
        text = description.lower()
        
        # Critical issues
        if any(word in text for word in ["emergency", "critical", "down", "outage", "urgent"]):
            return TicketPriority.CRITICAL
        
        # High priority
        elif any(word in text for word in ["important", "asap", "quickly", "broken"]):
            return TicketPriority.HIGH
        
        # Low priority
        elif any(word in text for word in ["suggestion", "enhancement", "minor", "when possible"]):
            return TicketPriority.LOW
        
        # Default to medium
        else:
            return TicketPriority.MEDIUM
    
    def auto_assign_agent(self, category: TicketCategory, priority: TicketPriority) -> str:
        """Auto-assign ticket to best available agent"""
        
        agents_data = json.loads(self.agents_db.read_text())
        agents = agents_data["agents"]
        
        # Find agents with matching specialties
        suitable_agents = []
        for agent_id, agent in agents.items():
            if category.value in agent["specialties"]:
                if agent["current_load"] < agent["max_tickets"]:
                    suitable_agents.append((agent_id, agent))
        
        if not suitable_agents:
            # Fallback to any available agent
            suitable_agents = [
                (agent_id, agent) for agent_id, agent in agents.items()
                if agent["current_load"] < agent["max_tickets"]
            ]
        
        if suitable_agents:
            # Sort by current load and satisfaction rating
            suitable_agents.sort(key=lambda x: (x[1]["current_load"], -x[1]["satisfaction_rating"]))
            return suitable_agents[0][0]
        
        # If all agents are at capacity, assign to agent with highest rating
        return max(agents.items(), key=lambda x: x[1]["satisfaction_rating"])[0]
    
    def extract_tags(self, description: str) -> List[str]:
        """Extract relevant tags from ticket description"""
        
        text = description.lower()
        tags = []
        
        # Technology tags
        if "iphone" in text or "ios" in text:
            tags.append("ios")
        if "android" in text:
            tags.append("android")
        if "api" in text:
            tags.append("api")
        if "webhook" in text:
            tags.append("webhook")
        
        # Urgency tags
        if any(word in text for word in ["urgent", "asap", "critical"]):
            tags.append("urgent")
        
        # Feature tags
        if "appointment" in text:
            tags.append("appointments")
        if "client" in text:
            tags.append("clients")
        if "patient" in text:
            tags.append("patients")
        
        return tags
    
    def calculate_sla(self, priority: TicketPriority, category: TicketCategory) -> Dict[str, str]:
        """Calculate SLA deadlines based on priority and category"""
        
        now = datetime.now()
        
        if priority == TicketPriority.CRITICAL:
            first_response = now + timedelta(minutes=15)
            resolution = now + timedelta(hours=4)
        elif priority == TicketPriority.HIGH:
            first_response = now + timedelta(hours=1)
            resolution = now + timedelta(hours=24)
        elif priority == TicketPriority.MEDIUM:
            first_response = now + timedelta(hours=4)
            resolution = now + timedelta(days=3)
        else:  # LOW
            first_response = now + timedelta(hours=24)
            resolution = now + timedelta(days=7)
        
        return {
            "first_response_by": first_response.isoformat(),
            "resolution_by": resolution.isoformat()
        }
    
    def estimate_resolution_time(self, category: TicketCategory, priority: TicketPriority) -> str:
        """Estimate resolution time based on historical data"""
        
        # Base estimates (in production, use ML model with historical data)
        base_times = {
            TicketCategory.BILLING: "30 minutes",
            TicketCategory.GENERAL: "2 hours",
            TicketCategory.FEATURE_REQUEST: "2-4 weeks",
            TicketCategory.BUG_REPORT: "1-3 days",
            TicketCategory.PHONE_AGENT: "4 hours",
            TicketCategory.API_SUPPORT: "2 hours",
            TicketCategory.TRAINING: "1 hour",
            TicketCategory.TECHNICAL: "6 hours"
        }
        
        base_time = base_times.get(category, "4 hours")
        
        # Adjust for priority
        if priority == TicketPriority.CRITICAL:
            return f"ASAP (typically {base_time})"
        elif priority == TicketPriority.LOW:
            return f"When possible (typically {base_time})"
        else:
            return base_time
    
    def notify_assignment(self, ticket: Dict[str, Any]):
        """Send notifications for ticket assignment"""
        
        # In production, send actual emails/Slack notifications
        print(f"📧 Ticket #{ticket['id']} assigned to {ticket['assigned_agent']}")
        print(f"📋 Subject: {ticket['subject']}")
        print(f"⏰ SLA: First response by {ticket['sla']['first_response_by']}")
    
    def generate_help_desk_dashboard(self) -> str:
        """Generate HTML dashboard for help desk system"""
        
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HardCard Help Desk Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui;
            background: #f8fafc;
            color: #1e293b;
        }
        
        .header {
            background: #1e293b;
            color: white;
            padding: 2rem;
            text-align: center;
        }
        
        .container {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 2rem;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-bottom: 3rem;
        }
        
        .card {
            background: white;
            border-radius: 1rem;
            padding: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .card h3 {
            margin-bottom: 1rem;
            color: #1e293b;
            font-size: 1.25rem;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.75rem 0;
            border-bottom: 1px solid #e2e8f0;
        }
        
        .metric:last-child {
            border-bottom: none;
        }
        
        .metric-value {
            font-weight: 600;
            font-size: 1.5rem;
        }
        
        .priority-high { color: #dc2626; }
        .priority-medium { color: #f59e0b; }
        .priority-low { color: #10b981; }
        .priority-critical { color: #7c2d12; background: #fef7f0; }
        
        .ticket-form {
            background: white;
            border-radius: 1rem;
            padding: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 2rem;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
        }
        
        input, select, textarea {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #d1d5db;
            border-radius: 0.5rem;
            font-size: 1rem;
        }
        
        textarea {
            min-height: 120px;
            resize: vertical;
        }
        
        .btn {
            background: #3b82f6;
            color: white;
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 0.5rem;
            cursor: pointer;
            font-size: 1rem;
            font-weight: 500;
        }
        
        .btn:hover {
            background: #2563eb;
        }
        
        .knowledge-base {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin-top: 2rem;
        }
        
        .kb-article {
            background: white;
            border-radius: 0.5rem;
            padding: 1.5rem;
            border: 1px solid #e2e8f0;
        }
        
        .kb-article h4 {
            margin-bottom: 0.5rem;
            color: #3b82f6;
        }
        
        .kb-tags {
            display: flex;
            gap: 0.5rem;
            margin-top: 1rem;
            flex-wrap: wrap;
        }
        
        .tag {
            background: #e0e7ff;
            color: #3730a3;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
        }
        
        .search-box {
            width: 100%;
            padding: 1rem;
            border: 2px solid #e2e8f0;
            border-radius: 0.5rem;
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }
        
        .faq-item {
            background: white;
            border-radius: 0.5rem;
            padding: 1.5rem;
            margin-bottom: 1rem;
            border: 1px solid #e2e8f0;
        }
        
        .faq-question {
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #1e293b;
        }
        
        .faq-answer {
            color: #64748b;
            line-height: 1.6;
        }
        
        .agent-status {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
        }
        
        .agent-card {
            background: white;
            border-radius: 0.5rem;
            padding: 1.5rem;
            border: 1px solid #e2e8f0;
        }
        
        .agent-name {
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        
        .agent-load {
            background: #f3f4f6;
            border-radius: 0.25rem;
            padding: 0.5rem;
            margin-top: 1rem;
        }
        
        .load-bar {
            background: #e5e7eb;
            height: 8px;
            border-radius: 4px;
            overflow: hidden;
        }
        
        .load-fill {
            background: #10b981;
            height: 100%;
            transition: width 0.3s ease;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎧 HardCard Help Desk</h1>
        <p>Customer Support Dashboard & Knowledge Base</p>
    </div>
    
    <div class="container">
        <!-- Dashboard Metrics -->
        <div class="dashboard-grid">
            <div class="card">
                <h3>📊 Ticket Overview</h3>
                <div class="metric">
                    <span>Open Tickets</span>
                    <span class="metric-value">23</span>
                </div>
                <div class="metric">
                    <span>In Progress</span>
                    <span class="metric-value">8</span>
                </div>
                <div class="metric">
                    <span>Waiting Customer</span>
                    <span class="metric-value">5</span>
                </div>
                <div class="metric">
                    <span>Resolved Today</span>
                    <span class="metric-value">12</span>
                </div>
            </div>
            
            <div class="card">
                <h3>⚡ Priority Breakdown</h3>
                <div class="metric">
                    <span>Critical</span>
                    <span class="metric-value priority-critical">2</span>
                </div>
                <div class="metric">
                    <span>High</span>
                    <span class="metric-value priority-high">7</span>
                </div>
                <div class="metric">
                    <span>Medium</span>
                    <span class="metric-value priority-medium">12</span>
                </div>
                <div class="metric">
                    <span>Low</span>
                    <span class="metric-value priority-low">8</span>
                </div>
            </div>
            
            <div class="card">
                <h3>📈 Performance Metrics</h3>
                <div class="metric">
                    <span>Avg Response Time</span>
                    <span class="metric-value">18 min</span>
                </div>
                <div class="metric">
                    <span>Customer Satisfaction</span>
                    <span class="metric-value">4.8/5</span>
                </div>
                <div class="metric">
                    <span>Resolution Rate</span>
                    <span class="metric-value">94%</span>
                </div>
                <div class="metric">
                    <span>SLA Compliance</span>
                    <span class="metric-value">97%</span>
                </div>
            </div>
        </div>
        
        <!-- New Ticket Form -->
        <div class="ticket-form">
            <h3>🎫 Create New Ticket</h3>
            <form id="ticket-form">
                <div class="form-group">
                    <label for="customer-name">Customer Name</label>
                    <input type="text" id="customer-name" required>
                </div>
                
                <div class="form-group">
                    <label for="customer-email">Email Address</label>
                    <input type="email" id="customer-email" required>
                </div>
                
                <div class="form-group">
                    <label for="subject">Subject</label>
                    <input type="text" id="subject" required>
                </div>
                
                <div class="form-group">
                    <label for="category">Category</label>
                    <select id="category">
                        <option value="general">General</option>
                        <option value="phone_agent">Phone Agent</option>
                        <option value="api_support">API Support</option>
                        <option value="billing">Billing</option>
                        <option value="technical">Technical</option>
                        <option value="bug_report">Bug Report</option>
                        <option value="feature_request">Feature Request</option>
                        <option value="training">Training</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="priority">Priority</label>
                    <select id="priority">
                        <option value="low">Low</option>
                        <option value="medium" selected>Medium</option>
                        <option value="high">High</option>
                        <option value="critical">Critical</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="description">Description</label>
                    <textarea id="description" placeholder="Please describe your issue in detail..." required></textarea>
                </div>
                
                <button type="submit" class="btn">Create Ticket</button>
            </form>
        </div>
        
        <!-- Knowledge Base -->
        <div class="card">
            <h3>📚 Knowledge Base</h3>
            <input type="text" class="search-box" placeholder="Search knowledge base..." id="kb-search">
            
            <div class="knowledge-base">
                <div class="kb-article">
                    <h4>Getting Started Guide</h4>
                    <p>Complete setup guide for new HardCard users.</p>
                    <div class="kb-tags">
                        <span class="tag">setup</span>
                        <span class="tag">beginner</span>
                    </div>
                </div>
                
                <div class="kb-article">
                    <h4>Phone Agent Configuration</h4>
                    <p>How to set up and customize your AI phone agent.</p>
                    <div class="kb-tags">
                        <span class="tag">phone-agent</span>
                        <span class="tag">configuration</span>
                    </div>
                </div>
                
                <div class="kb-article">
                    <h4>API Authentication</h4>
                    <p>Guide to authenticating with the HardCard API.</p>
                    <div class="kb-tags">
                        <span class="tag">api</span>
                        <span class="tag">development</span>
                    </div>
                </div>
                
                <div class="kb-article">
                    <h4>Billing Overview</h4>
                    <p>Understanding HardCard subscription plans and billing.</p>
                    <div class="kb-tags">
                        <span class="tag">billing</span>
                        <span class="tag">pricing</span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- FAQ Section -->
        <div class="card">
            <h3>❓ Frequently Asked Questions</h3>
            
            <div class="faq-item">
                <div class="faq-question">How quickly can I get started with HardCard?</div>
                <div class="faq-answer">Most clinics are up and running within 30 minutes. Sign up, import your client data, and start using AI phone agents immediately.</div>
            </div>
            
            <div class="faq-item">
                <div class="faq-question">Can the AI phone agent handle emergency calls?</div>
                <div class="faq-answer">Yes! The AI agent can triage emergency calls and immediately route urgent cases to your emergency contact or on-call veterinarian.</div>
            </div>
            
            <div class="faq-item">
                <div class="faq-question">Do you integrate with existing practice management software?</div>
                <div class="faq-answer">Yes, we integrate with most major practice management systems including IDEXX, VetBlue, and others via our API.</div>
            </div>
        </div>
        
        <!-- Agent Status -->
        <div class="card">
            <h3>👥 Support Agent Status</h3>
            
            <div class="agent-status">
                <div class="agent-card">
                    <div class="agent-name">Sarah Chen</div>
                    <div>Senior Support Engineer</div>
                    <div class="agent-load">
                        <div>Load: 3/8 tickets</div>
                        <div class="load-bar">
                            <div class="load-fill" style="width: 37.5%"></div>
                        </div>
                        <div>Avg Response: 15 min</div>
                        <div>Rating: ⭐ 4.9/5</div>
                    </div>
                </div>
                
                <div class="agent-card">
                    <div class="agent-name">Dr. Marcus Webb</div>
                    <div>Veterinary Success Manager</div>
                    <div class="agent-load">
                        <div>Load: 2/6 tickets</div>
                        <div class="load-bar">
                            <div class="load-fill" style="width: 33.3%"></div>
                        </div>
                        <div>Avg Response: 20 min</div>
                        <div>Rating: ⭐ 4.8/5</div>
                    </div>
                </div>
                
                <div class="agent-card">
                    <div class="agent-name">Jessica Rodriguez</div>
                    <div>Billing Specialist</div>
                    <div class="agent-load">
                        <div>Load: 4/10 tickets</div>
                        <div class="load-bar">
                            <div class="load-fill" style="width: 40%"></div>
                        </div>
                        <div>Avg Response: 10 min</div>
                        <div>Rating: ⭐ 4.7/5</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Ticket form submission
        document.getElementById('ticket-form').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = {
                customer_name: document.getElementById('customer-name').value,
                customer_email: document.getElementById('customer-email').value,
                subject: document.getElementById('subject').value,
                category: document.getElementById('category').value,
                priority: document.getElementById('priority').value,
                description: document.getElementById('description').value
            };
            
            // In production, send to API
            console.log('Creating ticket:', formData);
            alert('Ticket created successfully! You will receive a confirmation email shortly.');
            
            // Reset form
            this.reset();
        });
        
        // Knowledge base search
        document.getElementById('kb-search').addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const articles = document.querySelectorAll('.kb-article');
            
            articles.forEach(article => {
                const title = article.querySelector('h4').textContent.toLowerCase();
                const content = article.querySelector('p').textContent.toLowerCase();
                
                if (title.includes(searchTerm) || content.includes(searchTerm)) {
                    article.style.display = 'block';
                } else {
                    article.style.display = 'none';
                }
            });
        });
        
        // Auto-refresh dashboard metrics (every 30 seconds)
        setInterval(function() {
            // In production, fetch real metrics from API
            console.log('Refreshing dashboard metrics...');
        }, 30000);
    </script>
</body>
</html>"""
    
    def generate_customer_portal(self) -> str:
        """Generate customer self-service portal"""
        
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HardCard Customer Support</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 2rem;
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        }
        
        .header {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            color: white;
            padding: 3rem 2rem;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        
        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        .content {
            padding: 3rem 2rem;
        }
        
        .help-options {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
            margin-bottom: 3rem;
        }
        
        .help-option {
            background: #f8fafc;
            padding: 2rem;
            border-radius: 1rem;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            border: 2px solid transparent;
        }
        
        .help-option:hover {
            background: #e2e8f0;
            border-color: #3b82f6;
            transform: translateY(-2px);
        }
        
        .help-option .icon {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        
        .help-option h3 {
            margin-bottom: 0.5rem;
            color: #1e293b;
        }
        
        .help-option p {
            color: #64748b;
            font-size: 0.9rem;
        }
        
        .quick-actions {
            background: #f1f5f9;
            padding: 2rem;
            border-radius: 1rem;
            margin-bottom: 3rem;
        }
        
        .quick-actions h3 {
            margin-bottom: 1.5rem;
            text-align: center;
            color: #1e293b;
        }
        
        .action-buttons {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
        }
        
        .action-btn {
            background: #3b82f6;
            color: white;
            padding: 1rem;
            border: none;
            border-radius: 0.75rem;
            cursor: pointer;
            font-size: 1rem;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .action-btn:hover {
            background: #2563eb;
            transform: translateY(-1px);
        }
        
        .action-btn.secondary {
            background: #64748b;
        }
        
        .action-btn.secondary:hover {
            background: #475569;
        }
        
        .support-form {
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 1rem;
            padding: 2rem;
            margin-bottom: 2rem;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
            color: #374151;
        }
        
        input, select, textarea {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #d1d5db;
            border-radius: 0.5rem;
            font-size: 1rem;
        }
        
        textarea {
            min-height: 120px;
            resize: vertical;
        }
        
        .submit-btn {
            background: #10b981;
            color: white;
            padding: 1rem 2rem;
            border: none;
            border-radius: 0.75rem;
            cursor: pointer;
            font-size: 1.1rem;
            font-weight: 600;
            width: 100%;
        }
        
        .submit-btn:hover {
            background: #059669;
        }
        
        .contact-info {
            background: #fef7cd;
            border: 1px solid #f59e0b;
            border-radius: 1rem;
            padding: 2rem;
            text-align: center;
        }
        
        .contact-info h4 {
            color: #92400e;
            margin-bottom: 1rem;
        }
        
        .contact-methods {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-top: 1.5rem;
        }
        
        .contact-method {
            background: white;
            padding: 1rem;
            border-radius: 0.5rem;
            text-align: center;
        }
        
        .contact-method .icon {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        
        .hidden {
            display: none;
        }
        
        .chat-widget {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            background: #3b82f6;
            color: white;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 1.5rem;
            box-shadow: 0 10px 20px rgba(59, 130, 246, 0.3);
            transition: all 0.3s ease;
        }
        
        .chat-widget:hover {
            transform: scale(1.1);
            box-shadow: 0 15px 30px rgba(59, 130, 246, 0.4);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🩺 HardCard Support</h1>
            <p>We're here to help you succeed</p>
        </div>
        
        <div class="content">
            <!-- Help Options -->
            <div class="help-options">
                <div class="help-option" onclick="showSection('knowledge-base')">
                    <div class="icon">📚</div>
                    <h3>Knowledge Base</h3>
                    <p>Search our comprehensive guides and tutorials</p>
                </div>
                
                <div class="help-option" onclick="showSection('contact-form')">
                    <div class="icon">📧</div>
                    <h3>Contact Support</h3>
                    <p>Get personalized help from our expert team</p>
                </div>
                
                <div class="help-option" onclick="showSection('phone-support')">
                    <div class="icon">📞</div>
                    <h3>Phone Support</h3>
                    <p>Speak directly with a support specialist</p>
                </div>
                
                <div class="help-option" onclick="window.open('https://status.hardcard.com', '_blank')">
                    <div class="icon">⚡</div>
                    <h3>System Status</h3>
                    <p>Check current system status and uptime</p>
                </div>
            </div>
            
            <!-- Quick Actions -->
            <div class="quick-actions">
                <h3>🚀 Quick Actions</h3>
                <div class="action-buttons">
                    <button class="action-btn" onclick="quickAction('reset-password')">Reset Password</button>
                    <button class="action-btn" onclick="quickAction('phone-test')">Test Phone Agent</button>
                    <button class="action-btn secondary" onclick="quickAction('billing-info')">Billing Info</button>
                    <button class="action-btn secondary" onclick="quickAction('api-docs')">API Docs</button>
                </div>
            </div>
            
            <!-- Contact Form Section -->
            <div id="contact-form" class="hidden">
                <div class="support-form">
                    <h3>📧 Contact Our Support Team</h3>
                    <form id="support-form">
                        <div class="form-group">
                            <label for="name">Your Name</label>
                            <input type="text" id="name" required>
                        </div>
                        
                        <div class="form-group">
                            <label for="email">Email Address</label>
                            <input type="email" id="email" required>
                        </div>
                        
                        <div class="form-group">
                            <label for="clinic">Clinic Name</label>
                            <input type="text" id="clinic">
                        </div>
                        
                        <div class="form-group">
                            <label for="issue-type">Type of Issue</label>
                            <select id="issue-type" required>
                                <option value="">Select an issue type</option>
                                <option value="phone_agent">Phone Agent Issues</option>
                                <option value="billing">Billing Questions</option>
                                <option value="technical">Technical Problems</option>
                                <option value="training">Training Request</option>
                                <option value="feature">Feature Request</option>
                                <option value="api">API Support</option>
                                <option value="general">General Question</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label for="urgency">Urgency Level</label>
                            <select id="urgency" required>
                                <option value="low">Low - General question</option>
                                <option value="medium" selected>Medium - Standard issue</option>
                                <option value="high">High - Affecting operations</option>
                                <option value="critical">Critical - System down</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label for="message">Describe Your Issue</label>
                            <textarea id="message" placeholder="Please provide as much detail as possible to help us assist you quickly..." required></textarea>
                        </div>
                        
                        <button type="submit" class="submit-btn">Send Support Request</button>
                    </form>
                </div>
            </div>
            
            <!-- Phone Support Section -->
            <div id="phone-support" class="hidden">
                <div class="contact-info">
                    <h4>📞 Phone Support Available</h4>
                    <p>Our support team is available during business hours</p>
                    
                    <div class="contact-methods">
                        <div class="contact-method">
                            <div class="icon">📞</div>
                            <div><strong>Main Support</strong></div>
                            <div>+1-800-HARDCARD</div>
                            <div>Mon-Fri: 8AM-6PM EST</div>
                        </div>
                        
                        <div class="contact-method">
                            <div class="icon">🚨</div>
                            <div><strong>Emergency Line</strong></div>
                            <div>+1-800-VET-HELP</div>
                            <div>24/7 for critical issues</div>
                        </div>
                        
                        <div class="contact-method">
                            <div class="icon">💬</div>
                            <div><strong>Live Chat</strong></div>
                            <div>Click the chat icon</div>
                            <div>Mon-Fri: 9AM-5PM EST</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Knowledge Base Section -->
            <div id="knowledge-base" class="hidden">
                <div class="support-form">
                    <h3>📚 Search Knowledge Base</h3>
                    <div class="form-group">
                        <input type="text" id="kb-search" placeholder="Search for help articles...">
                    </div>
                    
                    <div id="kb-results">
                        <h4>Popular Articles:</h4>
                        <ul style="list-style: none; padding: 0;">
                            <li style="padding: 0.5rem 0; border-bottom: 1px solid #e2e8f0;">
                                <a href="#" style="color: #3b82f6;">Getting Started with HardCard</a>
                            </li>
                            <li style="padding: 0.5rem 0; border-bottom: 1px solid #e2e8f0;">
                                <a href="#" style="color: #3b82f6;">Setting Up Your AI Phone Agent</a>
                            </li>
                            <li style="padding: 0.5rem 0; border-bottom: 1px solid #e2e8f0;">
                                <a href="#" style="color: #3b82f6;">API Authentication Guide</a>
                            </li>
                            <li style="padding: 0.5rem 0; border-bottom: 1px solid #e2e8f0;">
                                <a href="#" style="color: #3b82f6;">Understanding Your Bill</a>
                            </li>
                            <li style="padding: 0.5rem 0;">
                                <a href="#" style="color: #3b82f6;">Troubleshooting Common Issues</a>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Chat Widget -->
    <div class="chat-widget" onclick="openChat()">
        💬
    </div>
    
    <script>
        function showSection(sectionId) {
            // Hide all sections
            document.querySelectorAll('.hidden').forEach(section => {
                section.classList.add('hidden');
            });
            
            // Show selected section
            document.getElementById(sectionId).classList.remove('hidden');
        }
        
        function quickAction(action) {
            switch(action) {
                case 'reset-password':
                    alert('Password reset link sent to your email!');
                    break;
                case 'phone-test':
                    alert('Test call initiated. You should receive a call within 30 seconds.');
                    break;
                case 'billing-info':
                    window.open('https://app.hardcard.com/billing', '_blank');
                    break;
                case 'api-docs':
                    window.open('https://docs.hardcard.com/api', '_blank');
                    break;
            }
        }
        
        function openChat() {
            alert('Live chat would open here! Currently redirecting to contact form.');
            showSection('contact-form');
        }
        
        // Support form submission
        document.getElementById('support-form').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = {
                name: document.getElementById('name').value,
                email: document.getElementById('email').value,
                clinic: document.getElementById('clinic').value,
                issue_type: document.getElementById('issue-type').value,
                urgency: document.getElementById('urgency').value,
                message: document.getElementById('message').value
            };
            
            // Show success message
            alert('Support request submitted successfully! You will receive a confirmation email and response within 24 hours.');
            
            // Reset form
            this.reset();
        });
        
        // Knowledge base search
        document.getElementById('kb-search').addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            // In production, this would search the actual knowledge base
            console.log('Searching for:', searchTerm);
        });
    </script>
</body>
</html>"""


def main():
    """Initialize complete help desk system"""
    
    help_desk = HelpDeskSystem()
    
    # Create dashboard
    dashboard_html = help_desk.generate_help_desk_dashboard()
    (help_desk.base_dir / "dashboard.html").write_text(dashboard_html)
    
    # Create customer portal
    portal_html = help_desk.generate_customer_portal()
    (help_desk.base_dir / "customer_portal.html").write_text(portal_html)
    
    # Create example ticket
    example_ticket = help_desk.create_ticket({
        "customer_name": "Dr. Sarah Johnson",
        "customer_email": "sarah@sunshinevetclinic.com",
        "subject": "Phone agent not answering calls",
        "description": "Our AI phone agent stopped answering calls this morning. Clients are calling and getting voicemail instead of the agent. This is urgent as we're missing appointments.",
        "clinic_id": "clinic_123",
        "customer_phone": "+1234567890"
    })
    
    print("✅ Help Desk System Initialized")
    print(f"📁 System Directory: {help_desk.base_dir}")
    print(f"🎛️ Admin Dashboard: file://{help_desk.base_dir}/dashboard.html")
    print(f"👥 Customer Portal: file://{help_desk.base_dir}/customer_portal.html")
    print(f"🎫 Example Ticket Created: #{example_ticket['id']}")
    print(f"📧 Assigned to: {example_ticket['assigned_agent']}")
    print(f"⏰ SLA: Response by {example_ticket['sla']['first_response_by']}")
    print("🎧 Ready for customer support operations!")


if __name__ == "__main__":
    main()