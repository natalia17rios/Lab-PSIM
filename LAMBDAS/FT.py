import json
import math
import cmath

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

def lambda_handler(event, context):
    signal = [float(value) for value in event.get("signal", [])]
    transform_type = event.get("transform", "DFT")
    
    if transform_type == "DFT":
        result = calcular_dft(signal)
    elif transform_type == "IDFT":
        dft_input = event.get("dft_input", [])
        result = calcular_idft(dft_input)
    else:
        return json.dumps({"error": "Tipo de transformada no válido"})
    
    return json.dumps({"result": result})
