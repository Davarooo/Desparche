from flask import Flask, render_template, request, redirect, url_for, session, send_file
import pandas as pd
from datetime import datetime
import os
import requests

app = Flask(__name__)
app.secret_key = 'clave-super-secreta'
DATA_PATH = 'data/historial_portafolio.csv'

# Crear archivo con columnas correctas si no existe
def crear_archivo_si_no_existe():
    if not os.path.exists(DATA_PATH):
        df = pd.DataFrame(columns=["fecha", "nombre", "cantidad", "precio_usd", "valor_total_usd"])
        df.to_csv(DATA_PATH, index=False)

# Obtener precio actual desde CoinGecko
def obtener_precio(nombre):
    try:
        r = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={nombre}&vs_currencies=usd")
        return r.json()[nombre]['usd']
    except:
        return None

# Página principal (dashboard)
@app.route('/')
def home():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    crear_archivo_si_no_existe()
    df = pd.read_csv(DATA_PATH)

    # Limpiar filas vacías
    df.dropna(inplace=True)
    df.to_csv(DATA_PATH, index=False)

    columnas = df.columns.tolist()
    registros = df.to_dict(orient='records')

    # Protección por si faltan columnas clave
    if 'fecha' in df.columns and 'valor_total_usd' in df.columns:
        totales = df.groupby('fecha')['valor_total_usd'].sum().round(2).tolist()
        fechas = df['fecha'].unique().tolist()
    else:
        totales = []
        fechas = []

    return render_template("index.html", user=session['usuario'],
                           columnas=columnas, registros=registros,
                           totales=totales, fechas=fechas)

# Página de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        session['usuario'] = nombre
        return redirect(url_for('home'))
    return render_template("login.html")

# Cerrar sesión
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Agregar criptomoneda
@app.route('/agregar', methods=['POST'])
def agregar():
    crear_archivo_si_no_existe()
    nombre = request.form.get('nombre').lower()
    cantidad = float(request.form.get('cantidad'))
    precio = obtener_precio(nombre)

    if precio is None:
        return "Error al obtener el precio de CoinGecko"

    total = round(precio * cantidad, 2)
    hoy = datetime.now().strftime('%Y-%m-%d')

    nuevo = pd.DataFrame([{
        'fecha': hoy,
        'nombre': nombre,
        'cantidad': cantidad,
        'precio_usd': precio,
        'valor_total_usd': total
    }])

    if not nuevo.isnull().values.any():
        df = pd.read_csv(DATA_PATH)
        df = pd.concat([df, nuevo], ignore_index=True)
        df.to_csv(DATA_PATH, index=False)

    return redirect(url_for('home'))

# Editar criptomoneda
@app.route('/editar/<nombre>', methods=['POST'])
def editar(nombre):
    nueva_cantidad = float(request.form.get('nueva_cantidad'))
    precio = obtener_precio(nombre)

    if precio is None:
        return "Error con el precio"

    total = round(precio * nueva_cantidad, 2)
    hoy = datetime.now().strftime('%Y-%m-%d')

    df = pd.read_csv(DATA_PATH)
    df = df[df['nombre'] != nombre]

    nuevo = pd.DataFrame([{
        'fecha': hoy,
        'nombre': nombre,
        'cantidad': nueva_cantidad,
        'precio_usd': precio,
        'valor_total_usd': total
    }])

    if not nuevo.isnull().values.any():
        df = pd.concat([df, nuevo], ignore_index=True)
        df.to_csv(DATA_PATH, index=False)

    return redirect(url_for('home'))

# Eliminar criptomoneda
@app.route('/eliminar/<nombre>', methods=['POST'])
def eliminar(nombre):
    df = pd.read_csv(DATA_PATH)
    df = df[df['nombre'] != nombre]
    df.to_csv(DATA_PATH, index=False)
    return redirect(url_for('home'))

# Exportar a Excel
@app.route('/exportar')
def exportar():
    df = pd.read_csv(DATA_PATH)
    path = 'data/portafolio_exportado.xlsx'
    df.to_excel(path, index=False)
    return send_file(path, as_attachment=True)

# Ejecutar la app
if __name__ == '__main__':
    app.run(debug=True)
