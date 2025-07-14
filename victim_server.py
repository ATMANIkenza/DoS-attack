# victim_server.py
from flask import Flask, request, render_template_string
import bcrypt
import os

app = Flask(__name__)


CORRECT_PASSWORD_HASH = b"$2b$12$K1dJg0R.Zg2q8N5xV7Y9..gQ/zP.hA.k/F/Q.h0p.a.b.c.d.e.f." 

HTML_LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f4; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .login-container { background-color: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); width: 300px; text-align: center; }
        h1 { color: #333; margin-bottom: 25px; }
        label { display: block; text-align: left; margin-bottom: 8px; color: #555; font-weight: bold; }
        input[type="text"], input[type="password"] { width: calc(100% - 20px); padding: 10px; margin-bottom: 20px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        input[type="submit"] { background-color: #007bff; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; width: 100%; transition: background-color 0.3s ease; }
        input[type="submit"]:hover { background-color: #0056b3; }
        p { color: #dc3545; margin-top: 15px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="login-container">
        <h1>Login Page</h1>
        <form action="/login" method="post">
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" value="testuser">
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" value="fakepass">
            <input type="submit" value="Login">
        </form>
        {% if message %}
            <p>{{ message }}</p>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_LOGIN_PAGE)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    # Cette opération est intentionnellement coûteuse en CPU pour la sécurité.
    # C'est ce que nous allons exploiter pour le DoS.
    is_password_correct = bcrypt.checkpw(password.encode('utf-8'), CORRECT_PASSWORD_HASH)

    # La logique de connexion est secondaire pour le DoS, mais elle existe.
    if username == "admin" and is_password_correct:
        return "Login successful!", 200
    else:
        # Retourne une page avec le message d'erreur, mais le hachage a déjà été fait.
        return render_template_string(HTML_LOGIN_PAGE, message="Invalid username or password."), 200 # Retourne 200 même pour les erreurs pour ne pas bloquer le script d'attaque sur les 4xx

if __name__ == '__main__':
    # Le mode debug est désactivé pour simuler un comportement plus proche de la production
    app.run(host='0.0.0.0', port=8000, debug=False)