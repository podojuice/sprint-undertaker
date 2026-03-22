if (!requireAuth()) throw new Error("redirect");

const characterCard = document.querySelector("#character-card");
const titlePanel = document.querySelector("#title-panel");
const titleList = document.querySelector("#title-list");
const titleSummary = document.querySelector("#title-summary");
const projectPanel = document.querySelector("#project-panel");
const projectContent = document.querySelector("#project-content");
const noProjectPlaceholder = document.querySelector("#no-project-placeholder");

let currentActiveTitle = null;

function expBar(exp, expToNext) {
  const total = exp + expToNext;
  const pct = total > 0 ? Math.round((exp / total) * 100) : 0;
  return `
    <div class="exp-bar-wrap">
      <div class="exp-bar-track">
        <div class="exp-bar-fill" style="width: ${pct}%"></div>
      </div>
      <span class="exp-bar-label">${exp} / ${total} EXP</span>
    </div>
  `;
}

function renderCharacter(character) {
  if (!characterCard) return;
  currentActiveTitle = character.title;
  characterCard.className = "panel character-card-panel";
  characterCard.innerHTML = `
    <div class="char-header">
      <div>
        <h2 class="char-name">${escapeHtml(character.name)}</h2>
        <div class="character-meta">Lv.${character.level} · ${escapeHtml(character.character_class)}${character.title ? ` · <strong>${escapeHtml(character.title)}</strong>` : ""}</div>
      </div>
      <span class="char-level-badge">Lv.${character.level}</span>
    </div>
    ${expBar(character.exp, character.exp_to_next_level)}
    <div class="character-stats">
      <div><span>Impl</span><strong>${character.impl}</strong></div>
      <div><span>Focus</span><strong>${character.focus}</strong></div>
      <div><span>Stability</span><strong>${character.stability}</strong></div>
    </div>
  `;
}

function renderTitles(titles) {
  if (!titleList || !titlePanel) return;

  const unlockedCount = titles.filter((t) => t.unlocked).length;
  if (titleSummary) titleSummary.textContent = `${unlockedCount} / ${titles.length}`;

  titlePanel.classList.remove("hidden");
  titleList.className = "title-list";
  titleList.innerHTML = titles
    .map((title) => {
      const isActive = title.name === currentActiveTitle;
      const showEquip = title.unlocked && !isActive;
      const showUnequip = title.unlocked && isActive;

      let statusBadge = "";
      if (isActive) {
        statusBadge = `<span class="title-state title-state-active">Active</span>`;
      } else if (title.unlocked) {
        const note = title.earned_at ? `Earned ${title.earned_at.slice(0, 10)}` : "Unlocked";
        statusBadge = `<span class="title-state">${note}</span>`;
      } else if (title.status_label === "Available") {
        statusBadge = `<span class="title-state title-state-available">Available</span>`;
      } else if (title.status_label === "Scheduled") {
        statusBadge = `<span class="title-state title-state-muted">Upcoming</span>`;
      } else if (title.status_label === "Ended") {
        statusBadge = `<span class="title-state title-state-muted">Ended</span>`;
      } else {
        statusBadge = `<span class="title-state title-state-muted">Locked</span>`;
      }

      const equipButton = showEquip
        ? `<button class="button button-ghost equip-btn" data-title="${escapeHtml(title.name)}" type="button">Equip</button>`
        : "";
      const unequipButton = showUnequip
        ? `<button class="button button-ghost equip-btn" data-title="" type="button">Unequip</button>`
        : "";

      return `
        <article class="title-card ${title.unlocked ? "is-unlocked" : "is-locked"} ${isActive ? "is-active" : ""}" style="--title-accent: ${escapeHtml(title.theme_color)};">
          <div class="title-card-header">
            <div>
              <h3>${escapeHtml(title.name)}</h3>
              <p>${escapeHtml(title.description)}</p>
            </div>
            <div class="title-card-actions">
              ${statusBadge}
              ${equipButton}${unequipButton}
            </div>
          </div>
        </article>
      `;
    })
    .join("");

  titleList.querySelectorAll(".equip-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const titleName = btn.dataset.title || null;
      btn.disabled = true;
      try {
        const updated = await jsonRequest("/api/characters/me/title", {
          method: "PATCH",
          headers: { ...authHeaders(), "Content-Type": "application/json" },
          body: JSON.stringify({ title: titleName }),
        });
        currentActiveTitle = updated.title;
        renderTitles(titles.map((t) => ({ ...t })));
        if (characterCard) {
          characterCard.querySelector(".character-meta").innerHTML =
            `Lv.${updated.level} · ${escapeHtml(updated.character_class)}${updated.title ? ` · <strong>${escapeHtml(updated.title)}</strong>` : ""}`;
        }
      } catch (err) {
        alert(err.message);
        btn.disabled = false;
      }
    });
  });
}

