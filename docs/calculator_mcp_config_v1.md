# Calculator MCP - Configuración y Documentación

## Descripción General

Calculator MCP es un servidor de protocolo de comunicación de modelos (MCP) que proporciona capacidades de cálculo matemático avanzado utilizando la herramienta `bc` de Linux. Ofrece aritmética de precisión arbitraria, ideal para cálculos financieros, científicos y situaciones donde la precisión es crítica.

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

### Requisitos Previos

```bash
# Instalar dependencias del sistema
sudo apt-get update
sudo apt-get install bc

# Instalar dependencias Python
pip install mcp
```

### Configuración del Servidor

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

### Estructura del Proyecto

```
calculator-mcp/
├── calculator_mcp.py          # Servidor MCP principal
├── requirements.txt           # Dependencias Python
├── README.md                  # Documentación
└── examples/
    ├── financial_calculations.py
    ├── scientific_calculations.py
    └── algorithm_examples.py
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

- **Dependencia de bc**: Requ