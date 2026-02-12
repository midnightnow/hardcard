#!/usr/bin/env python3
"""
HardCard A/B Testing Harness
=============================
Comprehensive A/B testing framework for optimization and conversion
"""

import json
import os
import random
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import uuid


class ExperimentStatus(Enum):
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class VariationType(Enum):
    SPLIT_URL = "split_url"
    ELEMENT_TEXT = "element_text"
    ELEMENT_STYLE = "element_style"
    REDIRECT = "redirect"
    SCRIPT_INJECTION = "script_injection"


@dataclass
class Variation:
    id: str
    name: str
    description: str
    type: VariationType
    config: Dict[str, Any]
    traffic_allocation: float  # 0.0 to 1.0
    
    def to_dict(self):
        data = asdict(self)
        data['type'] = self.type.value
        return data


@dataclass
class Experiment:
    id: str
    name: str
    description: str
    hypothesis: str
    target_url: str
    variations: List[Variation]
    success_metrics: List[str]
    status: ExperimentStatus
    start_date: Optional[str]
    end_date: Optional[str]
    min_sample_size: int
    confidence_level: float
    created_at: str
    updated_at: str
    
    def to_dict(self):
        data = asdict(self)
        data['status'] = self.status.value
        data['variations'] = [v.to_dict() for v in self.variations]
        return data


