async function fetchTraceIdsSafe() {
  try {
    const res =
      await fetch(`${API_BASE}/traces`);

    if (!res.ok) {
      return [];
    }

    const ids =
      await res.json();

    return Array.isArray(ids)
      ? ids
      : [];

  } catch (err) {
    return [];
  }
}


async function rememberNewTracesForQuery(
  query
) {
  try {
    const ids =
      await fetchTraceIdsSafe();

    if (!ids.length) {
      return;
    }

    const newIds =
      ids.filter(
        id =>
          !traceIdsBeforeRun.includes(id)
      );

    if (newIds.length) {
      newIds.forEach(id => {
        traceQueryMap[id] = query;
      });

      persistTraceQueries();

    } else if (
      ids.length === 1 &&
      !traceQueryMap[ids[0]] &&
      query
    ) {
      traceQueryMap[ids[0]] =
        query;

      persistTraceQueries();
    }

    timelineTraceIds = ids;

  } catch (err) {
    console.warn(
      'Unable to associate trace query:',
      err
    );
  }
}


function persistTraceQueries() {
  try {
    localStorage.setItem(
      'permissionedAgentTraceQueries',
      JSON.stringify(traceQueryMap)
    );

  } catch (err) {
    console.warn(
      'Unable to persist trace query history.'
    );
  }
}


async function loadTraceTimeline(
  preferredTraceId = ''
) {
  const select =
    document.getElementById(
      'timeline-trace-select'
    );

  const spansEl =
    document.getElementById(
      'timeline-spans'
    );

  try {
    const res =
      await fetch(
        `${API_BASE}/traces`
      );

    if (!res.ok) {
      throw new Error(
        'Failed to load trace IDs'
      );
    }

    const traceIds =
      await res.json();

    timelineTraceIds =
      traceIds;

    if (!traceIds.length) {
      select.innerHTML =
        '<option value="">No trace IDs available</option>';

      document.getElementById(
        'timeline-query-text'
      ).innerText =
        'No traces recorded yet.';

      document.getElementById(
        'timeline-summary'
      ).style.display =
        'none';

      spansEl.innerHTML =
        '<div class="timeline-empty">Run an agent task to create a trace.</div>';

      return;
    }

    const currentSelection =
      preferredTraceId ||
      select.value;

    select.innerHTML =
      traceIds.map(
        (id, index) => `
          <option
            value="${escapeHtml(id)}"
            ${
              id === currentSelection ||
              (
                !currentSelection &&
                index ===
                  traceIds.length - 1
              )
                ? 'selected'
                : ''
            }
          >
            ${escapeHtml(id)}
          </option>
        `
      ).join('');

    const selectedId =
      select.value ||
      traceIds[
        traceIds.length - 1
      ];

    await selectTimelineTrace(
      selectedId
    );

  } catch (err) {
    select.innerHTML =
      '<option value="">Unable to load traces</option>';

    spansEl.innerHTML = `
      <div
        class="timeline-empty"
        style="color:var(--danger);"
      >
        Failed to load trace timeline:
        ${escapeHtml(err.message)}
      </div>
    `;
  }
}


async function selectTimelineTrace(
  traceId
) {
  const queryEl =
    document.getElementById(
      'timeline-query-text'
    );

  const summaryEl =
    document.getElementById(
      'timeline-summary'
    );

  const spansEl =
    document.getElementById(
      'timeline-spans'
    );

  if (!traceId) {
    queryEl.innerText =
      'Select a trace to inspect its execution.';

    summaryEl.style.display =
      'none';

    spansEl.innerHTML =
      '<div class="timeline-empty">No trace selected.</div>';

    return;
  }

  spansEl.innerHTML = `
    <div class="timeline-empty">
      <span class="loading-spinner"></span>
      Loading trace details...
    </div>
  `;

  try {
    const res =
      await fetch(
        `${API_BASE}/traces/${encodeURIComponent(
          traceId
        )}`
      );

    if (!res.ok) {
      const errData =
        await res
          .json()
          .catch(() => ({}));

      throw new Error(
        errData.detail ||
        'Failed to load trace'
      );
    }

    const spans =
      await res.json();

    renderTraceTimeline(
      traceId,
      spans
    );

    const traceQuery =
      getQueryFromSpans(spans);

    queryEl.innerText =
      traceQueryMap[traceId] ||
      traceQuery ||
      'Query unavailable for this trace.';

  } catch (err) {
    summaryEl.style.display =
      'none';

    spansEl.innerHTML = `
      <div
        class="timeline-empty"
        style="color:var(--danger);"
      >
        Error loading trace:
        ${escapeHtml(err.message)}
      </div>
    `;
  }
}


