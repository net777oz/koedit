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

# 2. stream_server (Node.js - 화면 스트리밍)
echo -e "\n${YELLOW}[2/3]${NC} Stream server deps..."

if [ ! -d "$BASE_DIR/stream_server/node_modules" ]; then
    echo -e "  ${YELLOW}-> npm install in stream_server...${NC}"
    cd "$BASE_DIR/stream_server"
    npm install --silent
    cd "$BASE_DIR"
fi
echo -e "  ${GREEN}OK${NC} stream_server ready"

# 3. Flask (5005) + stream_server (5174) 실행
echo -e "\n${YELLOW}[3/3]${NC} Starting servers..."

# 윈도우 호스트 IP 자동 감지 (TV 접속용)
# ipconfig.exe의 결과에서 인코딩에 상관없이 192. 또는 10. 으로 시작하는 IP 패턴만 추출합니다.
IPCONFIG_EXE="/mnt/c/Windows/system32/ipconfig.exe"
HOST_IP=$($IPCONFIG_EXE | grep -oE '192\.[0-9]+\.[0-9]+\.[0-9]+' | head -n 1)

# 192 대역이 없으면 10 대역 시도
if [ -z "$HOST_IP" ]; then
    HOST_IP=$($IPCONFIG_EXE | grep -oE '10\.[0-9]+\.[0-9]+\.[0-9]+' | head -n 1)
fi

# 그래도 없다면 최후의 보루
if [ -z "$HOST_IP" ]; then
    HOST_IP=$(hostname -I | awk '{print $1}')
fi

fuser -k 5005/tcp 2>/dev/null || true
fuser -k 5174/tcp 2>/dev/null || true
pkill -f "python3.*app.py" 2>/dev/null || true
pkill -f "stream_server/server.js" 2>/dev/null || true
sleep 1

cd "$BASE_DIR"
source "$BASE_DIR/venv/bin/activate"
python3 app.py > "$BASE_DIR/flask.log" 2>&1 &
FLASK_PID=$!
echo -e "  ${GREEN}OK${NC} Flask(5005) started"

echo -e "  ${CYAN}Flask 초기화 대기 중 (3초)...${NC}"
sleep 3

cd "$BASE_DIR/stream_server"
node server.js > "$BASE_DIR/stream.log" 2>&1 &
STREAM_PID=$!
cd "$BASE_DIR"
echo -e "  ${GREEN}OK${NC} Stream server(5174) started"

echo -e "\n${GREEN}=======================================${NC}"
echo -e "${GREEN}  에디터:   ${NC}http://localhost:5005/editor/"
echo -e "${GREEN}  게임:     ${NC}http://localhost:5005/emulator/"
echo -e "${GREEN}  TV 뷰어:  ${NC}http://${HOST_IP}:5005/viewer"
echo -e "\n${YELLOW}  [스마트 TV에서 위 주소로 접속하세요!]${NC}"
echo -e "${GREEN}=======================================${NC}"
echo -e "${CYAN}  로그:     ${NC}tail -f stream.log"
echo ""

cleanup() {
    echo -e "\n${YELLOW}Shutting down...${NC}"
    kill $FLASK_PID 2>/dev/null
    kill $STREAM_PID 2>/dev/null
    echo -e "${GREEN}All servers stopped${NC}"
    exit 0
}
trap cleanup SIGINT SIGTERM

wait $FLASK_PID
cleanup
