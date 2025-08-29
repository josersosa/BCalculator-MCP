# Calculator MCP - Configuración y Documentación

## Descripción General

Calculator MCP es un servidor de protocolo de comunicación de modelos (MCP) que proporciona capacidades de cálculo matemático avanzado utilizando la herramienta `bc` de Linux. Ofrece:
- Aritmética de precisión arbitraria
- Funciones matemáticas avanzadas
- Capacidades de algoritmos
- Seguridad robusta
- Es programable. Permite la definición de variables y funciones, cuenta con estructuras de control, por lo que ofrece muchas más posibilidades de simples operaciones aritméticas
- Es un comando bien conocido, por lo que todos los LLMs deberían poderlo usar

## Características Principales

### 🔢 Aritmética de Precisión Arbitraria
- Utiliza `bc` de Linux para cálculos sin limitaciones de punto flotante
- Precisión configurable hasta 100 dígitos decimales
- Ideal para cálculos financieros y científicos precisos

### 🧮 Funciones Matemáticas Avanzadas
- Funciones trigonométricas, logarítmicas y exponenciales
- Funciones personalizadas (factorial, fibonacci, gcd, lcm)
- Constantes matemáticas (π, e)

### 💡 Capacidades de Algoritmos
- Ejecución de algoritmos matemáticos complejos
- Variables de sesión para cálculos multi-paso
- Funciones definidas por el usuario

### 🔒 Seguridad
- Sanitización de expresiones para prevenir comandos peligrosos
- Validación de entrada robusta
- Manejo seguro de errores

## Instalación y Configuración

### Opción 1: Instalación Local

#### Requisitos Previos

```bash
# Instalar dependencias del sistema
sudo apt-get update
sudo apt-get install bc

# Instalar dependencias Python
pip install mcp
```

#### Configuración del Servidor

```json
{
  "mcpServers": {
    "calculator": {
      "command": "python",
      "args": ["calculator_mcp.py"],
      "env": {
        "PYTHONPATH": "/path/to/calculator/mcp"
      }
    }
  }
}
```

### Opción 2: Instalación con Docker

#### Dockerfile

```dockerfile
FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    bc \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de requisitos
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY calculator_mcp.py .
COPY examples/ ./examples/

# Crear usuario no-root para seguridad
RUN useradd -m -u 1000 calculator
USER calculator

# Exponer puerto para comunicación MCP
EXPOSE 8080

# Comando por defecto
CMD ["python", "calculator_mcp.py"]
```

#### docker-compose.yml

```yaml
version: '3.8'

services:
  calculator-mcp:
    build: .
    container_name: balculator-mcp
    ports:
      - "8080:8080"
    environment:
      - PYTHONPATH=/app
      - MCP_SERVER_NAME=calculator-mcp
      - MCP_SERVER_VERSION=1.0.0
      - DEFAULT_PRECISION=20
    volumes:
      - ./examples:/app/examples:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import subprocess; subprocess.run(['bc', '--version'], check=True)"]
      interval: 30s
      timeout: 10s
      retries: 3
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp:noexec,nosuid,size=100m
```

#### Construir y Ejecutar con Docker

```bash
# Clonar el repositorio
git clone <repository-url>
cd calculator-mcp

# Construir la imagen Docker
docker build -t bcalculator-mcp:latest .

# Ejecutar el contenedor
docker run -d \
  --name bcalculator-mcp \
  --port 8080:8080 \
  --restart unless-stopped \
  calculator-mcp:latest

# O usar docker-compose
docker-compose up -d
```

#### Configuración para Cliente MCP con Docker

```json
{
  "mcpServers": {
    "calculator": {
      "command": "docker",
      "args": [
        "exec",
        "-i",
        "bcalculator-mcp",
        "python",
        "calculator_mcp.py"
      ],
      "env": {
        "DOCKER_HOST": "unix:///var/run/docker.sock"
      }
    }
  }
}
```

#### Scripts de Utilidad Docker

