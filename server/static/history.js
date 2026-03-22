if (!requireAuth()) throw new Error("redirect");

const activityList = document.querySelector("#activity-list");

function formatDate(isoString) {
  return new Date(isoString).toLocaleString(undefined, {
    month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
  });
}

function renderActivity(items) {
  if (!activityList) return;

  if (items.length === 0) {
    activityList.className = "empty-state activity-empty";
    activityList.innerHTML = `
      No activity yet.
      <a href="/setup" class="activity-empty-link">Set up the plugin</a> to start tracking.
    `;
    return;
  }

  activityList.className = "activity-table";
  activityList.innerHTML = items
    .map((item) => {
      const date = formatDate(item.occurred_at);
      const isProjectClear = item.event_type === "project_cleared";
      const stats = item.stat_hints.length > 0
        ? item.stat_hints.map((h) => `<code class="stat-hint">${escapeHtml(h)}</code>`).join("")
        : "";
      return `
        <div class="activity-row ${isProjectClear ? "activity-row-highlight" : ""}">
          <span class="activity-row-date">${date}</span>
          <span class="activity-row-summary">${escapeHtml(item.summary)}</span>
          <span class="activity-row-stats">${stats}</span>
        </div>
      `;
    })
    .join("");
}

async function load() {
  try {
    const response = await jsonRequest("/api/characters/me/activity", {
      headers: authHeaders(),
    });
    renderActivity(response.items);
  } catch (error) {
    if (activityList) {
      activityList.className = "empty-state";
      activityList.textContent = error.message;
    }
  }
}

void load();
