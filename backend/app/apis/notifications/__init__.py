from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
import databutton as db
from typing import Dict, Any, List, Optional
import json
import re
from datetime import datetime

router = APIRouter()

class EmailNotification(BaseModel):
    customer_email: str
    subject: str
    content_html: str
    content_text: Optional[str] = None
    template_id: Optional[str] = None
    template_data: Optional[Dict[str, Any]] = None

class OrderNotification(BaseModel):
    order_id: str
    customer_email: str
    notification_type: str  # confirmation, processing, shipped, delivered, cancelled, refunded
    order_data: Dict[str, Any]

class EmailResponse(BaseModel):
    success: bool
    message: str
    email_id: Optional[str] = None

def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

@router.post("/send-email", response_model=EmailResponse)
async def send_email(email_data: EmailNotification):
    """Send an email notification"""
    try:
        # In production, we would connect to an email service provider
        # For now, we'll log the email to storage for testing
        email_log = {
            "to": email_data.customer_email,
            "subject": email_data.subject,
            "html_content": email_data.content_html,
            "text_content": email_data.content_text,
            "template_id": email_data.template_id,
            "template_data": email_data.template_data,
            "sent_at": datetime.now().isoformat()
        }
        
        # Generate a unique ID for this email
        email_id = f"email_{datetime.now().strftime('%Y%m%d%H%M%S')}_{sanitize_storage_key(email_data.customer_email)}"
        
        # Store the email in the email logs
        db.storage.json.put(sanitize_storage_key(email_id), email_log)
        
        # Actually send the email - for the prototype we'll just log it
        # In production, this would call an email service like SendGrid, Mailgun, etc.
        print(f"Email sent to {email_data.customer_email}: {email_data.subject}")
        
        return EmailResponse(
            success=True,
            message=f"Email sent to {email_data.customer_email}",
            email_id=email_id
        )
        
    except Exception as e:
        print(f"Error sending email: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send email: {str(e)}"
        )

