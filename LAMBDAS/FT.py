import json
import math
import cmath

# Función para calcular la Transformada Discreta de Fourier (DFT)
def calcular_dft(signal):
    N = len(signal)
    Y = []
    for k in range(N):  
        suma = 0  
        for n in range(N):  
            angulo = -2j * math.pi * k * n / N  
            suma += signal[n] * cmath.exp(angulo) 
        Y.append({
            "real": round(suma.real, 3),
            "imag": round(suma.imag, 3)
        })  
    return Y

# Función para calcular la Transformada Inversa de Fourier (IDFT)
def calcular_idft(dft_result):
    N = len(dft_result)
    x_recuperada = []
    for n in range(N):
        suma = 0  
        for k in range(N):
            angulo = 2j * math.pi * k * n / N  
            suma += (dft_result[k]["real"] + 1j * dft_result[k]["imag"]) * cmath.exp(angulo)  
        x_recuperada.append(round(suma.real / N))
    return x_recuperada

# Función principal que recibe el evento
def lambda_handler(event, context):
    # Obtener la señal del evento
    signal = [float(value) for value in event.get("signal", [])]

    # Calcular la DFT de la señal
    dft_result = calcular_dft(signal)

    # Calcular la IDFT a partir de la DFT
    idft_result = calcular_idft(dft_result)

    # Imprimir ambos resultados como listas
    print("Transformada de Fourier (DFT):", dft_result)
    print("Transformada Inversa de Fourier (IDFT):", idft_result)

    # Retornar los resultados en formato JSON
    return json.dumps({
        "DFT": dft_result,
        "signal": idft_result
    })
