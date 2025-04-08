import boto3
import cv2
import numpy as np
import os
import tempfile
from Filtro import aplicar_filtro_disco

s3 = boto3.client("s3")

def agregar_ruido_gaussiano(image, mean=0, sigma=20):
    """ Agrega ruido gaussiano a una imagen """
    ruido = np.random.normal(mean, sigma, image.shape)
    return np.clip(image + ruido, 0, 255).astype(np.uint8)

def dft_2d(image):
    """ Calcula la Transformada Discreta de Fourier en 2D """
    M, N = image.shape
    DFT = np.zeros((M, N), dtype=complex)

    for k in range(M):
        for l in range(N):
            DFT[k, l] = np.sum(image * np.exp(-2j * np.pi * (k * np.arange(M)[:, None] / M + l * np.arange(N) / N))) / (M * N)
    
    return DFT

def idft_2d(F_filtered):
    """ Calcula la Transformada Inversa de Fourier en 2D """
    M, N = F_filtered.shape
    IDFT = np.zeros((M, N), dtype=complex)

    for i in range(M):
        for h in range(N):
            IDFT[i, h] = np.sum(F_filtered * np.exp(2j * np.pi * (i * np.arange(M)[:, None] / M + h * np.arange(N) / N)))
    
    return np.abs(IDFT)

def handler(event, context):
    try:
        bucket = event["Records"][0]["s3"]["bucket"]["name"]
        image_key = event["Records"][0]["s3"]["object"]["key"]

        print(f"Procesando imagen: {image_key} desde el bucket: {bucket}")

        # Generar nombre de imagen filtrada
        name, ext = os.path.splitext(os.path.basename(image_key))
        filtered_image = f"{name}_filtrada{ext}"

        # Descargar imagen desde S3
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
            s3.download_file(bucket, image_key, temp_file.name)
            print(f"Imagen descargada en: {temp_file.name}")

            # Leer imagen en modo color para mantener calidad
            image = cv2.imread(temp_file.name, cv2.IMREAD_COLOR)

        if image is None:
            print("Error: No se pudo cargar la imagen.")
            return {"error": "No se pudo cargar la imagen."}

        print("Imagen cargada correctamente, convirtiendo a escala de grises...")

        # Convertir la imagen a escala de grises
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        print("Imagen convertida a escala de grises, aplicando procesamiento...")

        # Procesamiento
        image_noisy = agregar_ruido_gaussiano(gray_image)
        DFT = np.fft.fftshift(dft_2d(image_noisy))
        F_filtered = np.fft.ifftshift(aplicar_filtro_disco(DFT, radio=38))
        IDFT = idft_2d(F_filtered)

        # Normalizar y convertir a uint8 para evitar pérdida de calidad
        IDFT = np.abs(IDFT)
        IDFT = (IDFT / np.max(IDFT) * 255).astype(np.uint8)

        # Redimensionar si es necesario
        if IDFT.shape != gray_image.shape:
            print(f"Redimensionando imagen de {IDFT.shape} a {gray_image.shape}")
            IDFT = cv2.resize(IDFT, (gray_image.shape[1], gray_image.shape[0]))

        # Guardar imagen con máxima calidad
        result_path = f"/tmp/{filtered_image}"
        cv2.imwrite(result_path, IDFT, [cv2.IMWRITE_JPEG_QUALITY, 100])

        if not os.path.exists(result_path):
            print("Error: La imagen procesada no se generó en /tmp/")
            return {"error": "La imagen procesada no se generó en /tmp/"}

        print(f"Imagen procesada guardada en: {result_path}")

        # Subir imagen filtrada a S3
        s3.upload_file(result_path, bucket, filtered_image)
        print(f"Imagen subida a S3: s3://{bucket}/{filtered_image}")

        return {"output_image": f"s3://{bucket}/{filtered_image}"}

    except Exception as e:
        print(f"Error en la función: {str(e)}")
        return {"error": str(e)}
