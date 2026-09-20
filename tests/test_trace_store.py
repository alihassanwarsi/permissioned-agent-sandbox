from unittest.mock import MagicMock
from app.observability.trace_store import InMemoryTraceStore

def make_fake_span(trace_id_int: int):
    span = MagicMock()
    span.context.trace_id = trace_id_int
    return span

def test_export_groups_spans_by_trace_id():
    store = InMemoryTraceStore()
    span = make_fake_span(1)

    store.export([span])

    trace_id = format(1, "032x")
    assert store.get_trace(trace_id) == [span]

def test_different_trace_ids_stay_separate():
    store = InMemoryTraceStore()
    store.export([make_fake_span(1)])
    store.export([make_fake_span(2)])

    assert len(store.list_trace_ids()) == 2

def test_unknown_trace_id_returns_empty_list():
    store = InMemoryTraceStore()
    assert store.get_trace("does-not-exist") == []