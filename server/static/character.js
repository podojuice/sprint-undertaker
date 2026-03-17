if (!requireAuth()) throw new Error("redirect");

const characterCard = document.querySelector("#character-card");
const titlePanel = document.querySelector("#title-panel");
const titleList = document.querySelector("#title-list");
const titleSummary = document.querySelector("#title-summary");

function renderCharacter(character) {
  if (!characterCard) return;
  characterCard.className = "panel character-card-panel";
  characterCard.innerHTML = `
    <div class="char-header">
      <div>
        <h2 class="char-name">${escapeHtml(character.name)}</h2>
        <div class="character-meta">Lv.${character.level} · ${escapeHtml(character.character_class)}${character.title ? ` · <strong>${escapeHtml(character.title)}</strong>` : ""}</div>
      </div>
      <div class="char-exp">
        <span class="stat-label">EXP</span>
        <strong>${character.exp}</strong>
      </div>
    </div>
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
    .map((title) => `
      <article class="title-card ${title.unlocked ? "is-unlocked" : "is-locked"}" style="--title-accent: ${escapeHtml(title.theme_color)};">
        <div class="title-card-header">
          <div>
            <h3>${escapeHtml(title.name)}</h3>
            <p>${escapeHtml(title.description)}</p>
          </div>
          <span class="title-state">${escapeHtml(title.status_label)}</span>
        </div>
        <div class="title-meta">
          <span>${escapeHtml(title.status_note)}</span>
        </div>
      </article>
    `)
    .join("");
}

async function load() {
  try {
    const [character, titles] = await Promise.all([
      jsonRequest("/api/characters/me", { headers: authHeaders() }),
      jsonRequest("/api/titles/me", { headers: authHeaders() }),
    ]);
    renderCharacter(character);
    renderTitles(titles);
  } catch (error) {
    if (characterCard) {
      characterCard.className = "panel character-card-panel empty-state";
      characterCard.textContent = error.message;
    }
  }
}

void load();
