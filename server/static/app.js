const authStatus = document.querySelector("#auth-status");
const characterCard = document.querySelector("#character-card");
const installationCard = document.querySelector("#installation-card");
const titlePanel = document.querySelector("#title-panel");
const titleList = document.querySelector("#title-list");
const titleSummary = document.querySelector("#title-summary");
const activityPanel = document.querySelector("#activity-panel");
const activityList = document.querySelector("#activity-list");
const refreshButton = document.querySelector("#refresh-button");
const createInstallationButton = document.querySelector("#create-installation-button");
const registerForm = document.querySelector("#register-form");
const loginForm = document.querySelector("#login-form");
const authForms = document.querySelector("#auth-forms");
const accountPanel = document.querySelector("#account-panel");
const logoutButton = document.querySelector("#logout-button");

const TOKEN_KEY = "idle_rpg_access_token";

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  }[char]));
}

async function copyText(value, button) {
  try {
    await navigator.clipboard.writeText(value);
    if (button) {
      const previous = button.textContent;
      button.textContent = "Copied";
      window.setTimeout(() => {
        button.textContent = previous;
      }, 1200);
    }
  } catch (_error) {
    setStatus("Copy failed. Copy manually from the command box.");
  }
}

function getToken() {
  return window.localStorage.getItem(TOKEN_KEY);
}

function setToken(token) {
  window.localStorage.setItem(TOKEN_KEY, token);
}

function clearToken() {
  window.localStorage.removeItem(TOKEN_KEY);
}

function authHeaders() {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function setStatus(message) {
  if (authStatus) {
    authStatus.textContent = message;
  }
}

function updateAuthView() {
  const isLoggedIn = Boolean(getToken());
  authForms?.classList.toggle("hidden", isLoggedIn);
  accountPanel?.classList.toggle("hidden", !isLoggedIn);
  titlePanel?.classList.toggle("hidden", !isLoggedIn);
  activityPanel?.classList.toggle("hidden", !isLoggedIn);
}

async function jsonRequest(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || "Request failed");
  }
  return data;
}

function renderCharacter(character) {
  if (!characterCard) return;
  if (!character) {
    characterCard.className = "character-card empty-state";
    characterCard.textContent = "Login first to load your character.";
    return;
  }

  characterCard.className = "character-card";
  characterCard.innerHTML = `
    <h3>${character.name}</h3>
    <div class="character-meta">Lv.${character.level} · ${character.character_class}${character.title ? ` · ${character.title}` : ""}</div>
    <div class="character-stats">
      <div><span>EXP</span><strong>${character.exp}</strong></div>
      <div><span>Impl</span><strong>${character.impl}</strong></div>
      <div><span>Focus</span><strong>${character.focus}</strong></div>
      <div><span>Stability</span><strong>${character.stability}</strong></div>
    </div>
  `;
}

function claudeSettingsSnippet() {
  return JSON.stringify({
    hooks: {
      SessionStart: [
        {
          hooks: [
            {
              type: "command",
              command: 'python3 "$HOME/.config/idle-rpg/claude-code-hook.py" SessionStart',
            },
          ],
        },
      ],
      UserPromptSubmit: [
        {
          hooks: [
            {
              type: "command",
              command: 'python3 "$HOME/.config/idle-rpg/claude-code-hook.py" UserPromptSubmit',
            },
          ],
        },
      ],
      PostToolUse: [
        {
          matcher: "Edit|MultiEdit|Bash",
          hooks: [
            {
              type: "command",
              command: 'python3 "$HOME/.config/idle-rpg/claude-code-hook.py" PostToolUse',
            },
          ],
        },
      ],
      PostToolUseFailure: [
        {
          matcher: "Edit|MultiEdit|Bash",
          hooks: [
            {
              type: "command",
              command: 'python3 "$HOME/.config/idle-rpg/claude-code-hook.py" PostToolUseFailure',
            },
          ],
        },
      ],
      Stop: [
        {
          hooks: [
            {
              type: "command",
              command: 'python3 "$HOME/.config/idle-rpg/claude-code-hook.py" Stop',
            },
          ],
        },
      ],
    },
  }, null, 2);
}