**scripts/docker-start.sh**
```bash
#!/bin/bash
echo "🐳 Iniciando BCalculator MCP con Docker..."

# Verificar si Docker está corriendo
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker no está corriendo. Por favor, inicia Docker Desktop o el daemon."
    exit 1
fi

# Construir imagen si no existe
if [[ "$(docker images -q bcalculator-mcp:latest 2> /dev/null)" == "" ]]; then
    echo "🔨 Construyendo imagen Docker..."
    docker build -t bcalculator-mcp:latest .
fi

# Detener contenedor existente si está corriendo
if [ "$(docker ps -q -f name=calculator-mcp)" ]; then
    echo "🛑 Deteniendo contenedor existente..."
    docker stop bcalculator-mcp
    docker rm bcalculator-mcp
fi

# Iniciar nuevo contenedor
echo "🚀 Iniciando BCalculator MCP Server..."
docker run -d \
  --name bcalculator-mcp \
  --port 8080:8080 \
  --restart unless-stopped \
  bcalculator-mcp:latest

# Verificar que el contenedor está corriendo
if [ "$(docker ps -q -f name=calculator-mcp-server)" ]; then
    echo "✅ BCalculator MCP Server está corriendo en el puerto 8080"
    echo "📋 Logs: docker logs calculator-mcp-server"
    echo "🛑 Detener: docker stop calculator-mcp-server"
else
    echo "❌ Error iniciando el servidor"
    exit 1
fi
```

**scripts/docker-stop.sh**
```bash
#!/bin/bash
echo "🛑 Deteniendo BCalculator MCP Server..."

if [ "$(docker ps -q -f name=bcalculator-mcp)" ]; then
    docker stop bcalculator-mcp
    docker rm bcalculator-mcp
    echo "✅ BCalculator MCP Server detenido"
else
    echo "ℹ️  El servidor no está corriendo"
fi
```

### Estructura del Proyecto

```
calculator-mcp/
├── calculator_mcp.py          # Servidor MCP principal
├── requirements.txt           # Dependencias Python
├── Dockerfile                 # Configuración Docker
├── docker-compose.yml         # Orquestación Docker
├── README.md                  # Documentación
├── scripts/
│   ├── docker-start.sh        # Script de inicio Docker
│   └── docker-stop.sh         # Script de parada Docker
└── examples/
    ├── financial_calculations.py
    ├── scientific_calculations.py
    └── algorithm_examples.py
```

### requirements.txt

```txt
mcp>=1.0.0
asyncio-subprocess>=0.1.0
```

## Herramientas Disponibles

### 1. `calculate`
Ejecuta expresiones matemáticas con precisión arbitraria.

**Parámetros:**
- `expression` (string, requerido): Expresión matemática a evaluar
- `precision` (integer, opcional): Número de dígitos decimales (default: 20)

**Ejemplos:**
```javascript
// Cálculo básico
{
  "expression": "2^100",
  "precision": 10
}

// Cálculo financiero
{
  "expression": "1000 * (1 + 0.05)^10",
  "precision": 4
}

// Función matemática
{
  "expression": "factorial(50)"
}
```

### 2. `set_variable`
Define variables para usar en cálculos posteriores.

**Parámetros:**
- `name` (string): Nombre de la variable
- `value` (string): Valor de la variable

**Ejemplo:**
```javascript
{
  "name": "rate",
  "value": "0.05"
}
```

### 3. `define_function`
Define funciones personalizadas.

**Parámetros:**
- `name` (string): Nombre de la función
- `definition` (string): Definición en sintaxis bc

**Ejemplo:**
```javascript
{
  "name": "compound_interest",
  "definition": "define compound_interest(p, r, t) { return p * (1 + r)^t; }"
}
```

### 4. `solve_algorithm`
Ejecuta algoritmos de cálculo complejos.

**Parámetros:**
- `algorithm` (string): Algoritmo en sintaxis bc
- `precision` (integer, opcional): Precisión para los cálculos

**Ejemplo:**
```javascript
{
  "algorithm": "sum = 0; for (i = 1; i <= 100; i++) { sum += i; } sum",
  "precision": 10
}
```

### 5. `clear_session`
Limpia todas las variables y funciones de la sesión.

**Parámetros:** Ninguno

## Recursos Disponibles

### `calculator://functions`
Lista completa de funciones matemáticas disponibles.

### `calculator://examples`
Ejemplos de uso para diferentes tipos de cálculos.

### `calculator://precision-guide`
Guía sobre configuración de precisión para diferentes casos de uso.

## Ejemplos de Uso para Agentes de IA

### Cálculos Financieros

