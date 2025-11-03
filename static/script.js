const apiUrl = "http://localhost:5000";

document.addEventListener("DOMContentLoaded", () => {
  // mantém dark mode
  if (localStorage.getItem("modoEscuro") === "1") document.body.classList.add("dark");

  const page = (location.pathname.split("/").pop() || "index").toLowerCase();

  // conecta botões por id
  const loginBtn = document.querySelector("#btnLogin");
  if (loginBtn) loginBtn.addEventListener("click", fazerLogin);

  const registerBtn = document.querySelector("#btnRegister");
  if (registerBtn) registerBtn.addEventListener("click", registrar);

  // select tipo
  const tipoSelect = document.getElementById("tipo");
  if (tipoSelect) tipoSelect.addEventListener("change", mostrarCampo);

  // EULA links
  const eulaLink = document.querySelectorAll(".abrir-eula");
  eulaLink.forEach(el => el.addEventListener("click", (e)=>{ e.preventDefault(); abrirEULA(); }));

  // se página welcome -> popula session; senão verifica sessão e redireciona
  if (page === "welcome.html") {
    fetchSessionAndPopulate();
  } else {
    fetch(`${apiUrl}/session`, { credentials: 'include' })
      .then(r => { if (r.ok) window.location.href = "welcome.html"; })
      .catch(()=>{});
  }
});

// ================= util
function mostrarCampo() {
  const tipo = document.getElementById("tipo").value;
  const campo = document.getElementById("identificador");
  if (!campo) return;
  if (tipo === "aluno") {
    campo.style.display = "block";
    campo.placeholder = "RA (deve terminar com 7749)";
  } else if (tipo === "professor") {
    campo.style.display = "block";
    campo.placeholder = "Matrícula (mín. 9 dígitos)";
  } else {
    campo.style.display = "none";
  }
}

function mostrarMensagem(elementoMsg, texto, tipo='ok') {
  if (!elementoMsg) return;
  elementoMsg.innerHTML = tipo === 'ok' ? `<p class="message">${texto}</p>` : `<p class="error">${texto}</p>`;
}

// ================= registrar
async function registrar(ev) {
  const nomeEl = document.getElementById("nome");
  const emailEl = document.getElementById("email");
  const senhaEl = document.getElementById("senha");
  const tipoEl = document.getElementById("tipo");
  const idEl = document.getElementById("identificador");
  const aceitouEl = document.getElementById("aceitou");
  const msg = document.getElementById("msg");

  if (!nomeEl || !emailEl || !senhaEl || !tipoEl || !aceitouEl) {
    mostrarMensagem(msg, "Erro interno: campos não encontrados.", "err");
    return;
  }

  const nome = nomeEl.value.trim();
  const email = emailEl.value.trim();
  const senha = senhaEl.value;
  const tipo = tipoEl.value;
  const identificador = idEl ? idEl.value.trim() : "";
  const aceitou = aceitouEl.checked;

  // validações front-end
  if (!nome || !/^[A-Za-zÀ-ÖØ-öø-ÿ ]+$/.test(nome)) {
    mostrarMensagem(msg, "Nome inválido. Use apenas letras e espaços.", "err"); return;
  }
  if (!email || email.indexOf("@") === -1 || !email.endsWith(".com")) {
    mostrarMensagem(msg, "E-mail inválido.", "err"); return;
  }
  if (!senha || senha.length < 8 || !/[A-Z]/.test(senha) || !/[a-z]/.test(senha) || !/\d/.test(senha)) {
    mostrarMensagem(msg, "Senha fraca. Pelo menos 8 caracteres, 1 maiúscula, 1 minúscula e 1 número.", "err"); return;
  }
  if (tipo !== "aluno" && tipo !== "professor") {
    mostrarMensagem(msg, "Escolha aluno ou professor.", "err"); return;
  }
  if (tipo === "aluno" && (!/^\d+$/.test(identificador) || !identificador.endsWith("7749"))) {
    mostrarMensagem(msg, "RA inválido. Deve terminar com 7749.", "err"); return;
  }
  if (tipo === "professor" && (!/^\d{9,}$/.test(identificador))) {
    mostrarMensagem(msg, "Matrícula inválida. Deve conter ao menos 9 dígitos.", "err"); return;
  }
  if (!aceitou) {
    mostrarMensagem(msg, "Você deve aceitar os termos para registrar.", "err"); return;
  }

  try {
    const resp = await fetch(`${apiUrl}/register`, {
      method: "POST",
      credentials: 'include',
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nome, email, senha, tipo, identificador, termos: aceitou })
    });

    const data = await resp.json();
    if (resp.ok && data.success) {
      mostrarMensagem(msg, data.success, 'ok');
      senhaEl.value = "";
      setTimeout(()=> window.location.href = "login.html", 1200);
    } else {
      mostrarMensagem(msg, data.error || "Erro no registro.", "err");
    }
  } catch (err) {
    mostrarMensagem(msg, "Erro de conexão com servidor.", "err");
    console.error(err);
  }
}

