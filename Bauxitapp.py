from flask import Flask, render_template, request
from pulp import *

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    costo_total = None
    resultado = ""

    if request.method == "POST":
        # Capturar los costos ingresados por el usuario
        costo_B = float(request.form.get("costo_B"))
        costo_C = float(request.form.get("costo_C"))
        costo_D = float(request.form.get("costo_D"))
        costo_E = float(request.form.get("costo_E"))

        # Definición del modelo
        modelo = LpProblem("Problema_Bauxita", LpMinimize)

        # Conjuntos
        MINAS = ["A", "B", "C"]
        PLANTAS = ["B", "C", "D", "E"]
        ESMALTADO = ["D", "E"]

        # Parámetros (fijos)
        cap_mina = {"A": 36000, "B": 52000, "C": 28000}
        cap_planta = {"B": 40000, "C": 20000, "D": 30000, "E": 80000}
        cap_esmaltado = {"D": 4000, "E": 7000}

        costo_explotacion = {"A": 420, "B": 360, "C": 540}
        costo_produccion = {"B": 330, "C": 320, "D": 380, "E": 240}
        costo_esmaltado = {"D": 8500, "E": 5200}

        # Usamos los costos fijos que ingresó el usuario
        costo_fijo = {"B": costo_B, "C": costo_C, "D": costo_D, "E": costo_E}

        ctran_b = {
            ("A", "B"): 400, ("A", "C"): 2010, ("A", "D"): 510, ("A", "E"): 1920,
            ("B", "B"): 10, ("B", "C"): 630, ("B", "D"): 220, ("B", "E"): 1510,
            ("C", "B"): 1630, ("C", "C"): 10, ("C", "D"): 620, ("C", "E"): 940
        }

        ctran_a = {
            ("B", "D"): 220, ("B", "E"): 1510,
            ("C", "D"): 620, ("C", "E"): 940,
            ("D", "D"): 0, ("D", "E"): 1615,
            ("E", "D"): 1465, ("E", "E"): 0
        }

        demanda = {"D": 1000, "E": 1200}
        rend_bauxita = {"A": 0.06, "B": 0.08, "C": 0.062}
        rend_alumina = 0.4

        # Variables
        x = LpVariable.dicts("x", (MINAS, PLANTAS), lowBound=0)
        y = LpVariable.dicts("y", (PLANTAS, ESMALTADO), lowBound=0)
        w = LpVariable.dicts("w", PLANTAS, lowBound=0, upBound=1, cat=LpBinary)

        # Función objetivo
        modelo += (
            lpSum(costo_explotacion[i] * x[i][j] for i in MINAS for j in PLANTAS)
            + lpSum(costo_produccion[j] * y[j][k] for j in PLANTAS for k in ESMALTADO)
            + lpSum(costo_esmaltado[k] * y[j][k] for j in PLANTAS for k in ESMALTADO)
            + lpSum(ctran_b[(i, j)] * x[i][j] for i in MINAS for j in PLANTAS)
            + lpSum(ctran_a[(j, k)] * y[j][k] for j in PLANTAS for k in ESMALTADO)
            + lpSum(costo_fijo[j] * w[j] for j in PLANTAS)
        )

        # Restricciones
        for i in MINAS:
            modelo += lpSum(x[i][j] for j in PLANTAS) <= cap_mina[i]
        for j in PLANTAS:
            modelo += lpSum(x[i][j] for i in MINAS) <= cap_planta[j] * w[j]
        for k in ESMALTADO:
            modelo += lpSum(y[j][k] for j in PLANTAS) <= cap_esmaltado[k]
        for k in ESMALTADO:
            modelo += lpSum(rend_alumina * y[j][k] for j in PLANTAS) == demanda[k]
        for j in PLANTAS:
            modelo += lpSum(rend_bauxita[i] * x[i][j] for i in MINAS) == lpSum(y[j][k] for k in ESMALTADO)

        # Solución
        modelo.solve()
        estado = LpStatus[modelo.status]
        costo_total = value(modelo.objective)

        # Resultados
        resultado += f"El estado es: {estado}\n"
        resultado += f"El costo total es: ${costo_total:,.2f}\n\n"
        resultado += "Las plantas abiertas son:\n"
        for j in PLANTAS:
            resultado += f"  {j}: {int(value(w[j]))}\n"

    return render_template("bauxita.html", costo_total=costo_total, resultado=resultado)

if __name__ == "__main__":
    app.run(debug=True)