```python
# Interés compuesto
expression = "10000 * (1 + 0.08/12)^(12*5)"
precision = 2

# Valor presente neto
expression = "1000 / (1 + 0.1)^1 + 1500 / (1 + 0.1)^2 + 2000 / (1 + 0.1)^3"
precision = 2

# Amortización de préstamo
expression = "200000 * (0.005 * (1+0.005)^360) / ((1+0.005)^360 - 1)"
precision = 2
```

### Cálculos Científicos

```python
# Velocidad de escape terrestre
expression = "sqrt(2 * 9.8 * 6371000)"
precision = 10

# Energía relativista
expression = "sqrt((90 * 299792458^2)^2 + (70 * 299792458)^2)"
precision = 15

# Constante de Planck en cálculos cuánticos
expression = "6.62607015e-34 * 5e14"
precision = 20
```

### Matemáticas Avanzadas

```python
# Números de Fibonacci grandes
expression = "fibonacci(100)"
precision = 50

# Factorial de números grandes
expression = "factorial(100)"
precision = 50

# Aproximación de π usando serie
expression = "4 * (1 - 1/3 + 1/5 - 1/7 + 1/9 - 1/11 + 1/13 - 1/15)"
precision = 15
```

## Prompts para Agentes de IA

### Prompt de Sistema Base

```markdown
Eres un asistente matemático avanzado con acceso a Calculator MCP, que proporciona aritmética de precisión arbitraria usando bc de Linux. 

CAPACIDADES:
- Cálculos con precisión arbitraria (hasta 100 dígitos decimales)
- Funciones matemáticas avanzadas (trigonométricas, logarítmicas, factoriales)
- Algoritmos matemáticos complejos
- Variables de sesión para cálculos multi-paso
- Funciones definidas por el usuario

CASOS DE USO PRINCIPALES:
1. Cálculos financieros (interés compuesto, amortización, NPV)
2. Cálculos científicos (física, química, ingeniería)
3. Matemáticas teóricas (números grandes, precisión extrema)
4. Algoritmos matemáticos (iteraciones, aproximaciones)

CONFIGURACIÓN DE PRECISIÓN:
- Financiero: 2-4 dígitos decimales
- Científico: 10-20 dígitos decimales
- Teórico: 20-50+ dígitos decimales

Siempre especifica la precisión apropiada para el contexto del problema.
```

### Prompt para Cálculos Financieros

```markdown
Para cálculos financieros, utiliza Calculator MCP con estas configuraciones:

PRECISIÓN: 2-4 dígitos decimales (suficiente para moneda)
VARIABLES COMUNES:
- rate: tasa de interés
- principal: capital inicial
- time: período de tiempo
- payments: pagos periódicos

FÓRMULAS FRECUENTES:
- Interés compuesto: principal * (1 + rate)^time
- Valor presente: future_value / (1 + rate)^time
- Amortización: principal * (rate * (1+rate)^n) / ((1+rate)^n - 1)

Siempre presenta los resultados en formato monetario apropiado.
```

### Prompt para Cálculos Científicos

```markdown
Para cálculos científicos, utiliza Calculator MCP con estas configuraciones:

PRECISIÓN: 10-20 dígitos decimales (según precisión experimental)
CONSTANTES DISPONIBLES:
- pi(): 3.14159265358979323846...
- e(): 2.71828182845904523536...

FUNCIONES ÚTILES:
- sqrt(x): raíz cuadrada
- pow(x, y): potenciación
- abs(x): valor absoluto
- Trigonométricas: s(x), c(x), a(x)

Considera las unidades y órdenes de magnitud apropiados para cada cálculo.
```

## Manejo de Errores

El servidor incluye manejo robusto de errores:

- **Sanitización de entrada**: Previene comandos peligrosos
- **Validación de sintaxis**: Verifica expresiones antes de ejecutar
- **Timeouts**: Evita cálculos infinitos
- **Logging detallado**: Para debugging y monitoreo

## Mejores Prácticas

### Para Desarrolladores

1. **Validar entrada**: Siempre sanitizar expresiones del usuario
2. **Configurar precisión**: Usar precisión apropiada para cada caso
3. **Manejar errores**: Implementar manejo robusto de errores
4. **Optimizar rendimiento**: Usar variables de sesión para cálculos repetitivos

### Para Agentes de IA

