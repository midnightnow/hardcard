from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime, timedelta
import databutton as db
import base64
import json
import io
import os
import math
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.units import inch
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Initialize router
router = APIRouter(prefix="/report-generator")

class ReportRequest(BaseModel):
    profile_id: str
    report_type: Literal["monthly", "quarterly", "annual"] = "monthly"
    include_sections: List[str] = Field(
        default=["summary", "portfolio", "bitcoin", "revenue", "projects", "future_plans"],
        description="Sections to include in the report"
    )
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    custom_title: Optional[str] = None
    delivery_email: Optional[str] = None

class ReportResponse(BaseModel):
    success: bool
    report_id: Optional[str] = None
    download_url: Optional[str] = None
    message: Optional[str] = None

class ScheduleReportRequest(BaseModel):
    profile_id: str
    frequency: Literal["weekly", "monthly", "quarterly", "annual"] = "monthly"
    delivery_emails: List[str] = Field(..., min_items=1)
    include_sections: List[str] = Field(
        default=["summary", "portfolio", "bitcoin", "revenue", "projects", "future_plans"],
        description="Sections to include in the report"
    )
    next_delivery_date: Optional[str] = None

class ScheduleReportResponse(BaseModel):
    success: bool
    schedule_id: Optional[str] = None
    next_delivery_date: Optional[str] = None
    message: Optional[str] = None

class ListReportsResponse(BaseModel):
    reports: List[Dict[str, Any]]

def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    import re
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

def get_profile_data(profile_id: str) -> dict:
    """Get profile data from the API"""
    try:
        from app.apis.family_profiles import get_profile
        return get_profile(profile_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Profile not found: {str(e)}")

def get_portfolio_data(profile_id: str) -> dict:
    """Get portfolio data from the API"""
    try:
        from app.apis.portfolio import get_portfolio_data
        return get_portfolio_data(profile_id)
    except Exception as e:
        print(f"Error getting portfolio data: {str(e)}")
        return {"investments": [], "total_invested_usd": 0, "total_btc_amount": 0, "current_value_usd": 0, "roi_percentage": 0}

def get_trust_fund_revenue(profile_id: str) -> dict:
    """Get trust fund revenue data from the API"""
    try:
        from app.apis.trust_fund import get_trust_fund_revenue_data
        return get_trust_fund_revenue_data(profile_id)
    except Exception as e:
        print(f"Error getting trust fund revenue: {str(e)}")
        return {"total_revenue": 0, "revenue_sources": [], "allocations": []}

def get_content_daos_for_profile(profile_id: str) -> list:
    """Get content DAOs for a profile"""
    try:
        from app.apis.content_dao import get_content_daos_for_profile_data
        return get_content_daos_for_profile_data(profile_id)
    except Exception as e:
        print(f"Error getting content DAOs: {str(e)}")
        return []

def generate_portfolio_chart(portfolio_data: dict) -> str:
    """Generate a portfolio allocation chart"""
    # Create a buffer for the image
    buffer = io.BytesIO()
    
    # Create data for the chart
    if not portfolio_data or not portfolio_data.get("investments"):
        # Create a placeholder chart if no data
        plt.figure(figsize=(8, 4))
        plt.text(0.5, 0.5, "No portfolio data available", ha="center", va="center", fontsize=14)
        plt.axis("off")
        plt.savefig(buffer, format="png", dpi=100, bbox_inches="tight")
        plt.close()
        return buffer.getvalue()
    
    # Process the investment data
    investments = portfolio_data.get("investments", [])
    dates = [inv["date"] for inv in investments]
    values = [inv["current_value"] for inv in investments]
    invested = [inv["amount_usd"] for inv in investments]
    
    # Create the chart
    plt.figure(figsize=(8, 4))
    plt.plot(dates, values, marker="o", linewidth=2, color="#3b82f6", label="Current Value")
    plt.plot(dates, invested, marker="s", linewidth=2, color="#10b981", linestyle="--", label="Invested Amount")
    
    plt.title("Investment Growth Over Time", fontsize=14)
    plt.xlabel("Date")
    plt.ylabel("Value (USD)")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.legend()
    plt.tight_layout()
    
    # Save the chart to the buffer
    plt.savefig(buffer, format="png", dpi=100, bbox_inches="tight")
    plt.close()
    
    return buffer.getvalue()

def generate_revenue_chart(revenue_data: dict) -> str:
    """Generate a revenue chart"""
    buffer = io.BytesIO()
    
    if not revenue_data:
        # Create a placeholder chart if no data
        plt.figure(figsize=(8, 4))
        plt.text(0.5, 0.5, "No revenue data available", ha="center", va="center", fontsize=14)
        plt.axis("off")
        plt.savefig(buffer, format="png", dpi=100, bbox_inches="tight")
        plt.close()
        return buffer.getvalue()
    
    # Create data for the pie chart
    sources = revenue_data.get("revenue_sources", [])
    labels = [source.get("source", "Unknown") for source in sources]
    values = [source.get("amount", 0) for source in sources]
    
    # If no data, create a placeholder
    if not labels or sum(values) == 0:
        plt.figure(figsize=(8, 4))
        plt.text(0.5, 0.5, "No revenue data available", ha="center", va="center", fontsize=14)
        plt.axis("off")
        plt.savefig(buffer, format="png", dpi=100, bbox_inches="tight")
        plt.close()
        return buffer.getvalue()
    
    # Create the pie chart
    plt.figure(figsize=(8, 4))
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, shadow=False,
            wedgeprops={'edgecolor': 'white', 'linewidth': 1})
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    plt.title("Revenue Sources", fontsize=14)
    plt.tight_layout()
    
    # Save the chart to the buffer
    plt.savefig(buffer, format="png", dpi=100, bbox_inches="tight")
    plt.close()
    
    return buffer.getvalue()

def format_currency(amount: float) -> str:
    """Format a currency value"""
    return f"${amount:,.2f}"

def format_percentage(value: float) -> str:
    """Format a percentage value"""
    return f"{value:.2f}%"

