"""
Monday Analyst - Sales Trend Analyzer
Finds marketing hooks based on sales data.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

from app.db.supabase import get_supabase_client


from app.models.schemas import StrategyType


@dataclass
class Insight:
    """Represents an analytical insight."""
    strategy_type: StrategyType
    insight_text: str
    target_data: Dict[str, Any]


async def analyze_restaurant(restaurant_id: str) -> List[Insight]:
    """
    Run all analyses for a restaurant and return actionable insights.
    This is the "Monday Analyst" that identifies marketing opportunities.
    """
    insights = []
    
    # Run each analysis strategy
    bestseller = await find_bestseller(restaurant_id)
    if bestseller:
        insights.append(bestseller)
    
    slow_day = await find_slow_day(restaurant_id)
    if slow_day:
        insights.append(slow_day)
    
    churning = await find_churning_customers(restaurant_id)
    if churning:
        insights.append(churning)
    
    return insights


async def find_bestseller(restaurant_id: str) -> Optional[Insight]:
    """
    Find the most popular item among dine-in customers last week.
    
    SQL Logic:
    SELECT item_ordered FROM universal_records
    WHERE visit_date > (now() - interval '7 days') AND source = 'Dine-In'
    GROUP BY item_ordered ORDER BY count(*) DESC LIMIT 1;
    """
    supabase = get_supabase_client()
    
    # Query for bestseller
    result = supabase.rpc(
        "get_bestseller",
        {"p_restaurant_id": restaurant_id, "p_days": 7}
    ).execute()
    
    if not result.data or not result.data[0]:
        return None
    
    item = result.data[0].get("item_ordered", "your special dish")
    count = result.data[0].get("order_count", 0)
    
    return Insight(
        strategy_type=StrategyType.BEST_SELLER,
        insight_text=f"🔥 {item} was ordered {count} times last week! Your customers love it.",
        target_data={"item": item, "count": count}
    )


async def find_slow_day(restaurant_id: str) -> Optional[Insight]:
    """
    Identify the slowest day of the week for the restaurant.
    Useful for planning Tuesday/Wednesday promotions.
    """
    supabase = get_supabase_client()
    
    # Query for slowest day
    result = supabase.rpc(
        "get_slowest_day",
        {"p_restaurant_id": restaurant_id, "p_weeks": 4}
    ).execute()
    
    if not result.data or not result.data[0]:
        return None
    
    day_name = result.data[0].get("day_name", "Tuesday")
    avg_orders = result.data[0].get("avg_orders", 0)
    
    return Insight(
        strategy_type=StrategyType.SLOW_DAY,
        insight_text=f"📉 {day_name}s are slow with only {avg_orders:.0f} avg orders. Perfect for a promo!",
        target_data={"day": day_name, "avg_orders": avg_orders}
    )


async def find_churning_customers(restaurant_id: str) -> Optional[Insight]:
    """
    Find customers who haven't visited in 30+ days but were regulars before.
    """
    supabase = get_supabase_client()
    
    # Query for churning customers
    result = supabase.rpc(
        "get_churning_customers",
        {"p_restaurant_id": restaurant_id, "p_inactive_days": 30}
    ).execute()
    
    if not result.data:
        return None
    
    count = len(result.data)
    
    if count < 5:  # Not enough to justify a campaign
        return None
    
    return Insight(
        strategy_type=StrategyType.CHURN_RECOVERY,
        insight_text=f"😢 {count} regular customers haven't visited in 30+ days. Win them back!",
        target_data={"count": count, "phones": [r["client_phone"] for r in result.data]}
    )


async def get_weekly_stats(restaurant_id: str) -> Dict[str, Any]:
    """Get summary statistics for the past week."""
    supabase = get_supabase_client()
    
    result = supabase.rpc(
        "get_weekly_stats",
        {"p_restaurant_id": restaurant_id}
    ).execute()
    
    if not result.data:
        return {
            "new_customers": 0,
            "total_orders": 0,
            "total_revenue": 0
        }
    
    return result.data[0]