1. **Especificar precisión**: Siempre definir precisión apropiada
2. **Usar variables**: Aprovechar variables de sesión para cálculos complejos
3. **Validar resultados**: Verificar que los resultados sean razonables
4. **Documentar cálculos**: Explicar el propósito y contexto de cada cálculo

## Limitaciones y Consideraciones

### Limitaciones Técnicas

- **Dependencia de bc**: Requiere que `bc` esté instalado en el sistema
- **Comunicación stdio**: Utiliza stdin/stdout para comunicación MCP
- **Timeout implícito**: Cálculos muy largos pueden causar timeout
- **Memoria**: Cálculos con números muy grandes pueden consumir mucha memoria

### Consideraciones de Seguridad

- **Sanitización**: Todas las expresiones se sanitizan antes de ejecutar
- **Usuario no-root**: El contenedor Docker ejecuta como usuario no-root
- **Filesystem de solo lectura**: Configuración de seguridad en Docker
- **Límites de recursos**: Configuración de CPU y memoria limitadas

### Consideraciones de Rendimiento

- **Precisión vs Velocidad**: Mayor precisión = mayor tiempo de cálculo
- **Caching**: Variables de sesión mejoran rendimiento en cálculos repetitivos
- **Paralelización**: bc es single-threaded, considerar múltiples instancias para alta concurrencia

### Monitoreo y Logs

Con Docker Compose se incluyen servicios de monitoreo:
- **Prometheus**: Métricas del servidor MCP
- **Grafana**: Dashboard visual de métricas
- **Logs centralizados**: Configuración JSON para análisis

## Uso con Diferentes Clientes MCP

### Claude Desktop

```json
{
  "mcpServers": {
    "calculator": {
      "command": "docker",
      "args": [
        "exec", "-i", "calculator-mcp-server",
        "python", "calculator_mcp.py"
      ]
    }
  }
}
```

### Cline (VSCode)

```json
{
  "mcp": {
    "servers": {
      "calculator": {
        "command": "docker",
        "args": [
          "exec", "-i", "calculator-mcp-server",
          "python", "calculator_mcp.py"
        ]
      }
    }
  }
}
```

### Configuración Personalizada

```bash
# Variables de entorno para personalización
export MCP_CALCULATOR_PRECISION=30
export MCP_CALCULATOR_TIMEOUT=60
export MCP_CALCULATOR_MAX_MEMORY=512M

# Iniciar con configuración personalizada
docker run -d \
  --name calculator-mcp-custom \
  -p 8080:8080 \
  -e DEFAULT_PRECISION=$MCP_CALCULATOR_PRECISION \
  -e CALCULATION_TIMEOUT=$MCP_CALCULATOR_TIMEOUT \
  --memory=$MCP_CALCULATOR_MAX_MEMORY \
  calculator-mcp:latest
```

## Contribuir y Extensiones

### Agregar Nuevas Funciones

1. **Modificar calculator_mcp.py**: Agregar funciones en `_prepare_bc_input`
2. **Actualizar documentación**: Incluir en recursos y ejemplos
3. **Probar extensivamente**: Validar con diferentes casos de uso
4. **Actualizar Docker**: Reconstruir imagen con cambios

### Integraciones Futuras

- **Jupyter Integration**: Usar Calculator MCP en notebooks
- **API REST**: Wrapper HTTP para el servidor MCP
- **WebSocket**: Comunicación en tiempo real
- **Distributed Computing**: Balanceador de carga para múltiples instancias

## Soporte y Troubleshooting

### Problemas Comunes

1. **bc no encontrado**: Verificar instalación de bc en el sistema
2. **Timeout en cálculos**: Aumentar timeout o reducir complejidad
3. **Memoria insuficiente**: Ajustar límites de memoria del contenedor
4. **Permisos Docker**: Verificar permisos de usuario para Docker

### Comandos de Diagnóstico

```bash
# Verificar estado del contenedor
docker ps -f name=calculator-mcp-server

# Verificar logs de error
docker logs --tail 50 calculator-mcp-server

# Verificar uso de recursos
docker stats calculator-mcp-server

# Probar bc manualmente
docker exec -it calculator-mcp-server bc -l
```

### Contacto y Soporte

Para reportar bugs o solicitar características:
- **Issues**: GitHub Issues del proyecto
- **Documentation**: Wiki del proyecto
- **Community**: Discord/Slack del proyecto MCP