def generate_pdf_report(request: ReportRequest) -> bytes:
    """Generate a PDF report for a vault"""
    # Get the profile data
    profile = get_profile_data(request.profile_id)
    
    # Get portfolio data
    portfolio = get_portfolio_data(request.profile_id)
    
    # Get revenue data
    revenue = get_trust_fund_revenue(request.profile_id)
    
    # Get content DAOs
    content_daos = get_content_daos_for_profile(request.profile_id)
    
    # Set up the document
    buffer = io.BytesIO()
    
    # Create a document with increased top margin to accommodate the header
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter, 
        rightMargin=72, 
        leftMargin=72, 
        topMargin=120,  # Increased to make room for header
        bottomMargin=90  # Increased to make room for footer
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Add custom styles with more luxurious design
    styles.add(ParagraphStyle(
        name='Title',
        parent=styles['Title'],
        fontName='Times-Bold',  # More elegant serif font
        fontSize=24,
        leading=28,
        alignment=1,  # 0=left, 1=center, 2=right
        spaceAfter=20,
        textColor=colors.HexColor('#b7922a')  # Rich gold color
    ))
    
    styles.add(ParagraphStyle(
        name='Heading1',
        parent=styles['Heading1'],
        fontName='Times-Bold',
        fontSize=18,
        leading=22,
        spaceAfter=12,
        textColor=colors.HexColor('#b7922a')  # Gold
    ))
    
    styles.add(ParagraphStyle(
        name='Heading2',
        parent=styles['Heading2'],
        fontName='Times-Bold',
        fontSize=14,
        leading=18,
        spaceAfter=8,
        textColor=colors.HexColor('#9a7a23')  # Darker gold
    ))
    
    styles.add(ParagraphStyle(
        name='Normal',
        parent=styles['Normal'],
        fontName='Times-Roman',  # Serif font for improved readability
        fontSize=10,
        leading=14,
        spaceAfter=8
    ))
    
    styles.add(ParagraphStyle(
        name='Footer',
        parent=styles['Normal'],
        fontName='Times-Italic',
        fontSize=8,
        leading=10,
        alignment=1,  # Centered
        textColor=colors.HexColor('#666666')  # Gray
    ))
    
    # Content elements
    elements = []
    
    # Report title
    report_title = request.custom_title or f"Legacy Vault Monthly Summary Report"
    elements.append(Paragraph(report_title, styles["Title"]))
    
    # Report subtitle with date range
    now = datetime.now()
    if request.start_date and request.end_date:
        start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(request.end_date, "%Y-%m-%d")
    else:
        # Default to the past month
        end_date = now
        if request.report_type == "monthly":
            start_date = end_date - timedelta(days=30)
        elif request.report_type == "quarterly":
            start_date = end_date - timedelta(days=90)
        else:  # annual
            start_date = end_date - timedelta(days=365)
    
    date_range = f"{start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}"
    elements.append(Paragraph(f"For {profile['name']} | {date_range}", styles["Heading2"]))
    elements.append(Spacer(1, 0.25 * inch))
    
    # Include selected sections
    sections = request.include_sections
    
    # Summary section
    if "summary" in sections:
        elements.append(Paragraph("Executive Summary", styles["Heading1"]))
        
        summary_text = f"""
        This monthly report provides an overview of the Legacy Vault status for {profile['name']}. 
        The report covers the period from {date_range} and includes analysis of portfolio performance, 
        revenue generation, and progress on ongoing projects.
        
        <b>Key Highlights:</b>
        
        • Total Portfolio Value: {format_currency(portfolio.get('current_value_usd', 0))}
        • Total Bitcoin Holdings: {portfolio.get('total_btc_amount', 0):.8f} BTC
        • Monthly Revenue: {format_currency(revenue.get('total_revenue', 0))}
        • Number of Active Projects: {len(content_daos)}
        """
        
        elements.append(Paragraph(summary_text, styles["Normal"]))
        elements.append(Spacer(1, 0.25 * inch))
    
    # Portfolio section
    if "portfolio" in sections:
        elements.append(Paragraph("Portfolio Performance", styles["Heading1"]))
        
        # Portfolio metrics
        portfolio_metrics = [
            ["Metric", "Value"],
            ["Total Invested", format_currency(portfolio.get('total_invested_usd', 0))],
            ["Current Value", format_currency(portfolio.get('current_value_usd', 0))],
            ["Return on Investment", format_percentage(portfolio.get('roi_percentage', 0))],
            ["Number of Investments", str(len(portfolio.get('investments', [])))]
        ]
        
        # Create the table
        portfolio_table = Table(portfolio_metrics, colWidths=[2.5*inch, 2.5*inch])
        portfolio_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#1e40af')),  # Header background
            ('TEXTCOLOR', (0, 0), (1, 0), colors.white),  # Header text color
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),  # Header alignment
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),  # Header font
            ('FONTSIZE', (0, 0), (1, 0), 12),  # Header font size
            ('BOTTOMPADDING', (0, 0), (1, 0), 8),  # Header bottom padding
            ('BACKGROUND', (0, 1), (1, -1), colors.white),  # Cell background
            ('TEXTCOLOR', (0, 1), (0, -1), colors.HexColor('#6b7280')),  # Row header text color
            ('TEXTCOLOR', (1, 1), (1, -1), colors.HexColor('#111827')),  # Value text color
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),  # Row header font
            ('FONTNAME', (1, 1), (1, -1), 'Helvetica'),  # Value font
            ('FONTSIZE', (0, 1), (1, -1), 10),  # Cell font size
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Row header alignment
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),  # Value alignment
            ('VALIGN', (0, 0), (1, -1), 'MIDDLE'),  # Vertical alignment
            ('GRID', (0, 0), (1, -1), 0.5, colors.HexColor('#e5e7eb')),  # Grid color
            ('ROWBACKGROUNDS', (0, 1), (1, -1), [colors.HexColor('#f9fafb'), colors.white])  # Alternating row colors
        ]))
        
        elements.append(portfolio_table)
        elements.append(Spacer(1, 0.25 * inch))
        
        # Portfolio chart
        if portfolio.get('investments'):
            chart_data = generate_portfolio_chart(portfolio)
            portfolio_chart = Image(io.BytesIO(chart_data), width=6*inch, height=3*inch)
            elements.append(portfolio_chart)
            elements.append(Spacer(1, 0.25 * inch))
        
        # Recent transactions
        elements.append(Paragraph("Recent Investments", styles["Heading2"]))
        
        investments = portfolio.get('investments', [])
        if investments:
            # Sort investments by date (most recent first) and take the last 5
            recent_investments = sorted(investments, key=lambda x: x.get('date', ''), reverse=True)[:5]
            
            # Create table data
            investment_data = [["Date", "Amount (USD)", "BTC Price", "BTC Amount"]]
            for inv in recent_investments:
                investment_data.append([
                    inv.get('date', 'N/A'),
                    format_currency(inv.get('amount_usd', 0)),
                    format_currency(inv.get('btc_price', 0)),
                    f"{inv.get('btc_amount', 0):.8f}"
                ])
            
            # Create the table
            investment_table = Table(investment_data, colWidths=[1.25*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            investment_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (3, 0), colors.HexColor('#3b82f6')),  # Header background
                ('TEXTCOLOR', (0, 0), (3, 0), colors.white),  # Header text color
                ('ALIGN', (0, 0), (3, 0), 'CENTER'),  # Header alignment
                ('FONTNAME', (0, 0), (3, 0), 'Helvetica-Bold'),  # Header font
                ('FONTSIZE', (0, 0), (3, 0), 10),  # Header font size
                ('BOTTOMPADDING', (0, 0), (3, 0), 6),  # Header bottom padding
                ('BACKGROUND', (0, 1), (3, -1), colors.white),  # Cell background
                ('FONTNAME', (0, 1), (3, -1), 'Helvetica'),  # Cell font
                ('FONTSIZE', (0, 1), (3, -1), 9),  # Cell font size
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Date alignment
                ('ALIGN', (1, 1), (3, -1), 'RIGHT'),  # Numeric data alignment
                ('VALIGN', (0, 0), (3, -1), 'MIDDLE'),  # Vertical alignment
                ('GRID', (0, 0), (3, -1), 0.5, colors.HexColor('#e5e7eb')),  # Grid color
                ('ROWBACKGROUNDS', (0, 1), (3, -1), [colors.HexColor('#f9fafb'), colors.white])  # Alternating row colors
            ]))
            
            elements.append(investment_table)
        else:
            elements.append(Paragraph("No investment records found.", styles["Normal"]))
        
        elements.append(Spacer(1, 0.25 * inch))
    
    # Bitcoin section
    if "bitcoin" in sections:
        elements.append(Paragraph("Bitcoin Holdings", styles["Heading1"]))
        
        btc_text = f"""
        Total Bitcoin: <b>{portfolio.get('total_btc_amount', 0):.8f} BTC</b>\n
        Current Value: <b>{format_currency(portfolio.get('current_value_usd', 0))}</b>\n
        Average Purchase Price: <b>{format_currency(portfolio.get('total_invested_usd', 0) / portfolio.get('total_btc_amount', 1) if portfolio.get('total_btc_amount', 0) > 0 else 0)}</b>\n
        Return on Investment: <b>{format_percentage(portfolio.get('roi_percentage', 0))}</b>
        """
        
        elements.append(Paragraph(btc_text, styles["Normal"]))
        elements.append(Spacer(1, 0.25 * inch))
    
    # Revenue section
    if "revenue" in sections:
        elements.append(Paragraph("Revenue & Royalties", styles["Heading1"]))
        
        revenue_sources = revenue.get('revenue_sources', [])
        if revenue_sources:
            # Create the revenue chart
            chart_data = generate_revenue_chart(revenue)
            revenue_chart = Image(io.BytesIO(chart_data), width=6*inch, height=3*inch)
            elements.append(revenue_chart)
            elements.append(Spacer(1, 0.25 * inch))
            
            # Revenue metrics table
            revenue_data = [["Revenue Source", "Amount"]]
            for source in revenue_sources:
                revenue_data.append([
                    source.get('source', 'Unknown'),
                    format_currency(source.get('amount', 0))
                ])
            
            # Add total row
            revenue_data.append(["Total Revenue", format_currency(revenue.get('total_revenue', 0))])
            
            # Create the table
            revenue_table = Table(revenue_data, colWidths=[3*inch, 2*inch])
            revenue_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#3b82f6')),  # Header background
                ('TEXTCOLOR', (0, 0), (1, 0), colors.white),  # Header text color
                ('ALIGN', (0, 0), (1, 0), 'CENTER'),  # Header alignment
                ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),  # Header font
                ('FONTSIZE', (0, 0), (1, 0), 10),  # Header font size
                ('BOTTOMPADDING', (0, 0), (1, 0), 6),  # Header bottom padding
                ('BACKGROUND', (0, 1), (1, -2), colors.white),  # Cell background
                ('BACKGROUND', (0, -1), (1, -1), colors.HexColor('#f9fafb')),  # Total row background
                ('FONTNAME', (0, 1), (1, -2), 'Helvetica'),  # Cell font
                ('FONTNAME', (0, -1), (1, -1), 'Helvetica-Bold'),  # Total row font
                ('FONTSIZE', (0, 1), (1, -1), 9),  # Cell font size
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Source alignment
                ('ALIGN', (1, 1), (1, -1), 'RIGHT'),  # Amount alignment
                ('VALIGN', (0, 0), (1, -1), 'MIDDLE'),  # Vertical alignment
                ('GRID', (0, 0), (1, -1), 0.5, colors.HexColor('#e5e7eb')),  # Grid color
                ('ROWBACKGROUNDS', (0, 1), (1, -2), [colors.HexColor('#f9fafb'), colors.white])  # Alternating row colors
            ]))
            
            elements.append(revenue_table)
        else:
            elements.append(Paragraph("No revenue data available for this period.", styles["Normal"]))
        
        elements.append(Spacer(1, 0.25 * inch))
    
    # Projects section
    if "projects" in sections:
        elements.append(Paragraph("Active Projects", styles["Heading1"]))
        
        if content_daos:
            # Project status table
            project_data = [["Project Name", "Type", "Status", "Revenue"]]
            for dao in content_daos:
                project_data.append([
                    dao.get('name', 'Unknown'),
                    dao.get('type', 'General'),
                    dao.get('status', 'Active'),
                    format_currency(dao.get('total_revenue', 0))
                ])
            
            # Create the table
            project_table = Table(project_data, colWidths=[2*inch, 1.25*inch, 1.25*inch, 1.25*inch])
            project_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (3, 0), colors.HexColor('#3b82f6')),  # Header background
                ('TEXTCOLOR', (0, 0), (3, 0), colors.white),  # Header text color
                ('ALIGN', (0, 0), (3, 0), 'CENTER'),  # Header alignment
                ('FONTNAME', (0, 0), (3, 0), 'Helvetica-Bold'),  # Header font
                ('FONTSIZE', (0, 0), (3, 0), 10),  # Header font size
                ('BOTTOMPADDING', (0, 0), (3, 0), 6),  # Header bottom padding
                ('BACKGROUND', (0, 1), (3, -1), colors.white),  # Cell background
                ('FONTNAME', (0, 1), (3, -1), 'Helvetica'),  # Cell font
                ('FONTSIZE', (0, 1), (3, -1), 9),  # Cell font size
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Project name alignment
                ('ALIGN', (1, 1), (2, -1), 'CENTER'),  # Type and status alignment
                ('ALIGN', (3, 1), (3, -1), 'RIGHT'),  # Revenue alignment
                ('VALIGN', (0, 0), (3, -1), 'MIDDLE'),  # Vertical alignment
                ('GRID', (0, 0), (3, -1), 0.5, colors.HexColor('#e5e7eb')),  # Grid color
                ('ROWBACKGROUNDS', (0, 1), (3, -1), [colors.HexColor('#f9fafb'), colors.white])  # Alternating row colors
            ]))
            
            elements.append(project_table)
            
            # Project details
            for dao in content_daos[:3]:  # Limit to top 3 projects
                elements.append(Spacer(1, 0.15 * inch))
                elements.append(Paragraph(dao.get('name', 'Unknown Project'), styles["Heading2"]))
                
                project_detail = f"""
                <b>Type:</b> {dao.get('type', 'General')}\n
                <b>Status:</b> {dao.get('status', 'Active')}\n
                <b>Revenue Generated:</b> {format_currency(dao.get('total_revenue', 0))}\n
                <b>Description:</b> {dao.get('description', 'No description available.')}\n
                <b>Trust Contribution:</b> {format_currency(dao.get('trust_contribution', 0))}
                """
                
                elements.append(Paragraph(project_detail, styles["Normal"]))
        else:
            elements.append(Paragraph("No active projects found for this profile.", styles["Normal"]))
        
        elements.append(Spacer(1, 0.25 * inch))
    
    # Future plans section
    if "future_plans" in sections:
        elements.append(Paragraph("Future Plans & Recommendations", styles["Heading1"]))
        
        # Generate some analysis and recommendations based on the portfolio data
        avg_roi = portfolio.get('roi_percentage', 0)
        recommendations = []
        
        if avg_roi < 0:
            recommendations.append("Consider rebalancing the portfolio to reduce exposure to volatile assets.")
        elif 0 <= avg_roi < 10:
            recommendations.append("The portfolio is showing positive but modest returns. Consider increasing allocation to higher-growth assets.")
        else:
            recommendations.append("The portfolio is performing well. Consider taking some profits and diversifying into other asset classes.")
        
        if portfolio.get('total_btc_amount', 0) < 0.1:
            recommendations.append("Bitcoin allocation is relatively low. Consider increasing Bitcoin purchases during market dips.")
        elif portfolio.get('total_btc_amount', 0) > 1.0:
            recommendations.append("Bitcoin allocation is substantial. Monitor market conditions closely for potential profit-taking opportunities.")
        
        if len(content_daos) == 0:
            recommendations.append("No creative projects found. Consider exploring creative revenue streams through Content DAOs.")
        elif len(content_daos) < 3:
            recommendations.append("Limited creative diversification. Consider expanding creative projects into additional domains.")
        else:
            recommendations.append("Good diversification across creative projects. Focus on optimizing performance of existing Content DAOs.")
        
        next_review = (now + timedelta(days=30)).strftime('%B %d, %Y')
        next_investment = (now + timedelta(days=14)).strftime('%B %d, %Y')
        next_analysis = (now + timedelta(days=90)).strftime('%B %d, %Y')
        
        plans_text = f"""
        <b>Strategic Recommendations:</b>
        
        • {recommendations[0]}
        • {recommendations[1]}
        • {recommendations[2]}
        
        <b>Upcoming Milestones:</b>
        
        • Next portfolio review: {next_review}
        • Next investment contribution: {next_investment}
        • Quarterly performance analysis: {next_analysis}
        """
        
        elements.append(Paragraph(plans_text, styles["Normal"]))
    
    # Define header and footer
    def header_footer(canvas, doc):
        # Save the state of the canvas so we can restore it
        canvas.saveState()
        
        # Add decorative elements
        add_decorative_elements(canvas, doc)
        
        # Header with logo and profile name
        # Create geometric hexagon logo (representing blockchain and generational stability)
        import math
        centerX, centerY = doc.leftMargin + 0.4*inch, doc.height + doc.topMargin - 0.4*inch
        radius = 18
        sides = 6  # hexagon
        
        # Draw the hexagon
        points = []
        for i in range(sides):
            angle = 2 * math.pi * i / sides + math.pi/6  # Rotate slightly
            x = centerX + radius * math.cos(angle)
            y = centerY + radius * math.sin(angle)
            points.append((x, y))
        
        # Draw outer hexagon
        canvas.setFillColorRGB(0.1, 0.1, 0.1)  # Almost black fill
        canvas.setStrokeColorRGB(0.8, 0.65, 0.15)  # Gold color
        canvas.setLineWidth(1.5)
        p = canvas.beginPath()
        p.moveTo(points[0][0], points[0][1])
        for x, y in points[1:]:
            p.lineTo(x, y)
        p.close()
        canvas.drawPath(p, fill=1, stroke=1)
        
        # Draw inner hexagon
        inner_radius = radius * 0.6
        inner_points = []
        for i in range(sides):
            angle = 2 * math.pi * i / sides + math.pi/6  # Rotate slightly
            x = centerX + inner_radius * math.cos(angle)
            y = centerY + inner_radius * math.sin(angle)
            inner_points.append((x, y))
        
        canvas.setStrokeColorRGB(0.8, 0.65, 0.15)  # Gold color
        canvas.setLineWidth(1)
        p = canvas.beginPath()
        p.moveTo(inner_points[0][0], inner_points[0][1])
        for x, y in inner_points[1:]:
            p.lineTo(x, y)
        p.close()
        canvas.drawPath(p, stroke=1)
        
        # Add the letter 'L' in the center of the hexagon
        canvas.setFillColorRGB(0.8, 0.65, 0.15)  # Gold color
        canvas.setFont('Times-Bold', 18)
        canvas.drawCentredString(centerX, centerY - 5, 'L')
        
        # Profile name
        canvas.setFont('Times-Bold', 14)
        canvas.setFillColorRGB(0.8, 0.65, 0.15)  # Gold color
        canvas.drawString(doc.leftMargin + 0.9*inch, doc.height + doc.topMargin - 0.3*inch, profile['name'])
        
        # Document type and date
        canvas.setFont('Times-Italic', 10)
        canvas.setFillColorRGB(0.4, 0.4, 0.4)  # Gray color
        canvas.drawString(doc.leftMargin + 0.9*inch, doc.height + doc.topMargin - 0.5*inch, 
                          f"Legacy Vault Report - {datetime.now().strftime('%B %d, %Y')}")
        
        # Horizontal separator line
        canvas.setStrokeColorRGB(0.8, 0.65, 0.15)  # Gold color
        canvas.setLineWidth(1)
        canvas.line(doc.leftMargin, doc.height + doc.topMargin - 0.7*inch, 
                   doc.width + doc.leftMargin, doc.height + doc.topMargin - 0.7*inch)
        
        # Footer with page number and branding
        footer_text = f"Legacy Vault - Building Generational Wealth \u2022 Page {canvas.getPageNumber()}"
        canvas.setFont('Times-Italic', 8)
        canvas.setFillColorRGB(0.4, 0.4, 0.4)  # Gray color
        canvas.drawCentredString(doc.width/2 + doc.leftMargin, 0.5*inch, footer_text)
        
        # Add Claude/Suno usage metrics to footer
        canvas.setFont('Times-Roman', 7)
        canvas.setFillColorRGB(0.4, 0.4, 0.4)  # Gray color
        claude_text = "Claude Tokens Used: 13"
        suno_text = "Suno Songs Generated: 2"
        canvas.drawString(doc.leftMargin, 0.3*inch, claude_text)
        canvas.drawString(doc.leftMargin, 0.2*inch, suno_text)
        
        # Gold line before footer
        canvas.setStrokeColorRGB(0.8, 0.65, 0.15)  # Gold color
        canvas.setLineWidth(0.5)
        canvas.line(doc.leftMargin, 0.75*inch, doc.width + doc.leftMargin, 0.75*inch)
        
        # Watermark for document protection
        canvas.setFont('Times-Roman', 7)
        canvas.setFillColorRGB(0.3, 0.3, 0.3)  # Dark gray
        canvas.drawRightString(doc.width + doc.leftMargin, 0.3*inch, 
                            f"Legacy Vault ID: {profile['id'][:8]} \u2022 Confidential")
        
        canvas.restoreState()
    
    def add_decorative_elements(canvas, doc):
        """Add decorative elements to enhance family branding"""
        import math  # Import math here to ensure it's available
        
        # Right side vertical gold line with small hexagons
        right_x = doc.width + doc.leftMargin - 0.2*inch
        canvas.setStrokeColorRGB(0.8, 0.65, 0.15, 0.5)  # Semi-transparent gold
        canvas.setLineWidth(0.5)
        canvas.line(right_x, doc.topMargin, right_x, doc.height + doc.topMargin - 1*inch)
        
        # Add small hexagons along the line (blockchain reference)
        canvas.setFillColorRGB(0.8, 0.65, 0.15, 0.3)  # Semi-transparent gold
        for y_pos in range(int(doc.topMargin), int(doc.height + doc.topMargin - 1*inch), 60):
            # Calculate small hexagon points
            hex_radius = 4
            hex_points = []
            for i in range(6):
                angle = 2 * math.pi * i / 6 + math.pi/6
                x = right_x + hex_radius * math.cos(angle)
                y = y_pos + hex_radius * math.sin(angle)
                hex_points.append((x, y))
            
            # Draw small hexagon
            p = canvas.beginPath()
            p.moveTo(hex_points[0][0], hex_points[0][1])
            for x, y in hex_points[1:]:
                p.lineTo(x, y)
            p.close()
            canvas.drawPath(p, fill=1, stroke=0)
        
        # Left margin subtle architectural element (arches reference for generational stability)
        left_x = doc.leftMargin + 0.1*inch
        canvas.setStrokeColorRGB(0.8, 0.65, 0.15, 0.3)  # Semi-transparent gold
        canvas.setLineWidth(0.3)
        
        # Draw a few small arches in the left margin
        for y_pos in range(int(doc.topMargin + 1*inch), int(doc.height + doc.topMargin - 2*inch), 100):
            # Draw small arch
            canvas.arc(left_x, y_pos, left_x + 8, y_pos + 16, 180, 360)
        
        # Sophisticated corner elements - architectural frames at each corner
        corner_size = 20
        # Top left corner
        canvas.setStrokeColorRGB(0.8, 0.65, 0.15, 0.4)  # Gold with opacity
        canvas.setLineWidth(0.75)
        # Top-left L shape
        canvas.line(doc.leftMargin, doc.height + doc.topMargin - 0.9*inch, 
                   doc.leftMargin + corner_size, doc.height + doc.topMargin - 0.9*inch)
        canvas.line(doc.leftMargin, doc.height + doc.topMargin - 0.9*inch, 
                   doc.leftMargin, doc.height + doc.topMargin - 0.9*inch - corner_size)
        # Top-right L shape
        canvas.line(doc.width + doc.leftMargin - corner_size, doc.height + doc.topMargin - 0.9*inch, 
                   doc.width + doc.leftMargin, doc.height + doc.topMargin - 0.9*inch)
        canvas.line(doc.width + doc.leftMargin, doc.height + doc.topMargin - 0.9*inch, 
                   doc.width + doc.leftMargin, doc.height + doc.topMargin - 0.9*inch - corner_size)
        # Bottom-left L shape
        canvas.line(doc.leftMargin, doc.topMargin + corner_size, 
                   doc.leftMargin, doc.topMargin)
        canvas.line(doc.leftMargin, doc.topMargin, 
                   doc.leftMargin + corner_size, doc.topMargin)
        # Bottom-right L shape
        canvas.line(doc.width + doc.leftMargin, doc.topMargin + corner_size, 
                   doc.width + doc.leftMargin, doc.topMargin)
        canvas.line(doc.width + doc.leftMargin - corner_size, doc.topMargin, 
                   doc.width + doc.leftMargin, doc.topMargin)
        
        # Background hexagonal grid pattern (very subtle)
        canvas.saveState()
        canvas.setFillColorRGB(0.8, 0.65, 0.15, 0.015)  # Almost invisible gold
        canvas.setStrokeColorRGB(0.8, 0.65, 0.15, 0.02)  # Almost invisible gold stroke
        canvas.setLineWidth(0.2)
        
        # Create a hexagonal grid pattern
        hex_size = 40
        grid_width = int(doc.width / hex_size) + 2
        grid_height = int(doc.height / hex_size) + 2
        
        for row in range(grid_height):
            for col in range(grid_width):
                # Offset every other row
                x_offset = (hex_size / 2) if row % 2 else 0
                center_x = doc.leftMargin + col * hex_size + x_offset
                center_y = doc.topMargin + row * (hex_size * 0.866)  # 0.866 = sqrt(3)/2
                
                # Skip if outside the page margins (with a buffer)
                if center_x < doc.leftMargin - 10 or center_x > doc.width + doc.leftMargin + 10:
                    continue
                if center_y < doc.topMargin - 10 or center_y > doc.height + doc.topMargin + 10:
                    continue
                
                # Draw a hexagon at this position
                hex_points = []
                r = hex_size / 2 * 0.8  # Slightly smaller than half the size
                for i in range(6):
                    angle = 2 * math.pi * i / 6
                    x = center_x + r * math.cos(angle)
                    y = center_y + r * math.sin(angle)
                    hex_points.append((x, y))
                
                # Draw only if it's a "special" hexagon (every 5th in each direction)
                if (row % 5 == 0 and col % 5 == 0):
                    p = canvas.beginPath()
                    p.moveTo(hex_points[0][0], hex_points[0][1])
                    for x, y in hex_points[1:]:
                        p.lineTo(x, y)
                    p.close()
                    canvas.drawPath(p, fill=0, stroke=1)
        
        canvas.restoreState()
        
        # Background watermark - very subtle
        canvas.saveState()
        canvas.translate(doc.width/2 + doc.leftMargin, doc.height/2 + doc.topMargin)
        canvas.rotate(30)
        canvas.setFillColorRGB(0.8, 0.65, 0.15, 0.03)  # Very transparent gold
        canvas.setFont('Times-Bold', 80)
        canvas.drawCentredString(0, 0, "LEGACY")
        canvas.restoreState()
        
        # Add a subtle timeline element along the bottom margin
        canvas.setStrokeColorRGB(0.8, 0.65, 0.15, 0.2)  # Semi-transparent gold
        canvas.setLineWidth(0.5)
        timeline_y = 0.6*inch
        timeline_start = doc.leftMargin + 0.5*inch
        timeline_end = doc.width + doc.leftMargin - 0.5*inch
        canvas.line(timeline_start, timeline_y, timeline_end, timeline_y)
        
        # Add generational markers on the timeline
        markers = ["Birth", "18", "30", "60", "Legacy"]
        marker_positions = [0, 0.25, 0.5, 0.75, 1.0]  # Positions along the timeline
        
        canvas.setFont('Times-Roman', 6)
        canvas.setFillColorRGB(0.8, 0.65, 0.15, 0.5)  # Gold
        
        for i, marker in enumerate(markers):
            x_pos = timeline_start + marker_positions[i] * (timeline_end - timeline_start)
            # Small circle marker
            canvas.circle(x_pos, timeline_y, 2, fill=1)
            # Label
            canvas.drawCentredString(x_pos, timeline_y - 8, marker)
    
    # Build the PDF document with header and footer
    doc.build(elements, onFirstPage=header_footer, onLaterPages=header_footer)
    buffer.seek(0)
    return buffer.getvalue()

