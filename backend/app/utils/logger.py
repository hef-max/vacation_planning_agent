"""
Audit logging utility.
Tracks semua aksi penting terutama yang berkaitan dengan booking dan payment.
"""
import json
from datetime import datetime
from typing import Optional, Any
from loguru import logger
import sys

# Configure loguru
logger.remove()  # Remove default handler
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention="30 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
    level="DEBUG"
)
logger.add(
    "logs/audit.log",
    rotation="50 MB",
    retention="90 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
    filter=lambda record: record["extra"].get("audit", False),
    level="INFO"
)

class AuditLogger:
    """
    Audit logger untuk tracking aksi-aksi penting.
    Semua booking dan payment actions HARUS di-log.
    """
    
    @staticmethod
    def log_action(
        user_id: str,
        action: str,
        details: dict,
        ip_address: Optional[str] = None,
        status: str = "success"
    ):
        """Log an auditable action."""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action,
            "status": status,
            "ip_address": ip_address,
            "details": _sanitize_details(details)
        }
        logger.bind(audit=True).info(json.dumps(audit_entry))
        return audit_entry
    
    @staticmethod
    def log_plan_created(user_id: str, plan_id: str, destination: str, budget: int):
        return AuditLogger.log_action(
            user_id=user_id,
            action="PLAN_CREATED",
            details={
                "plan_id": plan_id,
                "destination": destination,
                "budget_idr": budget
            }
        )
    
    @staticmethod
    def log_booking_attempt(user_id: str, plan_id: str, booking_type: str, amount: int):
        return AuditLogger.log_action(
            user_id=user_id,
            action="BOOKING_ATTEMPT",
            details={
                "plan_id": plan_id,
                "booking_type": booking_type,
                "amount_idr": amount
            }
        )
    
    @staticmethod
    def log_booking_success(user_id: str, booking_ref: str, booking_type: str, amount: int, transaction_id: str):
        return AuditLogger.log_action(
            user_id=user_id,
            action="BOOKING_SUCCESS",
            details={
                "booking_ref": booking_ref,
                "booking_type": booking_type,
                "amount_idr": amount,
                "transaction_id": transaction_id
            }
        )
    
    @staticmethod
    def log_booking_failed(user_id: str, plan_id: str, booking_type: str, error: str):
        return AuditLogger.log_action(
            user_id=user_id,
            action="BOOKING_FAILED",
            status="failed",
            details={
                "plan_id": plan_id,
                "booking_type": booking_type,
                "error": error
            }
        )
    
    @staticmethod
    def log_payment_attempt(user_id: str, amount: int, description: str):
        return AuditLogger.log_action(
            user_id=user_id,
            action="PAYMENT_ATTEMPT",
            details={
                "amount_idr": amount,
                "description": description
                # Note: NEVER log payment tokens!
            }
        )
    
    @staticmethod
    def log_agent_action(user_id: str, agent_action: str, tools_called: list, input_summary: str):
        return AuditLogger.log_action(
            user_id=user_id,
            action="AGENT_ACTION",
            details={
                "agent_action": agent_action,
                "tools_called": tools_called,
                "input_summary": input_summary[:200]  # Truncate for safety
            }
        )

def _sanitize_details(details: dict) -> dict:
    """
    Remove sensitive information from details before logging.
    NEVER log: payment tokens, full card numbers, passwords.
    """
    sensitive_keys = ["payment_token", "card_number", "cvv", "password", "token"]
    sanitized = {}
    
    for key, value in details.items():
        if any(s in key.lower() for s in sensitive_keys):
            sanitized[key] = "[REDACTED]"
        elif isinstance(value, dict):
            sanitized[key] = _sanitize_details(value)
        else:
            sanitized[key] = value
    
    return sanitized

# Convenience export
audit = AuditLogger()