from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter

def build_tracer_provider(exporters=None) -> TracerProvider:
    if exporters is None:
        exporters = [ConsoleSpanExporter()]

    provider = TracerProvider()
    for exporter in exporters:
        provider.add_span_processor(SimpleSpanProcessor(exporter))
    return provider

def get_tracer(provider: TracerProvider, name: str = "agent-sandbox"):
    return provider.get_tracer(name)