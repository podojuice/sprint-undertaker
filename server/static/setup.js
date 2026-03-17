const notLoggedInNote = document.querySelector("#not-logged-in-note");
const installationCard = document.querySelector("#installation-card");
const createWrap = document.querySelector("#create-wrap");
const createButton = document.querySelector("#create-installation-button");

function claudeSettingsSnippet() {
  return JSON.stringify({
    hooks: {
      SessionStart: [{ hooks: [{ type: "command", command: 'python3 "$HOME/.config/sprint-undertaker/claude-code-hook.py" SessionStart' }] }],
      UserPromptSubmit: [{ hooks: [{ type: "command", command: 'python3 "$HOME/.config/sprint-undertaker/claude-code-hook.py" UserPromptSubmit' }] }],
      PostToolUse: [{ matcher: "Edit|MultiEdit|Bash", hooks: [{ type: "command", command: 'python3 "$HOME/.config/sprint-undertaker/claude-code-hook.py" PostToolUse' }] }],
      PostToolUseFailure: [{ matcher: "Edit|MultiEdit|Bash", hooks: [{ type: "command", command: 'python3 "$HOME/.config/sprint-undertaker/claude-code-hook.py" PostToolUseFailure' }] }],
      Stop: [{ hooks: [{ type: "command", command: 'python3 "$HOME/.config/sprint-undertaker/claude-code-hook.py" Stop' }] }],
    },
  }, null, 2);
}

function renderInstallation(installation) {
  if (!installationCard) return;
  createWrap?.classList.add("hidden");

  const installCommand = `curl -fsSL "${window.location.origin}/install/claude-code.sh?api_key=${encodeURIComponent(installation.api_key)}&installation_name=${encodeURIComponent(installation.installation_name)}" | bash`;
  const safeCommand = escapeHtml(installCommand);
  const safeApiKey = escapeHtml(installation.api_key);
  const safeName = escapeHtml(installation.installation_name);

  installationCard.className = "install-output";
  installationCard.innerHTML = `
    <div class="install-summary">
      <div>
        <p><strong>${safeName}</strong> · ${escapeHtml(installation.provider)}</p>
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
    </div>
  `;
  installationCard.classList.remove("hidden");
  installationCard.querySelectorAll(".copy-trigger").forEach((btn) => {
    btn.addEventListener("click", () => void copyText(btn.dataset.copy || "", btn));
  });
}

async function createInstallation() {
  try {
    const installation = await jsonRequest("/api/installations", {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify({
        provider: "claude_code",
        installation_name: `claude-${new Date().toISOString().slice(0, 10)}`,
      }),
    });
    renderInstallation(installation);
  } catch (error) {
    if (installationCard) {
      installationCard.className = "";
      installationCard.textContent = error.message;
      installationCard.classList.remove("hidden");
    }
  }
}

async function init() {
  if (!getToken()) return;

  notLoggedInNote?.classList.add("hidden");

  try {
    const installations = await jsonRequest("/api/installations", { headers: authHeaders() });
    const existing = installations.find((i) => i.provider === "claude_code");
    if (existing) {
      renderInstallation(existing);
    } else {
      createWrap?.classList.remove("hidden");
    }
  } catch (_error) {
    createWrap?.classList.remove("hidden");
  }
}

createButton?.addEventListener("click", createInstallation);
document.querySelectorAll(".copy-trigger").forEach((btn) => {
  btn.addEventListener("click", () => void copyText(btn.dataset.copy || "", btn));
});

void init();
