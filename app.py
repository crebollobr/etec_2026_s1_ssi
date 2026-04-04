import sqlite3
from flask import Flask, request, render_template_string

app = Flask(__name__)

# 1. Cria o banco e o usuário admin ao iniciar
def init_db():
    conn = sqlite3.connect('usuarios.db')
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS usuarios')
    cursor.execute('CREATE TABLE usuarios (id INTEGER, user TEXT, senha TEXT)')
    cursor.execute("INSERT INTO usuarios VALUES (1, 'admin', 'senha123')")
    conn.commit()
    conn.close()

# HTML simples com o formulário de login
LOGIN_PAGE = '''
<!DOCTYPE html>
<html>
<head><title>Login do Sistema</title></head>
<body>
    <h2>Área Restrita</h2>
    <form method="POST" action="/login">
        Usuário: <input type="text" name="usuario"><br>
        Senha: <input type="password" name="senha"><br>
        <input type="submit" value="Entrar">
    </form>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(LOGIN_PAGE)

@app.route('/login', methods=['POST'])
def login():
    user = request.form.get('usuario')
    pw = request.form.get('senha')
    
    # O ERRO CRÍTICO: Concatenação de Strings (SQL Injection)
    # Um hacker pode digitar no campo usuário: admin' --
    query = f"SELECT * FROM usuarios WHERE user = '{user}' AND senha = '{pw}'"
    
# FORMA CORRETA (Protegida):
# query = "SELECT * FROM usuarios WHERE user = ? AND senha = ?"
# cursor.execute(query, (user, pw)) # O SQLite trata os dados com segurança

    try:
        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()
        cursor.execute(query) # O ZAP vai explodir isso aqui
        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            return f"<h1>Bem-vindo, {resultado[1]}!</h1><p>Logado com sucesso.</p>"
        else:
            return "<h1>Acesso Negado!</h1>", 401
    except Exception as e:
        return f"Erro no Banco de Dados: {str(e)}", 500

if __name__ == "__main__":
    init_db()
    app.run(port=5000)