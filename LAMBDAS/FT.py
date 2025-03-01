import json
import math
import cmath
import boto3

client = boto3.client('lambda')

def generar_senal(fs, T, f1, f2, A1, A2):
    N = int(fs * T)  
    signal = [A1 * math.sin(2 * math.pi * f1 * t / fs) + A2 * math.sin(2 * math.pi * f2 * t / fs) for t in range(N)]
    return signal

def calcular_dft(signal, fs):
    N = len(signal)
    Y = []
    for k in range(N):  
        suma = 0  
        for n in range(N):  
            angulo = -2j * math.pi * k * n / N  
            suma += signal[n] * cmath.exp(angulo) 
        frecuencia = (k if k < N // 2 else k - N) * fs / N  # FRECUENCIA
        Y.append({
            "real": round(suma.real, 6),
            "imag": round(suma.imag, 6),
            "frecuencia": round(frecuencia, 6)
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
        x_recuperada.append(suma.real / N)  
    return x_recuperada

def aplicar_filtro(dft_result, filter_type, f_low=None, f_high=None, fs=None):
    payload = {
        "dft_input": dft_result,
        "filter": filter_type,
        "f_low": f_low,
        "f_high": f_high,
        "fs": fs
    }

    response = client.invoke(
        FunctionName='Filtro_ideal',  # ¡¡CAMBIAR PO NOMBRE DE FUNCIÓN DE FILTROS!!
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )

    response_payload = json.loads(response['Payload'].read().decode('utf-8'))

    return response_payload.get("filtered_signal", [])

def lambda_handler(event, context):
    print(event)
    body = json.loads(event['body'])
    #body = event['body']
    print(body)

    
    fs = body['fs']
    T = body['T']
    f1 = body['f1']
    f2 = body['f2']
    A1 = body['A1']
    A2 = body['A2']
    filter_type = body.get('filter', None)
    f_low = body.get('f_low', None)
    f_high = body.get('f_high', None)
    
    # Generar la señal
    signal = generar_senal(fs, T, f1, f2, A1, A2)
    
    # Calcular la DFT
    dft_result = calcular_dft(signal, fs)
    
    # Aplicar filtro si se especifica
    if filter_type:
        dft_result = aplicar_filtro(dft_result, filter_type, f_low, f_high, fs)
    
    # Calcular la IDFT de la señal filtrada
    result = calcular_idft(dft_result)
    
    return {"result": result}