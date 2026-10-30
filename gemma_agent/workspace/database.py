from typing import Dict, Any

# In a real application, this would handle database connections (e.g., SQLAlchemy, MongoDB)
# For now, we use a simple in-memory store.
db: Dict[str, Any] = {
    "menu": {},
    "orders": {}
}

def get_db():
    """Dependency to get the database connection."""
    return db

def initialize_db():
    """Initialize the database with some default data."""
    # Example menu items
    db["menu"]["1"] = {"name": "Burger", "price": 10.0, "description": "Classic burger"}
    db["menu"]["2"] = {"name": "Fries", "price": 3.0, "description": "Crispy fries"}
    print("Database initialized with sample menu items.")

# Initialize the database when the module is loaded
initialize_db()