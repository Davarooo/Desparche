from flask import Flask, render_template, request, redirect
import pandas as pd
import os
from datetime import date

app = Flask(__name__)
DATA_PATH = 'data/historial_portafolio.csv'

@app.route("/")
def inicio():
    try:
        df = pd.read_csv(DATA_PATH)
        columnas = df.columns.tolist()
        registros = df.to_dict(orient="records")
        fechas = df['fecha'].tolist()
        totales = df['valor_total_usd'].tolist()
    except Exception as e:
        columnas, registros, fechas, totales = [], [], [], []
    return render_template("index.html", columnas=columnas, registros=registros, fechas=fechas, totales=totales)

@app.route("/agregar", methods=["POST"])
def agregar():
    nombre = request.form['nombre'].lower()
    cantidad = float(request.form['cantidad'])

    # Aquí simulas un precio actual (podrías conectarlo con tu API real)
    precio_actual = 1000  # ⚠️ puedes cambiar esto por API real
    total_usd = cantidad * precio_actual

    nueva_fila = {
        'fecha': date.today().isoformat(),
        'nombre': nombre,
        'cantidad': cantidad,
        'precio_usd': precio_actual,
        'valor_total_usd': total_usd
    }

    # Crear archivo si no existe
    if not os.path.exists(DATA_PATH):
        df = pd.DataFrame(columns=nueva_fila.keys())
    else:
        df = pd.read_csv(DATA_PATH)

    df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
    df.to_csv(DATA_PATH, index=False)

    return redirect("/")
