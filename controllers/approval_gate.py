"""Human-in-the-loop approval gate for sensitive operations."""
from typing import Dict, Any, Optional, Callable
from schemas import SQLValidation

class ApprovalGate:
    """Manages human approval for operations that require oversight.

    In a Streamlit UI, this would render approval buttons.
    In headless mode, it uses a callback function.
    """

    def __init__(self, approval_callback: Optional[Callable] = None):
        self.approval_callback = approval_callback
        self.pending_approvals: Dict[str, Dict[str, Any]] = {}
        self.approval_history: List[Dict[str, Any]] = []

    def check_approval_needed(self, validation: SQLValidation, query: str, 
                               user_role: str = "viewer") -> Dict[str, Any]:
        """Check if an operation requires human approval.

        Returns:
            Dict with 'approved' (bool), 'reason', and 'requires_interaction' (bool).
        """
        # Admin bypass
        if user_role == "admin":
            return {"approved": True, "reason": "Admin bypass", "requires_interaction": False}

        # Validation-based gate
        if not validation.get("is_valid", True):
            return {
                "approved": False, 
                "reason": f"Validation failed: {validation.get('errors', [])}",
                "requires_interaction": False
            }

        if validation.get("requires_approval", False):
            approval_id = f"approval_{hash(query) % 10000000}"
            self.pending_approvals[approval_id] = {
                "query": query,
                "validation": validation,
                "status": "pending"
            }
            return {
                "approved": False,
                "reason": validation.get("approval_reason", "Manual approval required"),
                "requires_interaction": True,
                "approval_id": approval_id
            }

        return {"approved": True, "reason": "Auto-approved", "requires_interaction": False}

    def approve(self, approval_id: str, approver: str = "system") -> bool:
        """Approve a pending operation."""
        if approval_id not in self.pending_approvals:
            return False

        self.pending_approvals[approval_id]["status"] = "approved"
        self.pending_approvals[approval_id]["approver"] = approver
        self.approval_history.append(self.pending_approvals[approval_id])
        return True

    def reject(self, approval_id: str, reason: str = "") -> bool:
        """Reject a pending operation."""
        if approval_id not in self.pending_approvals:
            return False

        self.pending_approvals[approval_id]["status"] = "rejected"
        self.pending_approvals[approval_id]["rejection_reason"] = reason
        self.approval_history.append(self.pending_approvals[approval_id])
        return True

    def get_pending(self) -> Dict[str, Dict[str, Any]]:
        """Return all pending approvals."""
        return {k: v for k, v in self.pending_approvals.items() if v["status"] == "pending"}
