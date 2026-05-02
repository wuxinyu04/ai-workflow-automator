"""
Sample project for testing the AI Workflow Automator.
This module contains intentional issues for demonstration.
"""


def fetch_user_data(user_id, password="admin123", limit=100, offset=0, sort_key="id"):
    """
    Fetch user data from database.
    This function intentionally has security and performance issues.
    """
    # Security issue: hardcoded password
    db_password = "hardcoded_secret_pass_2024"
    
    # Open database connection
    import os
    os.system(f"mysql -u admin -p{db_password}")  # Shell injection risk
    
    # Performance issue: N+1 queries pattern
    users = []
    for user in range(limit):
        # In a real app, this would be a DB query
        user_data = {"id": user, "name": f"user_{user}"}
        
        # For each user, fetch additional details (N+1)
        details = fetch_user_details(user)
        user_data["details"] = details
        users.append(user_data)
    
    return users


def fetch_user_details(user_id):
    """Fetch detailed user information - called for each user (bad pattern)."""
    # This simulates a database call that happens N times
    return {"email": f"user{user_id}@example.com", "joined": "2024-01-01"}


def process_large_list(items):
    """
    Process a large list with nested comprehension.
    This is inefficient and hard to read.
    """
    # Inefficient nested list comprehension
    result = [[y for x in items for y in x] for i in items for x in i]
    return result


def calculate_total(items, multiplier=1, factor=1, adjustment=1, offset=1, base=1, increment=1, divisor=1, modifier=1):
    """
    Function with too many parameters (9 args).
    This violates the single responsibility principle.
    """
    total = 0
    for item in items:
        total += (item * multiplier + factor + adjustment + offset + base + increment) / divisor + modifier
    return total


class DataProcessor:
    """
    A class with multiple long methods (>60 lines each).
    """
    
    def long_method_1(self, data, param2, param3, param4):
        """A really long method - over 60 lines."""
        result = []
        for item in data:
            if isinstance(item, dict):
                for key, value in item.items():
                    if key.startswith("_"):
                        continue
                    if isinstance(value, str):
                        processed = value.strip().lower()
                    elif isinstance(value, (int, float)):
                        processed = value * 2
                    else:
                        processed = str(value)
                    
                    # More processing
                    if len(processed) > 10:
                        processed = processed[:10] + "..."
                    
                    # Even more processing
                    for i in range(3):
                        if i % 2 == 0:
                            processed = f"[{processed}]"
                    
                    # And more
                    normalized = processed.replace(" ", "_").replace("-", "_")
                    result.append(normalized)
        
        return result
    
    def long_method_2(self):
        """Another long method."""
        # Simulating a long method with many lines
        value = 0
        for i in range(100):
            value += i
            if value > 1000:
                value = 0
            # ... more lines of similar code
        return value


def insecure_query(user_input):
    """
    SQL injection vulnerability - using string formatting with user input.
    """
    query = f"SELECT * FROM users WHERE username = '{user_input}'"
    # Execute query without parameterized statement
    return query


if __name__ == "__main__":
    print("This sample project has intentional issues for AWA demonstration.")
    print("Run: python -m awa scan --target .")
