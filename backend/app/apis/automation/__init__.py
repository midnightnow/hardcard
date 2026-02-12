from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import databutton as db
import json
from datetime import datetime

router = APIRouter()

class NotificationSettings(BaseModel):
    """Notification settings for the system"""
    enabled: bool
    recipients: List[str]
    low_stock_threshold: str  # all, critical, none

class AutomationRule(BaseModel):
    """Automation rule definition"""
    id: str
    name: str
    description: str
    category: str
    enabled: bool
    conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    priority: str
    createdAt: str
    lastModified: str

class AutomationRuleRequest(BaseModel):
    """Request model for creating/updating automation rules"""
    name: str
    description: str
    category: str
    enabled: bool
    conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    priority: str

class AutomationTask(BaseModel):
    """Automation task model"""
    id: str
    title: str
    description: str
    status: str
    category: str
    source: str
    createdAt: str
    priority: str
    suggestedAction: str
    autoMatchConfidence: int
    relatedRules: List[str]
    metadata: Optional[Dict[str, Any]]

class BasicResponse(BaseModel):
    """Basic response model"""
    success: bool
    message: str

# Storage keys
NOTIFICATION_SETTINGS_KEY = "notification_settings"
AUTOMATION_RULES_KEY = "automation_rules"
AUTOMATION_TASKS_KEY = "automation_tasks"

# Helper function for storage keys
def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    import re
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

# Notification Settings Endpoints
@router.get("/automation-notification-settings")
async def get_automation_notification_settings() -> Dict[str, Any]:
    """Get all notification settings"""
    try:
        try:
            settings = db.storage.json.get(sanitize_storage_key(NOTIFICATION_SETTINGS_KEY))
        except FileNotFoundError:
            # Default settings
            settings = {
                "inventory_notifications": {
                    "enabled": True,
                    "recipients": ["inventory@hempex.com"],
                    "low_stock_threshold": "all"  # all, critical, none
                }
            }
            db.storage.json.put(sanitize_storage_key(NOTIFICATION_SETTINGS_KEY), settings)
        
        return settings
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving notification settings: {str(e)}"
        )

@router.put("/automation-notification-settings/{category}")
async def update_automation_notification_settings(
    category: str,
    settings: NotificationSettings
) -> BasicResponse:
    """Update notification settings for a specific category"""
    try:
        # Validate category
        valid_categories = ["inventory_notifications", "order_notifications", "system_notifications"]
        if category not in valid_categories:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category. Valid options are: {', '.join(valid_categories)}"
            )
            
        # Get current settings
        try:
            current_settings = db.storage.json.get(sanitize_storage_key(NOTIFICATION_SETTINGS_KEY))
        except FileNotFoundError:
            current_settings = {}
        
        # Update settings for the specified category
        current_settings[category] = settings.dict()
        
        # Save updated settings
        db.storage.json.put(sanitize_storage_key(NOTIFICATION_SETTINGS_KEY), current_settings)
        
        return BasicResponse(
            success=True,
            message=f"Successfully updated {category} notification settings"
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500, 
            detail=f"Error updating notification settings: {str(e)}"
        )

# Automation Rules Endpoints
@router.get("/rules")
async def get_automation_rules(category: Optional[str] = None) -> List[AutomationRule]:
    """Get all automation rules or filter by category"""
    try:
        try:
            rules = db.storage.json.get(sanitize_storage_key(AUTOMATION_RULES_KEY))
        except FileNotFoundError:
            rules = []
        
        # Filter by category if provided
        if category:
            rules = [rule for rule in rules if rule.get("category") == category]
            
        return rules
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving automation rules: {str(e)}"
        )

@router.post("/rules")
async def create_automation_rule(rule: AutomationRuleRequest) -> AutomationRule:
    """Create a new automation rule"""
    try:
        # Get existing rules
        try:
            rules = db.storage.json.get(sanitize_storage_key(AUTOMATION_RULES_KEY))
        except FileNotFoundError:
            rules = []
        
        # Create new rule with generated ID
        import uuid
        rule_id = f"R-{rule.category.upper()}-{str(uuid.uuid4())[:8]}"
        
        # Set timestamps
        now = datetime.utcnow().isoformat()
        
        # Create complete rule
        new_rule = {
            "id": rule_id,
            "name": rule.name,
            "description": rule.description,
            "category": rule.category,
            "enabled": rule.enabled,
            "conditions": rule.conditions,
            "actions": rule.actions,
            "priority": rule.priority,
            "createdAt": now,
            "lastModified": now
        }
        
        # Add to rules list
        rules.append(new_rule)
        
        # Save updated rules
        db.storage.json.put(sanitize_storage_key(AUTOMATION_RULES_KEY), rules)
        
        return new_rule
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error creating automation rule: {str(e)}"
        )

