from flask import Flask, render_template, request, redirect, make_response, send_file
import pandas as pd
import os
from datetime import datetime
import requests

app = Flask(__name__)
CSV_PATH = 'data/historial_portafolio.csv'
COINGECKO_URL = 'https://api.coingecko.com/api/v3/simple/price'


def inicializar_csv():
    if not os.path.exists(CSV_PATH):
        os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
        ejemplo = pd.DataFrame([
            {"nombre": "bitcoin", "cantidad": 1.0, "precio_usd": 64000, "valor_total_usd": 64000},
            {"nombre": "ethereum", "cantidad": 2.0, "precio_usd": 3500, "valor_total_usd": 7000},
            {"nombre": "solana", "cantidad": 10, "precio_usd": 150, "valor_total_usd": 1500}
        ])
        ejemplo.to_csv(CSV_PATH, index=False)


def cargar_portafolio():
    try:
        df = pd.read_csv(CSV_PATH)
        columnas_esperadas = {"nombre", "cantidad", "precio_usd", "valor_total_usd"}
        if not columnas_esperadas.issubset(df.columns):
            raise ValueError("CSV mal estructurado.")
        return df
    except:
        return pd.DataFrame(columns=["nombre", "cantidad", "precio_usd", "valor_total_usd"])


def guardar_portafolio(df):
    df.to_csv(CSV_PATH, index=False)


def obtener_precios(criptos):
    try:
        r = requests.get(COINGECKO_URL, params={'ids': ','.join(criptos), 'vs_currencies': 'usd'})
        return r.json()
    except:
        return {}


@app.route("/")
def index():
    user = request.cookies.get("user_name")
    if not user:
        return redirect("/login")

    inicializar_csv()
    df = cargar_portafolio()
    columnas = df.columns.tolist()
    registros = df.to_dict(orient="records")
    fechas = [datetime.now().strftime("%Y-%m-%d")]
    totales = [df["valor_total_usd"].sum()] if not df.empty else [0]

    return render_template("index.html", columnas=columnas, registros=registros, fechas=fechas, totales=totales, user=user)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nombre = request.form["nombre"]
        resp = make_response(redirect("/"))
        resp.set_cookie("user_name", nombre)
        return resp
    return render_template("login.html")


@app.route("/logout")
def logout():
    resp = make_response(redirect("/login"))
    resp.set_cookie("user_name", "", expires=0)
    return resp


@app.route("/agregar", methods=["POST"])
def agregar():
    df = cargar_portafolio()
    nombre = request.form["nombre"].lower()
    try:
        cantidad = float(request.form["cantidad"])
    except:
        cantidad = 0
    precios = obtener_precios([nombre])
    precio = precios.get(nombre, {}).get("usd", 0)
    total = precio * cantidad
    nuevo = pd.DataFrame([{
        "nombre": nombre,
        "cantidad": cantidad,
        "precio_usd": precio,
        "valor_total_usd": total
    }])
    df = pd.concat([df, nuevo], ignore_index=True)
    guardar_portafolio(df)
    return redirect("/")


@app.route("/editar/<nombre>", methods=["POST"])
def editar(nombre):
    df = cargar_portafolio()
    nueva = float(request.form["nueva_cantidad"])
    precios = obtener_precios([nombre])
    precio = precios.get(nombre, {}).get("usd", 0)
    df.loc[df["nombre"] == nombre, "cantidad"] = nueva
    df.loc[df["nombre"] == nombre, "precio_usd"] = precio
    df.loc[df["nombre"] == nombre, "valor_total_usd"] = precio * nueva
    guardar_portafolio(df)
    return redirect("/")


@app.route("/eliminar/<nombre>", methods=["POST"])
def eliminar(nombre):
    df = cargar_portafolio()
    df = df[df["nombre"] != nombre]
    guardar_portafolio(df)
    return redirect("/")


@app.route("/exportar")
def exportar():
    return send_file(CSV_PATH, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