// ================= login
async function fazerLogin(ev) {
  const emailEl = document.getElementById("email");
  const senhaEl = document.getElementById("senha");
  const msg = document.getElementById("msg");
  if (!emailEl || !senhaEl) { mostrarMensagem(msg, "Campos não encontrados.", "err"); return; }

  const email = emailEl.value.trim();
  const senha = senhaEl.value;

  if (!email || !senha) { mostrarMensagem(msg, "Preencha e-mail e senha.", "err"); return; }

  try {
    const resp = await fetch(`${apiUrl}/login`, {
      method: "POST",
      credentials: 'include',
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, senha })
    });
    const data = await resp.json();
    if (resp.ok && data.success) {
      mostrarMensagem(msg, data.success, 'ok');
      setTimeout(()=> window.location.href = "welcome.html", 900);
    } else {
      mostrarMensagem(msg, data.error || "Erro ao logar.", "err");
    }
  } catch (err) {
    mostrarMensagem(msg, "Erro de conexão com servidor.", "err");
    console.error(err);
  }
}

// ================= welcome/session
async function fetchSessionAndPopulate() {
  try {
    const resp = await fetch(`${apiUrl}/session`, { credentials: 'include' });
    if (!resp.ok) { window.location.href = "login.html"; return; }
    const user = await resp.json();
    const boas = document.getElementById("boasVindas");
    const tipoMsg = document.getElementById("mensagemTipo");
    if (boas) boas.textContent = `Olá, ${user.nome}!`;
    if (tipoMsg) tipoMsg.textContent = user.tipo === "aluno" ? "Você entrou como aluno. Bons estudos!" : "Você entrou como professor. Bom trabalho!";
  } catch (err) {
    console.error(err);
    window.location.href = "login.html";
  }
}

async function logout() {
  try {
    await fetch(`${apiUrl}/logout`, { method: "POST", credentials: 'include' });
  } catch (e) { /* ignore */ }
  window.location.href = "login.html";
}

// ================= EULA modal
function abrirEULA() {
  const modal = document.getElementById("eulaModal");
  const texto = document.getElementById("eulaTexto");
  if (!modal || !texto) return;
  fetch("eula.txt").then(r => r.text()).then(t => {
    texto.textContent = t;
    modal.style.display = "block";
  }).catch(()=> {
    texto.textContent = "Erro ao carregar termos.";
    modal.style.display = "block";
  });
}
function fecharEULA() {
  const modal = document.getElementById("eulaModal");
  if (modal) modal.style.display = "none";
}

// ================= dark mode
function toggleDarkMode() {
  document.body.classList.toggle("dark");
  localStorage.setItem("modoEscuro", document.body.classList.contains("dark") ? "1" : "0");
}