function getQueryFromSpans(
  spans
) {
  for (
    const span of
    (
      Array.isArray(spans)
        ? spans
        : []
    )
  ) {
    const attrs =
      span.attributes || {};

    const query =
      attrs.query ||
      attrs['user.query'] ||
      attrs['input.query'] ||
      attrs['user_message'];

    if (query) {
      return String(query);
    }
  }

  return '';
}


function renderTraceTimeline(
  traceId,
  spans
) {
  const summaryEl =
    document.getElementById(
      'timeline-summary'
    );

  const spansEl =
    document.getElementById(
      'timeline-spans'
    );

  if (
    !Array.isArray(spans) ||
    spans.length === 0
  ) {
    summaryEl.style.display =
      'none';

    spansEl.innerHTML =
      '<div class="timeline-empty">This trace has no recorded spans.</div>';

    return;
  }

  const sortedSpans =
    [...spans].sort(
      (a, b) =>
        Number(
          a.start_time || 0
        ) -
        Number(
          b.start_time || 0
        )
    );

  const traceStart =
    Number(
      sortedSpans[0]
        .start_time || 0
    );

  const traceEnd =
    Math.max(
      ...sortedSpans.map(
        span =>
          Number(
            span.end_time ||
            span.start_time ||
            0
          )
      )
    );

  const totalDuration =
    formatDurationNs(
      traceEnd - traceStart
    );

  const decisions =
    sortedSpans
      .map(
        span =>
          span.attributes
            ?.decision
      )
      .filter(Boolean);

  const errors =
    sortedSpans.filter(
      span =>
        (
          span.attributes
            ?.status ||
          ''
        ).toLowerCase() ===
        'error'
    ).length;

  summaryEl.style.display =
    'flex';

  summaryEl.innerHTML = `
    <span class="timeline-meta-chip">
      <b>Trace:</b>
      ${escapeHtml(traceId)}
    </span>

    <span class="timeline-meta-chip">
      <b>Nodes:</b>
      ${sortedSpans.length}
    </span>

    <span class="timeline-meta-chip">
      <b>Total:</b>
      ${escapeHtml(totalDuration)}
    </span>

    ${
      decisions.length
        ? `
          <span class="timeline-meta-chip">
            <b>Decisions:</b>
            ${escapeHtml(
              [
                ...new Set(
                  decisions
                )
              ].join(', ')
            )}
          </span>
        `
        : ''
    }

    ${
      errors
        ? `
          <span
            class="timeline-meta-chip"
            style="
              border-color:var(--danger);
              color:#fca5a5;
            "
          >
            <b>Errors:</b>
            ${errors}
          </span>
        `
        : ''
    }
  `;

  spansEl.innerHTML = `
    <div class="timeline">
      ${
        sortedSpans
          .map(
            (
              span,
              index
            ) =>
              renderTimelineItem(
                span,
                index,
                sortedSpans.length
              )
          )
          .join('')
      }
    </div>
  `;
}


