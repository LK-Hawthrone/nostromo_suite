from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
import os
import json
import re
import bcrypt

app = Flask(__name__, static_folder="static")
CORS(app, supports_credentials=True)
app.secret_key = "segredo_super_seguro"  # troque em produção

# =============================
# 🔧 Helpers para JSON/DB
# =============================
DB_DIR = "database"
DB_FILE = os.path.join(DB_DIR, "users.json")

def carregar_usuarios():
    """Carrega usuários do arquivo JSON; lida com arquivo vazio/corrompido."""
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            conteudo = f.read().strip()
            if not conteudo:
                return {}
            return json.loads(conteudo)
    except (json.JSONDecodeError, ValueError):
        print("⚠️ Aviso: users.json vazio/corrompido. Reiniciando em memória.")
        return {}

def salvar_usuarios(usuarios):
    os.makedirs(DB_DIR, exist_ok=True)
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(usuarios, f, indent=4, ensure_ascii=False)

# =============================
# 🔎 Validações
# =============================
def validar_email(email):
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

def validar_nome(nome):
    return bool(re.match(r"^[A-Za-zÀ-ÿ\s]+$", nome))

def validar_senha(senha):
    return bool(re.match(r"^(?=.*[a-z])(?=.*[A-Z]).{8,}$", senha))

def validar_ra(ra):
    return bool(re.match(r"^\d+$", ra)) and ra.endswith("7749")

def validar_matricula(matricula):
    return bool(re.match(r"^\d{9,}$", matricula))

# =============================
# 🌐 Rotas
# =============================
@app.route("/")
def index():
    return send_from_directory("static", "login.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory("static", path)

@app.route("/session", methods=["GET"])
def get_session():
    user = session.get("user")
    if user:
        return jsonify(user), 200
    return jsonify({"error": "Não autenticado"}), 401

# --------- Register ---------
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    nome = (data.get("nome") or "").strip()
    email = (data.get("email") or "").strip().lower()
    senha = data.get("senha") or ""
    tipo = (data.get("tipo") or "").strip().lower()
    identificador = (data.get("identificador") or "").strip()
    termos = bool(data.get("termos", False))

    # validações
    if not all([nome, email, senha, tipo, identificador]):
        return jsonify({"error": "Preencha todos os campos!"}), 400
    if not validar_nome(nome):
        return jsonify({"error": "O nome deve conter apenas letras e espaços."}), 400
    if not validar_email(email):
        return jsonify({"error": "E-mail inválido."}), 400
    if not validar_senha(senha):
        return jsonify({"error": "Senha fraca: mínimo 8 caracteres, 1 maiúscula e 1 minúscula."}), 400
    if not termos:
        return jsonify({"error": "Você deve aceitar os termos."}), 400
    if tipo not in ("aluno", "professor"):
        return jsonify({"error": "Tipo inválido."}), 400
    if tipo == "aluno" and not validar_ra(identificador):
        return jsonify({"error": "RA inválido (deve terminar com 7749)."}), 400
    if tipo == "professor" and not validar_matricula(identificador):
        return jsonify({"error": "Matrícula inválida (mínimo 9 dígitos)."}), 400

    usuarios = carregar_usuarios()
    if email in usuarios:
        return jsonify({"error": "E-mail já registrado."}), 400

    # hash da senha com bcrypt
    senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    usuarios[email] = {
        "nome": nome,
        "senha": senha_hash,
        "tipo": tipo,
        "identificador": identificador
    }
    salvar_usuarios(usuarios)
    return jsonify({"success": "Registro concluído com sucesso!"}), 200

# --------- Login ---------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    senha = data.get("senha") or ""

    usuarios = carregar_usuarios()
    user = usuarios.get(email)
    if not user:
        return jsonify({"error": "E-mail não registrado."}), 400

    # compara hash
    if not bcrypt.checkpw(senha.encode("utf-8"), user["senha"].encode("utf-8")):
        return jsonify({"error": "Senha incorreta."}), 400

    session["user"] = {"nome": user["nome"], "tipo": user["tipo"], "email": email}
    return jsonify({"success": "Login bem-sucedido!", "user": session["user"]}), 200

# --------- Logout ---------
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": "Sessão encerrada."}), 200

# =============================
# Inicialização
# =============================
if __name__ == "__main__":
    os.makedirs(DB_DIR, exist_ok=True)
    # garante arquivo com {} se não existir
    if not os.path.exists(DB_FILE) or os.path.getsize(DB_FILE) == 0:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            f.write("{}")
    app.run(debug=True)