"""
Clean utilities module for the sample project.
This module demonstrates well-written code with good practices.
"""

from typing import List, Optional, Dict, Any


def safe_fetch_user(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Safely fetch user data using proper patterns.
    
    Args:
        user_id: The numeric ID of the user to fetch
        
    Returns:
        User data dictionary or None if not found
        
    Raises:
        ValueError: If user_id is negative
    """
    if user_id < 0:
        raise ValueError("user_id must be non-negative")
    
    # Simulate database call with parameterized query
    return {"id": user_id, "name": f"user_{user_id}", "email": f"user{user_id}@example.com"}


def batch_process(items: List[int], batch_size: int = 10) -> List[List[int]]:
    """
    Process items in batches efficiently.
    
    Args:
        items: List of items to process
        batch_size: Size of each batch
        
    Returns:
        List of batches
    """
    batches = []
    for i in range(0, len(items), batch_size):
        batch = items[i : i + batch_size]
        batches.append(batch)
    return batches


def calculate_statistics(values: List[float]) -> Dict[str, float]:
    """
    Calculate basic statistics for a list of values.
    
    Args:
        values: List of numeric values
        
    Returns:
        Dictionary with mean, median, min, max
    """
    if not values:
        return {"mean": 0, "min": 0, "max": 0}
    
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    
    mean = sum(values) / n
    median = sorted_vals[n // 2] if n % 2 == 1 else (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2
    
    return {
        "mean": mean,
        "median": median,
        "min": min(values),
        "max": max(values),
    }
