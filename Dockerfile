# Dockerfile para Calculator MCP Server
# Proporciona aritmética de precisión arbitraria usando bc de Linux

FROM python:3.11-slim

# Metadatos del contenedor
LABEL maintainer="Calculator MCP Team"
LABEL description="Servidor MCP para cálculos matemáticos de precisión arbitraria"
LABEL version="1.0.0"

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    bc \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de requisitos primero (para aprovechar cache de Docker)
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY calculator_mcp.py .
COPY examples/ ./examples/

# Crear directorio para logs
RUN mkdir -p /app/logs

# Crear usuario no-root para seguridad
RUN useradd -m -u 1000 calculator \
    && chown -R calculator:calculator /app

# Cambiar al usuario no-root
USER calculator

# Verificar que bc está disponible
RUN bc --version

# Exponer puerto para comunicación MCP (si se usa TCP en lugar de stdio)
EXPOSE 8080

# Variables de entorno
ENV PYTHONPATH=/app
ENV MCP_SERVER_NAME=calculator-mcp
ENV MCP_SERVER_VERSION=1.0.0
ENV DEFAULT_PRECISION=20

# Healthcheck para verificar que el servidor está funcionando
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import subprocess; subprocess.run(['bc', '--version'], check=True)" || exit 1

# Comando por defecto
CMD ["python", "calculator_mcp.py"]