@router.post("/send-order-notification", response_model=EmailResponse)
async def send_order_notification(notification: OrderNotification):
    """Send an order-related notification email"""
    try:
        # Format currency for display
        def format_currency(amount):
            return f"${amount / 100:.2f}"
        
        # Get customer name from order data
        customer_name = notification.order_data.get("shipping_address", {}).get("name", "Customer")
        order_id = notification.order_id
        order_total = format_currency(notification.order_data.get("total", 0))
        
        # Determine subject and content based on notification type
        if notification.notification_type == "confirmation":
            subject = f"Order Confirmation - #{order_id}"
            content_html = f"""
            <html>
                <body>
                    <h1>Thank you for your order!</h1>
                    <p>Hello {customer_name},</p>
                    <p>We've received your order #{order_id} and are processing it now.</p>
                    <p>Order Total: {order_total}</p>
                    <p>You can track your order status in your account.</p>
                    <p>Thank you for shopping with Hempex!</p>
                </body>
            </html>
            """
            content_text = f"Thank you for your order! We've received your order #{order_id} and are processing it now. Order Total: {order_total}"
        
        elif notification.notification_type == "processing":
            subject = f"Your Order is Being Processed - #{order_id}"
            content_html = f"""
            <html>
                <body>
                    <h1>Your order is being processed!</h1>
                    <p>Hello {customer_name},</p>
                    <p>We're currently processing your order #{order_id}.</p>
                    <p>We'll send you another notification when your order ships.</p>
                    <p>Thank you for shopping with Hempex!</p>
                </body>
            </html>
            """
            content_text = f"Your order #{order_id} is being processed! We'll send you another notification when your order ships."
        
        elif notification.notification_type == "shipped":
            subject = f"Your Order Has Shipped - #{order_id}"
            tracking_info = ""
            if notification.order_data.get("shipping", {}).get("tracking_number"):
                tracking_number = notification.order_data["shipping"]["tracking_number"]
                carrier = notification.order_data["shipping"].get("carrier", "our shipping partner")
                tracking_url = notification.order_data["shipping"].get("tracking_url", "")
                
                if tracking_url:
                    tracking_info = f"<p>You can track your package with {carrier} using tracking number <a href='{tracking_url}'>{tracking_number}</a>.</p>"
                else:
                    tracking_info = f"<p>You can track your package with {carrier} using tracking number {tracking_number}.</p>"
            
            content_html = f"""
            <html>
                <body>
                    <h1>Your order is on its way!</h1>
                    <p>Hello {customer_name},</p>
                    <p>Great news! Your order #{order_id} has shipped.</p>
                    {tracking_info}
                    <p>Thank you for shopping with Hempex!</p>
                </body>
            </html>
            """
            content_text = f"Your order #{order_id} has shipped! Track your package with the information in your account."
        
        elif notification.notification_type == "delivered":
            subject = f"Your Order Has Been Delivered - #{order_id}"
            content_html = f"""
            <html>
                <body>
                    <h1>Your order has been delivered!</h1>
                    <p>Hello {customer_name},</p>
                    <p>Your order #{order_id} has been delivered.</p>
                    <p>We hope you enjoy your products. If you have any questions or concerns, please contact us.</p>
                    <p>Thank you for shopping with Hempex!</p>
                </body>
            </html>
            """
            content_text = f"Your order #{order_id} has been delivered! We hope you enjoy your products."
        
        elif notification.notification_type == "cancelled":
            subject = f"Your Order Has Been Cancelled - #{order_id}"
            content_html = f"""
            <html>
                <body>
                    <h1>Your order has been cancelled</h1>
                    <p>Hello {customer_name},</p>
                    <p>Your order #{order_id} has been cancelled.</p>
                    <p>If you did not request this cancellation or have any questions, please contact us.</p>
                    <p>Thank you for your interest in Hempex.</p>
                </body>
            </html>
            """
            content_text = f"Your order #{order_id} has been cancelled. If you did not request this cancellation, please contact us."
        
        elif notification.notification_type == "refunded":
            subject = f"Your Order Has Been Refunded - #{order_id}"
            content_html = f"""
            <html>
                <body>
                    <h1>Your order has been refunded</h1>
                    <p>Hello {customer_name},</p>
                    <p>Your order #{order_id} has been refunded. The amount of {order_total} will be credited back to your original payment method.</p>
                    <p>If you have any questions or concerns, please contact us.</p>
                    <p>Thank you for your understanding.</p>
                </body>
            </html>
            """
            content_text = f"Your order #{order_id} has been refunded. The amount of {order_total} will be credited back to your original payment method."
        
        else:
            # Default generic notification
            subject = f"Update on Your Order - #{order_id}"
            content_html = f"""
            <html>
                <body>
                    <h1>Update on your order</h1>
                    <p>Hello {customer_name},</p>
                    <p>There's an update on your order #{order_id}.</p>
                    <p>Please log in to your account to view the details.</p>
                    <p>Thank you for shopping with Hempex!</p>
                </body>
            </html>
            """
            content_text = f"There's an update on your order #{order_id}. Please log in to your account to view the details."
        
        # Create the email notification
        email_notification = EmailNotification(
            customer_email=notification.customer_email,
            subject=subject,
            content_html=content_html,
            content_text=content_text
        )
        
        # Send the email
        response = await send_email(email_notification)
        
        # Log the order notification
        notification_log = {
            "order_id": notification.order_id,
            "notification_type": notification.notification_type,
            "customer_email": notification.customer_email,
            "sent_at": datetime.now().isoformat(),
            "email_id": response.email_id
        }
        
        log_key = f"order_notification_{notification.order_id}_{notification.notification_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        db.storage.json.put(sanitize_storage_key(log_key), notification_log)
        
        return response
        
    except Exception as e:
        print(f"Error sending order notification: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send order notification: {str(e)}"
        )
