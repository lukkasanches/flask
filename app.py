
from flask import Flask, request, jsonify
import sqlite3

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

app = Flask(__name__)


# CONEXÃO COM O BANCO DE DADOS
def conectar_banco():
    conexao = sqlite3.connect("usuarios.db")
    conexao.row_factory = sqlite3.Row
    return conexao


# CRIAR TABELA DE USUÁRIOS
def criar_banco():
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha_hash TEXT NOT NULL
        )
    """)

    conexao.commit()
    conexao.close()


# CADASTRO DE USUÁRIOS
@app.route("/cadastro", methods=["POST"])
def cadastro():

    dados = request.get_json()

    nome = dados["nome"]
    email = dados["email"]
    senha = dados["senha"]

    senha_hash = generate_password_hash(senha)

    conexao = conectar_banco()
    cursor = conexao.cursor()

    try:
        cursor.execute("""
            INSERT INTO usuarios
            (nome, email, senha_hash)
            VALUES (?, ?, ?)
        """, (nome, email, senha_hash))

        conexao.commit()
        conexao.close()

        return jsonify({
            "mensagem": "Usuário cadastrado com sucesso!"
        }), 201

    except sqlite3.IntegrityError:

        conexao.close()

        return jsonify({
            "erro": "E-mail já cadastrado."
        }), 409


# LOGIN DE USUÁRIOS
@app.route("/login", methods=["POST"])
def login():

    dados = request.get_json()

    email = dados["email"]
    senha = dados["senha"]

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute(
        "SELECT * FROM usuarios WHERE email = ?",
        (email,)
    )

    usuario = cursor.fetchone()

    conexao.close()

    if usuario and check_password_hash(
        usuario["senha_hash"],
        senha
    ):

        return jsonify({
            "mensagem": "Login realizado com sucesso!"
        }), 200

    return jsonify({
        "erro": "E-mail ou senha inválidos."
    }), 401


# INICIALIZAÇÃO DA APLICAÇÃO
if __name__ == "__main__":
    criar_banco()
    app.run(debug=True)