def store_report(profile_id: str, report_pdf: bytes, report_type: str = "monthly") -> str:
    """Store a report in the database and return its ID"""
    # Generate a report ID
    now = datetime.now()
    report_id = f"report_{profile_id}_{report_type}_{now.strftime('%Y%m%d_%H%M%S')}"
    sanitized_report_id = sanitize_storage_key(report_id)
    
    # Store the PDF in the binary storage
    db.storage.binary.put(sanitized_report_id, report_pdf)
    
    # Get report metadata from storage or create new metadata record
    reports_meta_key = sanitize_storage_key(f"reports_meta_{profile_id}")
    try:
        reports_meta = db.storage.json.get(reports_meta_key, default=[])
    except:
        reports_meta = []
    
    # Generate filename with fallback logic
    try:
        # Try to get profile data for more personalized filename
        profile = get_profile_data(profile_id)
        
        # Vault ID with fallback
        vault_id = profile.get('vault_id') or profile.get('id') or profile.get('alias')
        vault_id = vault_id if vault_id else profile_id
        
        # Format: Vault_Report_Month_Year.pdf (standard format)
        # We don't include profile name or vault ID in the filename to maintain consistent format
        file_name = f"Vault_Report_{now.strftime('%B_%Y')}.pdf"
    except Exception as e:
        # Log the error for debugging
        print(f"Error creating personalized filename, using fallback: {str(e)}")
        # Fallback if profile data is unavailable - use consistent format regardless
        file_name = f"Vault_Report_{now.strftime('%B_%Y')}.pdf"
        
    # Ensure month name is capitalized and no spaces in filename
    file_name = file_name.replace(' ', '_')
    
    # Add the new report metadata
    reports_meta.append({
        "report_id": sanitized_report_id,
        "profile_id": profile_id,
        "report_type": report_type,
        "created_at": now.isoformat(),
        "size_bytes": len(report_pdf),
        "file_name": file_name
    })
    
    # Store the updated metadata
    db.storage.json.put(reports_meta_key, reports_meta)
    
    return sanitized_report_id

