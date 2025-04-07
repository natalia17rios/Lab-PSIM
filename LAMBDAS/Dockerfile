FROM public.ecr.aws/lambda/python:3.10

# Copia el archivo de dependencias y lo instala en el directorio de trabajo
COPY requirements.txt .
RUN pip install -r requirements.txt --target /var/task/

# Copiar archivos fuente
COPY lambda_function.py .

# Establecer el handler
CMD [ "lambda_function.handler" ]