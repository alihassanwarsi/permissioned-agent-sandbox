function safeJson(value) {
  return escapeHtml(
    JSON.stringify(value, null, 2)
  );
}

function cleanAgentResponse(text) {
  return String(text ?? '')
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/__(.*?)__/g, '$1')
    .replace(/`([^`]+)`/g, '$1')
    .replace(/^#{1,6}\s+/gm, '')
    .replace(/\[(.*?)\]\((.*?)\)/g, '$1 ($2)')
    .trim();
}


async function startAgentRun() {
  const msg = document
    .getElementById('run-message')
    .value
    .trim();

  const role =
    document.getElementById('run-role').value;

  activeQuery = msg;

  const runBtn =
    document.getElementById('run-btn');

  const card =
    document.getElementById(
      'run-interaction-card'
    );

  const title =
    document.getElementById(
      'interaction-status-title'
    );

  const badge =
    document.getElementById(
      'interaction-badge'
    );

  const loading =
    document.getElementById(
      'interaction-loading'
    );

  const loadingText =
    document.getElementById(
      'loading-text'
    );

  const approvalContainer =
    document.getElementById(
      'approval-container'
    );

  const responseContainer =
    document.getElementById(
      'final-response-container'
    );

  const responseText =
    document.getElementById(
      'final-response-text'
    );

  if (!msg) {
    alert('Please enter a message.');
    return;
  }

  runBtn.disabled = true;

  traceIdsBeforeRun =
    await fetchTraceIdsSafe();

  card.style.display = 'block';

  approvalContainer.style.display = 'none';
  approvalContainer.innerHTML = '';

  responseContainer.style.display = 'none';

  responseText.innerText = '';
  responseText.style.color = '';

  title.innerText = 'Processing Task';

  badge.className = 'badge badge-low';
  badge.innerText = 'RUNNING';

  loading.style.display = 'block';

  loadingText.innerText =
    'Agent is planning and evaluating permissions...';

  try {
    const res = await fetch(
      `${API_BASE}/run`,
      {
        method: 'POST',

        headers: {
          'Content-Type': 'application/json'
        },

        body: JSON.stringify({
          user_message: msg,
          role: role
        })
      }
    );

    const data = await res.json();

    await rememberNewTracesForQuery(
      activeQuery
    );

    loading.style.display = 'none';

    if (data.status === 'awaiting_approval') {
      activeThreadId = data.thread_id;

      title.innerText =
        'Approval Required';

      badge.className =
        'badge badge-medium';

      badge.innerText =
        'WAITING FOR INPUT';

      await loadInPlaceApproval(
        data.thread_id
      );

      return;
    }

    title.innerText = 'Task Completed';

    badge.className =
      'badge badge-low';

    badge.innerText = 'COMPLETED';

    responseContainer.style.display =
      'block';

    responseText.style.color = '';

    responseText.innerText =
      cleanAgentResponse(
        data.final_response ||
        'No response text returned.'
      );

  } catch (err) {
    loading.style.display = 'none';

    title.innerText =
      'Execution Failed';

    badge.className =
      'badge badge-high';

    badge.innerText =
      'ERROR';

    responseContainer.style.display =
      'block';

    responseText.style.color =
      'var(--danger)';

    responseText.innerText =
      `Error connecting to backend: ${err.message}. ` +
      `Ensure backend is running at ${API_BASE}`;

  } finally {
    runBtn.disabled = false;
  }
}


async function loadInPlaceApproval(
  threadId
) {
  const container =
    document.getElementById(
      'approval-container'
    );

  container.style.display = 'block';

  container.innerHTML = `
    <div
      style="
        font-size:13px;
        color:var(--text-muted);
      "
    >
      <span class="loading-spinner"></span>
      Retrieving approval parameters...
    </div>
  `;

  try {
    const res = await fetch(
      `${API_BASE}/approvals`
    );

    const items = await res.json();

    const req =
      items.find(
        item => item.thread_id === threadId
      ) ||
      items[items.length - 1];

    if (!req) {
      container.innerHTML = `
        <p
          style="
            color:var(--warning);
            font-size:13px;
          "
        >
          No pending approval found in queue.
        </p>
      `;

      return;
    }

    activeRequestId = req.request_id;

    const isMediumRisk =
      (req.risk_level || '')
        .toLowerCase() === 'medium';

    const isConfirmation =
      req.kind === 'confirmation';

    if (
      isMediumRisk ||
      isConfirmation
    ) {
      container.innerHTML = `
        <div
          class="approval-box"
          id="box-${req.request_id}"
        >
          <div class="approval-box-header">

            <div class="approval-box-title">
              <span>
                Confirmation Required: Are you sure?
              </span>
            </div>

            <span class="badge badge-medium">
              MEDIUM RISK
            </span>

          </div>

          <div
            style="
              font-size:13px;
              color:var(--text-muted);
              margin-bottom:8px;
            "
          >
            The agent proposes to run
            <b>${escapeHtml(
              req.tool_name
            )}</b>.
            Do you want to proceed?
          </div>

          <div
            style="
              font-size:13px;
              margin-bottom:4px;
            "
          >
            <b>Tool parameters:</b>
          </div>

          <pre>${safeJson(
            req.tool_input
          )}</pre>

          <div
            id="btn-group-${req.request_id}"
            class="action-row"
          >
            <button
              class="btn-success"
              onclick="
                executeDecision(
                  '${req.request_id}',
                  'approved'
                )
              "
            >
              Yes, Approve
            </button>

            <button
              class="btn-danger"
              onclick="
                executeDecision(
                  '${req.request_id}',
                  'rejected'
                )
              "
            >
              No, Reject
            </button>
          </div>

          <div
            id="reject-note-box-${req.request_id}"
            style="
              display:none;
              margin-top:10px;
            "
          >
            <input
              type="text"
              id="reject-note-${req.request_id}"
              placeholder="Optional reason for rejection..."
              style="
                width:70%;
                margin-right:8px;
              "
            >

            <button
              class="btn-danger"
              onclick="
                confirmReject(
                  '${req.request_id}'
                )
              "
            >
              Confirm Reject
            </button>
          </div>

          <div
            id="decision-banner-${req.request_id}"
            style="display:none;"
          ></div>
        </div>
      `;

      return;
    }

    container.innerHTML = `
      <div
        class="approval-box high-risk"
        id="box-${req.request_id}"
      >
        <div class="approval-box-header">

          <div class="approval-box-title">
            <span>
              High Risk Tool Action Approval
            </span>
          </div>

          <span class="badge badge-high">
            HIGH RISK
          </span>

        </div>

        <div
          style="
            font-size:13px;
            margin-bottom:6px;
          "
        >
          Action:
          <b>${escapeHtml(
            req.tool_name
          )}</b>
        </div>

        <div
          style="
            font-size:13px;
            color:var(--text-muted);
            margin-bottom:8px;
          "
        >
          <b>Reasoning:</b>
          ${escapeHtml(
            req.reasoning ||
            'Agent requested execution'
          )}
        </div>

        <div
          style="
            font-size:12px;
            color:var(--text-muted);
            margin-bottom:4px;
          "
        >
          Tool Input Arguments:
        </div>

        <pre
          id="display-input-${req.request_id}"
        >${safeJson(
          req.tool_input
        )}</pre>

        <div
          id="btn-group-${req.request_id}"
          class="action-row"
        >
          <button
            class="btn-success"
            onclick="
              executeDecision(
                '${req.request_id}',
                'approved'
              )
            "
          >
            Approve
          </button>

          <button
            class="btn-danger"
            onclick="
              showRejectInput(
                '${req.request_id}'
              )
            "
          >
            Reject
          </button>

          <button
            class="btn-warning"
            onclick="
              toggleModifyEditor(
                '${req.request_id}'
              )
            "
          >
            Modify & Approve
          </button>

          <button
            class="btn-sec"
            onclick="
              executeDecision(
                '${req.request_id}',
                'replan'
              )
            "
          >
            Replan
          </button>
        </div>

        <div
          id="reject-note-box-${req.request_id}"
          style="
            display:none;
            margin-top:12px;
          "
        >
          <input
            type="text"
            id="reject-note-${req.request_id}"
            placeholder="Reason for rejection..."
            style="
              width:70%;
              margin-right:8px;
            "
          >

          <button
            class="btn-danger"
            onclick="
              confirmReject(
                '${req.request_id}'
              )
            "
          >
            Confirm Rejection
          </button>

          <button
            class="btn-sec"
            onclick="
              cancelReject(
                '${req.request_id}'
              )
            "
          >
            Cancel
          </button>
        </div>

        <div
          id="modify-box-${req.request_id}"
          class="modify-editor"
          style="display:none;"
        >
          <div
            style="
              font-size:13px;
              font-weight:600;
              margin-bottom:6px;
            "
          >
            Edit JSON Arguments:
          </div>

          <textarea
            id="modify-input-${req.request_id}"
            style="
              min-height:100px;
              font-family:monospace;
              font-size:12px;
            "
          >${safeJson(
            req.tool_input
          )}</textarea>

          <div
            style="
              margin-top:8px;
              display:flex;
              gap:8px;
            "
          >
            <button
              class="btn-success"
              onclick="
                submitModifiedDecision(
                  '${req.request_id}'
                )
              "
            >
              Save & Approve
            </button>

            <button
              class="btn-sec"
              onclick="
                toggleModifyEditor(
                  '${req.request_id}'
                )
              "
            >
              Cancel
            </button>
          </div>
        </div>

        <div
          id="decision-banner-${req.request_id}"
          style="display:none;"
        ></div>
      </div>
    `;

  } catch (err) {
    container.innerHTML = `
      <p
        style="
          color:var(--danger);
          font-size:13px;
        "
      >
        Error loading approval details:
        ${escapeHtml(err.message)}
      </p>
    `;
  }
}


function showRejectInput(
  requestId
) {
  document.getElementById(
    `btn-group-${requestId}`
  ).style.display = 'none';

  document.getElementById(
    `reject-note-box-${requestId}`
  ).style.display = 'flex';
}


function cancelReject(
  requestId
) {
  document.getElementById(
    `reject-note-box-${requestId}`
  ).style.display = 'none';

  document.getElementById(
    `btn-group-${requestId}`
  ).style.display = 'flex';
}


function confirmReject(
  requestId
) {
  const noteInput =
    document.getElementById(
      `reject-note-${requestId}`
    );

  const note =
    noteInput
      ? noteInput.value.trim()
      : '';

  executeDecision(
    requestId,
    'rejected',
    null,
    note || 'Rejected by user'
  );
}


function toggleModifyEditor(
  requestId
) {
  const box =
    document.getElementById(
      `modify-box-${requestId}`
    );

  const btnGroup =
    document.getElementById(
      `btn-group-${requestId}`
    );

  if (box.style.display === 'none') {
    box.style.display = 'block';
    btnGroup.style.display = 'none';
  } else {
    box.style.display = 'none';
    btnGroup.style.display = 'flex';
  }
}


function submitModifiedDecision(
  requestId
) {
  const textarea =
    document.getElementById(
      `modify-input-${requestId}`
    );

  try {
    const parsed =
      JSON.parse(
        textarea.value.trim()
      );

    executeDecision(
      requestId,
      'modified',
      parsed,
      'User modified inputs'
    );

  } catch (err) {
    alert('Invalid JSON formatting.');
  }
}


async function executeDecision(
  requestId,
  outcome,
  modifiedInput = null,
  note = null
) {
  const btnGroup =
    document.getElementById(
      `btn-group-${requestId}`
    );

  const rejectBox =
    document.getElementById(
      `reject-note-box-${requestId}`
    );

  const modifyBox =
    document.getElementById(
      `modify-box-${requestId}`
    );

  const banner =
    document.getElementById(
      `decision-banner-${requestId}`
    );

  const badge =
    document.getElementById(
      'interaction-badge'
    );

  const title =
    document.getElementById(
      'interaction-status-title'
    );

  const responseContainer =
    document.getElementById(
      'final-response-container'
    );

  const responseText =
    document.getElementById(
      'final-response-text'
    );

  if (btnGroup) {
    btnGroup.style.display = 'none';
  }

  if (rejectBox) {
    rejectBox.style.display = 'none';
  }

  if (modifyBox) {
    modifyBox.style.display = 'none';
  }

  banner.style.display = 'flex';

  banner.className =
    `decision-banner ${
      outcome === 'approved' ||
      outcome === 'modified'
        ? 'approved'
        : outcome === 'rejected'
          ? 'rejected'
          : 'replan'
    }`;

  banner.innerHTML = `
    <span class="loading-spinner"></span>
    Applying decision
    (${escapeHtml(outcome.toUpperCase())})
    and resuming agent...
  `;

  try {
    /*
      The approval resume creates a new trace.

      Capture existing trace IDs immediately before
      resuming so the new trace can be associated
      with the same original user query.
    */
    traceIdsBeforeRun =
      await fetchTraceIdsSafe();

    const res = await fetch(
      `${API_BASE}/approvals/${requestId}/resolve`,
      {
        method: 'POST',

        headers: {
          'Content-Type': 'application/json'
        },

        body: JSON.stringify({
          outcome: outcome,
          decided_by: 'Ali',
          note: note || undefined,
          modified_input:
            modifiedInput || undefined
        })
      }
    );

    if (!res.ok) {
      const errData =
        await res
          .json()
          .catch(() => ({}));

      throw new Error(
        errData.detail ||
        'Failed to resolve approval'
      );
    }

    const data = await res.json();

    /*
      Attach the original query to the newly-created
      resume trace.
    */
    await rememberNewTracesForQuery(
      activeQuery
    );

    if (outcome === 'approved') {
      banner.innerHTML =
        '<b>Approved:</b> Action confirmed and executed.';

    } else if (outcome === 'modified') {
      banner.innerHTML =
        '<b>Modified & Approved:</b> Action executed with modified parameters.';

    } else if (outcome === 'rejected') {
      banner.innerHTML =
        `<b>Rejected:</b> Action denied (${escapeHtml(
          note || 'No reason specified'
        )}).`;

    } else if (outcome === 'replan') {
      banner.innerHTML =
        '<b>Replanning:</b> Agent prompted to devise an alternative approach.';
    }

    responseContainer.style.display =
      'block';

    responseText.style.color = '';

    if (
      data.status === 'awaiting_approval'
    ) {
      title.innerText =
        'Next Step Awaiting Approval';

      badge.className =
        'badge badge-medium';

      badge.innerText =
        'WAITING FOR INPUT';

      await loadInPlaceApproval(
        data.thread_id
      );

      return;
    }

    title.innerText =
      'Execution Complete';

    badge.className =
      outcome === 'rejected'
        ? 'badge badge-high'
        : 'badge badge-low';

    badge.innerText =
      outcome === 'rejected'
        ? 'REJECTED'
        : 'COMPLETED';

    responseText.innerText =
      cleanAgentResponse(
        data.final_response ||
        'No response text returned.'
      );

  } catch (err) {
    banner.className =
      'decision-banner rejected';

    banner.innerText =
      'Error: ' + err.message;
  }
}