@router.put("/rules/{rule_id}")
async def update_automation_rule(rule_id: str, rule: AutomationRuleRequest) -> AutomationRule:
    """Update an existing automation rule"""
    try:
        # Get existing rules
        try:
            rules = db.storage.json.get(sanitize_storage_key(AUTOMATION_RULES_KEY))
        except FileNotFoundError:
            raise HTTPException(
                status_code=404,
                detail=f"Rule with ID {rule_id} not found"
            )
        
        # Find the rule
        rule_index = None
        for i, r in enumerate(rules):
            if r.get("id") == rule_id:
                rule_index = i
                break
                
        if rule_index is None:
            raise HTTPException(
                status_code=404,
                detail=f"Rule with ID {rule_id} not found"
            )
            
        # Update the rule
        now = datetime.utcnow().isoformat()
        
        updated_rule = {
            "id": rule_id,
            "name": rule.name,
            "description": rule.description,
            "category": rule.category,
            "enabled": rule.enabled,
            "conditions": rule.conditions,
            "actions": rule.actions,
            "priority": rule.priority,
            "createdAt": rules[rule_index].get("createdAt"),
            "lastModified": now
        }
        
        # Replace in list
        rules[rule_index] = updated_rule
        
        # Save updated rules
        db.storage.json.put(sanitize_storage_key(AUTOMATION_RULES_KEY), rules)
        
        return updated_rule
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500, 
            detail=f"Error updating automation rule: {str(e)}"
        )

@router.delete("/rules/{rule_id}")
async def delete_automation_rule(rule_id: str) -> BasicResponse:
    """Delete an automation rule"""
    try:
        # Get existing rules
        try:
            rules = db.storage.json.get(sanitize_storage_key(AUTOMATION_RULES_KEY))
        except FileNotFoundError:
            raise HTTPException(
                status_code=404,
                detail=f"Rule with ID {rule_id} not found"
            )
        
        # Find the rule
        rule_index = None
        for i, r in enumerate(rules):
            if r.get("id") == rule_id:
                rule_index = i
                break
                
        if rule_index is None:
            raise HTTPException(
                status_code=404,
                detail=f"Rule with ID {rule_id} not found"
            )
            
        # Remove from list
        rules.pop(rule_index)
        
        # Save updated rules
        db.storage.json.put(sanitize_storage_key(AUTOMATION_RULES_KEY), rules)
        
        return BasicResponse(
            success=True,
            message=f"Successfully deleted rule {rule_id}"
        )
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500, 
            detail=f"Error deleting automation rule: {str(e)}"
        )

# Automation Tasks Endpoints
@router.get("/tasks")
async def get_automation_tasks(
    category: Optional[str] = None,
    status: Optional[str] = None
) -> List[AutomationTask]:
    """Get all automation tasks with optional filtering"""
    try:
        try:
            tasks = db.storage.json.get(sanitize_storage_key(AUTOMATION_TASKS_KEY))
        except FileNotFoundError:
            tasks = []
        
        # Apply filters
        if category:
            tasks = [task for task in tasks if task.get("category") == category]
            
        if status:
            tasks = [task for task in tasks if task.get("status") == status]
            
        return tasks
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving automation tasks: {str(e)}"
        )

@router.get("/tasks/{task_id}")
async def get_automation_task(task_id: str) -> AutomationTask:
    """Get a specific automation task by ID"""
    try:
        try:
            tasks = db.storage.json.get(sanitize_storage_key(AUTOMATION_TASKS_KEY))
        except FileNotFoundError:
            raise HTTPException(
                status_code=404,
                detail=f"Task with ID {task_id} not found"
            )
        
        # Find the task
        task = None
        for t in tasks:
            if t.get("id") == task_id:
                task = t
                break
                
        if task is None:
            raise HTTPException(
                status_code=404,
                detail=f"Task with ID {task_id} not found"
            )
            
        return task
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving task: {str(e)}"
        )

