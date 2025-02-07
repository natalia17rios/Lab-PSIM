import json
import math
import cmath  

def transformada_fourier(x):
    """Calcula la Transformada Discreta de Fourier (DFT)."""
    N = len(x)
    Y = []

    for k in range(N):  
        sum_complej = 0  
        for n in range(N):  
            ang = -2j * math.pi * k * n / N  
            sum_complej += x[n] * cmath.exp(ang) 
        Y.append(sum_complej)  
    return [{"real": val.real, "imag": val.imag} for val in Y]  

def transformada_inversa_fourier(X):
    """Calcula la Transformada Inversa de Fourier (IDFT)."""
    N = len(X)
    x = []

    for n in range(N):
        sum_complej = 0  
        for k in range(N):
            ang = 2j * math.pi * k * n / N  # Cambia el signo para la inversa
            sum_complej += (X[k]["real"] + 1j * X[k]["imag"]) * cmath.exp(ang)  
        x.append(sum_complej.real / N)  # Normalización  
    return x  

def cargar_datos(event):
    """Carga la señal o la transformada desde el JSON recibido en AWS Lambda."""
    try:
        if "body" in event:
            data = json.loads(event["body"])  # Si viene como string dentro de "body"
        else:
            data = event  # Si ya es un diccionario

        if "signal" in data:
            return "DFT", [float(value) for value in data["signal"]]  # Convertir valores a flotantes
        elif "DFT" in data:
            return "IDFT", data["DFT"]  # Recuperar los coeficientes de frecuencia
        else:
            return None, None
    except Exception as e:
        return None, None

def lambda_handler(event, context):
    """Función Lambda para procesar la señal y calcular DFT o IDFT."""
    tipo, datos = cargar_datos(event)

    if datos is None:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Formato de entrada incorrecto. Asegúrate de enviar un JSON válido con "signal" o "DFT".'})
        }

    if tipo == "DFT":
        resultado = transformada_fourier(datos)
        return {
            'statusCode': 200,
            'body': json.dumps({'DFT': resultado})
        }
    elif tipo == "IDFT":
        resultado = transformada_inversa_fourier(datos)
        return {
            'statusCode': 200,
            'body': json.dumps({'signal': resultado})
        }
