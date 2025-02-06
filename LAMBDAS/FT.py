"""Acá estará la TF"""
import json
import math
import cmath  

def transformada_fourier(x):
    N = len(x)
    Y = []

    for k in range(N):  
        sum_complej = 0  
        for n in range(N):  
            ang = -2j * math.pi * k * n / N  
            sum_complej += x[n] * cmath.exp(ang) 
        Y.append(sum_complej)  
    return [{"real": val.real, "imag": val.imag} for val in Y]  

def cargar_señal(event):
    """Carga la señal desde el JSON recibido en AWS Lambda."""
    try:
        if "body" in event:
            data = json.loads(event["body"])  # Si viene como string dentro de "body"
        else:
            data = event  # Si ya es un diccionario
        
        return [float(value) for value in data["signal"]]  # Convertir valores a flotantes
    except Exception as e:
        return None

def lambda_handler(event, context):
    """Función Lambda para procesar la señal desde JSON."""
    signal = cargar_señal(event)

    if signal is None:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Formato de entrada incorrecto. Asegúrate de enviar un JSON válido con "signal".'})
        }

    resultado = transformada_fourier(signal)  
    return {
        'statusCode': 200,
        'body': json.dumps({'DFT': resultado})
    }