@router.put("/tasks/{task_id}/status")
async def update_task_status(
    task_id: str, 
    status: str = Body(..., embed=True)
) -> AutomationTask:
    """Update the status of an automation task"""
    try:
        # Validate status
        valid_statuses = ["pending", "in_progress", "completed", "cancelled"]
        if status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Valid options are: {', '.join(valid_statuses)}"
            )
        
        # Get tasks
        try:
            tasks = db.storage.json.get(sanitize_storage_key(AUTOMATION_TASKS_KEY))
        except FileNotFoundError:
            raise HTTPException(
                status_code=404,
                detail=f"Task with ID {task_id} not found"
            )
        
        # Find the task
        task_index = None
        for i, t in enumerate(tasks):
            if t.get("id") == task_id:
                task_index = i
                break
                
        if task_index is None:
            raise HTTPException(
                status_code=404,
                detail=f"Task with ID {task_id} not found"
            )
            
        # Update status
        tasks[task_index]["status"] = status
        
        # If completing a task and it's an inventory alert, also resolve the alert
        if status == "completed" and tasks[task_index].get("category") == "inventory":
            if "metadata" in tasks[task_index] and "alert_id" in tasks[task_index]["metadata"]:
                alert_id = tasks[task_index]["metadata"]["alert_id"]
                try:
                    from app.apis.inventory import resolve_inventory_alert
                    resolve_inventory_alert(alert_id, "Resolved via automation task")
                except Exception as alert_error:
                    print(f"Error resolving inventory alert: {alert_error}")
        
        # Save updated tasks
        db.storage.json.put(sanitize_storage_key(AUTOMATION_TASKS_KEY), tasks)
        
        return tasks[task_index]
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=500, 
            detail=f"Error updating task status: {str(e)}"
        )

# Generate automation rule templates
@router.get("/rule-templates")
async def get_rule_templates() -> List[Dict[str, Any]]:
    """Get a list of rule templates"""
    templates = [
        {
            "id": "tpl-inv-low-stock",
            "name": "Low Stock Alert",
            "description": "Create a task when inventory falls below threshold",
            "category": "inventory",
            "template": {
                "name": "Low Stock Alert",
                "description": "Automatically create tasks when inventory falls below threshold",
                "category": "inventory",
                "enabled": True,
                "conditions": {
                    "type": "inventory",
                    "operator": "below_threshold",
                    "threshold": 5
                },
                "actions": [
                    {
                        "type": "create_task",
                        "priority": "medium"
                    },
                    {
                        "type": "send_notification",
                        "recipients": ["inventory@hempex.com"]
                    }
                ],
                "priority": "medium"
            }
        },
        {
            "id": "tpl-inv-out-of-stock",
            "name": "Out of Stock Alert",
            "description": "Create a high priority task when product goes out of stock",
            "category": "inventory",
            "template": {
                "name": "Out of Stock Alert",
                "description": "Automatically create high priority tasks when a product is out of stock",
                "category": "inventory",
                "enabled": True,
                "conditions": {
                    "type": "inventory",
                    "operator": "equals",
                    "value": 0
                },
                "actions": [
                    {
                        "type": "create_task",
                        "priority": "high"
                    },
                    {
                        "type": "send_notification",
                        "recipients": ["inventory@hempex.com", "management@hempex.com"]
                    }
                ],
                "priority": "high"
            }
        },
        {
            "id": "tpl-inv-expiring",
            "name": "Expiring Batch Alert",
            "description": "Create a task when product batches are approaching expiration",
            "category": "inventory",
            "template": {
                "name": "Expiring Batch Alert",
                "description": "Automatically create tasks when product batches are approaching expiration",
                "category": "inventory",
                "enabled": True,
                "conditions": {
                    "type": "batch",
                    "operator": "expiring_within",
                    "days": 30
                },
                "actions": [
                    {
                        "type": "create_task",
                        "priority": "medium"
                    },
                    {
                        "type": "send_notification",
                        "recipients": ["inventory@hempex.com"]
                    }
                ],
                "priority": "medium"
            }
        },
        {
            "id": "tpl-inv-auto-reorder",
            "name": "Automatic Reorder",
            "description": "Automatically create a purchase order when stock is low",
            "category": "inventory",
            "template": {
                "name": "Automatic Reorder",
                "description": "Automatically create a purchase order when stock falls below threshold",
                "category": "inventory",
                "enabled": True,
                "conditions": {
                    "type": "inventory",
                    "operator": "below_threshold",
                    "threshold": 10,
                    "products": ["all"]
                },
                "actions": [
                    {
                        "type": "create_purchase_order",
                        "supplier": "preferred",
                        "quantity": "reorder_amount"
                    },
                    {
                        "type": "send_notification",
                        "recipients": ["purchasing@hempex.com"]
                    }
                ],
                "priority": "high"
            }
        }
    ]
    
    return templates
