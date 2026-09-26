const API_BASE = 'http://localhost:8000';

let activeThreadId = null;
let activeRequestId = null;
let activeQuery = '';

const traceQueryMap = {};
let timelineTraceIds = [];

try {
  Object.assign(
    traceQueryMap,
    JSON.parse(
      localStorage.getItem('permissionedAgentTraceQueries') || '{}'
    )
  );
} catch (e) {
  console.warn('Unable to restore trace query history.');
}

let traceIdsBeforeRun = [];

function switchTab(name) {
  document.querySelectorAll('.tab-btn').forEach(b => {
    b.classList.remove('active');
  });

  document.querySelectorAll('.tab-content').forEach(c => {
    c.classList.remove('active');
  });

  const tabButton = [...document.querySelectorAll('.tab-btn')].find(
    b => b.getAttribute('onclick') === `switchTab('${name}')`
  );

  if (tabButton) {
    tabButton.classList.add('active');
  }

  document.getElementById('tab-' + name).classList.add('active');

  if (name === 'timeline') {
    loadTraceTimeline();
  }

  if (name === 'analytics') {
    loadAnalytics();
  }
}