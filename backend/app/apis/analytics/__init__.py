from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import databutton as db
from firebase_admin import firestore

router = APIRouter(prefix="/analytics")

# Initialize Firestore DB
db_firestore = firestore.client()

# Collection constants
COLLECTIONS = {
    "ORDERS": "orders",
    "PRODUCTS": "products",
    "INVENTORY": "inventory"
}

# Model definitions
class TimeRangeParams(BaseModel):
    """Parameters for time range filtering"""
    start_date: Optional[str] = None  # ISO format date string
    end_date: Optional[str] = None    # ISO format date string
    period: Optional[str] = "daily"  # daily, weekly, monthly

class SalesMetricsResponse(BaseModel):
    """Response model for sales metrics"""
    total_sales: int  # Total revenue in cents
    order_count: int
    average_order_value: int  # In cents
    time_period: Dict[str, str]  # Start and end dates of the period
    period_comparison: Optional[Dict[str, Any]] = None  # Comparison with previous period

class SalesTrendsResponse(BaseModel):
    """Response model for sales trends over time"""
    data_points: List[Dict[str, Any]]  # List of data points (date, sales, orders)
    totals: Dict[str, Any]  # Aggregated totals
    period: str  # daily, weekly, monthly

class ProductPerformanceResponse(BaseModel):
    """Response model for product performance"""
    products: List[Dict[str, Any]]  # List of products with sales metrics
    top_performers: List[Dict[str, Any]]  # Top selling products
    worst_performers: List[Dict[str, Any]]  # Worst selling products

class CustomerMetricsResponse(BaseModel):
    """Response model for customer metrics"""
    total_customers: int
    new_customers: int  # New customers in the time period
    returning_customers: int  # Returning customers in the time period
    avg_ltv: Optional[int] = None  # Average lifetime value in cents

class FullDashboardResponse(BaseModel):
    """Combined response with all dashboard metrics"""
    sales_metrics: SalesMetricsResponse
    sales_trends: SalesTrendsResponse
    product_performance: ProductPerformanceResponse
    customer_metrics: Optional[CustomerMetricsResponse] = None

