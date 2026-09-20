from app.models.approval import ApprovalOutcome, ApprovalRequest, ApprovalStatus

class ApprovalQueue:
    def __init__(self) -> None:
        self._requests: dict[str, ApprovalRequest] = {}

    def add(self, request: ApprovalRequest) -> None:
        self._requests[request.request_id] = request

    def get(self, request_id: str) -> ApprovalRequest:
        return self._requests[request_id]

    def list_pending(self) -> list[ApprovalRequest]:
        return [r for r in self._requests.values() if r.status == ApprovalStatus.PENDING]

    def all_requests(self) -> list[ApprovalRequest]:
        return list(self._requests.values())

    def resolve(
            self,
            request_id: str,
            outcome: ApprovalOutcome,
            decided_by: str,
            note: str | None = None,
            modified_input: dict | None = None
    ) -> ApprovalRequest:
        request = self._requests[request_id]
        request.status = ApprovalStatus.RESOLVED
        request.outcome = outcome
        request.decided_by = decided_by
        request.note = note
        request.modified_input = modified_input
        return request