function renderInstallation(installation) {
  if (!installationCard) return;
  if (!installation) {
    installationCard.className = "empty-state";
    installationCard.textContent = "Login, then create an installation to get your Claude hook API key.";
    return;
  }

  const installCommand = `curl -fsSL "${window.location.origin}/install/claude-code.sh?api_key=${encodeURIComponent(
    installation.api_key,
  )}&installation_name=${encodeURIComponent(installation.installation_name)}" | bash`;
  const safeCommand = escapeHtml(installCommand);
  const safeApiKey = escapeHtml(installation.api_key);
  const safeName = escapeHtml(installation.installation_name);
  const hookSnippet = claudeSettingsSnippet();
  const safeHookSnippet = escapeHtml(hookSnippet);

  installationCard.className = "install-output";
  installationCard.innerHTML = `
    <div class="install-summary">
      <div>
        <p><strong>${safeName}</strong> · ${installation.provider}</p>
        <div class="installation-meta">Install the local hook collector once, then add the settings snippet to Claude Code. The collector requires <code>python3</code>.</div>
      </div>
      <span class="install-chip">Privacy-safe summary only</span>
    </div>
    <div class="command-block">
      <div class="command-header">
        <span>Installer Command</span>
        <button class="button button-ghost copy-trigger" type="button" data-copy="${safeCommand}">Copy</button>
      </div>
      <pre><code>${safeCommand}</code></pre>
    </div>
    <div class="command-grid">
      <div class="command-block compact">
        <div class="command-header">
          <span>API Key</span>
          <button class="button button-ghost copy-trigger" type="button" data-copy="${safeApiKey}">Copy</button>
        </div>
        <pre><code>${safeApiKey}</code></pre>
      </div>
      <div class="command-block compact">
        <div class="command-header">
          <span>Hook Script</span>
          <button class="button button-ghost copy-trigger" type="button" data-copy='python3 "$HOME/.config/idle-rpg/claude-code-hook.py"'>Copy</button>
        </div>
        <pre><code>python3 "$HOME/.config/idle-rpg/claude-code-hook.py"</code></pre>
      </div>
    </div>
    <div class="command-block">
      <div class="command-header">
        <span>Claude Hook Settings Snippet</span>
        <button class="button button-ghost copy-trigger" type="button" data-copy="${escapeHtml(hookSnippet)}">Copy</button>
      </div>
      <pre><code>${safeHookSnippet}</code></pre>
    </div>
    <div class="install-checklist install-checklist-compact">
      <div>
        <span class="step-badge">1</span>
        <div>
          <strong>Run the installer once</strong>
          <p>The script writes <code>~/.config/idle-rpg/claude-code-hook.py</code> and <code>~/.config/idle-rpg/claude-code-hook.env</code>. It requires <code>python3</code>.</p>
        </div>
      </div>
      <div>
        <span class="step-badge">2</span>
        <div>
          <strong>Add the settings snippet</strong>
          <p>Merge the JSON into <code>~/.claude/settings.json</code> or <code>.claude/settings.local.json</code>. Do not replace unrelated settings in the file.</p>
        </div>
      </div>
      <div>
        <span class="step-badge">3</span>
        <div>
          <strong>Use Claude Code normally</strong>
          <p>The hook collector listens to Claude hook events and sends one summary per completed turn.</p>
        </div>
      </div>
    </div>
  `;
  installationCard.querySelectorAll(".copy-trigger").forEach((button) => {
    button.addEventListener("click", () => {
      void copyText(button.dataset.copy || "", button);
    });
  });
}

