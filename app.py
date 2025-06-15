from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

@app.route("/")
def index():
    try:
        df = pd.read_csv("data/historial_portafolio.csv")
        df["Fecha"] = pd.to_datetime(df["Fecha"]).dt.strftime("%Y-%m-%d")
        df = df.sort_values("Fecha", ascending=True)
        columnas = df.columns.tolist()
        registros = df.to_dict(orient="records")
        fechas = df["Fecha"].tolist()
        totales = df["Total"].astype(float).tolist()
        return render_template("index.html", columnas=columnas, registros=registros, fechas=fechas, totales=totales)
    except Exception as e:
        return f"<h1>Error al cargar los datos: {e}</h1>"

if __name__ == "__main__":
    app.run(debug=True)
