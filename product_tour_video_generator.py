#!/usr/bin/env python3
"""
HardCard Product Tour Video Generator
====================================
Creates compelling product demonstration scripts and storyboards
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class ProductTourVideoGenerator:
    """Generate comprehensive product tour videos and scripts"""
    
    def __init__(self):
        self.base_dir = Path("/Users/studio/hardcard/product_tours")
        self.videos_dir = self.base_dir / "videos"
        self.scripts_dir = self.base_dir / "scripts"
        self.assets_dir = self.base_dir / "assets"
        
        # Initialize directories
        self.setup_directories()
    
    def setup_directories(self):
        """Initialize directory structure"""
        
        for directory in [self.base_dir, self.videos_dir, self.scripts_dir, self.assets_dir]:
            directory.mkdir(exist_ok=True)
    
    def generate_ai_phone_agent_tour(self) -> Dict[str, Any]:
        """Generate AI Phone Agent product tour script"""
        
        return {
            "title": "HardCard AI Phone Agent - Never Miss Another Call",
            "duration": "3 minutes",
            "target_audience": "Veterinary practice owners and managers",
            "key_messages": [
                "24/7 availability replaces human receptionists",
                "Natural conversation handling",
                "Instant appointment booking",
                "Emergency call triage",
                "Cost savings and efficiency"
            ],
            "scenes": [
                {
                    "scene_number": 1,
                    "title": "Hook - The Problem",
                    "duration": "15 seconds",
                    "visual_description": "Split screen showing busy vet clinic with ringing phones vs missed calls going to voicemail",
                    "narration": "Every missed call is a missed opportunity. Your clients need you, but you can't answer the phone 24/7.",
                    "on_screen_text": "47% of veterinary calls go unanswered",
                    "music": "Tense, problem-focused",
                    "transitions": "Quick cuts between ringing phones and frustrated pet owners"
                },
                {
                    "scene_number": 2,
                    "title": "Introduce the Solution",
                    "duration": "20 seconds",
                    "visual_description": "HardCard AI Phone Agent interface, showing AI avatar answering call",
                    "narration": "Meet your new AI receptionist. HardCard's Phone Agent answers every call with natural conversation and intelligent appointment booking.",
                    "on_screen_text": "AI Phone Agent - Always Available",
                    "music": "Uplifting, solution-oriented",
                    "transitions": "Smooth fade from problem to solution"
                },
                {
                    "scene_number": 3,
                    "title": "Live Call Demonstration",
                    "duration": "45 seconds",
                    "visual_description": "Screen recording of actual phone conversation with transcript overlay",
                    "narration": "Watch a real conversation. The AI understands natural speech, accesses your calendar, and books appointments instantly.",
                    "dialogue": [
                        "AI: Hello, this is Luna from Sunshine Veterinary Clinic. How can I help you today?",
                        "Caller: Hi, I need to schedule a checkup for my dog Bella.",
                        "AI: I'd be happy to help schedule Bella's checkup. What's your name and phone number?",
                        "Caller: This is Sarah Johnson, 555-0123.",
                        "AI: Perfect! I see Bella's previous visit. I have Tuesday at 2 PM or Thursday at 10 AM available. Which works better?",
                        "Caller: Tuesday at 2 PM sounds great.",
                        "AI: Excellent! I've booked Bella for Tuesday, July 23rd at 2 PM. You'll receive a confirmation text shortly."
                    ],
                    "on_screen_text": "Real conversation in under 60 seconds",
                    "music": "Calm, professional background",
                    "visual_effects": "Highlight calendar booking in real-time"
                },
                {
                    "scene_number": 4,
                    "title": "Key Features Showcase",
                    "duration": "30 seconds",
                    "visual_description": "Split screen showing multiple features with icons and brief demonstrations",
                    "narration": "Emergency triage routes urgent calls immediately. Multi-language support serves diverse communities. Integration with your existing practice management system.",
                    "features": [
                        {
                            "icon": "🚨",
                            "title": "Emergency Triage",
                            "description": "Urgent calls routed immediately"
                        },
                        {
                            "icon": "🌍",
                            "title": "Multi-Language",
                            "description": "English, Spanish, and more"
                        },
                        {
                            "icon": "🔗",
                            "title": "Integrations",
                            "description": "Works with your existing systems"
                        }
                    ],
                    "on_screen_text": "Advanced Features",
                    "music": "Modern, tech-focused"
                },
                {
                    "scene_number": 5,
                    "title": "Results & Benefits",
                    "duration": "25 seconds",
                    "visual_description": "Animated statistics and testimonial from happy vet clinic",
                    "narration": "Clinics using HardCard see 95% fewer missed calls, 40% more appointments booked, and staff freed up for patient care.",
                    "statistics": [
                        "95% fewer missed calls",
                        "40% more appointments",
                        "60% staff time savings",
                        "$3,200 average monthly revenue increase"
                    ],
                    "testimonial": {
                        "quote": "HardCard transformed our practice. We never miss calls anymore, and our staff can focus on what they do best - caring for animals.",
                        "author": "Dr. Michael Chen, Riverside Veterinary Hospital"
                    },
                    "on_screen_text": "Proven Results",
                    "music": "Success-oriented, uplifting"
                },
                {
                    "scene_number": 6,
                    "title": "Call to Action",
                    "duration": "15 seconds",
                    "visual_description": "Clean signup form with special offer highlighted",
                    "narration": "Start your free 14-day trial today. No setup fees, no long-term contracts. Just results.",
                    "cta_elements": [
                        "Start Free Trial",
                        "14 days free",
                        "No setup fees",
                        "Cancel anytime"
                    ],
                    "on_screen_text": "Get Started Today - 14 Days Free",
                    "music": "Confident, action-oriented"
                }
            ],
            "production_notes": {
                "style": "Modern, clean animation with real interface screenshots",
                "color_scheme": "HardCard brand colors (blues, grays, white)",
                "fonts": "Clean, professional sans-serif",
                "animation_style": "Smooth transitions, minimal motion graphics",
                "voiceover": "Professional, friendly female voice",
                "background_music": "Licensed corporate/tech music"
            },
            "technical_specs": {
                "resolution": "1920x1080 (Full HD)",
                "frame_rate": "30fps",
                "format": "MP4 H.264",
                "aspect_ratio": "16:9",
                "estimated_file_size": "50-80 MB"
            }
        }
    
    def generate_practice_management_tour(self) -> Dict[str, Any]:
        """Generate Practice Management System tour script"""
        
        return {
            "title": "HardCard Practice Management - Complete Veterinary Solution",
            "duration": "4 minutes",
            "target_audience": "Veterinary professionals, practice managers",
            "key_messages": [
                "Complete EMR solution",
                "Integrated client and patient management",
                "Advanced analytics and reporting",
                "Seamless workflow optimization",
                "Modern, intuitive interface"
            ],
            "scenes": [
                {
                    "scene_number": 1,
                    "title": "Opening - The Modern Veterinary Practice",
                    "duration": "20 seconds",
                    "visual_description": "Time-lapse of busy modern veterinary clinic with staff using various systems",
                    "narration": "Running a modern veterinary practice requires more than just medical expertise. You need intelligent systems that work as hard as you do.",
                    "on_screen_text": "The Modern Veterinary Practice",
                    "music": "Inspiring, professional"
                },
                {
                    "scene_number": 2,
                    "title": "Dashboard Overview",
                    "duration": "30 seconds",
                    "visual_description": "Screen recording of HardCard dashboard with key metrics highlighted",
                    "narration": "HardCard's dashboard gives you instant visibility into your practice. Today's appointments, waiting patients, revenue metrics, and staff performance - all in one view.",
                    "dashboard_elements": [
                        "Today's schedule",
                        "Waiting room status",
                        "Revenue tracking",
                        "Staff utilization",
                        "Quick actions"
                    ],
                    "on_screen_text": "Complete Practice Visibility",
                    "music": "Modern, tech-focused"
                },
                {
                    "scene_number": 3,
                    "title": "Client Management Workflow",
                    "duration": "40 seconds",
                    "visual_description": "Step-by-step demonstration of client check-in process",
                    "narration": "From check-in to checkout, every interaction is streamlined. Scan QR codes for contactless check-in, access complete patient histories, and update records in real-time.",
                    "workflow_steps": [
                        "QR code check-in",
                        "Patient history review",
                        "Visit documentation",
                        "Treatment planning",
                        "Billing and checkout"
                    ],
                    "on_screen_text": "Streamlined Workflows",
                    "music": "Smooth, efficient"
                },
                {
                    "scene_number": 4,
                    "title": "EMR Capabilities",
                    "duration": "45 seconds",
                    "visual_description": "Deep dive into electronic medical records interface",
                    "narration": "Comprehensive electronic medical records keep everything organized. Vaccination schedules, surgical notes, diagnostic images, and treatment plans - all searchable and accessible.",
                    "emr_features": [
                        "Complete medical histories",
                        "Vaccination tracking",
                        "Diagnostic integration",
                        "Treatment templates",
                        "Prescription management",
                        "Photo/image storage"
                    ],
                    "on_screen_text": "Complete EMR System",
                    "music": "Professional, medical"
                },
                {
                    "scene_number": 5,
                    "title": "Analytics & Insights",
                    "duration": "35 seconds",
                    "visual_description": "Interactive charts and reports showing practice analytics",
                    "narration": "Data-driven insights help you grow your practice. Track revenue trends, identify popular services, monitor staff productivity, and discover opportunities.",
                    "analytics_features": [
                        "Revenue analytics",
                        "Service popularity",
                        "Client retention metrics",
                        "Staff performance",
                        "Inventory optimization",
                        "Predictive insights"
                    ],
                    "on_screen_text": "Business Intelligence",
                    "music": "Analytical, intelligent"
                },
                {
                    "scene_number": 6,
                    "title": "Integration Ecosystem",
                    "duration": "25 seconds",
                    "visual_description": "Network diagram showing HardCard connecting to various systems",
                    "narration": "HardCard integrates with the tools you already use. IDEXX lab results, imaging systems, payment processors, and more - all connected seamlessly.",
                    "integrations": [
                        "IDEXX Labs",
                        "Stripe Payments",
                        "QuickBooks",
                        "Digital X-ray systems",
                        "Pharmacy systems",
                        "Marketing platforms"
                    ],
                    "on_screen_text": "Seamless Integrations",
                    "music": "Connected, harmonious"
                },
                {
                    "scene_number": 7,
                    "title": "Mobile Experience",
                    "duration": "20 seconds",
                    "visual_description": "Mobile app demonstration on tablet and smartphone",
                    "narration": "Access everything from anywhere. Mobile apps for staff keep you connected whether you're in surgery, making house calls, or at home.",
                    "mobile_features": [
                        "Full EMR access",
                        "Appointment scheduling",
                        "Client communication",
                        "Prescription approval",
                        "Emergency notifications"
                    ],
                    "on_screen_text": "Mobile-First Design",
                    "music": "Modern, mobile"
                },
                {
                    "scene_number": 8,
                    "title": "Success Stories",
                    "duration": "25 seconds",
                    "visual_description": "Testimonials from real veterinary professionals",
                    "narration": "Join thousands of veterinary professionals who trust HardCard to run their practices more efficiently.",
                    "testimonials": [
                        {
                            "quote": "HardCard reduced our administrative time by 60% while improving patient care quality.",
                            "author": "Dr. Lisa Park, Metro Animal Hospital"
                        },
                        {
                            "quote": "The integrated phone agent alone paid for the entire system in the first month.",
                            "author": "Dr. James Wilson, Wilson Veterinary Clinic"
                        }
                    ],
                    "statistics": [
                        "2,500+ practices served",
                        "99.9% uptime",
                        "4.9/5 customer satisfaction"
                    ],
                    "on_screen_text": "Trusted by Professionals",
                    "music": "Trustworthy, established"
                },
                {
                    "scene_number": 9,
                    "title": "Call to Action",
                    "duration": "20 seconds",
                    "visual_description": "Demo booking interface with calendar and contact form",
                    "narration": "See HardCard in action. Schedule a personalized demo and discover how we can transform your practice.",
                    "cta_elements": [
                        "Schedule Demo",
                        "Free consultation",
                        "Custom pricing",
                        "Migration support"
                    ],
                    "on_screen_text": "Schedule Your Demo Today",
                    "music": "Action-oriented, closing"
                }
            ]
        }
    
    def generate_quick_wins_tour(self) -> Dict[str, Any]:
        """Generate Quick Wins & ROI tour script"""
        
        return {
            "title": "HardCard Quick Wins - See Results in 30 Days",
            "duration": "2 minutes",
            "target_audience": "Decision makers, practice owners",
            "key_messages": [
                "Immediate ROI",
                "Fast implementation",
                "Measurable results",
                "Risk-free trial",
                "Success guarantee"
            ],
            "scenes": [
                {
                    "scene_number": 1,
                    "title": "Time is Money",
                    "duration": "15 seconds",
                    "visual_description": "Clock animation with dollar signs, showing time wasted on inefficient processes",
                    "narration": "Every minute your staff spends on administrative tasks is time not spent on patient care. And every missed call is lost revenue.",
                    "on_screen_text": "Time = Money",
                    "music": "Urgent, attention-grabbing"
                },
                {
                    "scene_number": 2,
                    "title": "30-Day Challenge",
                    "duration": "20 seconds",
                    "visual_description": "Calendar animation showing 30-day progression with checkmarks",
                    "narration": "We're so confident in HardCard, we guarantee you'll see measurable results in your first 30 days, or we'll refund your money.",
                    "guarantee_points": [
                        "30-day money-back guarantee",
                        "Measurable results",
                        "No risk trial"
                    ],
                    "on_screen_text": "30-Day Success Guarantee",
                    "music": "Confident, guarantee-focused"
                },
                {
                    "scene_number": 3,
                    "title": "Week 1 - Setup & Training",
                    "duration": "20 seconds",
                    "visual_description": "Fast-forward setup process with progress indicators",
                    "narration": "Week one: Complete setup in under 4 hours. Our team migrates your data and trains your staff. You're operational day one.",
                    "week1_milestones": [
                        "Data migration complete",
                        "Staff training finished",
                        "Phone agent active",
                        "First appointments booked"
                    ],
                    "on_screen_text": "Week 1: Up and Running",
                    "music": "Progress, setup"
                },
                {
                    "scene_number": 4,
                    "title": "Week 2-3 - Results Appear",
                    "duration": "25 seconds",
                    "visual_description": "Charts showing improving metrics with upward arrows",
                    "narration": "Weeks two and three: Watch the results roll in. More calls answered, appointments booked, staff productivity soaring.",
                    "early_results": [
                        "95% call answer rate",
                        "30% more appointments",
                        "2 hours daily staff savings",
                        "Client satisfaction up 25%"
                    ],
                    "on_screen_text": "Weeks 2-3: Results Visible",
                    "music": "Upward, successful"
                },
                {
                    "scene_number": 5,
                    "title": "Week 4 - Full ROI",
                    "duration": "25 seconds",
                    "visual_description": "ROI calculator showing positive returns with celebration animations",
                    "narration": "Week four: Full return on investment. The average practice saves $3,200 monthly while improving patient care quality.",
                    "roi_breakdown": [
                        "Monthly software cost: $199",
                        "Staff time savings: $2,400",
                        "Additional appointments: $1,800",
                        "Reduced missed calls: $600",
                        "Net monthly benefit: $4,601"
                    ],
                    "on_screen_text": "Week 4: Full ROI Achieved",
                    "music": "Triumphant, successful"
                },
                {
                    "scene_number": 6,
                    "title": "Real Practice Example",
                    "duration": "20 seconds",
                    "visual_description": "Before/after comparison of actual practice metrics",
                    "narration": "Riverside Veterinary saw these results in their first month. Your practice could be next.",
                    "case_study": {
                        "practice": "Riverside Veterinary Hospital",
                        "before": {
                            "missed_calls": "47%",
                            "staff_overtime": "15 hours/week",
                            "client_complaints": "12/month"
                        },
                        "after": {
                            "missed_calls": "3%",
                            "staff_overtime": "2 hours/week",
                            "client_complaints": "1/month"
                        }
                    },
                    "on_screen_text": "Real Results",
                    "music": "Credible, testimonial"
                },
                {
                    "scene_number": 7,
                    "title": "Start Today",
                    "duration": "15 seconds",
                    "visual_description": "Simple signup form with immediate access messaging",
                    "narration": "Don't wait. Start your risk-free trial today and see results in 30 days, guaranteed.",
                    "cta_elements": [
                        "Start Free Trial",
                        "30-day guarantee",
                        "Setup in 4 hours",
                        "Results guaranteed"
                    ],
                    "on_screen_text": "Start Today - Risk Free",
                    "music": "Urgent call-to-action"
                }
            ]
        }
    
    def create_storyboards(self, tour_script: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create detailed storyboards from tour scripts"""
        
        storyboards = []
        
        for scene in tour_script["scenes"]:
            storyboard = {
                "scene_number": scene["scene_number"],
                "title": scene["title"],
                "duration": scene["duration"],
                "shots": self.break_into_shots(scene),
                "visual_notes": scene["visual_description"],
                "audio_notes": {
                    "narration": scene["narration"],
                    "music": scene.get("music", ""),
                    "sound_effects": self.suggest_sound_effects(scene)
                },
                "graphics_needed": self.identify_graphics_needed(scene),
                "animation_notes": self.create_animation_notes(scene)
            }
            storyboards.append(storyboard)
        
        return storyboards
    
    def break_into_shots(self, scene: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Break scene into individual shots"""
        
        # Estimate 3-5 shots per scene based on duration
        duration_seconds = self.parse_duration(scene["duration"])
        num_shots = max(2, min(6, duration_seconds // 5))
        
        shots = []
        shot_duration = duration_seconds / num_shots
        
        for i in range(num_shots):
            shots.append({
                "shot_number": i + 1,
                "duration": f"{shot_duration:.1f} seconds",
                "shot_type": self.determine_shot_type(i, num_shots),
                "description": f"Shot {i+1} of {scene['title']}",
                "camera_movement": self.suggest_camera_movement(i, scene),
                "visual_focus": self.determine_visual_focus(i, scene)
            })
        
        return shots
    
    def parse_duration(self, duration_str: str) -> int:
        """Parse duration string to seconds"""
        if "minute" in duration_str:
            minutes = int(duration_str.split()[0])
            return minutes * 60
        elif "second" in duration_str:
            return int(duration_str.split()[0])
        return 30  # Default
    
    def determine_shot_type(self, shot_index: int, total_shots: int) -> str:
        """Determine appropriate shot type"""
        shot_types = ["wide", "medium", "close-up", "detail", "transition"]
        return shot_types[shot_index % len(shot_types)]
    
    def suggest_camera_movement(self, shot_index: int, scene: Dict[str, Any]) -> str:
        """Suggest camera movement for shot"""
        movements = ["static", "slow zoom in", "pan left", "pan right", "pull back"]
        return movements[shot_index % len(movements)]
    
    def determine_visual_focus(self, shot_index: int, scene: Dict[str, Any]) -> str:
        """Determine what should be the visual focus"""
        if "interface" in scene["visual_description"].lower():
            return "Screen recording with UI highlights"
        elif "testimonial" in scene["visual_description"].lower():
            return "Speaker with text overlay"
        else:
            return "Main product demonstration"
    
    def suggest_sound_effects(self, scene: Dict[str, Any]) -> List[str]:
        """Suggest appropriate sound effects"""
        effects = []
        
        description = scene["visual_description"].lower()
        
        if "phone" in description or "call" in description:
            effects.append("Phone ring/pickup sound")
        if "click" in description or "interface" in description:
            effects.append("UI click sounds")
        if "notification" in description:
            effects.append("Notification chime")
        if "success" in description or "complete" in description:
            effects.append("Success ding")
        
        return effects
    
    def identify_graphics_needed(self, scene: Dict[str, Any]) -> List[str]:
        """Identify graphics and animations needed"""
        graphics = []
        
        if "statistics" in scene:
            graphics.append("Animated statistics")
        if "testimonial" in scene:
            graphics.append("Testimonial quote graphics")
        if "features" in scene:
            graphics.append("Feature icon animations")
        if "on_screen_text" in scene:
            graphics.append(f"Text overlay: {scene['on_screen_text']}")
        
        return graphics
    
    def create_animation_notes(self, scene: Dict[str, Any]) -> List[str]:
        """Create detailed animation notes"""
        notes = []
        
        if "dashboard" in scene["visual_description"].lower():
            notes.append("Smooth transitions between dashboard sections")
            notes.append("Highlight key metrics with subtle glow effects")
        
        if "workflow" in scene["visual_description"].lower():
            notes.append("Step-by-step process animation with progress indicators")
            notes.append("Smooth transitions between workflow steps")
        
        if "statistics" in scene.get("narration", "").lower():
            notes.append("Count-up animations for numbers")
            notes.append("Chart/graph animations building from zero")
        
        return notes
    
    def generate_production_package(self) -> Dict[str, Any]:
        """Generate complete production package"""
        
        tours = {
            "ai_phone_agent": self.generate_ai_phone_agent_tour(),
            "practice_management": self.generate_practice_management_tour(), 
            "quick_wins": self.generate_quick_wins_tour()
        }
        
        # Create storyboards for each tour
        for tour_name, tour_script in tours.items():
            storyboards = self.create_storyboards(tour_script)
            tour_script["storyboards"] = storyboards
        
        # Save all tour scripts
        for tour_name, tour_script in tours.items():
            script_file = self.scripts_dir / f"{tour_name}_script.json"
            script_file.write_text(json.dumps(tour_script, indent=2))
        
        # Create production guide
        production_guide = self.create_production_guide(tours)
        (self.base_dir / "production_guide.md").write_text(production_guide)
        
        # Create asset checklist
        asset_checklist = self.create_asset_checklist(tours)
        (self.base_dir / "asset_checklist.json").write_text(json.dumps(asset_checklist, indent=2))
        
        return {
            "tours": tours,
            "production_guide": production_guide,
            "asset_checklist": asset_checklist,
            "total_videos": len(tours),
            "estimated_production_time": "5-7 days",
            "estimated_cost": "$3,000 - $5,000"
        }
    
    def create_production_guide(self, tours: Dict[str, Any]) -> str:
        """Create comprehensive production guide"""
        
        return f"""# HardCard Product Tour Video Production Guide

## Project Overview

This production package includes {len(tours)} professional product tour videos designed to showcase HardCard's key capabilities and drive conversions.

### Video Lineup

1. **AI Phone Agent Tour** (3 minutes)
   - Primary focus: Phone agent capabilities
   - Target: Practice owners concerned about missed calls
   - Goal: Demonstrate 24/7 availability and natural conversation

2. **Practice Management Tour** (4 minutes)
   - Primary focus: Complete EMR and practice management
   - Target: Practice managers and veterinarians
   - Goal: Show comprehensive workflow integration

3. **Quick Wins Tour** (2 minutes)
   - Primary focus: ROI and fast results
   - Target: Decision makers and budget holders
   - Goal: Overcome objections and drive trial signups

## Production Standards

### Visual Style
- **Color Palette**: HardCard brand colors (primary blue #3b82f6, grays, white)
- **Typography**: Clean, professional sans-serif fonts
- **Animation Style**: Smooth, modern motion graphics
- **Screen Quality**: All interface recordings in 1920x1080 minimum

### Audio Standards
- **Voiceover**: Professional female narrator, friendly but authoritative
- **Music**: Licensed corporate/tech background music, non-intrusive
- **Sound Effects**: Subtle UI sounds, notification chimes
- **Audio Quality**: 48kHz/24-bit minimum

### Technical Specifications
- **Resolution**: 1920x1080 (Full HD)
- **Frame Rate**: 30fps
- **Format**: MP4 with H.264 codec
- **Bitrate**: 8-10 Mbps for high quality
- **File Size Target**: 50-100 MB per video

## Pre-Production Checklist

### Assets Needed
- [ ] HardCard dashboard screenshots (high resolution)
- [ ] Phone agent interface recordings
- [ ] Mobile app demonstrations
- [ ] Client testimonial videos or quotes
- [ ] Statistics and metrics (verified and current)
- [ ] Logo files and brand assets
- [ ] Stock footage for B-roll (veterinary clinic scenes)

### Script Approval
- [ ] All scripts reviewed by marketing team
- [ ] Medical accuracy verified by veterinary consultant
- [ ] Legal review of claims and statistics
- [ ] Final approval from executive team

### Talent & Resources
- [ ] Professional voiceover artist booked
- [ ] Motion graphics designer assigned
- [ ] Video editor confirmed
- [ ] Music licensing arranged
- [ ] Project timeline established

## Production Workflow

### Phase 1: Asset Creation (Days 1-2)
1. Capture all interface recordings
2. Create motion graphics templates
3. Record voiceover narration
4. Source and license background music

### Phase 2: Editing (Days 3-4)
1. Rough cut assembly
2. Motion graphics integration
3. Audio mixing and mastering
4. Color correction and grading

### Phase 3: Review & Revision (Days 5-6)
1. Internal review and feedback
2. Revisions and refinements
3. Final quality check
4. Export and delivery

### Phase 4: Optimization (Day 7)
1. Multiple format exports
2. Platform-specific optimizations
3. Closed captions creation
4. Thumbnail design

## Distribution Strategy

### Primary Platforms
- **Website**: Embedded on landing pages and product pages
- **YouTube**: SEO-optimized with keyword targeting
- **LinkedIn**: B2B professional audience
- **Sales Demos**: Direct sales presentation use

### Secondary Platforms
- **Facebook/Instagram**: Shorter cuts for social media
- **Email Marketing**: Embedded in email campaigns
- **Trade Shows**: Loop display versions

## Success Metrics

### Engagement Metrics
- View completion rates (target: >70% for 2-min video, >50% for 4-min video)
- Click-through rates to trial signup
- Social shares and comments
- Time spent on video pages

### Conversion Metrics
- Trial signups attributed to video views
- Demo requests from video CTAs
- Sales qualified leads from video traffic
- Revenue attributed to video campaigns

## Budget Breakdown

### Production Costs
- Voiceover talent: $800 - $1,200
- Motion graphics: $1,500 - $2,500
- Video editing: $800 - $1,200
- Music licensing: $200 - $400
- Revisions buffer: $400 - $600

### Total Estimated Cost: $3,700 - $5,900

## Timeline

| Phase | Days | Deliverables |
|-------|------|-------------|
| Pre-production | 1-2 | Assets, scripts, planning |
| Production | 3-5 | Recording, graphics, editing |
| Post-production | 6-7 | Final edits, optimization |
| Delivery | 7 | Final videos, all formats |

## Quality Assurance

### Technical QA
- [ ] Audio levels consistent across all videos
- [ ] Video quality meets specifications
- [ ] No compression artifacts
- [ ] Smooth playback on all target platforms

### Content QA
- [ ] All claims verified and accurate
- [ ] Brand guidelines followed consistently
- [ ] Accessibility compliance (captions, contrast)
- [ ] Legal review completed

### Performance QA
- [ ] Loading times optimized
- [ ] Mobile compatibility verified
- [ ] Analytics tracking implemented
- [ ] A/B testing setup prepared

## Post-Launch Activities

### Immediate (Week 1)
- Monitor initial performance metrics
- Gather feedback from sales team
- Track conversion impact
- Identify optimization opportunities

### Ongoing (Monthly)
- Update statistics and testimonials
- Refresh screenshots for new features
- Create shorter cuts for different use cases
- Analyze performance data for improvements

---

*This production guide ensures professional, on-brand video content that effectively communicates HardCard's value proposition and drives measurable business results.*
"""
    
    def create_asset_checklist(self, tours: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive asset checklist"""
        
        return {
            "video_assets": {
                "interface_recordings": [
                    "HardCard dashboard main view",
                    "Phone agent interface during call",
                    "Client management workflow",
                    "Appointment booking process",
                    "EMR patient records view",
                    "Analytics dashboard",
                    "Mobile app demonstration",
                    "Integration setup screens"
                ],
                "graphics_needed": [
                    "HardCard logo (various formats)",
                    "Feature icons set",
                    "Statistics animations",
                    "Process flow diagrams",
                    "Before/after comparisons",
                    "Testimonial quote designs",
                    "Call-to-action graphics",
                    "Success metric visualizations"
                ],
                "stock_footage": [
                    "Busy veterinary clinic scenes",
                    "Ringing phones (unanswered)",
                    "Happy pet owners",
                    "Veterinarians at work",
                    "Time-lapse of clinic operations",
                    "Mobile device usage",
                    "Dashboard analytics views"
                ]
            },
            "audio_assets": {
                "voiceover": [
                    "AI Phone Agent script (3 min)",
                    "Practice Management script (4 min)",
                    "Quick Wins script (2 min)",
                    "CTA variants for testing"
                ],
                "music_tracks": [
                    "Opening theme (problem-focused)",
                    "Solution presentation (uplifting)",
                    "Feature demonstration (modern tech)",
                    "Success stories (triumphant)",
                    "Call-to-action (urgent, confident)"
                ],
                "sound_effects": [
                    "Phone ring/pickup sounds",
                    "UI click/interaction sounds",
                    "Notification chimes",
                    "Success completion sounds",
                    "Transition whooshes"
                ]
            },
            "data_requirements": [
                "Current customer success statistics",
                "Verified ROI calculations",
                "Customer testimonial approvals",
                "Competitive comparison data",
                "Feature availability by plan",
                "Pricing information (current)",
                "Integration partner logos"
            ],
            "legal_requirements": [
                "Customer testimonial releases",
                "Music licensing agreements",
                "Stock footage licenses",
                "Trademark usage approvals",
                "Claims substantiation docs",
                "Privacy compliance check"
            ],
            "technical_requirements": [
                "Brand guideline compliance",
                "Accessibility standards (WCAG 2.1)",
                "Platform-specific formats",
                "Closed caption files",
                "Thumbnail variations",
                "Mobile optimization"
            ]
        }


def main():
    """Generate complete product tour video package"""
    
    generator = ProductTourVideoGenerator()
    production_package = generator.generate_production_package()
    
    print("✅ Product Tour Video Package Generated")
    print(f"📁 Production Directory: {generator.base_dir}")
    print(f"🎬 Total Videos: {production_package['total_videos']}")
    print(f"⏱️ Estimated Production Time: {production_package['estimated_production_time']}")
    print(f"💰 Estimated Cost: {production_package['estimated_cost']}")
    
    print("\n📺 Video Scripts Created:")
    for tour_name in production_package['tours'].keys():
        script_file = generator.scripts_dir / f"{tour_name}_script.json"
        print(f"   • {script_file}")
    
    print(f"\n📋 Production Guide: {generator.base_dir}/production_guide.md")
    print(f"✅ Asset Checklist: {generator.base_dir}/asset_checklist.json")
    print("\n🎯 Ready for professional video production!")


if __name__ == "__main__":
    main()