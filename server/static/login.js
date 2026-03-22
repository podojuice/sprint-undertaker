const registerForm = document.querySelector("#register-form");
const loginForm = document.querySelector("#login-form");
const registerError = document.querySelector("#register-error");
const loginError = document.querySelector("#login-error");

function showError(el, message) {
  if (!el) return;
  el.textContent = message;
  el.classList.remove("hidden");
}

function clearError(el) {
  if (!el) return;
  el.textContent = "";
  el.classList.add("hidden");
}

if (getToken()) {
  window.location.href = "/character";
}

async function register(event) {
  event.preventDefault();
  clearError(registerError);
  const formData = new FormData(registerForm);
  try {
    const data = await jsonRequest("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(Object.fromEntries(formData.entries())),
    });
    setToken(data.access_token);
    window.location.href = "/character";
  } catch (error) {
    showError(registerError, error.message);
  }
}

async function login(event) {
  event.preventDefault();
  clearError(loginError);
  const formData = new FormData(loginForm);
  try {
    const data = await jsonRequest("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(Object.fromEntries(formData.entries())),
    });
    setToken(data.access_token);
    window.location.href = "/character";
  } catch (error) {
    showError(loginError, error.message);
  }
}

registerForm?.addEventListener("submit", register);
loginForm?.addEventListener("submit", login);
