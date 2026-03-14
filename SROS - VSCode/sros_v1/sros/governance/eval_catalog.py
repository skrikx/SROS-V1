"""
Policy Catalog

Maintains library of policies and governance templates.
Enables rapid policy composition and versioning.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class PolicyTemplate:
    """Template for reusable policy patterns."""
    id: str
    name: str
    description: str
    category: str  # e.g., "safety", "cost", "performance", "audit"
    template: Dict[str, Any]  # Policy structure
    parameters: Dict[str, Any]  # Configurable parameters
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def instantiate(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create policy instance from template with config."""
        policy = self.template.copy()
        
        # Substitute parameters
        for key, value in self.parameters.items():
            if key in config:
                # Replace placeholder values
                policy_str = str(policy)
                policy_str = policy_str.replace(f"${{{key}}}", str(config[key]))
                # Note: This is simplified; real implementation would use proper templating
        
        return policy


class PolicyCatalog:
    """
    Maintains library of policies and templates.
    
    Features:
    - Policy storage and retrieval
    - Template management for policy patterns
    - Policy versioning
    - Category-based organization
    - Search and filtering
    """
    
    def __init__(self):
        """Initialize policy catalog."""
        self.policies: Dict[str, Dict[str, Any]] = {}
        self.templates: Dict[str, PolicyTemplate] = {}
        self.versions: Dict[str, List[Dict[str, Any]]] = {}  # policy_id -> versions
        self.categories: Dict[str, List[str]] = {}  # category -> policy_ids
    
    def add_policy(
        self,
        policy_id: str,
        policy: Dict[str, Any],
        category: str = "general"
    ) -> bool:
        """
        Add a policy to the catalog.
        
        Args:
            policy_id: Unique policy ID
            policy: Policy definition
            category: Policy category
        
        Returns:
            True if added
        """
        if policy_id in self.policies:
            logger.warning(f"Policy {policy_id} already exists; updating")
        
        self.policies[policy_id] = policy
        
        # Initialize versions list
        if policy_id not in self.versions:
            self.versions[policy_id] = []
        
        # Track in version history
        self.versions[policy_id].append({
            "version": len(self.versions[policy_id]) + 1,
            "policy": policy.copy(),
            "timestamp": datetime.now()
        })
        
        # Add to category
        if category not in self.categories:
            self.categories[category] = []
        
        if policy_id not in self.categories[category]:
            self.categories[category].append(policy_id)
        
        logger.info(f"Added policy {policy_id} to catalog (category: {category})")
        return True
    
    def get_policy(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """
        Get policy by ID.
        
        Args:
            policy_id: Policy ID
        
        Returns:
            Policy definition or None
        """
        return self.policies.get(policy_id)
    
    def get_policies_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all policies in a category.
        
        Args:
            category: Policy category
        
        Returns:
            List of policies in category
        """
        policy_ids = self.categories.get(category, [])
        return [self.policies[pid] for pid in policy_ids if pid in self.policies]
    
    def add_template(
        self,
        template_id: str,
        template: PolicyTemplate
    ) -> bool:
        """
        Add a policy template to the catalog.
        
        Args:
            template_id: Unique template ID
            template: PolicyTemplate instance
        
        Returns:
            True if added
        """
        self.templates[template_id] = template
        logger.info(f"Added template {template_id} ({template.category})")
        return True
    
    def get_template(self, template_id: str) -> Optional[PolicyTemplate]:
        """Get template by ID."""
        return self.templates.get(template_id)
    
    def list_templates(self, category: str = None) -> List[PolicyTemplate]:
        """
        List templates, optionally filtered by category.
        
        Args:
            category: Optional category filter
        
        Returns:
            List of templates
        """
        templates = list(self.templates.values())
        
        if category:
            templates = [t for t in templates if t.category == category]
        
        return templates
    
    def create_policy_from_template(
        self,
        policy_id: str,
        template_id: str,
        config: Dict[str, Any],
        category: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a policy from a template.
        
        Args:
            policy_id: ID for new policy
            template_id: ID of template to use
            config: Configuration parameters
            category: Optional category override
        
        Returns:
            Created policy or None if template not found
        """
        template = self.get_template(template_id)
        if not template:
            logger.warning(f"Template {template_id} not found")
            return None
        
        policy = template.instantiate(config)
        policy["_template_id"] = template_id
        
        use_category = category or template.category
        self.add_policy(policy_id, policy, use_category)
        
        logger.info(f"Created policy {policy_id} from template {template_id}")
        return policy
    
    def remove_policy(self, policy_id: str) -> bool:
        """
        Remove a policy from the catalog.
        
        Args:
            policy_id: Policy ID to remove
        
        Returns:
            True if removed
        """
        if policy_id not in self.policies:
            return False
        
        del self.policies[policy_id]
        
        # Remove from categories
        for category in self.categories.values():
            if policy_id in category:
                category.remove(policy_id)
        
        logger.info(f"Removed policy {policy_id}")
        return True
    
    def get_policy_history(self, policy_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get version history for a policy.
        
        Args:
            policy_id: Policy ID
            limit: Maximum versions to return
        
        Returns:
            List of policy versions
        """
        versions = self.versions.get(policy_id, [])
        return versions[-limit:] if limit else versions
    
    def search_policies(self, query: str) -> List[Dict[str, Any]]:
        """
        Search policies by ID or content.
        
        Args:
            query: Search query
        
        Returns:
            List of matching policies
        """
        results = []
        
        for policy_id, policy in self.policies.items():
            # Simple search in ID and policy string representation
            if query.lower() in policy_id.lower() or query.lower() in str(policy).lower():
                results.append(policy)
        
        return results
    
    def export_catalog(self) -> Dict[str, Any]:
        """Export full catalog as dict."""
        return {
            "policies": self.policies.copy(),
            "templates": {
                tid: {
                    "id": t.id,
                    "name": t.name,
                    "category": t.category,
                    "description": t.description
                }
                for tid, t in self.templates.items()
            },
            "categories": self.categories.copy()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get catalog statistics."""
        return {
            "total_policies": len(self.policies),
            "total_templates": len(self.templates),
            "categories": len(self.categories),
            "categories_detail": {
                cat: len(pids) for cat, pids in self.categories.items()
            }
        }