function renderTimelineItem(
  span,
  index,
  total
) {
  const attrs =
    span.attributes || {};

  const status =
    String(
      attrs.status || ''
    ).toLowerCase();

  const decision =
    attrs.decision
      ? String(
          attrs.decision
        )
      : '';

  const dotClass =
    status === 'error' ||
    decision === 'denied'
      ? 'danger'

      : decision ===
          'needs_approval' ||
        decision ===
          'needs_confirmation' ||
        decision ===
          'rate_limited'
        ? 'warning'

        : 'success';

  const duration =
    formatDurationNs(
      Number(
        span.end_time || 0
      ) -
      Number(
        span.start_time || 0
      )
    );

  const startTime =
    formatTimestamp(
      span.start_time
    );

  const endTime =
    formatTimestamp(
      span.end_time
    );

  const selectedTool =
    attrs['tool.selected'];

  const fields = [
    {
      label: 'Node',
      value:
        span.name ||
        'Unknown'
    },
    {
      label: 'Duration',
      value:
        duration
    },
    {
      label: 'Start',
      value:
        startTime
    },
    {
      label: 'End',
      value:
        endTime
    }
  ];

  if (selectedTool) {
    fields.push({
      label: 'Tool',
      value:
        selectedTool
    });
  }

  if (decision) {
    fields.push({
      label: 'Decision',
      value:
        decision
    });
  }

  if (status) {
    fields.push({
      label: 'Status',
      value:
        status
    });
  }

  return `
    <div class="timeline-item">

      <div
        class="timeline-dot ${dotClass}"
      ></div>

      <div class="timeline-node">

        <div
          class="timeline-node-header"
        >

          <div
            class="timeline-node-name"
          >
            ${escapeHtml(
              span.name ||
              `Node ${index + 1}`
            )}
          </div>

          <div
            class="timeline-node-duration"
          >
            ${escapeHtml(
              duration
            )}
          </div>

        </div>

        <div
          class="timeline-node-summary"
        >
          ${
            fields.map(
              field => `
                <div
                  class="timeline-field"
                >

                  <span
                    class="timeline-field-label"
                  >
                    ${escapeHtml(
                      field.label
                    )}
                  </span>

                  <span
                    class="timeline-field-value"
                  >
                    ${escapeHtml(
                      String(
                        field.value
                      )
                    )}
                  </span>

                </div>
              `
            ).join('')
          }
        </div>

        <details
          class="timeline-details"
        >
          <summary>
            View deep details
          </summary>

          <pre>${escapeHtml(
            JSON.stringify(
              {
                name:
                  span.name,

                start_time:
                  span.start_time,

                end_time:
                  span.end_time,

                duration_ms:
                  calculateDurationMs(
                    span.start_time,
                    span.end_time
                  ),

                attributes:
                  attrs
              },
              null,
              2
            )
          )}</pre>
        </details>

      </div>
    </div>
  `;
}


function calculateDurationMs(
  startTime,
  endTime
) {
  const start =
    Number(
      startTime || 0
    );

  const end =
    Number(
      endTime || 0
    );

  if (
    !start ||
    !end ||
    end < start
  ) {
    return null;
  }

  return Number(
    (
      (end - start) /
      1e6
    ).toFixed(3)
  );
}


function formatDurationNs(
  durationNs
) {
  const ms =
    Number(
      durationNs || 0
    ) / 1e6;

  if (
    !Number.isFinite(ms) ||
    ms < 0
  ) {
    return 'N/A';
  }

  if (ms < 1) {
    return `${ms.toFixed(3)} ms`;
  }

  if (ms < 1000) {
    return `${ms.toFixed(2)} ms`;
  }

  return `${
    (
      ms / 1000
    ).toFixed(2)
  } s`;
}


function formatTimestamp(
  value
) {
  if (!value) {
    return 'N/A';
  }

  const ns =
    Number(value);

  if (
    !Number.isFinite(ns)
  ) {
    return String(value);
  }

  const date =
    new Date(
      ns / 1e6
    );

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return String(value);
  }

  return date.toLocaleString();
}


function escapeHtml(
  value
) {
  return String(
    value ?? ''
  )
    .replace(
      /&/g,
      '&amp;'
    )
    .replace(
      /</g,
      '&lt;'
    )
    .replace(
      />/g,
      '&gt;'
    )
    .replace(
      /"/g,
      '&quot;'
    )
    .replace(
      /'/g,
      '&#039;'
    );
}