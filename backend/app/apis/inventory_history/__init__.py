from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import os
import uuid
import re
import json
import pandas as pd
import numpy as np
from fastapi import APIRouter, HTTPException, Query, Path, Depends
from pydantic import BaseModel, Field
import databutton as db

router = APIRouter()

# Helper function to sanitize storage keys
def sanitize_storage_key(key: str) -> str:
    """Sanitize a storage key to only include alphanumeric characters, dots, hyphens and underscores"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

# Pydantic models
class InventoryHistoryEntry(BaseModel):
    product_id: str
    timestamp: str
    stock_level: int
    change_amount: int
    change_type: str  # purchase_order, sale, adjustment, return, initial
    batch_id: Optional[str] = None
    order_id: Optional[str] = None
    purchase_order_id: Optional[str] = None
    notes: Optional[str] = None

class InventoryHistoryResponse(BaseModel):
    product_id: str
    history: List[Dict[str, Any]]
    total_entries: int

class ForecastRequest(BaseModel):
    product_id: str
    days_to_forecast: int = Field(30, description="Number of days to forecast ahead")
    include_history: bool = Field(False, description="Whether to include historical data in response")

class ForecastDataPoint(BaseModel):
    date: str
    predicted_demand: float
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    confidence: Optional[float] = None

class ForecastResponse(BaseModel):
    product_id: str
    forecast: List[ForecastDataPoint]
    avg_daily_demand: float
    recommended_reorder_point: Optional[int] = None
    recommended_safety_stock: Optional[int] = None
    history: Optional[List[Dict[str, Any]]] = None
    model_type: str = "simple_moving_average"

@router.post("/inventory-history", response_model=Dict[str, Any])
def record_inventory_change(entry: InventoryHistoryEntry) -> Dict[str, Any]:
    """Record a change in inventory level for historical tracking"""
    try:
        # Sanitize product_id for storage key
        product_id = sanitize_storage_key(entry.product_id)
        
        # Get current history or create new
        history_key = f"inventory_history_{product_id}"
        
        try:
            history = db.storage.json.get(history_key)
        except FileNotFoundError:
            history = []
        
        # Create new history entry
        history_entry = entry.dict()
        
        # Add entry to history
        history.append(history_entry)
        
        # Save updated history
        db.storage.json.put(history_key, history)
        
        return {
            "success": True,
            "message": "Inventory change recorded successfully",
            "entry_id": len(history) - 1
        }
    except Exception as e:
        print(f"Error recording inventory history: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error recording inventory history: {str(e)}"
        )

@router.get("/inventory-history/{product_id}", response_model=InventoryHistoryResponse)
def get_inventory_history(
    product_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
    change_type: Optional[str] = None
) -> Dict[str, Any]:
    """Get historical inventory changes for a product"""
    try:
        # Sanitize product_id for storage key
        product_id_key = sanitize_storage_key(product_id)
        history_key = f"inventory_history_{product_id_key}"
        
        try:
            history = db.storage.json.get(history_key)
        except FileNotFoundError:
            history = []
        
        # Filter by date range if provided
        filtered_history = history
        
        if start_date:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            filtered_history = [h for h in filtered_history if datetime.fromisoformat(h["timestamp"].replace('Z', '+00:00')) >= start]
        
        if end_date:
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            filtered_history = [h for h in filtered_history if datetime.fromisoformat(h["timestamp"].replace('Z', '+00:00')) <= end]
        
        # Filter by change type if provided
        if change_type:
            filtered_history = [h for h in filtered_history if h["change_type"] == change_type]
        
        # Sort by timestamp (newest first)
        filtered_history.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Apply limit
        limited_history = filtered_history[:limit]
        
        return {
            "product_id": product_id,
            "history": limited_history,
            "total_entries": len(filtered_history)
        }
    except Exception as e:
        print(f"Error retrieving inventory history: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving inventory history: {str(e)}"
        )

@router.post("/forecast/{product_id}", response_model=ForecastResponse)
def forecast_demand(product_id: str, request: ForecastRequest) -> Dict[str, Any]:
    """Forecast demand for a product based on historical data"""
    try:
        # Sanitize product_id for storage key
        product_id_key = sanitize_storage_key(product_id)
        history_key = f"inventory_history_{product_id_key}"
        
        # Get inventory history
        try:
            history = db.storage.json.get(history_key)
        except FileNotFoundError:
            raise HTTPException(
                status_code=404,
                detail=f"No historical data found for product {product_id}"
            )
        
        # Filter history to only include sales (negative changes)
        sales_history = [h for h in history if h["change_type"] == "sale" and h["change_amount"] < 0]
        
        if len(sales_history) < 7:  # Need at least a week of data
            # If not enough data, use a very simple approach
            if sales_history:
                # Calculate average daily demand from available data
                total_sales = sum(abs(h["change_amount"]) for h in sales_history)
                
                # Get date range
                dates = [datetime.fromisoformat(h["timestamp"].replace('Z', '+00:00')) for h in sales_history]
                min_date = min(dates)
                max_date = max(dates)
                date_range = (max_date - min_date).days + 1
                
                # Calculate daily average
                avg_daily_demand = total_sales / max(date_range, 1)
            else:
                avg_daily_demand = 0
            
            # Generate forecast
            forecast = []
            today = datetime.utcnow().date()
            
            for i in range(request.days_to_forecast):
                forecast_date = today + timedelta(days=i)
                forecast.append({
                    "date": forecast_date.isoformat(),
                    "predicted_demand": avg_daily_demand,
                    "lower_bound": max(0, avg_daily_demand * 0.7),
                    "upper_bound": avg_daily_demand * 1.3,
                    "confidence": 0.5  # Low confidence with limited data
                })
            
            # Calculate recommended reorder point
            lead_time = 7  # Assume 7 days lead time as default
            safety_factor = 1.5  # Conservative safety factor with limited data
            recommended_safety_stock = int(avg_daily_demand * lead_time * safety_factor) if avg_daily_demand > 0 else 5
            recommended_reorder_point = int(avg_daily_demand * lead_time) + recommended_safety_stock
            
            result = {
                "product_id": product_id,
                "forecast": forecast,
                "avg_daily_demand": avg_daily_demand,
                "recommended_reorder_point": recommended_reorder_point,
                "recommended_safety_stock": recommended_safety_stock,
                "model_type": "basic_average"
            }
            
            # Include history if requested
            if request.include_history:
                result["history"] = history
            
            return result
        
        # If we have enough data, use a more sophisticated approach
        # Group by date and sum quantities
        sales_data = {}
        for sale in sales_history:
            date_str = datetime.fromisoformat(sale["timestamp"].replace('Z', '+00:00')).date().isoformat()
            if date_str not in sales_data:
                sales_data[date_str] = 0
            sales_data[date_str] += abs(sale["change_amount"])
        
        # Convert to DataFrame for time series analysis
        df = pd.DataFrame(list(sales_data.items()), columns=["date", "quantity"])
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
        
        # Fill missing dates with zeros
        date_range = pd.date_range(start=df["date"].min(), end=df["date"].max())
        df = df.set_index("date").reindex(date_range, fill_value=0).reset_index()
        df.columns = ["date", "quantity"]
        
        # Simple moving average forecast
        window_size = min(7, len(df))  # Use at most 7 days for moving average
        df["ma"] = df["quantity"].rolling(window=window_size, min_periods=1).mean()
        
        # Calculate standard deviation for confidence intervals
        df["std"] = df["quantity"].rolling(window=window_size, min_periods=1).std()
        df["std"] = df["std"].fillna(df["std"].mean())
        
        # Calculate average daily demand
        avg_daily_demand = df["quantity"].mean()
        
        # Generate forecast
        forecast = []
        last_date = df["date"].max().date()
        last_ma = df["ma"].iloc[-1]
        last_std = max(df["std"].iloc[-1], 0.1 * last_ma)  # Ensure some variation
        
        for i in range(1, request.days_to_forecast + 1):
            forecast_date = last_date + timedelta(days=i)
            predicted_demand = last_ma
            lower_bound = max(0, predicted_demand - 1.96 * last_std)  # 95% confidence interval
            upper_bound = predicted_demand + 1.96 * last_std
            
            forecast.append({
                "date": forecast_date.isoformat(),
                "predicted_demand": float(predicted_demand),
                "lower_bound": float(lower_bound),
                "upper_bound": float(upper_bound),
                "confidence": 0.95
            })
        
        # Calculate recommended reorder point and safety stock
        # Try to get lead time from supplier info if available
        lead_time = 7  # Default lead time in days
        try:
            # Check if this product has supplier info with lead time
            from app.apis.supplier import list_suppliers
            from app.apis.inventory import get_product_inventory
            
            # Get product inventory with batch info to find supplier
            inventory = get_product_inventory(product_id, include_batches=True)
            supplier_id = None
            
            # Look for supplier info in batch data
            if inventory.get("batch_tracking", False) and inventory.get("batch_info"):
                for batch_data in inventory.get("batch_info", {}).values():
                    if batch_data.get("supplier_id"):
                        supplier_id = batch_data.get("supplier_id")
                        break
            
            if supplier_id:
                # Get supplier info
                suppliers_response = list_suppliers()
                for supplier in suppliers_response.get("suppliers", []):
                    if supplier.get("id") == supplier_id and supplier.get("lead_time_days"):
                        lead_time = supplier.get("lead_time_days")
                        break
        except Exception as e:
            # Continue with default lead time
            print(f"Error getting supplier lead time: {e}")
        
        # Calculate safety stock and reorder point
        # Use simple formula: Safety Stock = Z * σ * √L where Z is safety factor, σ is std dev, L is lead time
        safety_factor = 1.645  # 95% service level
        std_dev = float(df["quantity"].std())
        recommended_safety_stock = int(safety_factor * std_dev * (lead_time ** 0.5)) if std_dev > 0 else int(0.5 * avg_daily_demand * lead_time)
        recommended_reorder_point = int(avg_daily_demand * lead_time) + recommended_safety_stock
        
        result = {
            "product_id": product_id,
            "forecast": forecast,
            "avg_daily_demand": float(avg_daily_demand),
            "recommended_reorder_point": recommended_reorder_point,
            "recommended_safety_stock": recommended_safety_stock,
            "model_type": "moving_average"
        }
        
        # Include history if requested
        if request.include_history:
            result["history"] = history
        
        return result
    
    except Exception as e:
        print(f"Error generating forecast: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating forecast: {str(e)}"
        )

@router.get("/inventory-history-aggregated/{product_id}", response_model=Dict[str, Any])
def get_aggregated_history(
    product_id: str,
    interval: str = "day",  # day, week, month
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """Get aggregated historical inventory data for a product"""
    try:
        # Sanitize product_id for storage key
        product_id_key = sanitize_storage_key(product_id)
        history_key = f"inventory_history_{product_id_key}"
        
        try:
            history = db.storage.json.get(history_key)
        except FileNotFoundError:
            return {
                "product_id": product_id,
                "data": [],
                "interval": interval
            }
        
        # Filter by date range if provided
        filtered_history = history
        
        if start_date:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            filtered_history = [h for h in filtered_history if datetime.fromisoformat(h["timestamp"].replace('Z', '+00:00')) >= start]
        
        if end_date:
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            filtered_history = [h for h in filtered_history if datetime.fromisoformat(h["timestamp"].replace('Z', '+00:00')) <= end]
        
        # Group by interval
        aggregated_data = {}
        
        for entry in filtered_history:
            date = datetime.fromisoformat(entry["timestamp"].replace('Z', '+00:00'))
            
            if interval == "day":
                key = date.date().isoformat()
            elif interval == "week":
                # ISO week format: YYYY-WW
                key = f"{date.year}-W{date.isocalendar()[1]:02d}"
            elif interval == "month":
                key = f"{date.year}-{date.month:02d}"
            else:
                # Default to day
                key = date.date().isoformat()
            
            if key not in aggregated_data:
                aggregated_data[key] = {
                    "period": key,
                    "total_changes": 0,
                    "sales": 0,
                    "incoming": 0,
                    "adjustments": 0,
                    "returns": 0
                }
            
            change_amount = entry["change_amount"]
            change_type = entry["change_type"]
            
            aggregated_data[key]["total_changes"] += 1
            
            if change_type == "sale":
                aggregated_data[key]["sales"] += abs(change_amount) if change_amount < 0 else 0
            elif change_type == "purchase_order":
                aggregated_data[key]["incoming"] += change_amount if change_amount > 0 else 0
            elif change_type == "return":
                aggregated_data[key]["returns"] += change_amount if change_amount > 0 else 0
            else:  # adjustment or other
                aggregated_data[key]["adjustments"] += change_amount
        
        # Convert to list and sort by period
        result_data = list(aggregated_data.values())
        result_data.sort(key=lambda x: x["period"])
        
        return {
            "product_id": product_id,
            "data": result_data,
            "interval": interval
        }
    
    except Exception as e:
        print(f"Error getting aggregated history: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting aggregated history: {str(e)}"
        )
