"""OSS authorization service package (pass-through default; plugins enforce)."""

from flowos.services.authorization.actions import (
    DeploymentAction,
    FileAction,
    FlowAction,
    KnowledgeBaseAction,
    ProjectAction,
    ShareAction,
    VariableAction,
)
from flowos.services.authorization.audit import (
    audit_decision,
    drain_pending_audit_writes,
)
from flowos.services.authorization.decorators import requires_flow_permission, requires_resource_permission
from flowos.services.authorization.fetch import authorized_or_owner_scoped, deny_to_404
from flowos.services.authorization.guards import (
    ensure_deployment_permission,
    ensure_file_permission,
    ensure_flow_permission,
    ensure_knowledge_base_permission,
    ensure_permission,
    ensure_project_permission,
    ensure_share_permission,
    ensure_variable_permission,
)
from flowos.services.authorization.listing import filter_visible_resources
from flowos.services.authorization.service import FlowOSAuthorizationService

__all__ = [
    "DeploymentAction",
    "FileAction",
    "FlowAction",
    "KnowledgeBaseAction",
    "FlowOSAuthorizationService",
    "ProjectAction",
    "ShareAction",
    "VariableAction",
    "audit_decision",
    "authorized_or_owner_scoped",
    "deny_to_404",
    "drain_pending_audit_writes",
    "ensure_deployment_permission",
    "ensure_file_permission",
    "ensure_flow_permission",
    "ensure_knowledge_base_permission",
    "ensure_permission",
    "ensure_project_permission",
    "ensure_share_permission",
    "ensure_variable_permission",
    "filter_visible_resources",
    "requires_flow_permission",
    "requires_resource_permission",
]