@router.post("/generate-report")
def generator_generate_report(request: ReportRequest) -> ReportResponse:
    """Generate a monthly vault summary report
    
    This endpoint generates a PDF report for a family profile with customizable sections and delivery options.
    Reports can include portfolio performance, bitcoin holdings, revenue streams, active projects, and future plans.
    """
    try:
        # Generate the PDF report
        pdf_data = generate_pdf_report(request)
        
        # Store the report
        report_id = store_report(request.profile_id, pdf_data, request.report_type)
        
        # If delivery email is provided, send the report
        if request.delivery_email:
            try:
                import databutton as db
                
                # Get profile data for email subject
                profile = get_profile_data(request.profile_id)
                
                # Read the PDF from storage to ensure we're sending the saved version
                pdf_data = db.storage.binary.get(report_id)
                
                # Encode the PDF as base64 for email attachment
                pdf_b64 = base64.b64encode(pdf_data).decode('utf-8')
                
                # Format date for email subject
                now = datetime.now()
                date_str = now.strftime("%B %Y")
                
                # Send the email with the report attached
                # Note: This functionality depends on the email sending capabilities available
                # in your Databutton environment
                email_subject = f"Legacy Vault Summary Report - {profile['name']} - {date_str}"
                email_body = f"""<p>Attached is the Legacy Vault Summary Report for {profile['name']} for {date_str}.</p>
                <p>This report provides an overview of the vault's performance, including portfolio status, revenue, and projects.</p>
                <p>Please let us know if you have any questions.</p>
                <p>Best regards,<br>Legacy Vault Management</p>"""
                
                # Send email using databutton notify
                # Get the filename from metadata
                reports_meta_key = sanitize_storage_key(f"reports_meta_{request.profile_id}")
                reports_meta = db.storage.json.get(reports_meta_key, default=[])
                filename = f"Vault_Report_{now.strftime('%B_%Y')}.pdf"  # Default fallback
                
                # Find the report in metadata to get its filename
                for report in reports_meta:
                    if report.get("report_id") == report_id:
                        stored_filename = report.get("file_name")
                        if stored_filename:
                            filename = stored_filename
                        # Ensure filename follows standard format even if stored incorrectly
                        if not filename.startswith("Vault_Report_"):
                            filename = f"Vault_Report_{now.strftime('%B_%Y')}.pdf"
                        break
                
                db.notify.email(
                    to=request.delivery_email,
                    subject=email_subject,
                    content_html=email_body,
                    content_text=email_body,
                    #attachments=[
                    #    {
                    #        "content": pdf_b64,
                    #        "filename": filename,
                    #        "type": "application/pdf",
                    #        "disposition": "attachment"
                    #    }
                    #]
                )
            except Exception as e:
                print(f"Error sending email: {str(e)}")
                # Continue even if email fails
        
        return ReportResponse(
            success=True,
            report_id=report_id,
            download_url=f"/api/reports/download/{report_id}",
            message="Report generated successfully"
        )
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        import traceback
        traceback.print_exc()
        return ReportResponse(
            success=False,
            message=f"Error generating report: {str(e)}"
        )