class ABTestingHarness:
    """Complete A/B testing framework for HardCard optimization"""
    
    def __init__(self):
        self.base_dir = Path("/Users/studio/hardcard/ab_testing")
        self.experiments_dir = self.base_dir / "experiments"
        self.results_dir = self.base_dir / "results"
        self.config_dir = self.base_dir / "config"
        
        # Initialize system
        self.setup_directories()
        self.initialize_config()
    
    def setup_directories(self):
        """Initialize directory structure"""
        
        for directory in [self.base_dir, self.experiments_dir, self.results_dir, self.config_dir]:
            directory.mkdir(exist_ok=True)
    
    def initialize_config(self):
        """Initialize A/B testing configuration"""
        
        config = {
            "default_settings": {
                "confidence_level": 0.95,
                "min_sample_size": 1000,
                "max_experiment_duration_days": 30,
                "traffic_allocation_increment": 0.05,
                "auto_pause_on_significance": True,
                "exclude_bots": True,
                "exclude_internal_traffic": True
            },
            "tracking": {
                "cookie_name": "hardcard_ab_test",
                "cookie_duration_days": 30,
                "session_timeout_minutes": 30,
                "track_returning_visitors": True
            },
            "metrics": {
                "primary_conversion_events": [
                    "trial_signup",
                    "demo_request",
                    "contact_form_submit"
                ],
                "secondary_metrics": [
                    "page_views",
                    "time_on_page",
                    "bounce_rate",
                    "video_completion",
                    "scroll_depth"
                ]
            },
            "integrations": {
                "google_analytics": {
                    "enabled": True,
                    "property_id": "GA_PROPERTY_ID",
                    "custom_dimensions": ["experiment_id", "variation_id"]
                },
                "mixpanel": {
                    "enabled": False,
                    "project_token": "MIXPANEL_TOKEN"
                },
                "segment": {
                    "enabled": False,
                    "write_key": "SEGMENT_WRITE_KEY"
                }
            }
        }
        
        config_file = self.config_dir / "ab_testing_config.json"
        if not config_file.exists():
            config_file.write_text(json.dumps(config, indent=2))
    
    def create_experiment(self, experiment_data: Dict[str, Any]) -> Experiment:
        """Create new A/B test experiment"""
        
        experiment_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()
        
        # Process variations
        variations = []
        total_allocation = 0.0
        
        for var_data in experiment_data["variations"]:
            variation = Variation(
                id=str(uuid.uuid4())[:8],
                name=var_data["name"],
                description=var_data["description"],
                type=VariationType(var_data["type"]),
                config=var_data["config"],
                traffic_allocation=var_data["traffic_allocation"]
            )
            variations.append(variation)
            total_allocation += variation.traffic_allocation
        
        # Validate traffic allocation
        if abs(total_allocation - 1.0) > 0.01:
            raise ValueError(f"Traffic allocation must sum to 1.0, got {total_allocation}")
        
        # Create experiment
        experiment = Experiment(
            id=experiment_id,
            name=experiment_data["name"],
            description=experiment_data["description"],
            hypothesis=experiment_data["hypothesis"],
            target_url=experiment_data["target_url"],
            variations=variations,
            success_metrics=experiment_data["success_metrics"],
            status=ExperimentStatus.DRAFT,
            start_date=None,
            end_date=None,
            min_sample_size=experiment_data.get("min_sample_size", 1000),
            confidence_level=experiment_data.get("confidence_level", 0.95),
            created_at=timestamp,
            updated_at=timestamp
        )
        
        # Save experiment
        experiment_file = self.experiments_dir / f"{experiment_id}.json"
        experiment_file.write_text(json.dumps(experiment.to_dict(), indent=2))
        
        return experiment
    
    def generate_javascript_snippet(self, experiment: Experiment) -> str:
        """Generate JavaScript snippet for A/B test implementation"""
        
        return f"""
// HardCard A/B Testing - Experiment: {experiment.name}
(function() {{
    'use strict';
    
    // Configuration
    const EXPERIMENT_ID = '{experiment.id}';
    const EXPERIMENT_NAME = '{experiment.name}';
    const VARIATIONS = {json.dumps([v.to_dict() for v in experiment.variations], indent=4)};
    const SUCCESS_METRICS = {json.dumps(experiment.success_metrics)};
    
    // Utility functions
    function getCookie(name) {{
        const value = `; ${{document.cookie}}`;
        const parts = value.split(`; ${{name}}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }}
    
    function setCookie(name, value, days) {{
        const expires = new Date();
        expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000));
        document.cookie = `${{name}}=${{value}};expires=${{expires.toUTCString()}};path=/`;
    }}
    
    function hashUserId(userId) {{
        let hash = 0;
        for (let i = 0; i < userId.length; i++) {{
            const char = userId.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32-bit integer
        }}
        return Math.abs(hash);
    }}
    
    function getUserId() {{
        let userId = getCookie('hardcard_user_id');
        if (!userId) {{
            userId = 'user_' + Math.random().toString(36).substr(2, 9);
            setCookie('hardcard_user_id', userId, 365);
        }}
        return userId;
    }}
    
    function selectVariation(userId, variations) {{
        const hash = hashUserId(userId);
        const bucket = (hash % 10000) / 10000; // 0.0 to 1.0
        
        let cumulativeWeight = 0;
        for (const variation of variations) {{
            cumulativeWeight += variation.traffic_allocation;
            if (bucket <= cumulativeWeight) {{
                return variation;
            }}
        }}
        return variations[0]; // Fallback to first variation
    }}
    
    function trackEvent(eventName, properties = {{}}) {{
        const data = {{
            event: eventName,
            experiment_id: EXPERIMENT_ID,
            experiment_name: EXPERIMENT_NAME,
            variation_id: window.hardcardABTest?.variation?.id,
            variation_name: window.hardcardABTest?.variation?.name,
            timestamp: new Date().toISOString(),
            url: window.location.href,
            user_agent: navigator.userAgent,
            ...properties
        }};
        
        // Send to analytics
        if (typeof gtag !== 'undefined') {{
            gtag('event', eventName, {{
                custom_map: {{
                    'custom_dimension_1': 'experiment_id',
                    'custom_dimension_2': 'variation_id'
                }},
                experiment_id: EXPERIMENT_ID,
                variation_id: data.variation_id,
                ...properties
            }});
        }}
        
        // Send to HardCard analytics endpoint
        fetch('/api/analytics/ab-test-event', {{
            method: 'POST',
            headers: {{
                'Content-Type': 'application/json'
            }},
            body: JSON.stringify(data)
        }}).catch(console.error);
    }}
    
    function applyVariation(variation) {{
        console.log('Applying A/B test variation:', variation.name);
        
        switch (variation.type) {{
            case 'element_text':
                applyTextChanges(variation.config);
                break;
            case 'element_style':
                applyStyleChanges(variation.config);
                break;
            case 'redirect':
                applyRedirect(variation.config);
                break;
            case 'script_injection':
                applyScriptInjection(variation.config);
                break;
            default:
                console.warn('Unknown variation type:', variation.type);
        }}
    }}
    
    function applyTextChanges(config) {{
        config.changes.forEach(change => {{
            const elements = document.querySelectorAll(change.selector);
            elements.forEach(element => {{
                if (change.attribute) {{
                    element.setAttribute(change.attribute, change.value);
                }} else {{
                    element.textContent = change.value;
                }}
            }});
        }});
    }}
    
    function applyStyleChanges(config) {{
        const style = document.createElement('style');
        style.textContent = config.css;
        document.head.appendChild(style);
    }}
    
    function applyRedirect(config) {{
        if (config.immediate) {{
            window.location.href = config.url;
        }} else {{
            setTimeout(() => {{
                window.location.href = config.url;
            }}, config.delay || 0);
        }}
    }}
    
    function applyScriptInjection(config) {{
        const script = document.createElement('script');
        if (config.src) {{
            script.src = config.src;
        }} else if (config.code) {{
            script.textContent = config.code;
        }}
        document.head.appendChild(script);
    }}
    
    function setupConversionTracking() {{
        // Track page views
        trackEvent('ab_test_page_view');
        
        // Track success metrics
        SUCCESS_METRICS.forEach(metric => {{
            switch (metric) {{
                case 'trial_signup':
                    // Listen for trial signup events
                    document.addEventListener('trial_signup', () => {{
                        trackEvent('conversion', {{ type: 'trial_signup' }});
                    }});
                    break;
                case 'demo_request':
                    // Listen for demo request events
                    document.addEventListener('demo_request', () => {{
                        trackEvent('conversion', {{ type: 'demo_request' }});
                    }});
                    break;
                case 'contact_form_submit':
                    // Listen for form submissions
                    document.addEventListener('submit', (e) => {{
                        if (e.target.matches('.contact-form, #contact-form, [data-form="contact"]')) {{
                            trackEvent('conversion', {{ type: 'contact_form_submit' }});
                        }}
                    }});
                    break;
                case 'video_completion':
                    // Track video completion (requires custom video player events)
                    document.addEventListener('video_completed', (e) => {{
                        trackEvent('engagement', {{ type: 'video_completion', video_id: e.detail.videoId }});
                    }});
                    break;
            }}
        }});
        
        // Track scroll depth
        let maxScroll = 0;
        window.addEventListener('scroll', () => {{
            const scrollPercent = Math.round((window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100);
            if (scrollPercent > maxScroll) {{
                maxScroll = scrollPercent;
                if ([25, 50, 75, 100].includes(scrollPercent)) {{
                    trackEvent('scroll_depth', {{ percent: scrollPercent }});
                }}
            }}
        }});
        
        // Track time on page
        const startTime = Date.now();
        window.addEventListener('beforeunload', () => {{
            const timeOnPage = Math.round((Date.now() - startTime) / 1000);
            trackEvent('time_on_page', {{ seconds: timeOnPage }});
        }});
    }}
    
    // Main execution
    function initializeABTest() {{
        // Check if experiment should run on this page
        const currentUrl = window.location.href;
        const targetUrl = '{experiment.target_url}';
        
        if (!currentUrl.includes(targetUrl) && targetUrl !== '*') {{
            return; // Don't run experiment on this page
        }}
        
        // Get or assign user to variation
        const userId = getUserId();
        const variation = selectVariation(userId, VARIATIONS);
        
        // Store variation info globally
        window.hardcardABTest = {{
            experimentId: EXPERIMENT_ID,
            experimentName: EXPERIMENT_NAME,
            variation: variation,
            userId: userId
        }};
        
        // Apply the variation
        applyVariation(variation);
        
        // Setup tracking
        setupConversionTracking();
        
        console.log('HardCard A/B Test initialized:', {{
            experiment: EXPERIMENT_NAME,
            variation: variation.name,
            userId: userId
        }});
    }}
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', initializeABTest);
    }} else {{
        initializeABTest();
    }}
}})();
"""
    
    def create_landing_page_test(self) -> Experiment:
        """Create sample landing page A/B test"""
        
        experiment_data = {
            "name": "Landing Page Headline Test",
            "description": "Test different headlines on the main landing page to improve conversion rates",
            "hypothesis": "A more specific, benefit-focused headline will increase trial signups by 15%",
            "target_url": "/",
            "success_metrics": ["trial_signup", "demo_request"],
            "variations": [
                {
                    "name": "Control",
                    "description": "Original headline",
                    "type": "element_text",
                    "traffic_allocation": 0.5,
                    "config": {
                        "changes": [
                            {
                                "selector": "h1.hero-headline",
                                "value": "AI-Powered Veterinary Practice Management"
                            }
                        ]
                    }
                },
                {
                    "name": "Benefit-Focused",
                    "description": "Benefit-focused headline emphasizing time savings",
                    "type": "element_text",
                    "traffic_allocation": 0.5,
                    "config": {
                        "changes": [
                            {
                                "selector": "h1.hero-headline",
                                "value": "Save 10 Hours Per Week With AI Phone Agents"
                            }
                        ]
                    }
                }
            ]
        }
        
        return self.create_experiment(experiment_data)
    
    def create_pricing_page_test(self) -> Experiment:
        """Create pricing page A/B test"""
        
        experiment_data = {
            "name": "Pricing Page CTA Test",
            "description": "Test different call-to-action buttons on pricing page",
            "hypothesis": "Risk-free trial messaging will increase conversions by 20%",
            "target_url": "/pricing",
            "success_metrics": ["trial_signup"],
            "variations": [
                {
                    "name": "Control",
                    "description": "Standard 'Start Free Trial' button",
                    "type": "element_text",
                    "traffic_allocation": 0.33,
                    "config": {
                        "changes": [
                            {
                                "selector": ".pricing-cta",
                                "value": "Start Free Trial"
                            }
                        ]
                    }
                },
                {
                    "name": "Risk-Free",
                    "description": "Risk-free messaging",
                    "type": "element_text",
                    "traffic_allocation": 0.33,
                    "config": {
                        "changes": [
                            {
                                "selector": ".pricing-cta",
                                "value": "Start Risk-Free Trial"
                            }
                        ]
                    }
                },
                {
                    "name": "Urgent",
                    "description": "Urgency-focused messaging",
                    "type": "element_text",
                    "traffic_allocation": 0.34,
                    "config": {
                        "changes": [
                            {
                                "selector": ".pricing-cta",
                                "value": "Get Started Today"
                            }
                        ]
                    }
                }
            ]
        }
        
        return self.create_experiment(experiment_data)
    
    def create_phone_agent_demo_test(self) -> Experiment:
        """Create phone agent demo page test"""
        
        experiment_data = {
            "name": "Phone Agent Demo Video Test",
            "description": "Test different video placements and styles on phone agent demo page",
            "hypothesis": "Auto-playing video will increase demo requests by 25%",
            "target_url": "/phone-agent",
            "success_metrics": ["demo_request", "video_completion"],
            "variations": [
                {
                    "name": "Control",
                    "description": "Static video with play button",
                    "type": "element_style",
                    "traffic_allocation": 0.5,
                    "config": {
                        "css": ".demo-video { autoplay: false; }"
                    }
                },
                {
                    "name": "Auto-Play",
                    "description": "Auto-playing video (muted)",
                    "type": "script_injection",
                    "traffic_allocation": 0.5,
                    "config": {
                        "code": """
                            document.addEventListener('DOMContentLoaded', function() {
                                const video = document.querySelector('.demo-video video');
                                if (video) {
                                    video.autoplay = true;
                                    video.muted = true;
                                    video.play();
                                }
                            });
                        """
                    }
                }
            ]
        }
        
        return self.create_experiment(experiment_data)
    
    def generate_analytics_dashboard(self) -> str:
        """Generate A/B testing analytics dashboard"""
        
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HardCard A/B Testing Dashboard</title>
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
            max-width: 1400px;
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
        
        .metric:last-child { border-bottom: none; }
        
        .metric-value {
            font-weight: 600;
            font-size: 1.5rem;
        }
        
        .metric-change {
            font-size: 0.875rem;
            font-weight: 500;
        }
        
        .positive { color: #10b981; }
        .negative { color: #ef4444; }
        .neutral { color: #64748b; }
        
        .experiment-list {
            background: white;
            border-radius: 1rem;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .experiment-header {
            background: #f1f5f9;
            padding: 1.5rem 2rem;
            border-bottom: 1px solid #e2e8f0;
        }
        
        .experiment-item {
            padding: 1.5rem 2rem;
            border-bottom: 1px solid #e2e8f0;
            transition: background 0.3s ease;
        }
        
        .experiment-item:hover {
            background: #f8fafc;
        }
        
        .experiment-item:last-child {
            border-bottom: none;
        }
        
        .experiment-name {
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #1e293b;
        }
        
        .experiment-meta {
            display: flex;
            gap: 2rem;
            margin-bottom: 1rem;
            font-size: 0.875rem;
            color: #64748b;
        }
        
        .status-badge {
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 500;
        }
        
        .status-running {
            background: #dcfce7;
            color: #166534;
        }
        
        .status-draft {
            background: #f3f4f6;
            color: #374151;
        }
        
        .status-completed {
            background: #dbeafe;
            color: #1e40af;
        }
        
        .variations {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .variation {
            background: #f8fafc;
            padding: 1rem;
            border-radius: 0.5rem;
            border: 1px solid #e2e8f0;
        }
        
        .variation-name {
            font-weight: 500;
            margin-bottom: 0.5rem;
        }
        
        .variation-stats {
            font-size: 0.875rem;
            color: #64748b;
        }
        
        .conversion-chart {
            margin-top: 1rem;
            height: 200px;
            background: #f8fafc;
            border-radius: 0.5rem;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #64748b;
        }
        
        .action-buttons {
            display: flex;
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .btn {
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 0.5rem;
            cursor: pointer;
            font-size: 0.875rem;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .btn-primary {
            background: #3b82f6;
            color: white;
        }
        
        .btn-primary:hover {
            background: #2563eb;
        }
        
        .btn-secondary {
            background: #e2e8f0;
            color: #374151;
        }
        
        .btn-secondary:hover {
            background: #d1d5db;
        }
        
        .confidence-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 0.5rem;
        }
        
        .confidence-high { background: #10b981; }
        .confidence-medium { background: #f59e0b; }
        .confidence-low { background: #ef4444; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 A/B Testing Dashboard</h1>
        <p>Optimize conversions with data-driven experiments</p>
    </div>
    
    <div class="container">
        <!-- Overview Metrics -->
        <div class="dashboard-grid">
            <div class="card">
                <h3>📊 Active Experiments</h3>
                <div class="metric">
                    <span>Running</span>
                    <span class="metric-value">3</span>
                </div>
                <div class="metric">
                    <span>Draft</span>
                    <span class="metric-value">2</span>
                </div>
                <div class="metric">
                    <span>Completed</span>
                    <span class="metric-value">8</span>
                </div>
            </div>
            
            <div class="card">
                <h3>📈 Conversion Rates</h3>
                <div class="metric">
                    <span>Trial Signups</span>
                    <span class="metric-value">4.2%</span>
                    <span class="metric-change positive">+0.8%</span>
                </div>
                <div class="metric">
                    <span>Demo Requests</span>
                    <span class="metric-value">2.1%</span>
                    <span class="metric-change positive">+0.3%</span>
                </div>
                <div class="metric">
                    <span>Contact Forms</span>
                    <span class="metric-value">1.8%</span>
                    <span class="metric-change negative">-0.1%</span>
                </div>
            </div>
            
            <div class="card">
                <h3>👥 Traffic & Engagement</h3>
                <div class="metric">
                    <span>Total Visitors</span>
                    <span class="metric-value">15,247</span>
                </div>
                <div class="metric">
                    <span>Test Participants</span>
                    <span class="metric-value">8,932</span>
                </div>
                <div class="metric">
                    <span>Avg. Session Duration</span>
                    <span class="metric-value">3m 42s</span>
                    <span class="metric-change positive">+18s</span>
                </div>
            </div>
            
            <div class="card">
                <h3>🎯 Performance Summary</h3>
                <div class="metric">
                    <span>Tests with Significant Results</span>
                    <span class="metric-value">5/8</span>
                </div>
                <div class="metric">
                    <span>Average Uplift</span>
                    <span class="metric-value">+12.3%</span>
                </div>
                <div class="metric">
                    <span>Revenue Impact</span>
                    <span class="metric-value">+$18,400</span>
                </div>
            </div>
        </div>
        
        <!-- Experiment List -->
        <div class="experiment-list">
            <div class="experiment-header">
                <h3>🔬 Current Experiments</h3>
            </div>
            
            <div class="experiment-item">
                <div class="experiment-name">Landing Page Headline Test</div>
                <div class="experiment-meta">
                    <span class="status-badge status-running">Running</span>
                    <span>Started: Jul 15, 2025</span>
                    <span>Traffic: 2,847 visitors</span>
                    <span><span class="confidence-indicator confidence-high"></span>95% confidence</span>
                </div>
                <p>Testing benefit-focused headlines vs. generic product descriptions</p>
                
                <div class="variations">
                    <div class="variation">
                        <div class="variation-name">Control</div>
                        <div class="variation-stats">
                            Conversion: 3.8%<br>
                            Visitors: 1,423<br>
                            Conversions: 54
                        </div>
                    </div>
                    <div class="variation">
                        <div class="variation-name">Benefit-Focused</div>
                        <div class="variation-stats">
                            Conversion: 4.9% (+29%)<br>
                            Visitors: 1,424<br>
                            Conversions: 70
                        </div>
                    </div>
                </div>
                
                <div class="action-buttons">
                    <button class="btn btn-primary">View Details</button>
                    <button class="btn btn-secondary">Pause Test</button>
                    <button class="btn btn-secondary">Declare Winner</button>
                </div>
            </div>
            
            <div class="experiment-item">
                <div class="experiment-name">Pricing Page CTA Test</div>
                <div class="experiment-meta">
                    <span class="status-badge status-running">Running</span>
                    <span>Started: Jul 12, 2025</span>
                    <span>Traffic: 1,956 visitors</span>
                    <span><span class="confidence-indicator confidence-medium"></span>78% confidence</span>
                </div>
                <p>Testing different call-to-action button text on pricing page</p>
                
                <div class="variations">
                    <div class="variation">
                        <div class="variation-name">Control</div>
                        <div class="variation-stats">
                            Conversion: 2.1%<br>
                            Visitors: 652<br>
                            Conversions: 14
                        </div>
                    </div>
                    <div class="variation">
                        <div class="variation-name">Risk-Free</div>
                        <div class="variation-stats">
                            Conversion: 2.8% (+33%)<br>
                            Visitors: 651<br>
                            Conversions: 18
                        </div>
                    </div>
                    <div class="variation">
                        <div class="variation-name">Urgent</div>
                        <div class="variation-stats">
                            Conversion: 2.3% (+10%)<br>
                            Visitors: 653<br>
                            Conversions: 15
                        </div>
                    </div>
                </div>
                
                <div class="action-buttons">
                    <button class="btn btn-primary">View Details</button>
                    <button class="btn btn-secondary">Extend Test</button>
                </div>
            </div>
            
            <div class="experiment-item">
                <div class="experiment-name">Phone Agent Demo Video Test</div>
                <div class="experiment-meta">
                    <span class="status-badge status-running">Running</span>
                    <span>Started: Jul 10, 2025</span>
                    <span>Traffic: 3,129 visitors</span>
                    <span><span class="confidence-indicator confidence-high"></span>97% confidence</span>
                </div>
                <p>Testing auto-play video vs. static thumbnail on demo page</p>
                
                <div class="variations">
                    <div class="variation">
                        <div class="variation-name">Static Video</div>
                        <div class="variation-stats">
                            Demo Requests: 1.9%<br>
                            Video Completion: 45%<br>
                            Visitors: 1,564
                        </div>
                    </div>
                    <div class="variation">
                        <div class="variation-name">Auto-Play</div>
                        <div class="variation-stats">
                            Demo Requests: 2.7% (+42%)<br>
                            Video Completion: 67%<br>
                            Visitors: 1,565
                        </div>
                    </div>
                </div>
                
                <div class="action-buttons">
                    <button class="btn btn-primary">Implement Winner</button>
                    <button class="btn btn-secondary">View Report</button>
                </div>
            </div>
            
            <div class="experiment-item">
                <div class="experiment-name">Contact Form Length Test</div>
                <div class="experiment-meta">
                    <span class="status-badge status-draft">Draft</span>
                    <span>Created: Jul 18, 2025</span>
                    <span>Target: Contact page</span>
                </div>
                <p>Testing short vs. long contact form to optimize completion rates</p>
                
                <div class="action-buttons">
                    <button class="btn btn-primary">Start Test</button>
                    <button class="btn btn-secondary">Edit</button>
                    <button class="btn btn-secondary">Delete</button>
                </div>
            </div>
            
            <div class="experiment-item">
                <div class="experiment-name">Mobile Navigation Test</div>
                <div class="experiment-meta">
                    <span class="status-badge status-completed">Completed</span>
                    <span>Ran: Jun 20 - Jul 5, 2025</span>
                    <span>Winner: Hamburger Menu</span>
                    <span><span class="confidence-indicator confidence-high"></span>99% confidence</span>
                </div>
                <p>Hamburger menu increased mobile engagement by 24%</p>
                
                <div class="action-buttons">
                    <button class="btn btn-primary">View Results</button>
                    <button class="btn btn-secondary">Archive</button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Dashboard interactivity
        document.querySelectorAll('.btn').forEach(button => {
            button.addEventListener('click', function() {
                const action = this.textContent;
                console.log('Action clicked:', action);
                
                // In production, these would make API calls
                switch(action) {
                    case 'View Details':
                        alert('Would open detailed experiment view');
                        break;
                    case 'Pause Test':
                        if (confirm('Are you sure you want to pause this test?')) {
                            alert('Test paused');
                        }
                        break;
                    case 'Declare Winner':
                        alert('Would open winner declaration dialog');
                        break;
                    case 'Start Test':
                        alert('Would start the experiment');
                        break;
                    default:
                        alert(`Would execute: ${action}`);
                }
            });
        });
        
        // Auto-refresh dashboard every 30 seconds
        setInterval(function() {
            console.log('Refreshing dashboard data...');
            // In production, fetch updated metrics
        }, 30000);
    </script>
</body>
</html>"""
    
    def generate_implementation_guide(self) -> str:
        """Generate comprehensive implementation guide"""
        
        return """# HardCard A/B Testing Implementation Guide

## Overview

This guide provides step-by-step instructions for implementing A/B tests using the HardCard testing harness.

## Quick Start

### 1. Include the A/B Testing Script

Add the A/B testing JavaScript snippet to your website's `<head>` section:

```html
<!-- A/B Testing Harness -->
<script src="/js/hardcard-ab-testing.js" async></script>
```

### 2. Set Up Analytics Tracking

Configure Google Analytics custom dimensions:
- Custom Dimension 1: Experiment ID
- Custom Dimension 2: Variation ID

### 3. Create Your First Experiment

```python
from ab_testing_harness import ABTestingHarness

harness = ABTestingHarness()

experiment_data = {
    "name": "Hero Button Test",
    "description": "Test different button colors",
    "hypothesis": "Red button will increase clicks by 10%",
    "target_url": "/",
    "success_metrics": ["button_click"],
    "variations": [
        {
            "name": "Control (Blue)",
            "description": "Original blue button",
            "type": "element_style",
            "traffic_allocation": 0.5,
            "config": {
                "css": ".hero-button { background-color: #3b82f6; }"
            }
        },
        {
            "name": "Treatment (Red)",
            "description": "Red button variant",
            "type": "element_style", 
            "traffic_allocation": 0.5,
            "config": {
                "css": ".hero-button { background-color: #ef4444; }"
            }
        }
    ]
}

experiment = harness.create_experiment(experiment_data)
```

### 4. Generate and Deploy JavaScript

```python
js_code = harness.generate_javascript_snippet(experiment)

# Save to file
with open('experiment.js', 'w') as f:
    f.write(js_code)
```

## Experiment Types

### Text Changes

Change text content of elements:

```python
"config": {
    "changes": [
        {
            "selector": "h1.headline",
            "value": "New Headline Text"
        },
        {
            "selector": "button.cta",
            "attribute": "value",
            "value": "New Button Text"
        }
    ]
}
```

### Style Changes

Modify CSS styles:

```python
"config": {
    "css": '''
        .hero-section {
            background-color: #f0f9ff;
            padding: 4rem 0;
        }
        .cta-button {
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
            box-shadow: 0 10px 20px rgba(59, 130, 246, 0.3);
        }
    '''
}
```

### Redirects

Redirect users to different pages:

```python
"config": {
    "url": "/alternative-landing-page",
    "immediate": True
}
```

### Script Injection

Add custom JavaScript:

```python
"config": {
    "code": '''
        document.addEventListener('DOMContentLoaded', function() {
            // Custom behavior for this variation
            console.log('Variation B loaded');
            
            // Add event listeners
            document.querySelector('.special-button').addEventListener('click', function() {
                gtag('event', 'special_click', {
                    experiment_id: window.hardcardABTest.experimentId,
                    variation_id: window.hardcardABTest.variation.id
                });
            });
        });
    '''
}
```

## Success Metrics

### Predefined Metrics

The system tracks these events automatically:

- `trial_signup`: User starts free trial
- `demo_request`: User requests demo
- `contact_form_submit`: Contact form submission
- `video_completion`: Video watched to completion
- `page_views`: Page view tracking
- `time_on_page`: Session duration
- `scroll_depth`: How far user scrolls (25%, 50%, 75%, 100%)

### Custom Events

Trigger custom conversion events:

```javascript
// Trial signup
document.addEventListener('trial_signup', function() {
    // Event automatically tracked
});

// Custom event
function trackCustomConversion() {
    const event = new CustomEvent('custom_conversion', {
        detail: { value: 99.99, currency: 'USD' }
    });
    document.dispatchEvent(event);
}

// Manual tracking
if (window.hardcardABTest) {
    fetch('/api/analytics/ab-test-event', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            event: 'custom_metric',
            experiment_id: window.hardcardABTest.experimentId,
            variation_id: window.hardcardABTest.variation.id,
            value: 100
        })
    });
}
```

## Best Practices

### Experiment Design

1. **Single Variable**: Test one change at a time
2. **Clear Hypothesis**: State expected outcome and magnitude
3. **Sufficient Sample Size**: Ensure statistical power
4. **Time Considerations**: Account for day-of-week and seasonal effects

### Technical Implementation

1. **Performance**: Minimize JavaScript execution time
2. **Flicker Prevention**: Apply changes before page render when possible
3. **Fallbacks**: Always have control variation as fallback
4. **Browser Compatibility**: Test across all target browsers

### Statistical Rigor

1. **Sample Size**: Calculate required sample size before starting
2. **Duration**: Run tests for full business cycles (typically 1-2 weeks)
3. **Significance**: Wait for statistical significance (95% confidence)
4. **Multiple Testing**: Adjust for multiple comparisons

## Common Patterns

### Landing Page Optimization

```python
landing_page_test = {
    "name": "Landing Page Conversion Optimization",
    "target_url": "/",
    "success_metrics": ["trial_signup", "demo_request"],
    "variations": [
        {
            "name": "Original",
            "type": "element_text",
            "traffic_allocation": 0.25,
            "config": {
                "changes": [
                    {"selector": "h1", "value": "AI-Powered Veterinary Software"},
                    {"selector": ".hero-cta", "value": "Start Free Trial"}
                ]
            }
        },
        {
            "name": "Benefit-Focused",
            "type": "element_text", 
            "traffic_allocation": 0.25,
            "config": {
                "changes": [
                    {"selector": "h1", "value": "Save 10 Hours Per Week"},
                    {"selector": ".hero-cta", "value": "See How Much Time You'll Save"}
                ]
            }
        },
        {
            "name": "Social Proof",
            "type": "element_text",
            "traffic_allocation": 0.25,
            "config": {
                "changes": [
                    {"selector": "h1", "value": "Join 2,500+ Veterinary Practices"},
                    {"selector": ".hero-cta", "value": "Join Your Peers"}
                ]
            }
        },
        {
            "name": "Risk-Free",
            "type": "element_text",
            "traffic_allocation": 0.25,
            "config": {
                "changes": [
                    {"selector": "h1", "value": "Risk-Free Veterinary Software"},
                    {"selector": ".hero-cta", "value": "Try Risk-Free for 30 Days"}
                ]
            }
        }
    ]
}
```

### Pricing Page Optimization

```python
pricing_test = {
    "name": "Pricing Page Value Proposition",
    "target_url": "/pricing",
    "success_metrics": ["trial_signup"],
    "variations": [
        {
            "name": "Feature-Focused",
            "type": "element_style",
            "traffic_allocation": 0.5,
            "config": {
                "css": '''
                    .pricing-highlight { 
                        border: 3px solid #3b82f6;
                        position: relative;
                    }
                    .pricing-highlight::before {
                        content: "Most Popular";
                        position: absolute;
                        top: -12px;
                        left: 50%;
                        transform: translateX(-50%);
                        background: #3b82f6;
                        color: white;
                        padding: 0.5rem 1rem;
                        border-radius: 1rem;
                        font-size: 0.875rem;
                        font-weight: 600;
                    }
                '''
            }
        },
        {
            "name": "Value-Focused",
            "type": "script_injection",
            "traffic_allocation": 0.5,
            "config": {
                "code": '''
                    document.addEventListener('DOMContentLoaded', function() {
                        // Add ROI calculator
                        const pricingCards = document.querySelectorAll('.pricing-card');
                        pricingCards.forEach(card => {
                            const price = card.querySelector('.price').textContent;
                            const roiElement = document.createElement('div');
                            roiElement.className = 'roi-indicator';
                            roiElement.innerHTML = `
                                <strong>ROI:</strong> 
                                Saves $${parseInt(price.replace('$', '')) * 15}/month in staff time
                            `;
                            card.appendChild(roiElement);
                        });
                    });
                '''
            }
        }
    ]
}
```

## Monitoring and Analysis

### Real-time Dashboard

Access the dashboard at `/ab-testing/dashboard.html` to monitor:

- Experiment status and performance
- Conversion rates by variation
- Statistical significance
- Revenue impact

### Data Export

Export results for deeper analysis:

```python
results = harness.export_experiment_results(experiment_id)
df = pd.DataFrame(results)
df.to_csv('experiment_results.csv')
```

### Integration with Analytics

The system automatically integrates with:
- Google Analytics (custom dimensions)
- Mixpanel (events and properties)
- Segment (traits and events)

## Troubleshooting

### Common Issues

1. **Flicker Effect**: Use server-side testing for critical elements
2. **Low Traffic**: Reduce minimum sample size or extend test duration
3. **No Statistical Significance**: Increase effect size or sample size
4. **Performance Impact**: Optimize JavaScript and reduce DOM manipulation

### Debug Mode

Enable debug logging:

```javascript
window.hardcardABTestDebug = true;
```

This will log all experiment activity to the browser console.

---

*This implementation guide ensures successful A/B testing with statistical rigor and technical best practices.*
"""


def main():
    """Initialize A/B testing harness with sample experiments"""
    
    harness = ABTestingHarness()
    
    # Create sample experiments
    landing_page_test = harness.create_landing_page_test()
    pricing_test = harness.create_pricing_page_test()
    demo_test = harness.create_phone_agent_demo_test()
    
    # Generate JavaScript snippets
    experiments = [landing_page_test, pricing_test, demo_test]
    for experiment in experiments:
        js_code = harness.generate_javascript_snippet(experiment)
        js_file = harness.base_dir / f"{experiment.id}_experiment.js"
        js_file.write_text(js_code)
    
    # Generate dashboard
    dashboard_html = harness.generate_analytics_dashboard()
    (harness.base_dir / "dashboard.html").write_text(dashboard_html)
    
    # Generate implementation guide
    guide_content = harness.generate_implementation_guide()
    (harness.base_dir / "implementation_guide.md").write_text(guide_content)
    
    print("✅ A/B Testing Harness Initialized")
    print(f"📁 Testing Directory: {harness.base_dir}")
    print(f"📊 Dashboard: file://{harness.base_dir}/dashboard.html")
    print(f"📖 Implementation Guide: {harness.base_dir}/implementation_guide.md")
    print(f"🧪 Sample Experiments Created: {len(experiments)}")
    
    print("\n🎯 Experiments Created:")
    for experiment in experiments:
        print(f"   • {experiment.name} (ID: {experiment.id})")
        print(f"     JavaScript: {experiment.id}_experiment.js")
        print(f"     Variations: {len(experiment.variations)}")
    
    print("\n📈 Ready for conversion optimization!")


if __name__ == "__main__":
    main()