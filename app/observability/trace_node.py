from opentelemetry.trace import Status, StatusCode

def traced_node(tracer, node_name: str, node_fn):

    def wrapped(state):
        with tracer.start_as_current_span(node_name) as span:
            span.set_attribute("node.name", node_name)

            try:
                result = node_fn(state)
            except Exception as exc:
                span.record_exception(exc)
                span.set_status(Status(StatusCode.ERROR, str(exc)))
                raise

            if getattr(result, "selected_tool", None):
                span.set_attribute("tool.selected", result.selected_tool)
            if getattr(result, "decision", None) is not None:
                span.set_attribute("decision", result.decision.value)

            return result

    return wrapped