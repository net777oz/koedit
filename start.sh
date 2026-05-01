#!/bin/bash
set -e

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$BASE_DIR"

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}=== Koedit Studio === Uncharted Waters 2 Editor ===${NC}"

# 1. Python venv
echo -e "\n${YELLOW}[1/4]${NC} Python venv..."

if [ ! -d "$BASE_DIR/venv" ]; then
    echo -e "  ${YELLOW}-> Creating venv...${NC}"
    python3 -m venv "$BASE_DIR/venv"
fi

source "$BASE_DIR/venv/bin/activate"
echo -e "  ${GREEN}OK${NC} venv activated ($(python3 --version))"

MISSING=""
python3 -c "import flask" 2>/dev/null || MISSING="$MISSING flask"
python3 -c "import PIL" 2>/dev/null || MISSING="$MISSING pillow"
python3 -c "import bitarray" 2>/dev/null || MISSING="$MISSING bitarray"

if [ -n "$MISSING" ]; then
    echo -e "  ${YELLOW}-> Installing:${NC}$MISSING"
    pip install --quiet $MISSING
    echo -e "  ${GREEN}OK${NC} packages installed"
else
    echo -e "  ${GREEN}OK${NC} all deps ready (Flask, Pillow, bitarray)"
fi

# 3. Flask editor (background)
echo -e "\n${YELLOW}[3/4]${NC} Starting Flask editor (port 5005)..."

# Force kill any process on 5000 or 5005 to be sure
fuser -k 5005/tcp 2>/dev/null || true
pkill -f "python3.*app.py" 2>/dev/null || true
sleep 1

cd "$BASE_DIR"
source "$BASE_DIR/venv/bin/activate"
# Output to flask.log for better debugging
python3 app.py > "$BASE_DIR/flask.log" 2>&1 &
FLASK_PID=$!
echo -e "  ${GREEN}OK${NC} Flask started (PID: $FLASK_PID)"

# 4. Wait for server (foreground)
echo -e "\n${YELLOW}[4/4]${NC} Server running..."
echo -e "\n${GREEN}=======================================${NC}"
echo -e "${GREEN}  Editor:  ${NC}http://localhost:5005/editor/"
echo -e "${GREEN}  Game:    ${NC}http://localhost:5005/emulator/"
echo -e "${GREEN}  Stop:    ${NC}Ctrl+C"
echo -e "${GREEN}=======================================${NC}"
echo -e "${CYAN}  Logs:    ${NC}tail -f flask.log"
echo ""

cleanup() {
    echo -e "\n${YELLOW}Shutting down...${NC}"
    kill $FLASK_PID 2>/dev/null
    echo -e "${GREEN}All servers stopped${NC}"
    exit 0
}
trap cleanup SIGINT SIGTERM


wait $FLASK_PID
cleanup
