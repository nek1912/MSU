"""Tests for entity resolution integration in chat route."""
import inspect
from app.services.rag_orchestrator import RAGOrchestrator

def test_orchestrator_run_accepts_entity_id():
    sig = inspect.signature(RAGOrchestrator.run)
    assert "entity_id" in sig.parameters

def test_orchestrator_run_entity_id_defaults_to_none():
    sig = inspect.signature(RAGOrchestrator.run)
    assert sig.parameters["entity_id"].default is None
