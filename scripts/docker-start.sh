#!/bin/bash
# Scripts de utilidad para Calculator MCP Docker

# =============================================================================
# docker-start.sh - Script de inicio del servidor
# =============================================================================

echo "🐳 Iniciando Calculator MCP con Docker..."

# Verificar si Docker está corriendo
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker no está corriendo. Por favor, inicia Docker Desktop o el daemon."
    exit 1
fi

# Función para mostrar ayuda
show_help() {
    echo "Uso: $0 [opciones]"
    echo ""
    echo "Opciones:"
    echo "  -h, --help          Mostrar esta ayuda"
    echo "  -d, --dev           Modo desarrollo (monta código fuente)"
    echo "  -p, --port PORT     Puerto personalizado (default: 8080)"
    echo "  -n, --name NAME     Nombre del contenedor (default: calculator-mcp-server)"
    echo "  --precision NUM     Precisión por defecto (default: 20)"
    echo "  --rebuild           Forzar reconstrucción de la imagen"
    echo "  --compose           Usar docker-compose en lugar de docker run"
    echo ""
    echo "Ejemplos:"
    echo "  $0                  # Inicio básico"
    echo "  $0 -d               # Modo desarrollo"
    echo "  $0 -p 9090          # Puerto personalizado"
    echo "  $0 --compose        # Usar docker-compose"
}

# Valores por defecto
PORT=8080
CONTAINER_NAME="calculator-mcp-server"
DEFAULT_PRECISION=20
DEV_MODE=false
REBUILD=false
USE_COMPOSE=false

# Parsear argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -d|--dev)
            DEV_MODE=true
            shift
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -n|--name)
            CONTAINER_NAME="$2"
            shift 2
            ;;
        --precision)
            DEFAULT_PRECISION="$2"
            shift 2
            ;;
        --rebuild)
            REBUILD=true
            shift
            ;;
        --compose)
            USE_COMPOSE=true
            shift
            ;;
        *)
            echo "❌ Opción desconocida: $1"
            show_help
            exit 1
            ;;
    esac
done

# Usar docker-compose si se especifica
if [ "$USE_COMPOSE" = true ]; then
    echo "🔧 Usando docker-compose..."
    
    if [ "$REBUILD" = true ]; then
        echo "🔨 Reconstruyendo servicios..."
        docker-compose down
        docker-compose build --no-cache
    fi
    
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        echo "✅ Calculator MCP Stack iniciado con docker-compose"
        echo "📋 Logs: docker-compose logs -f calculator-mcp"
        echo "🛑 Detener: docker-compose down"
        echo ""
        echo "🌐 Servicios disponibles:"
        echo "  - Calculator MCP: http://localhost:8080"
        echo "  - Prometheus: http://localhost:9090"
        echo "  - Grafana: http://localhost:3000 (admin/admin)"
    else
        echo "❌ Error iniciando con docker-compose"
        exit 1
    fi
    
    exit 0
fi

# Construir imagen si no existe o si se fuerza rebuild
if [[ "$(docker images -q calculator-mcp:latest 2> /dev/null)" == "" ]] || [ "$REBUILD" = true ]; then
    echo "🔨 Construyendo imagen Docker..."
    
    if [ "$REBUILD" = true ]; then
        docker build --no-cache -t calculator-mcp:latest .
    else
        docker build -t calculator-mcp:latest .
    fi
    
    if [ $? -ne 0 ]; then
        echo "❌ Error construyendo la imagen"
        exit 1
    fi
fi

# Detener contenedor existente si está corriendo
if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    echo "🛑 Deteniendo contenedor existente..."
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
fi

# Preparar argumentos para docker run
DOCKER_ARGS=(
    -d
    --name $CONTAINER_NAME
    -p $PORT:8080
    --restart unless-stopped
    -e DEFAULT_PRECISION=$DEFAULT_PRECISION
)

# Configuración para modo desarrollo
if [ "$DEV_MODE" = true ]; then
    echo "🔧 Modo desarrollo activado"
    DOCKER_ARGS+=(
        -v "$(pwd)/calculator_mcp.py:/app/calculator_mcp.py"
        -v "$(pwd)/examples:/app/examples"
        -e PYTHONUNBUFFERED=1
    )
fi

# Iniciar nuevo contenedor
echo "🚀 Iniciando Calculator MCP Server..."
docker run "${DOCKER_ARGS[@]}" calculator-mcp:latest

# Verificar que el contenedor está corriendo
sleep 2
if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    echo "✅ Calculator MCP Server está corriendo"
    echo "🌐 Servidor disponible en: http://localhost:$PORT"
    echo "📋 Logs: docker logs -f $CONTAINER_NAME"
    echo "🛑 Detener: docker stop $CONTAINER_NAME"
    echo ""
    
    # Mostrar algunos logs iniciales
    echo "📋 Logs iniciales:"
    docker logs --tail 10 $CONTAINER_NAME
else
    echo "❌ Error iniciando el servidor"
    echo "📋 Logs de error:"
    docker logs $CONTAINER_NAME
    exit 1
