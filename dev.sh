#!/usr/bin/env bash
# =============================================================================
# Stay Sidekick — Script de desarrollo (Linux / macOS)
# Levanta 11ty y Angular en paralelo
#
# Uso:
#   chmod +x dev.sh
#   ./dev.sh
# =============================================================================

set -e

BOLD='\033[1m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
YELLOW='\033[0;33m'
RESET='\033[0m'

echo -e "${BOLD}Stay Sidekick — Entorno de desarrollo${RESET}"
echo -e "──────────────────────────────────────────"
echo -e "${CYAN}  Sitio estático (11ty)  →  http://localhost:8080${RESET}"
echo -e "${MAGENTA}  App Angular            →  http://localhost:4200${RESET}"
echo -e "──────────────────────────────────────────"
echo ""

# Instala dependencias si no están presentes
if [ ! -d "node_modules" ]; then
  echo -e "${YELLOW}Instalando dependencias raíz...${RESET}"
  npm install
fi

if [ ! -d "frontend/node_modules" ]; then
  echo -e "${YELLOW}Instalando dependencias de frontend/...${RESET}"
  npm --prefix frontend install
fi

if [ ! -d "web/node_modules" ]; then
  echo -e "${YELLOW}Instalando dependencias de web/...${RESET}"
  npm --prefix web install
fi

echo -e "Levantando servidores con ${BOLD}concurrently${RESET}..."
npm run dev
