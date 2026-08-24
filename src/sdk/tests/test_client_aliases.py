"""Verify that Client / AsyncClient are proper aliases for the long-form names."""

from __future__ import annotations

import pytest
from flowos_sdk import AsyncClient, AsyncFlowOSClient, Client, FlowOSClient
from flowos_sdk.client import AsyncClient as AsyncClientFromModule
from flowos_sdk.client import Client as ClientFromModule


@pytest.mark.unit
def test_client_alias_is_flowos_client() -> None:
    assert Client is FlowOSClient


@pytest.mark.unit
def test_async_client_alias_is_async_flowos_client() -> None:
    assert AsyncClient is AsyncFlowOSClient


@pytest.mark.unit
def test_client_importable_from_module_directly() -> None:
    assert ClientFromModule is FlowOSClient


@pytest.mark.unit
def test_async_client_importable_from_module_directly() -> None:
    assert AsyncClientFromModule is AsyncFlowOSClient


@pytest.mark.unit
def test_client_instantiation_uses_short_name() -> None:
    """Client() should produce a FlowOSClient instance."""
    client = Client("http://localhost:7860")
    assert isinstance(client, FlowOSClient)
    assert isinstance(client, Client)
    client.close()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_client_instantiation_uses_short_name() -> None:
    """AsyncClient() should produce an AsyncFlowOSClient instance."""
    client = AsyncClient("http://localhost:7860")
    try:
        assert isinstance(client, AsyncFlowOSClient)
        assert isinstance(client, AsyncClient)
    finally:
        await client.aclose()


@pytest.mark.unit
def test_client_ticket_api_surface() -> None:
    """Reproduce the exact import path from the ticket spec."""
    # from flowos_sdk import Client
    # client = Client("https://flowos.example.com", api_key="...")
    # should have .list_flows(), .get_flow(), .run_flow()
    client = Client("https://flowos.example.com", api_key="test-key")  # pragma: allowlist secret
    assert hasattr(client, "list_flows")
    assert hasattr(client, "get_flow")
    assert hasattr(client, "run_flow")
    assert hasattr(client, "create_flow")
    assert hasattr(client, "update_flow")
    assert hasattr(client, "delete_flow")
    assert hasattr(client, "upsert_flow")
    client.close()
