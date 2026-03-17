if (!requireAuth()) throw new Error("redirect");

const activityList = document.querySelector("#activity-list");

const EVENT_TYPE_LABELS = {
  turn_completed: "Turn",
  project_cleared: "Project Clear",
};

const PROVIDER_LABELS = {
  claude_code: "Claude Code",
};

function renderActivity(items) {
  if (!activityList) return;

  if (items.length === 0) {
    activityList.className = "empty-state";
    activityList.textContent = "No growth activity yet.";
    return;
  }

  activityList.className = "activity-list";
  activityList.innerHTML = items
    .map((item) => {
      const label = EVENT_TYPE_LABELS[item.event_type] || item.event_type;
      const provider = PROVIDER_LABELS[item.provider] || item.provider;
      const date = new Date(item.occurred_at).toLocaleString(undefined, {
        month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
      });
      const stats = item.stat_hints.length > 0
        ? item.stat_hints.map((hint) => `<code>${escapeHtml(hint)}</code>`).join(" · ")
        : null;
      return `
        <article class="activity-card">
          <div class="activity-card-header">
            <h3>${escapeHtml(label)}</h3>
            <span class="activity-date">${date}</span>
          </div>
          <p>${escapeHtml(item.summary)}</p>
          <div class="activity-card-meta">
            <span>${escapeHtml(provider)}</span>
            ${stats ? `<span>${stats}</span>` : ""}
          </div>
        </article>
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
