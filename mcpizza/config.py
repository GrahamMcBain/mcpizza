"""Configuration for MCPizza server"""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class ServerConfig:
    """Server configuration"""
    
    # Safety settings
    enable_real_orders: bool = False  # Set to True to enable actual order placement
    require_confirmation: bool = True  # Require confirmation before placing orders
    max_order_amount: float = 100.0  # Maximum order amount without additional confirmation
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # API settings
    timeout_seconds: int = 30
    retry_attempts: int = 3
    
    @classmethod
    def from_env(cls) -> "ServerConfig":
        """Load configuration from environment variables"""
        return cls(
            enable_real_orders=os.getenv("MCPIZZA_ENABLE_ORDERS", "false").lower() == "true",
            require_confirmation=os.getenv("MCPIZZA_REQUIRE_CONFIRMATION", "true").lower() == "true",
            max_order_amount=float(os.getenv("MCPIZZA_MAX_ORDER_AMOUNT", "100.0")),
            log_level=os.getenv("MCPIZZA_LOG_LEVEL", "INFO"),
            log_file=os.getenv("MCPIZZA_LOG_FILE"),
            timeout_seconds=int(os.getenv("MCPIZZA_TIMEOUT", "30")),
            retry_attempts=int(os.getenv("MCPIZZA_RETRY_ATTEMPTS", "3"))
        )

# Global config instance
config = ServerConfig.from_env()
