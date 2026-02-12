from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
import streamlit as st
import io
import sys
from contextlib import redirect_stdout, redirect_stderr
from pydantic import BaseModel

router = APIRouter(prefix="/vaultos-streamlit")

# Helper function to run Streamlit code
def run_streamlit_app(script_code):
    # Capture stdout and stderr to return
    buffer = io.StringIO()
    with redirect_stdout(buffer), redirect_stderr(buffer):
        # Create a temporary module to execute the code
        try:
            exec(script_code, {"st": st})
            return {"success": True, "output": buffer.getvalue()}
        except Exception as e:
            return {"success": False, "error": str(e), "output": buffer.getvalue()}

@router.get("/", response_class=HTMLResponse)
def serve_vaultos_app():
    """Serve the VaultOS Streamlit application. This endpoint provides the core VaultOS interface
    that allows users to manage their family trust funds and investments."""
    # Basic HTML page that loads the Streamlit app in an iframe
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Legacy Vault OS</title>
        <style>
            body, html {
                margin: 0;
                padding: 0;
                height: 100%;
                overflow: hidden;
                background-color: #0f172a;
            }
            iframe {
                width: 100%;
                height: 100%;
                border: none;
            }
        </style>
    </head>
    <body>
        <iframe src="/vaultos-streamlit/dashboard" allow="camera;microphone"></iframe>
    </body>
    </html>
    """

class DashboardRequest(BaseModel):
    preset: str = "default"

@router.post("/dashboard")
def render_dashboard(request: DashboardRequest):
    """Render the VaultOS dashboard with real-time portfolio management, investment tracking,
    and trust fund administration features."""
    dashboard_code = """
    import streamlit as st
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    import time
    import json
    
    # Initialize session state for persistent settings
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.theme = "dark"
        st.session_state.selected_section = "Dashboard"
        st.session_state.user_preferences = {
            "show_experimental": False,
            "auto_invest": False,
            "notification_level": "Medium"
        }
    
    # Sidebar for navigation
    with st.sidebar:
        st.image("https://via.placeholder.com/150x150.png?text=Legacy+Vault", width=150)
        st.title("VaultOS")        
        
        # Navigation menu
        sections = [
            "Dashboard", 
            "Portfolio Manager", 
            "Bitcoin Tracker", 
            "Family Profiles", 
            "Trust Distribution", 
            "Investment Strategy", 
            "Security Center", 
            "Settings"
        ]
        
        selected = st.radio("Navigation", sections, index=sections.index(st.session_state.selected_section))
        st.session_state.selected_section = selected
        
        # User preferences section
        st.sidebar.markdown("---")
        with st.sidebar.expander("User Preferences"):
            st.session_state.user_preferences["show_experimental"] = st.checkbox(
                "Show Experimental Features", 
                value=st.session_state.user_preferences["show_experimental"]
            )
            st.session_state.user_preferences["auto_invest"] = st.checkbox(
                "Enable Auto-Investment", 
                value=st.session_state.user_preferences["auto_invest"]
            )
            st.session_state.user_preferences["notification_level"] = st.select_slider(
                "Notification Level", 
                options=["Low", "Medium", "High"], 
                value=st.session_state.user_preferences["notification_level"]
            )
    
    # Main content area
    st.title(f"📊 {st.session_state.selected_section}")
    
    if st.session_state.selected_section == "Dashboard":
        # Dashboard metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Portfolio Value", "$178,532.48", "2.4%")
        with col2:
            st.metric("Bitcoin Holdings", "2.34 BTC", "15.7%")
        with col3:
            st.metric("Trust Fund Performance", "8.3%", "-0.2%")
        
        # Create tabs for different sections
        tab1, tab2, tab3 = st.tabs(["Portfolio Overview", "Recent Transactions", "Investment Opportunities"])
        
        with tab1:
            st.subheader("Portfolio Allocation")
            # Mock data for portfolio allocation
            allocation_data = pd.DataFrame({
                'Asset Class': ['Bitcoin', 'Stocks', 'Bonds', 'Real Estate', 'Cash'],
                'Allocation': [35, 25, 15, 20, 5]
            })
            st.bar_chart(allocation_data.set_index('Asset Class'))
            
            st.subheader("Portfolio Growth")
            # Generate mock historical data
            chart_data = pd.DataFrame(
                np.random.randn(20, 3).cumsum(axis=0) + np.array([100, 50, 30]),
                columns=['Total', 'Bitcoin', 'Traditional']
            )
            st.line_chart(chart_data)
        
        with tab2:
            st.subheader("Recent Transactions")
            transactions = pd.DataFrame({
                'Date': [datetime.now() - timedelta(days=i) for i in range(5)],
                'Type': ['Buy', 'Deposit', 'Buy', 'Sell', 'Withdraw'],
                'Asset': ['Bitcoin', 'Cash', 'Stocks', 'Bonds', 'Bitcoin'],
                'Amount': ['0.1 BTC', '$1,000.00', '$2,500.00', '$1,200.00', '0.05 BTC'],
                'Value': ['$4,320.50', '$1,000.00', '$2,500.00', '$1,200.00', '$2,160.25']
            })
            st.dataframe(transactions, use_container_width=True)
        
        with tab3:
            st.subheader("Investment Opportunities")
            with st.expander("Bitcoin Dollar-Cost Averaging"):
                st.write("Automatically invest a fixed amount in Bitcoin on a regular schedule.")
                dca_amount = st.slider("Monthly Investment Amount", min_value=100, max_value=1000, value=250, step=50)
                st.button("Set Up DCA Plan", key="setup_dca")
            
            with st.expander("Trust Fund Contribution"):
                st.write("Make a contribution to the family trust fund.")
                st.number_input("Contribution Amount", min_value=100, value=1000, step=100)
                st.selectbox("Beneficiary", ["All Children", "Emma McMillan", "Noah McMillan", "Olivia McMillan"])
                st.button("Make Contribution", key="make_contribution")
    
    elif st.session_state.selected_section == "Bitcoin Tracker":
        st.subheader("Bitcoin Investment Tracker")
        
        # Mock Bitcoin price data
        btc_current_price = 43205.50
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Current Bitcoin Price", f"${btc_current_price:,.2f}", "1.2%")
        with col2:
            st.metric("24h Volume", "$42.8B", "5.7%")
        
        # Bitcoin investment summary
        st.subheader("Your Bitcoin Investments")
        investments = pd.DataFrame({
            'Date': [datetime(2022, 1, 15), datetime(2022, 2, 15), datetime(2022, 3, 15), datetime(2022, 4, 15)],
            'Amount': [0.5, 0.3, 0.8, 0.75],
            'Price': [38420.50, 44210.30, 40120.75, 41350.25],
            'Value at Purchase': [19210.25, 13263.09, 32096.60, 31012.69],
            'Current Value': [21602.75, 12961.65, 34564.40, 32404.13],
            'ROI': ['12.5%', '-2.3%', '7.7%', '4.5%']
        })
        st.dataframe(investments, use_container_width=True)
        
        # Bitcoin price chart
        st.subheader("Bitcoin Price History")
        # Generate mock price data
        days = 180
        base = 40000
        noise = np.random.normal(0, 1, days) * 1000
        trend = np.linspace(0, 5000, days) 
        seasonal = 2000 * np.sin(np.linspace(0, 12, days))
        price_data = base + trend + seasonal + noise.cumsum()
        
        btc_history = pd.DataFrame({
            'Date': [datetime.now() - timedelta(days=i) for i in range(days)][::-1],
            'Price': price_data
        })
        st.line_chart(btc_history.set_index('Date'))
        
        # Purchase form
        st.subheader("Purchase Bitcoin")
        with st.form("bitcoin_purchase_form"):
            purchase_amount = st.number_input("Amount to Purchase ($)", min_value=100, value=1000)
            beneficiary = st.selectbox("Beneficiary", ["Emma McMillan", "Noah McMillan", "Olivia McMillan"])
            submitted = st.form_submit_button("Purchase Bitcoin")
            if submitted:
                st.success(f"Purchased approximately {purchase_amount/btc_current_price:.6f} BTC for {beneficiary}")
    
    elif st.session_state.selected_section == "Family Profiles":
        st.subheader("Family Member Profiles")
        
        profiles = [
            {"name": "Emma McMillan", "dob": "2015-06-12", "portfolio": "$68,245.30", "btc": "0.92 BTC"},
            {"name": "Noah McMillan", "dob": "2017-03-25", "portfolio": "$52,129.75", "btc": "0.78 BTC"},
            {"name": "Olivia McMillan", "dob": "2019-11-08", "portfolio": "$38,157.43", "btc": "0.64 BTC"}
        ]
        
        # Tabs for each family member
        tabs = st.tabs([profile["name"] for profile in profiles])
        
        for i, tab in enumerate(tabs):
            with tab:
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.image(f"https://via.placeholder.com/150x150.png?text={profiles[i]['name'].split()[0]}", width=150)
                    st.write(f"**Date of Birth:** {profiles[i]['dob']}")
                    st.write(f"**Age:** {datetime.now().year - datetime.strptime(profiles[i]['dob'], '%Y-%m-%d').year} years")
                    st.write(f"**Portfolio Value:** {profiles[i]['portfolio']}")
                    st.write(f"**Bitcoin Holdings:** {profiles[i]['btc']}")
                
                with col2:
                    st.subheader("Investment Timeline")
                    milestone_dates = [
                        datetime.strptime(profiles[i]['dob'], '%Y-%m-%d') + timedelta(days=365*18),  # 18 years
                        datetime.strptime(profiles[i]['dob'], '%Y-%m-%d') + timedelta(days=365*21),  # 21 years
                        datetime.strptime(profiles[i]['dob'], '%Y-%m-%d') + timedelta(days=365*25),  # 25 years
                        datetime.strptime(profiles[i]['dob'], '%Y-%m-%d') + timedelta(days=365*30)   # 30 years
                    ]
                    
                    milestone_labels = ["18th Birthday", "21st Birthday", "25th Birthday", "30th Birthday"]
                    milestones = pd.DataFrame({
                        'Date': milestone_dates,
                        'Event': milestone_labels,
                        'Projected Value': ["$125K", "$175K", "$250K", "$500K"]
                    })
                    st.dataframe(milestones, use_container_width=True)
                    
                    # Visual timeline
                    st.subheader("Growth Projection")
                    years = [(datetime.now() + timedelta(days=365*i)).year for i in range(20)]
                    
                    base_value = float(profiles[i]['portfolio'].replace('$', '').replace(',', ''))
                    growth_rates = 1.15 ** np.arange(20)  # 15% annual growth
                    projections = base_value * growth_rates
                    
                    projection_data = pd.DataFrame({
                        'Year': years,
                        'Projected Value': projections
                    })
                    st.line_chart(projection_data.set_index('Year'))
    
    elif st.session_state.selected_section == "Settings":
        st.subheader("VaultOS Settings")
        
        with st.expander("System Preferences", expanded=True):
            st.selectbox("Theme", ["Dark", "Light"], index=0 if st.session_state.theme == "dark" else 1)
            st.toggle("Enable Notifications", value=True)
            st.slider("Data Refresh Interval (minutes)", min_value=1, max_value=60, value=15)
        
        with st.expander("Security Settings"):
            st.toggle("Two-Factor Authentication", value=True)
            st.selectbox("Login Session Timeout", ["15 minutes", "30 minutes", "1 hour", "4 hours"], index=1)
            st.button("Reset Security Credentials")
        
        with st.expander("Backup & Recovery"):
            st.write("Configure automatic backups of your investment data")
            st.selectbox("Backup Frequency", ["Daily", "Weekly", "Monthly"], index=1)
            st.button("Create Manual Backup")
            st.button("Restore from Backup")
    
    else:
        st.info(f"The {st.session_state.selected_section} section is under development.")
        st.image("https://via.placeholder.com/600x400.png?text=Coming+Soon", use_column_width=True)
    
    # Footer
    st.markdown("---")
    st.caption("Legacy Vault OS v1.0 | © 2025 McMillan Family Trust | Developed with Streamlit")
    """
    
    return run_streamlit_app(dashboard_code)
