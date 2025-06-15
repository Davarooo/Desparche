from flask import Flask, render_template, request, redirect, send_file
import pandas as pd
import requests
import os

app = Flask(__name__)
DATA_PATH = "data/historial_portafolio.csv"
COINGECKO_API = "https://api.coingecko.com/api/v3/simple/price"

# Obtener precio desde CoinGecko
def obtener_precio(nombre):
    try:
        res = requests.get(COINGECKO_API, params={
            "ids": nombre,
            "vs_currencies": "usd"
        })
        data = res.json()
        return data[nombre]["usd"]
    except:
        return None

# Página principal
@app.route("/")
def index():
    if not os.path.exists(DATA_PATH):
        columnas = ["nombre", "cantidad", "precio_usd", "valor_total_usd"]
        return render_template("index.html", columnas=columnas, registros=[], fechas=[], totales=[])

    df = pd.read_csv(DATA_PATH)
    columnas = df.columns.tolist()
    registros = df.to_dict(orient="records")

    # Agrupar por fecha si se incluye historial futuro
    fechas = list(range(1, len(df) + 1))  # Simulación temporal
    totales = df["valor_total_usd"].tolist()

    return render_template("index.html", columnas=columnas, registros=registros, fechas=fechas, totales=totales)

# Agregar nueva cripto
@app.route("/agregar", methods=["POST"])
def agregar():
    nombre = request.form["nombre"].lower()
    cantidad = float(request.form["cantidad"])
    precio = obtener_precio(nombre)
    if not precio:
        return "❌ No se pudo obtener el precio de CoinGecko."

    valor_total = cantidad * precio

    # Guardar
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        if nombre in df["nombre"].values:
            df.loc[df["nombre"] == nombre, "cantidad"] += cantidad
            df.loc[df["nombre"] == nombre, "precio_usd"] = precio
            df.loc[df["nombre"] == nombre, "valor_total_usd"] = df.loc[df["nombre"] == nombre, "cantidad"] * precio
        else:
            df = pd.concat([df, pd.DataFrame([{
                "nombre": nombre,
                "cantidad": cantidad,
                "precio_usd": precio,
                "valor_total_usd": valor_total
            }])], ignore_index=True)
    else:
        df = pd.DataFrame([{
            "nombre": nombre,
            "cantidad": cantidad,
            "precio_usd": precio,
            "valor_total_usd": valor_total
        }])

    df.to_csv(DATA_PATH, index=False)
    return redirect("/")

# Editar cantidad
@app.route("/editar/<nombre>", methods=["POST"])
def editar(nombre):
    nueva = float(request.form["nueva_cantidad"])
    df = pd.read_csv(DATA_PATH)

    if nombre not in df["nombre"].values:
        return "Cripto no encontrada"

    precio = obtener_precio(nombre)
    if not precio:
        return "Precio no encontrado"

    df.loc[df["nombre"] == nombre, "cantidad"] = nueva
    df.loc[df["nombre"] == nombre, "precio_usd"] = precio
    df.loc[df["nombre"] == nombre, "valor_total_usd"] = nueva * precio

    df.to_csv(DATA_PATH, index=False)
    return redirect("/")

# Eliminar cripto
@app.route("/eliminar/<nombre>", methods=["POST"])
def eliminar(nombre):
    df = pd.read_csv(DATA_PATH)
    df = df[df["nombre"] != nombre]
    df.to_csv(DATA_PATH, index=False)
    return redirect("/")

# Exportar a Excel
@app.route("/exportar")
def exportar():
    excel_path = "data/reporte_portafolio.xlsx"
    df = pd.read_csv(DATA_PATH)
    df.to_excel(excel_path, index=False)
    return send_file(excel_path, as_attachment=True)

# Ejecutar
if __name__ == "__main__":
    app.run(debug=True)
