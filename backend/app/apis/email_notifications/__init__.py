from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import databutton as db
from typing import Optional, List
from app.apis.firebase import get_user_data
import json

router = APIRouter()

class EmailNotificationRequest(BaseModel):
    user_id: str
    email: Optional[EmailStr] = None
    subject: str
    template_name: str
    template_data: dict

class EmailNotificationResponse(BaseModel):
    success: bool
    message: str

# Define email templates
EMAIL_TEMPLATES = {
    "hardcard_purchase": {
        "subject": "Your Hardcard Level Purchase Confirmation",
        "html": """
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #111111; color: #e0e0e0; border-radius: 8px; border: 1px solid #333;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #f59e0b; margin-bottom: 10px;">Purchase Confirmation</h1>
                <p style="font-size: 18px; color: #cccccc;">Thank you for upgrading your Hardcard</p>
            </div>
            
            <div style="background-color: #1a1a1a; padding: 20px; border-radius: 6px; margin-bottom: 20px; border: 1px solid #333;">
                <h2 style="color: #f59e0b; margin-top: 0;">Level {{level}} Unlocked: {{title}}</h2>
                <p>{{description}}</p>
                
                <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #333;">
                    <p><strong>Level Benefits:</strong></p>
                    <ul style="padding-left: 20px;">
                        {% for feature in features %}
                        <li style="margin-bottom: 8px;">{{feature}}</li>
                        {% endfor %}
                    </ul>
                </div>
            </div>
            
            <div style="background-color: #1a1a1a; padding: 15px; border-radius: 6px; margin-bottom: 20px; display: flex; justify-content: space-between; border: 1px solid #333;">
                <div>
                    <p style="margin: 0; color: #999;">XP Awarded</p>
                    <p style="margin: 5px 0 0; font-size: 20px; font-weight: bold; color: #3b82f6;">+{{xp_reward}}</p>
                </div>
                <div>
                    <p style="margin: 0; color: #999;">Vault Points</p>
                    <p style="margin: 5px 0 0; font-size: 20px; font-weight: bold; color: #8b5cf6;">+{{points_reward}}</p>
                </div>
            </div>
            
            {% if lore_fragments %}
            <div style="background-color: #1a1a1a; padding: 15px; border-radius: 6px; margin-bottom: 20px; border: 1px solid #333;">
                <h3 style="color: #f59e0b; margin-top: 0;">New Lore Unlocked</h3>
                <p>Your new Hardcard level has unlocked exclusive knowledge about the Vault system. Log in to view these revelations.</p>
            </div>
            {% endif %}
            
            <div style="text-align: center; margin-top: 30px;">
                <a href="{{dashboard_url}}" style="display: inline-block; background-color: #f59e0b; color: #000000; padding: 12px 25px; text-decoration: none; border-radius: 4px; font-weight: bold;">View Your Dashboard</a>
            </div>
            
            <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #333; text-align: center; font-size: 12px; color: #666;">
                <p>This is an automated message from Legacy Vault. Please do not reply to this email.</p>
                <p>© {{current_year}} Legacy Vault. All rights reserved.</p>
            </div>
        </div>
        """,
        "text": """
        Purchase Confirmation - Thank you for upgrading your Hardcard
        
        Level {{level}} Unlocked: {{title}}
        {{description}}
        
        Level Benefits:
        {% for feature in features %}
        - {{feature}}
        {% endfor %}
        
        XP Awarded: +{{xp_reward}}
        Vault Points: +{{points_reward}}
        
        {% if lore_fragments %}
        New Lore Unlocked
        Your new Hardcard level has unlocked exclusive knowledge about the Vault system. Log in to view these revelations.
        {% endif %}
        
        View Your Dashboard: {{dashboard_url}}
        
        This is an automated message from Legacy Vault. Please do not reply to this email.
        © {{current_year}} Legacy Vault. All rights reserved.
        """
    },
    "lore_unlocked": {
        "subject": "New Legacy Vault Lore Unlocked",
        "html": """
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #111111; color: #e0e0e0; border-radius: 8px; border: 1px solid #333;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #f59e0b; margin-bottom: 10px;">New Lore Unlocked</h1>
                <p style="font-size: 18px; color: #cccccc;">You've discovered hidden knowledge</p>
            </div>
            
            <div style="background-color: #1a1a1a; padding: 20px; border-radius: 6px; margin-bottom: 20px; border: 1px solid #333;">
                <h2 style="color: #f59e0b; margin-top: 0;">{{lore_title}}</h2>
                <p style="font-style: italic; color: #999;">From the Level {{level}} Archives</p>
                <p>{{lore_preview}}...</p>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <a href="{{lore_url}}" style="display: inline-block; background-color: #f59e0b; color: #000000; padding: 12px 25px; text-decoration: none; border-radius: 4px; font-weight: bold;">Read Full Chronicle</a>
            </div>
            
            <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #333; text-align: center; font-size: 12px; color: #666;">
                <p>This is an automated message from Legacy Vault. Please do not reply to this email.</p>
                <p>© {{current_year}} Legacy Vault. All rights reserved.</p>
            </div>
        </div>
        """,
        "text": """
        New Lore Unlocked - You've discovered hidden knowledge
        
        {{lore_title}}
        From the Level {{level}} Archives
        
        {{lore_preview}}...
        
        Read Full Chronicle: {{lore_url}}
        
        This is an automated message from Legacy Vault. Please do not reply to this email.
        © {{current_year}} Legacy Vault. All rights reserved.
        """
    }
}

