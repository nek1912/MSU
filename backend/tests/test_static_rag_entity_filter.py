"""Tests for StaticRAG entity_id filtering."""

from app.services.static_rag import StaticRAGService

def test_retrieve_accepts_entity_id():
    """retrieve() accepts entity_id parameter without error."""
    service = StaticRAGService()
    # Just verify the signature accepts entity_id
    import inspect
    sig = inspect.signature(service.retrieve)
    assert "entity_id" in sig.parameters

def test_retrieve_entity_id_defaults_to_none():
    """entity_id defaults to None for backwards compatibility."""
    service = StaticRAGService()
    import inspect
    sig = inspect.signature(service.retrieve)
    assert sig.parameters["entity_id"].default is None