function renderProject(project) {
  if (!projectPanel || !projectContent) return;

  if (!project) {
    return;
  }

  noProjectPlaceholder?.classList.add("hidden");
  projectPanel.classList.remove("hidden");

  const pct = project.target_progress > 0
    ? Math.round((Math.min(project.progress_value, project.target_progress) / project.target_progress) * 100)
    : 0;
  const status = project.is_completed ? "Cleared" : `${project.progress_value} / ${project.target_progress}`;
  const endsAt = project.ends_at.slice(0, 10);

  projectContent.innerHTML = `
    <p class="project-title">${escapeHtml(project.project_title)}</p>
    <p class="project-desc">${escapeHtml(project.description)}</p>
    <div class="exp-bar-wrap project-bar-wrap">
      <div class="exp-bar-track">
        <div class="exp-bar-fill ${project.is_completed ? "is-complete" : ""}" style="width: ${pct}%"></div>
      </div>
      <span class="exp-bar-label">${status}</span>
    </div>
    <p class="project-ends">Ends ${endsAt}</p>
  `;
}

function renderVisibility(character) {
  const existing = document.querySelector("#visibility-panel");
  if (existing) existing.remove();

  const panel = document.createElement("section");
  panel.id = "visibility-panel";
  panel.className = "panel visibility-panel";

  const profileUrl = `${location.origin}/u/${encodeURIComponent(character.name)}`;
  panel.innerHTML = `
    <div class="visibility-row">
      <div>
        <strong>Public profile</strong>
        <p>Share your character page with others.</p>
      </div>
      <label class="toggle-switch">
        <input type="checkbox" id="visibility-toggle" ${character.is_public ? "checked" : ""}>
        <span class="toggle-track"></span>
      </label>
    </div>
    ${character.is_public ? `<div class="visibility-link"><a href="${profileUrl}" target="_blank">${profileUrl}</a></div>` : ""}
  `;

  document.querySelector(".character-main")?.appendChild(panel);

  panel.querySelector("#visibility-toggle")?.addEventListener("change", async (e) => {
    const checked = e.target.checked;
    try {
      await jsonRequest("/api/characters/me/visibility", {
        method: "PATCH",
        headers: { ...authHeaders(), "Content-Type": "application/json" },
        body: JSON.stringify({ is_public: checked }),
      });
      character.is_public = checked;
      renderVisibility(character);
    } catch (err) {
      e.target.checked = !checked;
      alert(err.message);
    }
  });
}

async function load() {
  try {
    const [character, titles, project] = await Promise.all([
      jsonRequest("/api/characters/me", { headers: authHeaders() }),
      jsonRequest("/api/titles/me", { headers: authHeaders() }),
      jsonRequest("/api/characters/weekly-project", { headers: authHeaders() }).catch(() => null),
    ]);
    renderCharacter(character);
    renderTitles(titles);
    renderProject(project);
    renderVisibility(character);
  } catch (error) {
    if (characterCard) {
      characterCard.className = "panel character-card-panel empty-state";
      characterCard.textContent = error.message;
    }
  }
}

void load();
