if [ "$(docker ps -q -f 'name=bcalculator-mcp')" ]; then
    docker stop bcalculator-mcp
    docker rm bcalculator-mcp