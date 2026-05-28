from flask import Flask, render_template, request, redirect
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    UserMixin,
    current_user
)
from flask_bcrypt import Bcrypt
import sqlite3

# ======================================================
# APP CONFIG
# ======================================================

app = Flask(__name__)
app.secret_key = "secret-word"

login_manager = LoginManager()
login_manager.init_app(app)

# REDIRECT SI NO ESTÁ LOGUEADO
login_manager.login_view = "login"

bcrypt = Bcrypt(app)

# ======================================================
# VARIABLES COSTEO
# ======================================================

receta = []
total = 0

# ======================================================
# DATABASE
# ======================================================

def db():

    conn = sqlite3.connect("costeo.db")
    conn.row_factory = sqlite3.Row

    return conn

# ======================================================
# USER CLASS
# ======================================================

class User(UserMixin):

    def __init__(self, id, username, password):

        self.id = id
        self.username = username
        self.password = password

# ======================================================
# LOAD USER
# ======================================================

@login_manager.user_loader
def load_user(user_id):

    conn = db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    )

    user = cursor.fetchone()

    conn.close()

    if user:

        return User(
            user["id"],
            user["username"],
            user["password"]
        )

    return None

# ======================================================
# HOME
# ======================================================

@app.route("/")
@login_required
def home():

    return render_template(
        "index.html",
        user=current_user.username
    )

# ======================================================
# REGISTER
# ======================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]
        key = request.form["key"]

        # CLAVE BETA
        if key != "FamiliaMejia2026":

            return "❌ Clave incorrecta"

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        try:

            conn = db()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO users (username, password)
                VALUES (?, ?)
                """,
                (username, hashed_password)
            )

            conn.commit()
            conn.close()

            return redirect("/login")

        except:

            return "❌ Usuario ya existe"

    return render_template("register.html")

# ======================================================
# LOGIN
# ======================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )

        user = cursor.fetchone()

        conn.close()

        if user:

            if bcrypt.check_password_hash(
                user["password"],
                password
            ):

                login_user(
                    User(
                        user["id"],
                        user["username"],
                        user["password"]
                    )
                )

                return redirect("/")

        return "❌ Usuario o contraseña incorrectos"

    return render_template("login.html")

# ======================================================
# LOGOUT
# ======================================================

@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect("/login")

# ======================================================
# INGREDIENTES
# ======================================================

@app.route("/ingredientes", methods=["GET", "POST"])
@login_required
def ingredientes():

    conn = db()
    cursor = conn.cursor()

    # AGREGAR INGREDIENTE
    if request.method == "POST":

        nombre = request.form["nombre"]
        unidad = request.form["unidad"]
        precio = float(request.form["precio"])
        cantidad = float(request.form["cantidad"])

        # COSTO UNITARIO
        costo_unitario = precio / cantidad

        cursor.execute(
            """
            INSERT INTO ingredientes
            (
                nombre,
                unidad,
                precio,
                cantidad,
                costo_unitario
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                nombre,
                unidad,
                precio,
                cantidad,
                costo_unitario
            )
        )

        conn.commit()

    # MOSTRAR INGREDIENTES
    cursor.execute(
        """
        SELECT * FROM ingredientes
        ORDER BY id DESC
        """
    )

    data = cursor.fetchall()

    conn.close()

    return render_template(
        "ingredientes.html",
        data=data,
        user=current_user.username
    )

# ======================================================
# ELIMINAR INGREDIENTE
# ======================================================

@app.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):

    conn = db()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM ingredientes WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/ingredientes")

# ======================================================
# COSTEO DE PLATILLOS
# ======================================================

@app.route("/costeo", methods=["GET", "POST"])
@login_required
def costeo():

    global receta
    global total

    conn = db()
    cursor = conn.cursor()

    # OBTENER INGREDIENTES
    cursor.execute(
        """
        SELECT nombre, costo_unitario
        FROM ingredientes
        """
    )

    ingredientes = cursor.fetchall()

    # AGREGAR INGREDIENTE AL COSTEO
    if request.method == "POST":

        ingrediente = request.form["ingrediente"]
        cantidad = float(request.form["cantidad"])

        for i in ingredientes:

            if i["nombre"] == ingrediente:

                costo = i["costo_unitario"] * cantidad

                receta.append({
                    "ingrediente": ingrediente,
                    "cantidad": cantidad,
                    "costo": round(costo, 2)
                })

                total += costo

    venta = total / 0.35 if total > 0 else 0

    conn.close()

    return render_template(
        "costeo.html",
        ingredientes=ingredientes,
        receta=receta,
        total=round(total, 2),
        venta=round(venta, 2),
        user=current_user.username
    )

# ======================================================
# NUEVO COSTEO
# ======================================================

@app.route("/nuevo_costeo")
@login_required
def nuevo_costeo():

    global receta
    global total

    receta = []
    total = 0

    return redirect("/costeo")

# ======================================================
# CREAR BASE DE DATOS
# ======================================================

def crear_db():

    conn = db()
    cursor = conn.cursor()

    # USERS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT

    )
    """)

    # INGREDIENTES
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ingredientes (

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        unidad TEXT,
        precio REAL,
        cantidad REAL,
        costo_unitario REAL

    )
    """)

    conn.commit()
    conn.close()

# ======================================================
# RUN
# ======================================================

if __name__ == "__main__":

    crear_db()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )