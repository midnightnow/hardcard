#!/usr/bin/env python3
"""
MacAgent Business Workflow Templates
===================================
Pre-built automation templates for common business tasks.
Ready-to-use workflows that deliver immediate ROI.
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import json
import os

class WorkflowCategory(Enum):
    """Categories for business workflows"""
    DATA_TRANSFER = "Data Transfer"
    DATA_ENTRY = "Data Entry" 
    REPORTING = "Reporting"
    COMMUNICATION = "Communication"
    FILE_MANAGEMENT = "File Management"
    QUALITY_ASSURANCE = "Quality Assurance"

class DifficultyLevel(Enum):
    """Difficulty levels for workflows"""
    EASY = "Easy"          # 1-3 steps, basic automation
    MEDIUM = "Medium"      # 4-6 steps, some complexity
    ADVANCED = "Advanced"  # 7+ steps, complex logic

@dataclass
class WorkflowStep:
    """Individual step in a workflow"""
    action: str
    description: str
    parameters: Dict[str, Any]
    timeout_seconds: int = 10
    retry_count: int = 3
    user_confirmation: bool = False

@dataclass
class WorkflowTemplate:
    """Complete workflow template definition"""
    template_id: str
    name: str
    description: str
    category: WorkflowCategory
    difficulty: DifficultyLevel
    time_saved_minutes: int
    estimated_value_dollars: float
    steps: List[WorkflowStep]
    prerequisites: List[str]
    success_rate: float = 95.0
    usage_count: int = 0
    created_date: str = None
    
    def __post_init__(self):
        if self.created_date is None:
            self.created_date = datetime.now().isoformat()
        
        # Calculate estimated value if not provided
        if self.estimated_value_dollars == 0:
            hourly_rate = 50  # Default $50/hour
            self.estimated_value_dollars = (self.time_saved_minutes / 60) * hourly_rate

class TemplateLibrary:
    """Library of pre-built workflow templates"""
    
    def __init__(self):
        self.templates = {}
        self._initialize_templates()
    
    def _initialize_templates(self):
        """Initialize all pre-built templates"""
        templates = [
            self._excel_to_email(),
            self._web_form_filler(),
            self._daily_report_generator(),
            self._file_organizer(),
            self._invoice_processor(),
            self._crm_data_entry(),
            self._meeting_scheduler(),
            self._backup_creator(),
            self._quality_checker(),
            self._social_media_poster()
        ]
        
        for template in templates:
            self.templates[template.template_id] = template
    
    def get_all_templates(self) -> List[WorkflowTemplate]:
        """Get all available templates"""
        return list(self.templates.values())
    
    def get_by_category(self, category: WorkflowCategory) -> List[WorkflowTemplate]:
        """Get templates by category"""
        return [t for t in self.templates.values() if t.category == category]
    
    def get_by_difficulty(self, difficulty: DifficultyLevel) -> List[WorkflowTemplate]:
        """Get templates by difficulty level"""
        return [t for t in self.templates.values() if t.difficulty == difficulty]
    
    def get_template(self, template_id: str) -> Optional[WorkflowTemplate]:
        """Get specific template by ID"""
        return self.templates.get(template_id)
    
    def get_high_value_templates(self, min_value: float = 10.0) -> List[WorkflowTemplate]:
        """Get templates with high business value"""
        return [t for t in self.templates.values() if t.estimated_value_dollars >= min_value]
    
    # Template Definitions
    
    def _excel_to_email(self) -> WorkflowTemplate:
        """Excel data to email workflow"""
        return WorkflowTemplate(
            template_id="excel_to_email",
            name="Excel Data to Email",
            description="Copy spreadsheet data and create formatted email",
            category=WorkflowCategory.DATA_TRANSFER,
            difficulty=DifficultyLevel.EASY,
            time_saved_minutes=15,
            estimated_value_dollars=12.50,
            prerequisites=["Excel or Numbers", "Mail app"],
            steps=[
                WorkflowStep(
                    action="open_app",
                    description="Open Excel application",
                    parameters={"app_name": "Microsoft Excel", "fallback": "Numbers"}
                ),
                WorkflowStep(
                    action="user_select",
                    description="User selects data range",
                    parameters={"instruction": "Select the data you want to email"},
                    user_confirmation=True
                ),
                WorkflowStep(
                    action="copy_selection",
                    description="Copy selected data",
                    parameters={"hotkey": "cmd+c"}
                ),
                WorkflowStep(
                    action="open_app",
                    description="Open Mail application",
                    parameters={"app_name": "Mail"}
                ),
                WorkflowStep(
                    action="new_email",
                    description="Create new email",
                    parameters={"hotkey": "cmd+n"}
                ),
                WorkflowStep(
                    action="paste_content",
                    description="Paste data into email body",
                    parameters={"hotkey": "cmd+v"}
                )
            ]
        )
    
    def _web_form_filler(self) -> WorkflowTemplate:
        """Web form auto-fill workflow"""
        return WorkflowTemplate(
            template_id="web_form_filler",
            name="Web Form Auto-Fill",
            description="Automatically fill common form fields with saved data",
            category=WorkflowCategory.DATA_ENTRY,
            difficulty=DifficultyLevel.MEDIUM,
            time_saved_minutes=10,
            estimated_value_dollars=8.33,
            prerequisites=["Web browser", "Saved form data"],
            steps=[
                WorkflowStep(
                    action="find_field",
                    description="Find first name field",
                    parameters={"field_type": "text", "labels": ["First Name", "Name", "Given Name"]}
                ),
                WorkflowStep(
                    action="type_text",
                    description="Enter first name",
                    parameters={"text": "{{first_name}}", "clear_first": True}
                ),
                WorkflowStep(
                    action="find_field",
                    description="Find last name field",
                    parameters={"field_type": "text", "labels": ["Last Name", "Surname", "Family Name"]}
                ),
                WorkflowStep(
                    action="type_text",
                    description="Enter last name",
                    parameters={"text": "{{last_name}}", "clear_first": True}
                ),
                WorkflowStep(
                    action="find_field",
                    description="Find email field",
                    parameters={"field_type": "email", "labels": ["Email", "Email Address", "E-mail"]}
                ),
                WorkflowStep(
                    action="type_text",
                    description="Enter email address",
                    parameters={"text": "{{email}}", "clear_first": True}
                )
            ]
        )
    
    def _daily_report_generator(self) -> WorkflowTemplate:
        """Daily report generation workflow"""
        return WorkflowTemplate(
            template_id="daily_report_generator",
            name="Daily Report Generator",
            description="Compile data from multiple sources into standardized daily report",
            category=WorkflowCategory.REPORTING,
            difficulty=DifficultyLevel.ADVANCED,
            time_saved_minutes=45,
            estimated_value_dollars=37.50,
            prerequisites=["Numbers or Excel", "Data sources", "Email access"],
            steps=[
                WorkflowStep(
                    action="open_app",
                    description="Open spreadsheet application",
                    parameters={"app_name": "Numbers", "fallback": "Microsoft Excel"}
                ),
                WorkflowStep(
                    action="create_new",
                    description="Create new document from template",
                    parameters={"template": "Daily Report", "hotkey": "cmd+n"}
                ),
                WorkflowStep(
                    action="populate_date",
                    description="Insert today's date",
                    parameters={"format": "today", "cell": "A1"}
                ),
                WorkflowStep(
                    action="gather_metrics",
                    description="Collect data from various sources",
                    parameters={"sources": ["Excel files", "Web dashboards", "Email metrics"]},
                    user_confirmation=True
                ),
                WorkflowStep(
                    action="format_report",
                    description="Apply business formatting",
                    parameters={"style": "professional", "charts": True}
                ),
                WorkflowStep(
                    action="save_and_email",
                    description="Save report and email to team",
                    parameters={"save_path": "Reports/Daily", "recipients": "{{team_email}}"},
                    user_confirmation=True
                )
            ]
        )
    
    def _file_organizer(self) -> WorkflowTemplate:
        """File organization workflow"""
        return WorkflowTemplate(
            template_id="file_organizer",
            name="Smart File Organizer",
            description="Automatically organize files by type, date, or project",
            category=WorkflowCategory.FILE_MANAGEMENT,
            difficulty=DifficultyLevel.MEDIUM,
            time_saved_minutes=20,
            estimated_value_dollars=16.67,
            prerequisites=["Finder access", "File organization rules"],
            steps=[
                WorkflowStep(
                    action="open_folder",
                    description="Open source folder",
                    parameters={"path": "{{source_folder}}", "app": "Finder"}
                ),
                WorkflowStep(
                    action="scan_files",
                    description="Analyze file types and names",
                    parameters={"criteria": ["extension", "date", "name_pattern"]}
                ),
                WorkflowStep(
                    action="create_folders",
                    description="Create organization structure",
                    parameters={"structure": "{{folder_structure}}"}
                ),
                WorkflowStep(
                    action="move_files",
                    description="Move files to appropriate folders",
                    parameters={"confirm_each": False, "backup": True}
                ),
                WorkflowStep(
                    action="cleanup",
                    description="Remove empty folders and duplicates",
                    parameters={"safe_mode": True}
                )
            ]
        )
    
    def _invoice_processor(self) -> WorkflowTemplate:
        """Invoice processing workflow"""
        return WorkflowTemplate(
            template_id="invoice_processor",
            name="Invoice Processing Automation",
            description="Extract invoice data and update accounting system",
            category=WorkflowCategory.DATA_ENTRY,
            difficulty=DifficultyLevel.ADVANCED,
            time_saved_minutes=25,
            estimated_value_dollars=20.83,
            prerequisites=["PDF viewer", "Accounting software", "OCR capability"],
            steps=[
                WorkflowStep(
                    action="open_invoice",
                    description="Open PDF invoice",
                    parameters={"file_path": "{{invoice_path}}", "app": "Preview"}
                ),
                WorkflowStep(
                    action="extract_data",
                    description="Extract key invoice data using OCR",
                    parameters={"fields": ["amount", "date", "vendor", "invoice_number"]}
                ),
                WorkflowStep(
                    action="open_accounting",
                    description="Open accounting software",
                    parameters={"app_name": "{{accounting_app}}"}
                ),
                WorkflowStep(
                    action="create_entry",
                    description="Create new accounting entry",
                    parameters={"entry_type": "expense", "hotkey": "cmd+n"}
                ),
                WorkflowStep(
                    action="fill_fields",
                    description="Fill extracted data into accounting fields",
                    parameters={"mapping": "{{field_mapping}}", "validate": True}
                ),
                WorkflowStep(
                    action="save_entry",
                    description="Save accounting entry",
                    parameters={"hotkey": "cmd+s", "confirm": True},
                    user_confirmation=True
                )
            ]
        )
    
    def _crm_data_entry(self) -> WorkflowTemplate:
        """CRM data entry workflow"""
        return WorkflowTemplate(
            template_id="crm_data_entry",
            name="CRM Contact Entry",
            description="Add new contacts to CRM from business cards or forms",
            category=WorkflowCategory.DATA_ENTRY,
            difficulty=DifficultyLevel.MEDIUM,
            time_saved_minutes=12,
            estimated_value_dollars=10.00,
            prerequisites=["CRM software", "Contact data source"],
            steps=[
                WorkflowStep(
                    action="open_crm",
                    description="Open CRM application",
                    parameters={"app_name": "{{crm_app}}", "url": "{{crm_url}}"}
                ),
                WorkflowStep(
                    action="new_contact",
                    description="Create new contact entry",
                    parameters={"button_text": "New Contact", "hotkey": "cmd+n"}
                ),
                WorkflowStep(
                    action="fill_contact_info",
                    description="Fill contact information",
                    parameters={
                        "fields": {
                            "name": "{{contact_name}}",
                            "company": "{{company}}",
                            "email": "{{email}}",
                            "phone": "{{phone}}"
                        }
                    }
                ),
                WorkflowStep(
                    action="save_contact",
                    description="Save new contact",
                    parameters={"hotkey": "cmd+s", "confirm_dialog": True}
                )
            ]
        )
    
    def _meeting_scheduler(self) -> WorkflowTemplate:
        """Meeting scheduling workflow"""
        return WorkflowTemplate(
            template_id="meeting_scheduler",
            name="Smart Meeting Scheduler",
            description="Create calendar events and send invitations",
            category=WorkflowCategory.COMMUNICATION,
            difficulty=DifficultyLevel.MEDIUM,
            time_saved_minutes=8,
            estimated_value_dollars=6.67,
            prerequisites=["Calendar app", "Contact list"],
            steps=[
                WorkflowStep(
                    action="open_calendar",
                    description="Open Calendar application",
                    parameters={"app_name": "Calendar"}
                ),
                WorkflowStep(
                    action="new_event",
                    description="Create new calendar event",
                    parameters={"hotkey": "cmd+n", "view": "week"}
                ),
                WorkflowStep(
                    action="set_details",
                    description="Set meeting details",
                    parameters={
                        "title": "{{meeting_title}}",
                        "date": "{{meeting_date}}",
                        "time": "{{meeting_time}}",
                        "duration": "{{duration}}"
                    }
                ),
                WorkflowStep(
                    action="add_attendees",
                    description="Add meeting attendees",
                    parameters={"attendees": "{{attendee_list}}", "required": True}
                ),
                WorkflowStep(
                    action="send_invitations",
                    description="Send calendar invitations",
                    parameters={"include_agenda": True, "request_response": True}
                )
            ]
        )
    
    def _backup_creator(self) -> WorkflowTemplate:
        """Backup creation workflow"""
        return WorkflowTemplate(
            template_id="backup_creator",
            name="Automated Backup Creator",
            description="Create backups of important files and folders",
            category=WorkflowCategory.FILE_MANAGEMENT,
            difficulty=DifficultyLevel.EASY,
            time_saved_minutes=30,
            estimated_value_dollars=25.00,
            prerequisites=["External drive or cloud storage", "Important files identified"],
            steps=[
                WorkflowStep(
                    action="check_storage",
                    description="Verify backup destination is available",
                    parameters={"destination": "{{backup_path}}", "min_space": "1GB"}
                ),
                WorkflowStep(
                    action="create_backup_folder",
                    description="Create dated backup folder",
                    parameters={"name_format": "Backup_{{date}}", "path": "{{backup_path}}"}
                ),
                WorkflowStep(
                    action="copy_files",
                    description="Copy important files to backup",
                    parameters={
                        "sources": "{{source_folders}}",
                        "preserve_structure": True,
                        "verify_copy": True
                    }
                ),
                WorkflowStep(
                    action="compress_backup",
                    description="Compress backup for storage efficiency",
                    parameters={"format": "zip", "compression": "standard"}
                ),
                WorkflowStep(
                    action="verify_backup",
                    description="Verify backup integrity",
                    parameters={"test_random_files": 5, "checksum": True}
                )
            ]
        )
    
    def _quality_checker(self) -> WorkflowTemplate:
        """Quality assurance workflow"""
        return WorkflowTemplate(
            template_id="quality_checker",
            name="Document Quality Checker",
            description="Check documents for common errors and formatting issues",
            category=WorkflowCategory.QUALITY_ASSURANCE,
            difficulty=DifficultyLevel.MEDIUM,
            time_saved_minutes=15,
            estimated_value_dollars=12.50,
            prerequisites=["Document to check", "Quality standards defined"],
            steps=[
                WorkflowStep(
                    action="open_document",
                    description="Open document for review",
                    parameters={"file_path": "{{document_path}}", "app": "auto_detect"}
                ),
                WorkflowStep(
                    action="spell_check",
                    description="Run spell check",
                    parameters={"auto_correct": False, "highlight_errors": True}
                ),
                WorkflowStep(
                    action="grammar_check",
                    description="Check grammar and style",
                    parameters={"style_guide": "{{style_guide}}", "suggestions": True}
                ),
                WorkflowStep(
                    action="format_check",
                    description="Verify formatting consistency",
                    parameters={"check_headers": True, "check_fonts": True, "check_spacing": True}
                ),
                WorkflowStep(
                    action="generate_report",
                    description="Generate quality report",
                    parameters={"include_suggestions": True, "save_report": True}
                )
            ]
        )
    
    def _social_media_poster(self) -> WorkflowTemplate:
        """Social media posting workflow"""
        return WorkflowTemplate(
            template_id="social_media_poster",
            name="Social Media Post Scheduler",
            description="Create and schedule social media posts across platforms",
            category=WorkflowCategory.COMMUNICATION,
            difficulty=DifficultyLevel.MEDIUM,
            time_saved_minutes=18,
            estimated_value_dollars=15.00,
            prerequisites=["Social media accounts", "Content prepared"],
            steps=[
                WorkflowStep(
                    action="prepare_content",
                    description="Prepare post content and images",
                    parameters={"text": "{{post_text}}", "images": "{{image_paths}}"},
                    user_confirmation=True
                ),
                WorkflowStep(
                    action="open_platform",
                    description="Open first social media platform",
                    parameters={"platform": "{{platform_1}}", "url": "{{platform_1_url}}"}
                ),
                WorkflowStep(
                    action="create_post",
                    description="Create post on platform",
                    parameters={"post_type": "{{post_type}}", "schedule": "{{schedule_time}}"}
                ),
                WorkflowStep(
                    action="add_content",
                    description="Add text and media content",
                    parameters={"text": "{{post_text}}", "media": "{{image_paths}}"}
                ),
                WorkflowStep(
                    action="schedule_post",
                    description="Schedule or publish post",
                    parameters={"action": "{{publish_or_schedule}}", "time": "{{schedule_time}}"}
                )
            ]
        )
    
    def export_templates(self, file_path: str):
        """Export all templates to JSON file"""
        template_data = {}
        for template_id, template in self.templates.items():
            template_data[template_id] = asdict(template)
        
        with open(file_path, 'w') as f:
            json.dump(template_data, f, indent=2, default=str)
        
        print(f"Templates exported to {file_path}")
    
    def generate_business_report(self) -> Dict[str, Any]:
        """Generate business impact report for all templates"""
        total_templates = len(self.templates)
        total_time_savings = sum(t.time_saved_minutes for t in self.templates.values())
        total_value = sum(t.estimated_value_dollars for t in self.templates.values())
        
        # Category breakdown
        category_stats = {}
        for category in WorkflowCategory:
            category_templates = self.get_by_category(category)
            category_stats[category.value] = {
                "template_count": len(category_templates),
                "total_time_saved": sum(t.time_saved_minutes for t in category_templates),
                "total_value": sum(t.estimated_value_dollars for t in category_templates)
            }
        
        # Difficulty breakdown
        difficulty_stats = {}
        for difficulty in DifficultyLevel:
            difficulty_templates = self.get_by_difficulty(difficulty)
            difficulty_stats[difficulty.value] = {
                "template_count": len(difficulty_templates),
                "avg_time_saved": sum(t.time_saved_minutes for t in difficulty_templates) / max(len(difficulty_templates), 1),
                "avg_value": sum(t.estimated_value_dollars for t in difficulty_templates) / max(len(difficulty_templates), 1)
            }
        
        # Business projections
        daily_usage_per_template = 2  # Assumption: each template used 2x per day
        daily_value = total_value * daily_usage_per_template
        monthly_value = daily_value * 22  # 22 workdays
        annual_value = monthly_value * 12
        
        return {
            "summary": {
                "total_templates": total_templates,
                "total_time_saved_per_execution": total_time_savings,
                "total_value_per_execution": total_value,
                "daily_projected_value": daily_value,
                "monthly_projected_value": monthly_value,
                "annual_projected_value": annual_value
            },
            "category_breakdown": category_stats,
            "difficulty_breakdown": difficulty_stats,
            "roi_analysis": {
                "macagent_monthly_cost": 49,
                "monthly_roi_multiple": monthly_value / 49,
                "payback_period_days": 49 / (daily_value / 30),
                "annual_net_benefit": annual_value - (49 * 12)
            }
        }

def demo_template_library():
    """Demonstrate the template library capabilities"""
    print("🤖 MacAgent Workflow Template Library")
    print("=" * 45)
    print("📚 Pre-built automation templates for immediate business value\n")
    
    library = TemplateLibrary()
    
    # Show all templates
    templates = library.get_all_templates()
    print(f"📋 Available Templates ({len(templates)} total):\n")
    
    total_time_saved = 0
    total_value = 0
    
    for i, template in enumerate(templates, 1):
        print(f"{i:2}. {template.name}")
        print(f"    💰 Saves: {template.time_saved_minutes} min (${template.estimated_value_dollars:.2f})")
        print(f"    📝 {template.description}")
        print(f"    🏷️  {template.category.value} | {template.difficulty.value}")
        print(f"    📊 Success Rate: {template.success_rate:.1f}%")
        print(f"    🔧 Prerequisites: {', '.join(template.prerequisites)}")
        print()
        
        total_time_saved += template.time_saved_minutes
        total_value += template.estimated_value_dollars
    
    # Business impact summary
    print("📊 BUSINESS IMPACT ANALYSIS:")
    print("=" * 30)
    print(f"📈 Total time savings per full cycle: {total_time_saved} minutes ({total_time_saved/60:.1f} hours)")
    print(f"💵 Total value per full cycle: ${total_value:.2f}")
    print(f"📅 Daily value (2x usage): ${total_value * 2:.2f}")
    print(f"📅 Monthly value (22 workdays): ${total_value * 2 * 22:.2f}")
    print(f"💳 MacAgent monthly cost: $49")
    print(f"📈 Monthly ROI: {(total_value * 2 * 22) / 49:.1f}x")
    
    # Show high-value templates
    print("\n🌟 HIGH-VALUE TEMPLATES (>$15 each):")
    print("=" * 40)
    high_value = library.get_high_value_templates(15.0)
    for template in high_value:
        print(f"💎 {template.name}: {template.time_saved_minutes} min = ${template.estimated_value_dollars:.2f}")
    
    # Category breakdown
    print("\n📊 BY CATEGORY:")
    print("=" * 20)
    for category in WorkflowCategory:
        category_templates = library.get_by_category(category)
        if category_templates:
            category_value = sum(t.estimated_value_dollars for t in category_templates)
            print(f"{category.value}: {len(category_templates)} templates, ${category_value:.2f} value")
    
    # Generate and save business report
    report = library.generate_business_report()
    
    # Export templates
    library.export_templates("macagent_templates.json")
    
    # Save business report
    with open("template_business_report.json", 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n💾 Files created:")
    print("   • macagent_templates.json (template definitions)")
    print("   • template_business_report.json (business analysis)")
    
    print("\n🚀 NEXT STEPS:")
    print("1. Choose 2-3 templates that match your daily work")
    print("2. Test each template with real data")
    print("3. Measure actual time savings and ROI")
    print("4. Scale successful templates across your team")
    
    return library

if __name__ == "__main__":
    demo_template_library()