def get_date_range(start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Calculate start and end dates for the query"""
    now = datetime.utcnow()
    
    if end_date:
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    else:
        end = now
    
    if start_date:
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
    else:
        # Default to last 30 days if no start date provided
        start = end - timedelta(days=30)
    
    # Ensure end is at the end of the day
    end = end.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # Ensure start is at the beginning of the day
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    
    return start, end

def group_data_by_period(data, period, start_date, end_date):
    """Group data by the specified period (daily, weekly, monthly)"""
    result = []
    current = start_date
    
    if period == "daily":
        delta = timedelta(days=1)
        format_string = "%Y-%m-%d"
    elif period == "weekly":
        delta = timedelta(weeks=1)
        format_string = "%Y-W%W"  # ISO week format
    elif period == "monthly":
        delta = timedelta(days=1)  # Will be adjusted for each month
        format_string = "%Y-%m"
    else:
        # Default to daily
        delta = timedelta(days=1)
        format_string = "%Y-%m-%d"
    
    # Initialize buckets
    buckets = {}
    
    # Prepare empty buckets for each period
    while current <= end_date:
        if period == "monthly" and current.month == 12:
            next_date = datetime(current.year + 1, 1, 1)
        elif period == "monthly":
            next_date = datetime(current.year, current.month + 1, 1)
        else:
            next_date = current + delta
        
        period_key = current.strftime(format_string)
        
        if period_key not in buckets:
            buckets[period_key] = {
                "period": period_key,
                "sales": 0,
                "orders": 0,
                "start_date": current.isoformat(),
                "end_date": (next_date - timedelta(microseconds=1)).isoformat()
            }
        
        if period == "monthly":
            current = next_date
        else:
            current += delta
    
    # Fill buckets with data
    for item in data:
        date = datetime.fromisoformat(item.get("created_at").replace('Z', '+00:00'))
        period_key = date.strftime(format_string)
        
        if period_key in buckets:
            buckets[period_key]["sales"] += item.get("total", 0)
            buckets[period_key]["orders"] += 1
    
    # Convert buckets to sorted list
    result = list(buckets.values())
    result.sort(key=lambda x: x["period"])
    
    return result

@router.get("/health")
def check_analytics_health():
    """Check if the Analytics API is operational"""
    return {"status": "ok", "message": "Analytics API is operational"}

@router.get("/sales-metrics", response_model=SalesMetricsResponse)
def get_sales_metrics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    compare_previous: bool = False
):
    """Get aggregated sales metrics for a given time period"""
    try:
        start, end = get_date_range(start_date, end_date)
        
        # Query orders within the date range
        orders_ref = db_firestore.collection(COLLECTIONS["ORDERS"])
        orders = orders_ref.where("created_at", ">", start.isoformat()).where("created_at", "<=", end.isoformat()).get()
        
        # Calculate metrics
        order_documents = [order.to_dict() for order in orders]
        total_sales = sum(order.get("total", 0) for order in order_documents)
        order_count = len(order_documents)
        avg_order_value = total_sales // order_count if order_count > 0 else 0
        
        result = {
            "total_sales": total_sales,
            "order_count": order_count,
            "average_order_value": avg_order_value,
            "time_period": {
                "start_date": start.isoformat(),
                "end_date": end.isoformat()
            }
        }
        
        # Compare with previous period if requested
        if compare_previous:
            period_duration = end - start
            prev_end = start - timedelta(microseconds=1)
            prev_start = prev_end - period_duration
            
            prev_orders = orders_ref.where("created_at", ">", prev_start.isoformat()).where("created_at", "<=", prev_end.isoformat()).get()
            prev_order_documents = [order.to_dict() for order in prev_orders]
            prev_total_sales = sum(order.get("total", 0) for order in prev_order_documents)
            prev_order_count = len(prev_order_documents)
            prev_avg_order_value = prev_total_sales // prev_order_count if prev_order_count > 0 else 0
            
            # Calculate percentage changes
            sales_change_pct = ((total_sales - prev_total_sales) / prev_total_sales * 100) if prev_total_sales > 0 else None
            order_count_change_pct = ((order_count - prev_order_count) / prev_order_count * 100) if prev_order_count > 0 else None
            aov_change_pct = ((avg_order_value - prev_avg_order_value) / prev_avg_order_value * 100) if prev_avg_order_value > 0 else None
            
            result["period_comparison"] = {
                "previous_period": {
                    "start_date": prev_start.isoformat(),
                    "end_date": prev_end.isoformat(),
                    "total_sales": prev_total_sales,
                    "order_count": prev_order_count,
                    "average_order_value": prev_avg_order_value
                },
                "changes": {
                    "total_sales_change": total_sales - prev_total_sales,
                    "total_sales_change_pct": sales_change_pct,
                    "order_count_change": order_count - prev_order_count,
                    "order_count_change_pct": order_count_change_pct,
                    "aov_change": avg_order_value - prev_avg_order_value,
                    "aov_change_pct": aov_change_pct
                }
            }
        
        return result
    
    except Exception as e:
        print(f"Error getting sales metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve sales metrics: {str(e)}")

@router.get("/sales-trends", response_model=SalesTrendsResponse)
def get_sales_trends(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    period: str = "daily"
):
    """Get sales trends over time, grouped by period"""
    try:
        start, end = get_date_range(start_date, end_date)
        
        # Query orders within the date range
        orders_ref = db_firestore.collection(COLLECTIONS["ORDERS"])
        orders = orders_ref.where("created_at", ">", start.isoformat()).where("created_at", "<=", end.isoformat()).get()
        
        order_documents = [order.to_dict() for order in orders]
        
        # Group by period
        data_points = group_data_by_period(order_documents, period, start, end)
        
        # Calculate totals
        total_sales = sum(dp["sales"] for dp in data_points)
        total_orders = sum(dp["orders"] for dp in data_points)
        
        return {
            "data_points": data_points,
            "totals": {
                "total_sales": total_sales,
                "total_orders": total_orders,
                "average_order_value": total_sales // total_orders if total_orders > 0 else 0
            },
            "period": period
        }
    
    except Exception as e:
        print(f"Error getting sales trends: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve sales trends: {str(e)}")

@router.get("/product-performance", response_model=ProductPerformanceResponse)
def get_product_performance(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 10
):
    """Get product performance metrics"""
    try:
        start, end = get_date_range(start_date, end_date)
        
        # Query orders within the date range
        orders_ref = db_firestore.collection(COLLECTIONS["ORDERS"])
        orders = orders_ref.where("created_at", ">", start.isoformat()).where("created_at", "<=", end.isoformat()).get()
        
        order_documents = [order.to_dict() for order in orders]
        
        # Extract items from all orders
        product_performance = {}
        
        for order in order_documents:
            for item in order.get("items", []):
                product_id = item.get("product_id")
                product_name = item.get("product_name")
                quantity = item.get("quantity", 0)
                subtotal = item.get("subtotal", 0)
                
                if product_id not in product_performance:
                    product_performance[product_id] = {
                        "product_id": product_id,
                        "name": product_name,
                        "quantity_sold": 0,
                        "revenue": 0,
                        "order_count": 0
                    }
                
                product_performance[product_id]["quantity_sold"] += quantity
                product_performance[product_id]["revenue"] += subtotal
                product_performance[product_id]["order_count"] += 1
        
        # Convert to list and sort by revenue
        products = list(product_performance.values())
        products.sort(key=lambda x: x["revenue"], reverse=True)
        
        for product in products:
            # Calculate average order value for this product
            product["average_item_value"] = product["revenue"] // product["quantity_sold"] if product["quantity_sold"] > 0 else 0
        
        # Extract top and worst performers
        top_performers = products[:limit] if products else []
        worst_performers = products[-limit:] if len(products) >= limit else []
        worst_performers.reverse()  # Ascending order for worst performers
        
        return {
            "products": products,
            "top_performers": top_performers,
            "worst_performers": worst_performers
        }
    
    except Exception as e:
        print(f"Error getting product performance: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve product performance: {str(e)}")

@router.get("/customer-metrics", response_model=CustomerMetricsResponse)
def get_customer_metrics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get customer metrics"""
    try:
        start, end = get_date_range(start_date, end_date)
        
        # Query all orders to get customer history
        orders_ref = db_firestore.collection(COLLECTIONS["ORDERS"])
        all_orders = orders_ref.get()
        all_order_documents = [order.to_dict() for order in all_orders]
        
        # Query orders within the current date range
        period_orders = orders_ref.where("created_at", ">", start.isoformat()).where("created_at", "<=", end.isoformat()).get()
        period_order_documents = [order.to_dict() for order in period_orders]
        
        # Track all customers and their first order dates
        all_customers = {}
        for order in all_order_documents:
            user_id = order.get("user_id")
            email = order.get("email")
            created_at = order.get("created_at")
            
            # Use email as identifier if user_id is not available
            customer_id = user_id if user_id else email
            
            if customer_id not in all_customers:
                all_customers[customer_id] = {
                    "id": customer_id,
                    "first_order_date": created_at,
                    "orders": [],
                    "total_spent": 0
                }
            
            # Add order to customer history
            all_customers[customer_id]["orders"].append({
                "order_id": order.get("id"),
                "date": created_at,
                "total": order.get("total", 0)
            })
            
            # Update total spent
            all_customers[customer_id]["total_spent"] += order.get("total", 0)
        
        # Identify customers with orders in the current period
        period_customers = set()
        for order in period_order_documents:
            user_id = order.get("user_id")
            email = order.get("email")
            customer_id = user_id if user_id else email
            period_customers.add(customer_id)
        
        # Identify new vs. returning customers
        new_customers = 0
        returning_customers = 0
        
        for customer_id in period_customers:
            customer = all_customers.get(customer_id)
            if customer:
                # Check if first order is within the current period
                first_order_date = datetime.fromisoformat(customer["first_order_date"].replace('Z', '+00:00'))
                if first_order_date > start and first_order_date <= end:
                    new_customers += 1
                else:
                    returning_customers += 1
        
        # Calculate average lifetime value
        total_customers = len(all_customers)
        total_revenue = sum(customer["total_spent"] for customer in all_customers.values())
        avg_ltv = total_revenue // total_customers if total_customers > 0 else 0
        
        return {
            "total_customers": total_customers,
            "new_customers": new_customers,
            "returning_customers": returning_customers,
            "avg_ltv": avg_ltv
        }
    
    except Exception as e:
        print(f"Error getting customer metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve customer metrics: {str(e)}")

@router.get("/dashboard", response_model=FullDashboardResponse)
def get_dashboard(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    period: str = "daily",
    compare_previous: bool = True,
    product_limit: int = 5
):
    """Get all dashboard metrics in a single request"""
    try:
        # Get all metrics using the other endpoints
        sales_metrics = get_sales_metrics(start_date, end_date, compare_previous)
        sales_trends = get_sales_trends(start_date, end_date, period)
        product_performance = get_product_performance(start_date, end_date, product_limit)
        
        # Customer metrics are optional as they are more calculation intensive
        try:
            customer_metrics = get_customer_metrics(start_date, end_date)
        except Exception as e:
            print(f"Error calculating customer metrics: {str(e)}")
            customer_metrics = None
        
        return {
            "sales_metrics": sales_metrics,
            "sales_trends": sales_trends,
            "product_performance": product_performance,
            "customer_metrics": customer_metrics
        }
    
    except Exception as e:
        print(f"Error generating dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate dashboard: {str(e)}")
