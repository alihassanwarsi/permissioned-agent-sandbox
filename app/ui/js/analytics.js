// ANALYTICS TAB
async function loadAnalytics() {
  try {
    const res =
      await fetch(`${API_BASE}/analytics`);

    const stats =
      await res.json();

    document.getElementById(
      'stat-nodes'
    ).innerText =
      stats.total_nodes_run ?? 0;

    document.getElementById(
      'stat-denials'
    ).innerText =
      stats.denials ?? 0;

    document.getElementById(
      'stat-errors'
    ).innerText =
      stats.errors ?? 0;

    document.getElementById(
      'stat-rate'
    ).innerText =
      stats.approval_rate !== null
        ? (
            Math.round(
              stats.approval_rate * 100
            ) + '%'
          )
        : 'N/A';

    document.getElementById(
      'analytics-tools'
    ).innerText =
      JSON.stringify(
        stats.tool_usage || {},
        null,
        2
      );

  } catch (err) {
    console.error(
      'Analytics load error:',
      err
    );
  }
}