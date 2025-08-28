#!/usr/bin/env python3
"""
Calculator MCP Server - Aritmética de precisión arbitraria usando bc de Linux
==========================================================================

Este servidor MCP proporciona capacidades de cálculo matemático avanzado utilizando
la herramienta bc de Linux, ofreciendo aritmética de precisión arbitraria ideal
para cálculos financieros, científicos y situaciones donde la precisión es crítica.

Características:
- Aritmética de precisión arbitraria
- Funciones matemáticas avanzadas
- Ejecución de algoritmos de cálculo
- Manejo seguro de expresiones matemáticas
- Soporte para variables y funciones personalizadas

Autor: Assistant
Versión: 1.0
"""

import asyncio
import json
import subprocess
import sys
import re
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from mcp.server import Server
from mcp.server.lowlevel import NotificationOptions # Importación corregida
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CalculatorResult:
    """Resultado de una operación de cálculo"""
    result: str
    expression: str
    precision: int
    execution_time: float
    success: bool
    error_message: Optional[str] = None

class BCCalculator:
    """
    Wrapper para la herramienta bc de Linux con capacidades avanzadas
    """
    
    def __init__(self, default_precision: int = 20):
        self.default_precision = default_precision
        self.session_variables = {}
        self.custom_functions = {}
        
    def _sanitize_expression(self, expression: str) -> str:
        """
        Sanitiza la expresión matemática para evitar comandos peligrosos
        """
        # Remover comandos peligrosos
        dangerous_patterns = [
            r'system\s*\(',
            r'quit\s*\(',
            r'halt\s*\(',
            r'read\s*\(',
            r'print\s*\(',
            r'\..*',  # Comandos que empiezan con punto
            r'!.*',   # Comandos shell
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, expression, re.IGNORECASE):
                raise ValueError(f"Expresión contiene comando no permitido: {pattern}")
        
        return expression.strip()
    
    def _prepare_bc_input(self, expression: str, precision: Optional[int] = None) -> str:
        """
        Prepara la entrada para bc con configuración de precisión y funciones
        """
        if precision is None:
            precision = self.default_precision
            
        bc_input = f"scale={precision}\n"
        
        # Agregar funciones matemáticas comunes
        bc_input += """
        # Funciones matemáticas útiles
        define abs(x) { if (x < 0) return -x; return x; }
        define max(x, y) { if (x > y) return x; return y; }
        define min(x, y) { if (x < y) return x; return y; }
        define pow(x, y) { return x^y; }
        define factorial(n) { 
            if (n <= 1) return 1;
            return n * factorial(n-1);
        }
        define fibonacci(n) {
            if (n <= 1) return n;
            return fibonacci(n-1) + fibonacci(n-2);
        }
        define gcd(a, b) {
            if (b == 0) return a;
            return gcd(b, a % b);
        }
        define lcm(a, b) {
            return (a * b) / gcd(a, b);
        }
        define pi() { return 3.14159265358979323846; }
        define e() { return 2.71828182845904523536; }
        
        """
        
        # Agregar variables de sesión
        for var_name, var_value in self.session_variables.items():
            bc_input += f"{var_name} = {var_value}\n"
        
        # Agregar funciones personalizadas
        for func_name, func_def in self.custom_functions.items():
            bc_input += f"{func_def}\n"
        
        # Agregar la expresión principal
        bc_input += f"{expression}\n"
        
        return bc_input
    
    async def calculate(self, expression: str, precision: Optional[int] = None) -> CalculatorResult:
        """
        Ejecuta una expresión matemática usando bc
        """
        import time
        start_time = time.time()
        
        try:
            # Sanitizar expresión
            clean_expression = self._sanitize_expression(expression)
            
            # Preparar entrada para bc
            bc_input = self._prepare_bc_input(clean_expression, precision)
            
            # Ejecutar bc
            process = await asyncio.create_subprocess_exec(
                'bc', '-l',
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate(bc_input.encode())
            
            execution_time = time.time() - start_time
            
            if process.returncode != 0:
                error_msg = stderr.decode().strip()
                return CalculatorResult(
                    result="",
                    expression=expression,
                    precision=precision or self.default_precision,
                    execution_time=execution_time,
                    success=False,
                    error_message=f"Error en bc: {error_msg}"
                )
            
            result = stdout.decode().strip()
            
            # Limpiar resultado (remover líneas vacías)
            result_lines = [line for line in result.split('\n') if line.strip()]
            final_result = result_lines[-1] if result_lines else ""
            
            return CalculatorResult(
                result=final_result,
                expression=expression,
                precision=precision or self.default_precision,
                execution_time=execution_time,
                success=True
            )
            
        except Exception as e:
            return CalculatorResult(
                result="",
                expression=expression,
                precision=precision or self.default_precision,
                execution_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            )
    
    def set_variable(self, name: str, value: str):
        """Establece una variable de sesión"""
        self.session_variables[name] = value
    
    def set_function(self, name: str, definition: str):
        """Establece una función personalizada"""
        self.custom_functions[name] = definition
    
    def clear_session(self):
        """Limpia variables y funciones de sesión"""
        self.session_variables.clear()
        self.custom_functions.clear()

# Inicializar calculadora
calculator = BCCalculator()

# Crear servidor MCP
server = Server("calculator-mcp")

@server.list_resources()
async def handle_list_resources() -> List[Resource]:
    """
    Lista los recursos disponibles en el servidor de calculadora
    """
    return [
        Resource(
            uri="calculator://functions",
            name="Funciones Matemáticas Disponibles",
            description="Lista de funciones matemáticas predefinidas",
            mimeType="text/plain"
        ),
        Resource(
            uri="calculator://examples",
            name="Ejemplos de Uso",
            description="Ejemplos de expresiones matemáticas y algoritmos",
            mimeType="text/plain"
        ),
        Resource(
            uri="calculator://precision-guide",
            name="Guía de Precisión",
            description="Información sobre configuración de precisión",
            mimeType="text/plain"
        )
    ]

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """
    Lee el contenido de un recurso específico
    """
    if uri == "calculator://functions":
        return """
FUNCIONES MATEMÁTICAS DISPONIBLES EN CALCULATOR MCP
=================================================

Funciones Básicas:
- abs(x): Valor absoluto
- max(x, y): Máximo entre dos valores
- min(x, y): Mínimo entre dos valores
- pow(x, y): x elevado a la y (equivalente a x^y)

Funciones Avanzadas:
- factorial(n): Factorial de n
- fibonacci(n): n-ésimo número de Fibonacci
- gcd(a, b): Máximo común divisor
- lcm(a, b): Mínimo común múltiplo

Constantes:
- pi(): Constante π (3.14159...)
- e(): Constante e (2.71828...)

Operadores Disponibles:
- +, -, *, /: Operaciones básicas
- ^: Exponenciación
- %: Módulo
- sqrt(x): Raíz cuadrada
- s(x): Seno
- c(x): Coseno
- a(x): Arcotangente
- l(x): Logaritmo natural
- e(x): Función exponencial

Ejemplos de Uso:
- factorial(50)
- fibonacci(100)
- sqrt(2)
- pi() * 2^2
- gcd(48, 18)
        """
    
    elif uri == "calculator://examples":
        return """
EJEMPLOS DE USO - CALCULATOR MCP
==============================

1. Cálculos Financieros:
   - Interés compuesto: 1000 * (1 + 0.05)^10
   - Valor presente: 1000 / (1 + 0.08)^5
   - Amortización: 100000 * (0.005 * (1+0.005)^360) / ((1+0.005)^360 - 1)

2. Cálculos Científicos:
   - Velocidad de escape: sqrt(2 * 9.8 * 6371000)
   - Energía cinética: 0.5 * 70 * 25^2
   - Ley de Ohm: 220 / 10

3. Matemáticas Avanzadas:
   - Números grandes: factorial(100)
   - Secuencia Fibonacci: fibonacci(50)
   - Combinatoria: factorial(10) / (factorial(3) * factorial(7))

4. Algoritmos de Cálculo:
   - Serie de Taylor para e^x: 1 + x + x^2/2 + x^3/6 + x^4/24
   - Aproximación de π: 4 * (1 - 1/3 + 1/5 - 1/7 + 1/9)

5. Conversiones:
   - Grados a radianes: 180 * pi() / 180
   - Celsius a Fahrenheit: 25 * 9/5 + 32
        """
    
    elif uri == "calculator://precision-guide":
        return """
GUÍA DE PRECISIÓN - CALCULATOR MCP
=================================

Configuración de Precisión:
- Precisión por defecto: 20 dígitos decimales
- Precisión máxima recomendada: 100 dígitos
- Para cálculos financieros: 4-6 dígitos
- Para cálculos científicos: 15-20 dígitos
- Para matemáticas teóricas: 50+ dígitos

Ejemplos de Precisión:
- precision=2: 3.14
- precision=10: 3.1415926536
- precision=20: 3.14159265358979323846

Consideraciones:
- Mayor precisión = mayor tiempo de cálculo
- Algunos cálculos pueden requerir precisión específica
- La precisión afecta todas las operaciones en la expresión
        """
    
    else:
        raise ValueError(f"Recurso no encontrado: {uri}")

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """
    Lista las herramientas disponibles
    """
    return [
        Tool(
            name="calculate",
            description="Ejecuta expresiones matemáticas con precisión arbitraria usando bc",
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Expresión matemática a evaluar (ej: '2^100', 'factorial(50)', 'sqrt(2)')"
                    },
                    "precision": {
                        "type": "integer",
                        "description": "Número de dígitos decimales de precisión (opcional, default: 20)",
                        "minimum": 1,
                        "maximum": 100
                    }
                },
                "required": ["expression"]
            }
        ),
        Tool(
            name="set_variable",
            description="Define una variable para usar en cálculos posteriores",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Nombre de la variable"
                    },
                    "value": {
                        "type": "string",
                        "description": "Valor de la variable (expresión matemática)"
                    }
                },
                "required": ["name", "value"]
            }
        ),
        Tool(
            name="define_function",
            description="Define una función personalizada para usar en cálculos",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Nombre de la función"
                    },
                    "definition": {
                        "type": "string",
                        "description": "Definición de la función en sintaxis bc (ej: 'define square(x) { return x*x; }')"
                    }
                },
                "required": ["name", "definition"]
            }
        ),
        Tool(
            name="solve_algorithm",
            description="Ejecuta un algoritmo de cálculo complejo paso a paso",
            inputSchema={
                "type": "object",
                "properties": {
                    "algorithm": {
                        "type": "string",
                        "description": "Algoritmo de cálculo en sintaxis bc (múltiples líneas permitidas)"
                    },
                    "precision": {
                        "type": "integer",
                        "description": "Precisión para los cálculos (opcional, default: 20)",
                        "minimum": 1,
                        "maximum": 100
                    }
                },
                "required": ["algorithm"]
            }
        ),
        Tool(
            name="clear_session",
            description="Limpia todas las variables y funciones definidas en la sesión",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """
    Maneja las llamadas a herramientas
    """
    try:
        if name == "calculate":
            expression = arguments["expression"]
            precision = arguments.get("precision")
            
            result = await calculator.calculate(expression, precision)
            
            if result.success:
                response = f"""
✅ RESULTADO DEL CÁLCULO
========================

Expresión: {result.expression}
Resultado: {result.result}
Precisión: {result.precision} dígitos decimales
Tiempo de ejecución: {result.execution_time:.4f} segundos

📊 El cálculo se completó exitosamente usando aritmética de precisión arbitraria.
"""
            else:
                response = f"""
❌ ERROR EN EL CÁLCULO
=====================

Expresión: {result.expression}
Error: {result.error_message}
Tiempo de ejecución: {result.execution_time:.4f} segundos

💡 Revisa la sintaxis de tu expresión matemática.
"""
            
            return [TextContent(type="text", text=response)]
        
        elif name == "set_variable":
            var_name = arguments["name"]
            var_value = arguments["value"]
            
            calculator.set_variable(var_name, var_value)
            
            response = f"""
✅ VARIABLE DEFINIDA
==================

Variable: {var_name}
Valor: {var_value}

La variable está disponible para usar en cálculos posteriores.
"""
            
            return [TextContent(type="text", text=response)]
        
        elif name == "define_function":
            func_name = arguments["name"]
            func_definition = arguments["definition"]
            
            calculator.set_function(func_name, func_definition)
            
            response = f"""
✅ FUNCIÓN DEFINIDA
==================

Función: {func_name}
Definición: {func_definition}

La función está disponible para usar en cálculos posteriores.
"""
            
            return [TextContent(type="text", text=response)]
        
        elif name == "solve_algorithm":
            algorithm = arguments["algorithm"]
            precision = arguments.get("precision")
            
            result = await calculator.calculate(algorithm, precision)
            
            if result.success:
                response = f"""
✅ ALGORITMO EJECUTADO
=====================

Algoritmo:
{result.expression}

Resultado: {result.result}
Precisión: {result.precision} dígitos decimales
Tiempo de ejecución: {result.execution_time:.4f} segundos

🧮 El algoritmo se ejecutó exitosamente.
"""
            else:
                response = f"""
❌ ERROR EN EL ALGORITMO
=======================

Algoritmo:
{result.expression}

Error: {result.error_message}
Tiempo de ejecución: {result.execution_time:.4f} segundos

💡 Revisa la sintaxis del algoritmo.
"""
            
            return [TextContent(type="text", text=response)]
        
        elif name == "clear_session":
            calculator.clear_session()
            
            response = """
✅ SESIÓN LIMPIADA
=================

Se han eliminado todas las variables y funciones definidas en la sesión.
Puedes empezar con cálculos frescos.
"""
            
            return [TextContent(type="text", text=response)]
        
        else:
            raise ValueError(f"Herramienta desconocida: {name}")
    
    except Exception as e:
        error_response = f"""
❌ ERROR
========

Error: {str(e)}

Por favor, revisa los parámetros de entrada y vuelve a intentar.
"""
        return [TextContent(type="text", text=error_response)]

async def main():
    """
    Función principal para ejecutar el servidor MCP
    """
    logger.info("Iniciando Calculator MCP Server...")
    
    # Verificar que bc esté disponible
    try:
        process = await asyncio.create_subprocess_exec(
            'bc', '--version',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
        if process.returncode != 0:
            raise Exception("bc no está disponible")
    except Exception as e:
        logger.error(f"Error: bc no está disponible en el sistema: {e}")
        sys.exit(1)
    
    logger.info("✅ bc está disponible - Calculator MCP Server listo")
    
    # Ejecutar servidor
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="calculator-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(), # Cambiado de None a NotificationOptions()
                    experimental_capabilities=None
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
