import json
import os
import csv
from datetime import datetime
import matplotlib.pyplot as plt

class Portfolio:
    def __init__(self, filepath="portafolio.json"):
        self.filepath = filepath
        self.holdings = {}
        self.load_portfolio()

    def add_crypto(self, crypto_name, amount):
        if crypto_name in self.holdings:
            self.holdings[crypto_name] += amount
        else:
            self.holdings[crypto_name] = amount
        self.save_portfolio()

    def show_holdings(self):
        if not self.holdings:
            print("📭 Tu portafolio está vacío.")
            return

        print("📦 Portafolio actual:")
        for crypto, amount in self.holdings.items():
            print(f"  {crypto.capitalize()}: {amount} unidades")

    def calculate_value(self, prices):
        total = 0.0
        print("\n💰 Valor de cada moneda:")
        for crypto, amount in self.holdings.items():
            price = prices.get(crypto, {}).get("usd", 0)
            value = amount * price
            total += value
            print(f"  {crypto.capitalize()}: {amount} × ${price:.2f} = ${value:.2f}")
        print(f"\n🔹 Valor total del portafolio: ${total:.2f}")

    def save_portfolio(self):
        with open(self.filepath, "w") as f:
            json.dump(self.holdings, f)

    def load_portfolio(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, "r") as f:
                self.holdings = json.load(f)

    def show_pie_chart(self, prices):
        labels = []
        values = []

        for crypto, amount in self.holdings.items():
            price = prices.get(crypto, {}).get("usd", 0)
            total_value = price * amount
            if total_value > 10:  # filtrar monedas de valor muy pequeño
                labels.append(crypto.capitalize())
                values.append(total_value)

        if values:
            explode = [0.05] * len(values)  # separar visualmente los sectores

            plt.figure(figsize=(6, 6))
            plt.pie(
                values,
                labels=None,  # usamos leyenda en lugar de etiquetas en el gráfico
                autopct="%1.1f%%",
                startangle=140,
                explode=explode
            )
            plt.title("Distribución del Portafolio Cripto")
            plt.axis("equal")
            plt.legend(labels, loc="upper right", bbox_to_anchor=(1.3, 1))
            plt.tight_layout()
            plt.show()
        else:
            print("⚠️ No hay suficientes datos para generar el gráfico.")

    def save_daily_report(self, prices):
        os.makedirs("data", exist_ok=True)
        filename = "data/historial_portafolio.csv"

        today = datetime.now().strftime("%Y-%m-%d")

        row = {"Fecha": today}
        total = 0.0
        for crypto, amount in self.holdings.items():
            price = prices.get(crypto, {}).get("usd", 0)
            value = price * amount
            row[crypto.capitalize()] = f"{value:.2f}"
            total += value
        row["Total"] = f"{total:.2f}"

        write_header = not os.path.exists(filename)
        with open(filename, "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=row.keys())
            if write_header:
                writer.writeheader()
            writer.writerow(row)

        print(f"📁 Historial guardado en {filename}")
