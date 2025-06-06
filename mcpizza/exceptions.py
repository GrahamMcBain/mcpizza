"""Custom exceptions for MCPizza"""

class MCPizzaError(Exception):
    """Base exception for MCPizza errors"""
    pass

class StoreNotFoundError(MCPizzaError):
    """Raised when no Domino's store is found"""
    pass

class InvalidItemError(MCPizzaError):
    """Raised when trying to add invalid item to order"""
    pass

class OrderError(MCPizzaError):
    """Raised when there's an issue with the order"""
    pass

class CustomerInfoError(MCPizzaError):
    """Raised when customer information is invalid or missing"""
    pass

class PaymentError(MCPizzaError):
    """Raised when there's a payment issue"""
    pass

class APIError(MCPizzaError):
    """Raised when the Domino's API returns an error"""
    pass
