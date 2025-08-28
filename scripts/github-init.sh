#!/bin/bash
# Verificar que estás en el directorio correcto
Get-Location

# Inicializar git
git init
git add .
git commit -m "Initial commit: BCalculator-MCP"

# Crear repositorio vía API de GitHub (necesitas token personal)
# Primero, crea un token en: https://github.com/settings/tokens

# Luego ejecuta (reemplaza TU_USERNAME y TU_TOKEN):
TOKEN="tu-token-aquí"
USERNAME="tu-usuario-github"

# Crear repositorio via API
curl -H "Authorization: token $TOKEN" -d '{"name":"BCalculator-MCP","description":"Calculadora financiera con MCP server","private":false}' https://api.github.com/user/repos

# Conectar y subir
git remote add origin https://github.com/josersosa/BCalculator-MCP.git
git remote set-url origin https://$TOKEN@github.com/josersosa/BCalculator-MCP.git
git branch -M main
git push -u origin main