# Render a template with data
def render_template(template_str, data):
    """
    Render a template with data
    
    This function renders a simple template with variable substitution.
    It's a basic implementation that handles {{variable}} and {% for item in items %}...{% endfor %}
    
    Args:
        template_str (str): The template string
        data (dict): The data to render the template with
        
    Returns:
        str: The rendered template
    """
    rendered = template_str
    
    # Handle for loops
    # Very basic implementation that only handles single-level for loops
    for_start = rendered.find('{% for ')
    while for_start != -1:
        for_end = rendered.find('{% endfor %}', for_start)
        if for_end == -1:
            break
            
        # Extract the for loop syntax
        for_syntax = rendered[for_start + 8:rendered.find('%}', for_start)]
        item_var, collection_var = [x.strip() for x in for_syntax.split(' in ')]
        
        # Extract the loop content
        loop_content = rendered[rendered.find('%}', for_start) + 2:for_end]
        
        # Generate the rendered content
        items = data.get(collection_var, [])
        rendered_items = ''
        for item in items:
            item_content = loop_content
            item_content = item_content.replace('{{' + item_var + '}}', str(item))
            rendered_items += item_content
            
        # Replace the for loop with rendered content
        rendered = rendered[:for_start] + rendered_items + rendered[for_end + 12:]
        
        # Find next for loop
        for_start = rendered.find('{% for ')
    
    # Handle if conditions (very basic implementation)
    if_start = rendered.find('{% if ')
    while if_start != -1:
        if_end = rendered.find('{% endif %}', if_start)
        if if_end == -1:
            break
            
        # Extract the if condition
        if_cond = rendered[if_start + 6:rendered.find(' %}', if_start)]
        
        # Extract the if content
        if_content = rendered[rendered.find(' %}', if_start) + 3:if_end]
        
        # Check if condition is true
        condition_value = data.get(if_cond, False)
        
        # Replace the if block with content or empty string
        if condition_value:
            rendered = rendered[:if_start] + if_content + rendered[if_end + 10:]
        else:
            rendered = rendered[:if_start] + rendered[if_end + 10:]
            
        # Find next if statement
        if_start = rendered.find('{% if ')
    
    # Handle variables
    var_start = rendered.find('{{')
    while var_start != -1:
        var_end = rendered.find('}}', var_start)
        if var_end == -1:
            break
            
        var_name = rendered[var_start + 2:var_end].strip()
        var_value = str(data.get(var_name, ''))
        
        rendered = rendered[:var_start] + var_value + rendered[var_end + 2:]
        var_start = rendered.find('{{')
        
    return rendered

def send_email_notification(to_email, subject, content_html, content_text):
    """
    Send an email notification using the Databutton email service
    
    Args:
        to_email (str): The recipient's email address
        subject (str): The email subject
        content_html (str): The HTML content of the email
        content_text (str): The text content of the email
        
    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    try:
        db.notify.email(
            to=to_email,
            subject=subject,
            content_html=content_html,
            content_text=content_text,
        )
        return True
    except Exception as e:
        print(f"Error sending email notification: {str(e)}")
        return False

@router.post("/send-notification")
def send_email_notification_endpoint(request: EmailNotificationRequest) -> EmailNotificationResponse:
    """
    Send an email notification based on a template
    
    This endpoint sends an email notification based on a template,
    with the template data provided in the request.
    """
    # Get email template
    template = EMAIL_TEMPLATES.get(request.template_name)
    if not template:
        raise HTTPException(status_code=400, detail=f"Template '{request.template_name}' not found")
    
    # Determine email subject - either custom or from template
    subject = request.subject if request.subject else template["subject"]
    
    # Get user email if not provided in request
    to_email = request.email
    if not to_email:
        # Get user data from Firebase
        user_data = get_user_data(request.user_id)
        to_email = user_data.get("email")
        
        if not to_email:
            raise HTTPException(status_code=400, detail="No email address provided or found for user")
    
    # Render email content with template data
    content_html = render_template(template["html"], request.template_data)
    content_text = render_template(template["text"], request.template_data)
    
    # Send email notification
    success = send_email_notification(to_email, subject, content_html, content_text)
    
    if success:
        return EmailNotificationResponse(
            success=True,
            message=f"Email notification sent to {to_email}"
        )
    else:
        return EmailNotificationResponse(
            success=False,
            message="Failed to send email notification"
        )
