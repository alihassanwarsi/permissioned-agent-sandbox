from collections import defaultdict
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult

class InMemoryTraceStore(SpanExporter):
    def __init__(self) -> None:
        self._traces: dict[str, list] = defaultdict(list)

    def export(self, spans) -> SpanExportResult:
        for span in spans:
            trace_id = format(span.context.trace_id, "032x")
            self._traces[trace_id].append(span)
        return SpanExportResult.SUCCESS

    def shutdown(self) -> None:
        pass

    def get_trace(self, trace_id: str) -> list:
        return list(self._traces.get(trace_id, []))

    def list_trace_ids(self) -> list[str]:
        return list(self._traces.keys())