import pandas as pd
import matplotlib.pyplot as plt

def mostrar_evolucion_individual():
    try:
        df = pd.read_csv("data/historial_portafolio.csv")
        df["Fecha"] = pd.to_datetime(df["Fecha"])
        df = df.sort_values("Fecha")

        # Excluimos columnas que no son criptomonedas
        columnas_a_excluir = ["Fecha", "Total"]
        criptos = [col for col in df.columns if col not in columnas_a_excluir]

        # Graficar cada criptomoneda individualmente
        plt.figure(figsize=(10, 6))
        for cripto in criptos:
            df[cripto] = df[cripto].astype(float)
            plt.plot(df["Fecha"], df[cripto], marker="o", label=cripto)

        plt.title("📊 Evolución por Criptomoneda")
        plt.xlabel("Fecha")
        plt.ylabel("Valor en USD")
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    except FileNotFoundError:
        print("❌ No se encontró el archivo historial_portafolio.csv.")
    except Exception as e:
        print(f"⚠️ Error al procesar el archivo: {e}")

if __name__ == "__main__":
    mostrar_evolucion_individual()