fi

# =============================================================================
# docker-stop.sh - Script de parada del servidor
# =============================================================================

echo "🛑 Deteniendo Calculator MCP Server..."

# Función para mostrar ayuda
show_stop_help() {
    echo "Uso: $0 [opciones]"
    echo ""
    echo "Opciones:"
    echo "  -h, --help          Mostrar esta ayuda"
    echo "  -n, --name NAME     Nombre del contenedor (default: calculator-mcp-server)"
    echo "  --compose           Usar docker-compose para detener"
    echo "  --clean             Eliminar también la imagen"
    echo "  --volumes           Eliminar también los volúmenes"
    echo ""
    echo "Ejemplos:"
    echo "  $0                  # Detener servidor básico"
    echo "  $0 --compose        # Detener con docker-compose"
    echo "  $0 --clean          # Detener y limpiar imagen"
}

# Valores por defecto
CONTAINER_NAME="calculator-mcp-server"
USE_COMPOSE=false
CLEAN_IMAGE=false
CLEAN_VOLUMES=false

# Parsear argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_stop_help
            exit 0
            ;;
        -n|--name)
            CONTAINER_NAME="$2"
            shift 2
            ;;
        --compose)
            USE_COMPOSE=true
            shift
            ;;
        --clean)
            CLEAN_IMAGE=true
            shift
            ;;
        --volumes)
            CLEAN_VOLUMES=true
            shift
            ;;
        *)
            echo "❌ Opción desconocida: $1"
            show_stop_help
            exit 1
            ;;
    esac
done

# Usar docker-compose si se especifica
if [ "$USE_COMPOSE" = true ]; then
    echo "🔧 Deteniendo con docker-compose..."
    
    if [ "$CLEAN_VOLUMES" = true ]; then
        docker-compose down -v
        echo "🗑️  Volúmenes eliminados"
    else
        docker-compose down
    fi
    
    if [ "$CLEAN_IMAGE" = true ]; then
        docker-compose down --rmi all
        echo "🗑️  Imágenes eliminadas"
    fi
    
    echo "✅ Calculator MCP Stack detenido"
    exit 0
fi

# Detener contenedor individual
if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
    echo "✅ Calculator MCP Server detenido"
else
    echo "ℹ️  El servidor no está corriendo"
fi

# Limpiar imagen si se solicita
if [ "$CLEAN_IMAGE" = true ]; then
    if [[ "$(docker images -q calculator-mcp:latest 2> /dev/null)" != "" ]]; then
        docker rmi calculator-mcp:latest
        echo "🗑️  Imagen eliminada"
    fi
fi

# Limpiar volúmenes si se solicita
if [ "$CLEAN_VOLUMES" = true ]; then
    docker volume prune -f
    echo "🗑️  Volúmenes limpiados"
fi

# =============================================================================
# docker-logs.sh - Script para ver logs
# =============================================================================

echo "📋 Mostrando logs de Calculator MCP..."

# Función para mostrar ayuda
show_logs_help() {
    echo "Uso: $0 [opciones]"
    echo ""
    echo "Opciones:"
    echo "  -h, --help          Mostrar esta ayuda"
    echo "  -f, --follow        Seguir logs en tiempo real"
    echo "  -n, --name NAME     Nombre del contenedor (default: calculator-mcp-server)"
    echo "  --tail NUM          Mostrar últimas NUM líneas (default: 50)"
    echo "  --compose           Usar docker-compose logs"
    echo ""
    echo "Ejemplos:"
    echo "  $0                  # Mostrar logs"
    echo "  $0 -f               # Seguir logs en tiempo real"
    echo "  $0 --tail 100       # Mostrar últimas 100 líneas"
}

# Valores por defecto
CONTAINER_NAME="calculator-mcp-server"
FOLLOW=false
TAIL_LINES=50
USE_COMPOSE=false

# Parsear argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_logs_help
            exit 0
            ;;
        -f|--follow)
            FOLLOW=true
            shift
            ;;
        -n|--name)
            CONTAINER_NAME="$2"
            shift 2
            ;;
        --tail)
            TAIL_LINES="$2"
            shift 2
            ;;
        --compose)
            USE_COMPOSE=true
            shift
            ;;
        *)
            echo "❌ Opción desconocida: $1"
            show_logs_help
            exit 1
            ;;
    esac
done

# Usar docker-compose si se especifica
if [ "$USE_COMPOSE" = true ]; then
    if [ "$FOLLOW" = true ]; then
        docker-compose logs -f --tail $TAIL_LINES
    else
        docker-compose logs --tail $TAIL_LINES
    fi
    exit 0
fi

# Mostrar logs del contenedor individual
if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    if [ "$FOLLOW" = true ]; then
        docker logs -f --tail $TAIL_LINES $CONTAINER_NAME
    else
        docker logs --tail $TAIL_LINES $CONTAINER_NAME
    fi
else
    echo "❌ El contenedor $CONTAINER_NAME no está corriendo"
    exit 1
fi