@router.get("/download/{report_id}")
def download_report_generator(report_id: str):
    """Download a generated report"""
    try:
        # Read the PDF from storage
        sanitized_id = sanitize_storage_key(report_id)
        pdf_data = db.storage.binary.get(sanitized_id)
        
        # Try to get the filename from metadata
        try:
            # Extract profile ID from report ID
            parts = report_id.split('_')
            if len(parts) >= 2:
                profile_id = parts[1]
                
                # Get report metadata
                reports_meta_key = sanitize_storage_key(f"reports_meta_{profile_id}")
                reports_meta = db.storage.json.get(reports_meta_key, default=[])
                
                # Find report in metadata
                for report in reports_meta:
                    if report.get("report_id") == sanitized_id:
                        # Found the report, use its filename
                        stored_filename = report.get("file_name")
                        if stored_filename:
                            filename = stored_filename
                            # Validate filename format
                            if not filename.startswith("Vault_Report_"):
                                filename = f"Vault_Report_{datetime.now().strftime('%B_%Y')}.pdf"
                        else:
                            filename = f"Vault_Report_{datetime.now().strftime('%B_%Y')}.pdf"
                        break
                else:
                    # Report not found in metadata, use fallback
                    filename = f"Vault_Report_{datetime.now().strftime('%B_%Y')}.pdf"
            else:
                # Invalid report ID format, use fallback
                filename = f"Vault_Report_{datetime.now().strftime('%B_%Y')}.pdf"
        except Exception:
            # Error accessing metadata, use fallback
            current_date = datetime.now()
            # Ensure month name is properly formatted
            month_name = current_date.strftime('%B')
            filename = f"Vault_Report_{month_name}_{current_date.strftime('%Y')}.pdf"
            # Replace any spaces with underscores for consistent formatting
            filename = filename.replace(' ', '_')
        
        # Return the PDF file with proper filename
        from fastapi.responses import Response
        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=\"{filename}\""
            }
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Report not found: {str(e)}")

