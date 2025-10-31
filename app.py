import sqlite3
from flask import Flask, render_template_string, request, redirect, url_for, g

app = Flask(__name__)
DATABASE = "usuarios.db"

# -----------------------------
# FUNCIONES DE BASE DE DATOS
# -----------------------------
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """Crea la tabla y un usuario inicial"""
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        usuario TEXT UNIQUE,
                        clave TEXT
                    )''')
        # Insertar usuario por defecto si no existe
        c.execute("SELECT * FROM usuarios WHERE usuario = usuario")
        if not c.fetchone():
            c.execute("INSERT INTO usuarios (usuario, clave) VALUES (?, ?)", ("admin", "1234"))
        conn.commit()

# -----------------------------
# PLANTILLAS HTML
# -----------------------------
login_html = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Login con Flask y SQLite</title>
    <style>
        body { font-family: Arial; background-color: #f0f0f0;
               display: flex; justify-content: center; align-items: center; height: 100vh; }
        .login { background: white; padding: 30px; border-radius: 10px;
                 box-shadow: 0 0 10px #aaa; width: 300px; text-align: center; }
        input, button { width: 90%; padding: 10px; margin: 10px 0;
                        border-radius: 5px; border: 1px solid #ccc; }
        button { background-color: #007bff; color: white; border: none; cursor: pointer; }
        button:hover { background-color: #0056b3; }
        .error { color: red; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="login">
        <h2>Iniciar Sesión</h2>
        <form method="post">
            <input type="text" name="usuario" placeholder="Usuario" required>
            <input type="password" name="clave" placeholder="Contraseña" required>
            <button type="submit">Ingresar</button>
        </form>
        {% if error %}
            <p class="error">{{ error }}</p>
        {% endif %}
    </div>
</body>
</html>
"""

home_html = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Inicio</title>
</head>
<body style="font-family: Arial; text-align: center; margin-top: 100px;">
    <h1>Bienvenido, {{ usuario }} </h1>
    <p>Has iniciado sesión correctamente.</p>
    <a href="{{ url_for('logout') }}">Cerrar sesión</a>
</body>
</html>
"""

# -----------------------------
# RUTAS DE LA APLICACIÓN
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        usuario = request.form["usuario"]
        clave = request.form["clave"]

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND clave = ?", (usuario, clave))
        user = cursor.fetchone()

        if user:
            return redirect(url_for("home", usuario=usuario))
        else:
            error = "Usuario o contraseña incorrectos"

    return render_template_string(login_html, error=error)

@app.route("/home")
def home():
    usuario = request.args.get("usuario", "Invitado")
    return render_template_string(home_html, usuario=usuario)

@app.route("/logout")
def logout():
    return redirect(url_for("login"))

# -----------------------------
# EJECUCIÓN PRINCIPAL
# -----------------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
