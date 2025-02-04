"""Acá estará la TF"""
import math
import cmath  

def dft(x):
    N = len(x)
    Y = []  # almacenar la salida 

    for k in range(N):  # Para cada frecuencia k de salida
        sum_complej = 0  
        for n in range(N):  # Para cada muestra de la señal de entrada
            ang = -2j * math.pi * k * n / N  # exponente complejo
            sum_complej += x[n] * cmath.exp(ang)  #  fórmula fourier discreta
        
        Y.append(sum_complej)  
    
    return Y  

# Señal ejemplo clase
x = [1, 2, 3, 1, 1, 2]

Y = dft(x)

for k in range(len(Y)):  
    val = Y[k]
    print(f"Y[{k}] = {val.real:.4f} + {val.imag:.4f}j")
