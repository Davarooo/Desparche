from services.api_service import CryptoAPI
from portafolio.portfolio import Portfolio

def main():
    print("🟢 Bienvenido a tu Dashboard Cripto en Python 🪙\n")

    # Instancias
    api = CryptoAPI()
    portfolio = Portfolio()

    # Mostrar lo que ya tienes guardado
    print("🔐 Portafolio cargado desde archivo JSON:\n")
    portfolio.show_holdings()

    # Opción para agregar nuevas criptos
    agregar = input("\n¿Deseas agregar una criptomoneda? (s/n): ").lower()
    
    if agregar == "s":
        nombre = input("🔹 Nombre de la cripto (ej. bitcoin): ").lower()
        try:
            cantidad = float(input("🔹 Cantidad que posees: "))
            portfolio.add_crypto(nombre, cantidad)
            print(f"✅ {nombre} agregado correctamente al portafolio.\n")
        except ValueError:
            print("❌ Valor numérico inválido.")
    elif agregar == "n":
        print("✅ No se agregó ninguna criptomoneda al portafolio.")
    else:
        print("❌ Opción no válida.")

    # Obtener precios actuales
    cryptos = list(portfolio.holdings.keys())
    prices = api.get_prices(cryptos)

    # Mostrar análisis si hay datos
    if prices:
        portfolio.calculate_value(prices)
        portfolio.show_pie_chart(prices)
        portfolio.save_daily_report(prices)
    else:
        print("❌ No se pudieron obtener los precios. Verifica tu conexión.")

if __name__ == "__main__":
    main()
