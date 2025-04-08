import numpy as np

def aplicar_filtro_disco(f_transformada, radio):
    """
    Aplica un filtro de disco a la transformada de Fourier de una imagen.
    
    Parámetros:
    - f_transformada: Transformada de Fourier 2D de la imagen (numpy array complejo).
    - radio: Radio del filtro en píxeles (por defecto 80x80).
    
    Retorna:
    - Transformada de Fourier filtrada (multiplicada con la máscara).
    """
    # Obtener las dimensiones de la imagen
    M, N = f_transformada.shape
    
    # Crear una máscara de ceros con el mismo tamaño que la imagen
    mask = np.zeros((M, N), dtype=np.float32)

    # Coordenadas del centro de la imagen
    centro_x, centro_y = M // 2, N // 2

    # Crear el filtro de disco: valores dentro del radio son 1, fuera son 0
    for i in range(M):
        for j in range(N):
            if np.sqrt((i - centro_x)**2 + (j - centro_y)**2) <= radio:
                mask[i, j] = 1  # Mantener solo las frecuencias dentro del disco

    # Aplicar la máscara multiplicándola con la transformada de Fourier
    f_filtrada = f_transformada * mask
    
    return f_filtrada