function renderTitles(titles) {
  if (!titleList) return;
  if (!titles) {
    if (titleSummary) titleSummary.textContent = "";
    titleList.className = "empty-state";
    titleList.textContent = "Login first to load your title list.";
    return;
  }

  if (titles.length === 0) {
    if (titleSummary) titleSummary.textContent = "0 unlocked";
    titleList.className = "empty-state";
    titleList.textContent = "No titles have been seeded yet.";
    return;
  }

  const unlockedCount = titles.filter((title) => title.unlocked).length;
  if (titleSummary) {
    titleSummary.textContent = `${unlockedCount} unlocked / ${titles.length} visible`;
  }

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
          <span>${title.unlocked && title.earned_at ? `Earned: ${new Date(title.earned_at).toLocaleDateString()}` : "Not earned yet."}</span>
        </div>
      </article>
    `)
    .join("");
}

function renderActivity(items) {
  if (!activityList) return;
  if (!items) {
    activityList.className = "empty-state";
    activityList.textContent = "Login first to load your recent growth log.";
    return;
  }

  if (items.length === 0) {
    activityList.className = "empty-state";
    activityList.textContent = "No growth activity yet.";
    return;
  }

  activityList.className = "title-list";
  activityList.innerHTML = items
    .map((item) => `
      <article class="title-card is-unlocked">
        <div class="title-card-header">
          <div>
            <h3>${escapeHtml(item.event_type)}</h3>
            <p>${escapeHtml(item.summary)}</p>
          </div>
          <span class="title-state">${new Date(item.occurred_at).toLocaleString()}</span>
        </div>
        <div class="title-meta">
          <span>Provider: ${escapeHtml(item.provider)}</span>
          <span>Stats: ${item.stat_hints.length > 0 ? item.stat_hints.map((hint) => `<code>${escapeHtml(hint)}</code>`).join(", ") : "none"}</span>
          <span>${item.session_id ? `Session: ${escapeHtml(item.session_id)}` : "No session id"}</span>
        </div>
      </article>
    `)
    .join("");
}

async function loadCharacter() {
  if (!getToken()) {
    renderCharacter(null);
    return;
  }
  try {
    const character = await jsonRequest("/api/characters/me", {
      headers: { ...authHeaders() },
    });
    renderCharacter(character);
    setStatus("Logged in.");
    updateAuthView();
  } catch (error) {
    setStatus(error.message);
  }
}

async function loadInstallations() {
  if (!getToken()) {
    renderInstallation(null);
    return;
  }
  try {
    const installations = await jsonRequest("/api/installations", {
      headers: { ...authHeaders() },
    });
    const installation = installations.find((item) => item.provider === "claude_code");
    renderInstallation(installation || null);
  } catch (error) {
    installationCard.textContent = error.message;
  }
}

async function loadTitles() {
  if (!getToken()) {
    renderTitles(null);
    return;
  }
  try {
    const titles = await jsonRequest("/api/titles/me", {
      headers: { ...authHeaders() },
    });
    renderTitles(titles);
  } catch (error) {
    titleList.textContent = error.message;
  }
}

async function loadActivity() {
  if (!getToken()) {
    renderActivity(null);
    return;
  }
  try {
    const response = await jsonRequest("/api/characters/me/activity", {
      headers: { ...authHeaders() },
    });
    renderActivity(response.items);
  } catch (error) {
    activityList.textContent = error.message;
  }
}

async function register(event) {
  event.preventDefault();
  const formData = new FormData(registerForm);
  try {
    const data = await jsonRequest("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(Object.fromEntries(formData.entries())),
    });
    setToken(data.access_token);
    setStatus(`Registered as ${data.email}`);
    registerForm.reset();
    loginForm?.reset();
    updateAuthView();
    await Promise.all([loadCharacter(), loadInstallations(), loadTitles(), loadActivity()]);
  } catch (error) {
    setStatus(error.message);
  }
}

async function login(event) {
  event.preventDefault();
  const formData = new FormData(loginForm);
  try {
    const data = await jsonRequest("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(Object.fromEntries(formData.entries())),
    });
    setToken(data.access_token);
    setStatus(`Logged in as ${data.email}`);
    loginForm.reset();
    registerForm?.reset();
    updateAuthView();
    await Promise.all([loadCharacter(), loadInstallations(), loadTitles(), loadActivity()]);
  } catch (error) {
    setStatus(error.message);
  }
}

function logout() {
  clearToken();
  updateAuthView();
  renderCharacter(null);
  renderInstallation(null);
  renderTitles(null);
  renderActivity(null);
  registerForm?.reset();
  loginForm?.reset();
  setStatus("Not logged in.");
}

async function createClaudeInstallation() {
  if (!getToken()) {
    setStatus("Login first.");
    return;
  }
  try {
    const installation = await jsonRequest("/api/installations", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...authHeaders(),
      },
      body: JSON.stringify({
        provider: "claude_code",
        installation_name: `claude-${new Date().toISOString().slice(0, 10)}`,
      }),
    });
    renderInstallation(installation);
    setStatus("Claude Code installation created.");
  } catch (error) {
    installationCard.textContent = error.message;
  }
}

registerForm?.addEventListener("submit", register);
loginForm?.addEventListener("submit", login);
logoutButton?.addEventListener("click", logout);
refreshButton?.addEventListener("click", async () => {
  await Promise.all([loadCharacter(), loadInstallations(), loadTitles(), loadActivity()]);
});
createInstallationButton?.addEventListener("click", createClaudeInstallation);

updateAuthView();
void Promise.all([loadCharacter(), loadInstallations(), loadTitles(), loadActivity()]);
