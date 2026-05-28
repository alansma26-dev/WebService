from flask import Flask, render_template, request, redirect
import sqlite3
import csv

app = Flask(__name__)

receta = []
total = 0

def db():
    return sqlite3.connect("costeo.db")

# -------------------
# HOME
# -------------------
@app.route("/")
def home():
    return render_template("index.html")

# -------------------
# INGREDIENTES
# -------------------
@app.route("/ingredientes", methods=["GET", "POST"])
def ingredientes():

    conn = db()
    cursor = conn.cursor()

    if request.method == "POST":

        nombre = request.form["nombre"]
        unidad = request.form["unidad"]
        precio = float(request.form["precio"])
        cantidad = float(request.form["cantidad"])

        costo_unit = precio / (cantidad * 1000)

        cursor.execute("""
        INSERT OR REPLACE INTO ingredientes
        VALUES (?, ?, ?, ?, ?)
        """, (nombre, unidad, precio, cantidad, costo_unit))

        conn.commit()

    cursor.execute("SELECT * FROM ingredientes")
    data = cursor.fetchall()

    conn.close()

    return render_template("ingredientes.html", data=data)

# -------------------
# RECETA
# -------------------
@app.route("/receta", methods=["GET", "POST"])
def receta_view():

    global total

    conn = db()
    cursor = conn.cursor()

    cursor.execute("SELECT nombre, costo_unitario FROM ingredientes")
    ingredientes = cursor.fetchall()

    if request.method == "POST":

        ing = request.form["ingrediente"]
        cant = float(request.form["cantidad"])

        for i in ingredientes:
            if i[0] == ing:
                costo = i[1] * cant
                total += costo
                receta.append((ing, cant, costo))

    venta = total / 0.35

    return render_template(
        "receta.html",
        ingredientes=ingredientes,
        receta=receta,
        total=total,
        venta=venta
    )

# -------------------
# EXPORTAR CSV
# -------------------
@app.route("/exportar")
def exportar():

    with open("receta.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Ingrediente", "Cantidad", "Costo"])
        for r in receta:
            w.writerow(r)

    return redirect("/receta")

# -------------------
# NUEVA RECETA
# -------------------
@app.route("/nueva")
def nueva():

    global receta, total

    receta = []
    total = 0

    return redirect("/receta")

# -------------------
# RUN
# -------------------
if __name__ == "__main__":
    app.run(debug=True)