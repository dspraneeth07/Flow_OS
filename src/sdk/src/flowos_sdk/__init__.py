"""flowos-sdk -- Python SDK for the FlowOS REST API."""

from flowos_sdk._async_client import AsyncClient, AsyncFlowOSClient
from flowos_sdk.background_job import BackgroundJob
from flowos_sdk.client import Client, FlowOSClient
from flowos_sdk.environments import (
    EnvironmentConfig,
    get_async_client,
    get_client,
    get_environment,
    load_environments,
)
from flowos_sdk.exceptions import (
    EnvironmentConfigError,
    EnvironmentNotFoundError,
    FlowOSAuthError,
    FlowOSConnectionError,
    FlowOSError,
    FlowOSHTTPError,
    FlowOSNotFoundError,
    FlowOSTimeoutError,
    FlowOSValidationError,
)
from flowos_sdk.models import (
    Flow,
    FlowCreate,
    FlowUpdate,
    Project,
    ProjectCreate,
    ProjectUpdate,
    ProjectWithFlows,
    RunOutput,
    RunRequest,
    RunResponse,
    StreamChunk,
)
from flowos_sdk.serialization import flow_to_json, normalize_flow, normalize_flow_file

__all__ = [
    "AsyncClient",  # short alias for AsyncFlowOSClient (preferred)
    "AsyncFlowOSClient",
    "BackgroundJob",
    "Client",  # short alias for FlowOSClient (preferred)
    "EnvironmentConfig",
    "EnvironmentConfigError",
    "EnvironmentNotFoundError",
    "Flow",
    "FlowCreate",
    "FlowUpdate",
    "FlowOSAuthError",
    "FlowOSClient",
    "FlowOSConnectionError",
    "FlowOSError",
    "FlowOSHTTPError",
    "FlowOSNotFoundError",
    "FlowOSTimeoutError",
    "FlowOSValidationError",
    "Project",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectWithFlows",
    "RunOutput",
    "RunRequest",
    "RunResponse",
    "StreamChunk",
    "flow_to_json",
    "get_async_client",
    "get_client",
    "get_environment",
    "load_environments",
    "normalize_flow",
    "normalize_flow_file",
]