@router.post("/schedule")
def schedule_report_generator(request: ScheduleReportRequest) -> ScheduleReportResponse:
    """Schedule periodic reports"""
    try:
        # Generate a schedule ID
        schedule_id = f"schedule_{request.profile_id}_{request.frequency}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        sanitized_schedule_id = sanitize_storage_key(schedule_id)
        
        # Calculate next delivery date if not provided
        if not request.next_delivery_date:
            now = datetime.now()
            if request.frequency == "weekly":
                next_delivery = now + timedelta(days=7)
            elif request.frequency == "monthly":
                # Add a month (approximately)
                next_delivery = now + timedelta(days=30)
            elif request.frequency == "quarterly":
                next_delivery = now + timedelta(days=90)
            else:  # annual
                next_delivery = now + timedelta(days=365)
            
            next_delivery_date = next_delivery.strftime("%Y-%m-%d")
        else:
            next_delivery_date = request.next_delivery_date
        
        # Store the schedule information
        schedule_data = {
            "id": sanitized_schedule_id,
            "profile_id": request.profile_id,
            "frequency": request.frequency,
            "delivery_emails": request.delivery_emails,
            "include_sections": request.include_sections,
            "next_delivery_date": next_delivery_date,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        # Get schedules from storage or create new schedules record
        schedules_key = sanitize_storage_key("report_schedules")
        try:
            schedules = db.storage.json.get(schedules_key, default=[])
        except:
            schedules = []
        
        # Add the new schedule
        schedules.append(schedule_data)
        
        # Store the updated schedules
        db.storage.json.put(schedules_key, schedules)
        
        return ScheduleReportResponse(
            success=True,
            schedule_id=sanitized_schedule_id,
            next_delivery_date=next_delivery_date,
            message=f"Report scheduled successfully. Next delivery: {next_delivery_date}"
        )
    except Exception as e:
        print(f"Error scheduling report: {str(e)}")
        return ScheduleReportResponse(
            success=False,
            message=f"Error scheduling report: {str(e)}"
        )

@router.get("/list/{profile_id}")
def list_reports_generator(profile_id: str) -> ListReportsResponse:
    """List all reports generated for a profile"""
    try:
        # Get report metadata from storage
        reports_meta_key = sanitize_storage_key(f"reports_meta_{profile_id}")
        reports_meta = db.storage.json.get(reports_meta_key, default=[])
        
        # Sort by created_at in descending order (newest first)
        reports_meta.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return ListReportsResponse(reports=reports_meta)
    except Exception as e:
        print(f"Error listing reports: {str(e)}")
        return ListReportsResponse(reports=[])

@router.post("/process-scheduled")
def process_scheduled_reports_generator(process_all: bool = True) -> Dict[str, Any]:
    """Process all scheduled reports that are due
    
    This function checks all scheduled reports and generates reports for those that are due.
    It is designed to be called as a background task or endpoint.
    """
    import databutton as db
    from datetime import datetime, timedelta
    import traceback
    
    # Get report schedules
    schedules_key = "report_schedules"
    try:
        schedules = db.storage.json.get(schedules_key, default=[])
    except Exception as e:
        print(f"Error getting schedules: {str(e)}")
        return {"success": False, "processed": 0, "errors": [str(e)]}
    
    processed = 0
    errors = []
    today = datetime.now().strftime("%Y-%m-%d")
    
    for schedule in schedules:
        try:
            # Check if the schedule is due today or if we're processing all
            if process_all or schedule.get("next_delivery_date") == today:
                # Create a report request
                profile_id = schedule.get("profile_id")
                include_sections = schedule.get("include_sections", ["summary", "portfolio", "bitcoin", "revenue", "projects", "future_plans"])
                
                report_type = "monthly"
                if schedule.get("frequency") == "weekly":
                    report_type = "weekly"
                elif schedule.get("frequency") == "quarterly":
                    report_type = "quarterly"
                elif schedule.get("frequency") == "annual":
                    report_type = "annual"
                
                # Create a request object
                request = ReportRequest(
                    profile_id=profile_id,
                    report_type=report_type,
                    include_sections=include_sections
                )
                
                # The function is called directly, not via the endpoint route
                response = generator_generate_report(request)
                
                if response.success and response.report_id:
                    # Send the report to all delivery emails
                    delivery_emails = schedule.get("delivery_emails", [])
                    for email in delivery_emails:
                        # Update the request with the email
                        request.delivery_email = email
                        # The function is called directly, not via the endpoint route
                        generator_generate_report(request)
                    
                    # Update the next delivery date
                    now = datetime.now()
                    if schedule.get("frequency") == "weekly":
                        next_delivery = now + timedelta(days=7)
                    elif schedule.get("frequency") == "monthly":
                        next_delivery = now + timedelta(days=30)
                    elif schedule.get("frequency") == "quarterly":
                        next_delivery = now + timedelta(days=90)
                    else:  # annual
                        next_delivery = now + timedelta(days=365)
                    
                    schedule["next_delivery_date"] = next_delivery.strftime("%Y-%m-%d")
                    processed += 1
        except Exception as e:
            print(f"Error processing schedule for profile {schedule.get('profile_id')}: {str(e)}")
            traceback.print_exc()
            errors.append(f"Profile {schedule.get('profile_id')}: {str(e)}")
    
    # Save updated schedules
    if processed > 0:
        try:
            db.storage.json.put(schedules_key, schedules)
        except Exception as e:
            print(f"Error saving updated schedules: {str(e)}")
            errors.append(f"Error saving schedules: {str(e)}")
    
    return {
        "success": len(errors) == 0,
        "processed": processed,
        "errors": errors
    }
