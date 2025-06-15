from flask import Flask, render_template, request, redirect, url_for, session, send_file
import pandas as pd
from datetime import datetime
import os
import requests

app = Flask(__name__)
app.secret_key = 'clave-super-secreta'
DATA_PATH = 'data/historial_portafolio.csv'

# Crear archivo CSV con columnas si no existe
def crear_archivo_si_no_existe():
    columnas = ["fecha", "nombre", "cantidad", "precio_usd", "valor_total_usd"]
    if not os.path.exists(DATA_PATH):
        df = pd.DataFrame(columns=columnas)
        df.to_csv(DATA_PATH, index=False)
    else:
        df = pd.read_csv(DATA_PATH)
        for col in columnas:
            if col not in df.columns:
                df[col] = None
        df.to_csv(DATA_PATH, index=False)

# Obtener precio desde CoinGecko
def obtener_precio(nombre):
    try:
        r = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={nombre}&vs_currencies=usd")
        return r.json()[nombre]['usd']
    except:
        return None

@app.route('/')
def home():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    crear_archivo_si_no_existe()
    df = pd.read_csv(DATA_PATH).dropna()

    columnas = ["fecha", "nombre", "cantidad", "precio_usd", "valor_total_usd"]
    for col in columnas:
        if col not in df.columns:
            df[col] = None

    df.to_csv(DATA_PATH, index=False)
    registros = df.to_dict(orient='records')

    try:
        totales = df.groupby('fecha')['valor_total_usd'].sum().round(2).tolist()
        fechas = df['fecha'].unique().tolist()
    except:
        totales = []
        fechas = []

    return render_template("index.html", user=session['usuario'],
                           columnas=columnas, registros=registros,
                           totales=totales, fechas=fechas)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        session['usuario'] = nombre
        return redirect(url_for('home'))
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/agregar', methods=['POST'])
def agregar():
    crear_archivo_si_no_existe()
    nombre = request.form.get('nombre').lower()
    cantidad = float(request.form.get('cantidad'))
    precio = obtener_precio(nombre)

    if precio is None:
        return "❌ Error al obtener el precio"

    total = round(precio * cantidad, 2)
    hoy = datetime.now().strftime('%Y-%m-%d')

    nuevo = pd.DataFrame([{
        "fecha": hoy,
        "nombre": nombre,
        "cantidad": cantidad,
        "precio_usd": precio,
        "valor_total_usd": total
    }])

    df = pd.read_csv(DATA_PATH)
    df = pd.concat([df, nuevo], ignore_index=True)
    df.to_csv(DATA_PATH, index=False)

    return redirect(url_for('home'))

@app.route('/editar/<nombre>', methods=['POST'])
def editar(nombre):
    nueva_cantidad = float(request.form.get('nueva_cantidad'))
    precio = obtener_precio(nombre)
    if precio is None:
        return "❌ Error con precio"

    total = round(precio * nueva_cantidad, 2)
    hoy = datetime.now().strftime('%Y-%m-%d')

    df = pd.read_csv(DATA_PATH)
    df = df[df['nombre'] != nombre]

    nuevo = pd.DataFrame([{
        "fecha": hoy,
        "nombre": nombre,
        "cantidad": nueva_cantidad,
        "precio_usd": precio,
        "valor_total_usd": total
    }])
    df = pd.concat([df, nuevo], ignore_index=True)
    df.to_csv(DATA_PATH, index=False)

    return redirect(url_for('home'))

@app.route('/eliminar/<nombre>', methods=['POST'])
def eliminar(nombre):
    df = pd.read_csv(DATA_PATH)
    df = df[df['nombre'] != nombre]
    df.to_csv(DATA_PATH, index=False)
    return redirect(url_for('home'))

@app.route('/exportar')
def exportar():
    df = pd.read_csv(DATA_PATH)
    path = 'data/portafolio_exportado.xlsx'
    df.to_excel(path, index=False)
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
