const registerForm = document.querySelector("#register-form");
const loginForm = document.querySelector("#login-form");
const authStatus = document.querySelector("#auth-status");

function setStatus(message) {
  if (authStatus) authStatus.textContent = message;
}

if (getToken()) {
  window.location.href = "/character";
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
    window.location.href = "/character";
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
    window.location.href = "/character";
  } catch (error) {
    setStatus(error.message);
  }
}

registerForm?.addEventListener("submit", register);
loginForm?.addEventListener("submit", login);
