#!/usr/bin/env bash
set -e

echo "[*] LLM10 Unbounded Consumption Lab setup starting"

# ---- System deps ----
echo "[*] Installing system packages"
sudo apt update
sudo apt install -y curl python3 python3-venv python3-pip

# ---- Ollama ----
if ! command -v ollama >/dev/null; then
  echo "[*] Installing Ollama"
  curl -fsSL https://ollama.com/install.sh | sh
else
  echo "[*] Ollama already installed"
fi

export OLLAMA_NO_GPU=1

# ---- Start Ollama (background) ----
if ! pgrep -x ollama >/dev/null; then
  echo "[*] Starting Ollama"
  nohup ollama serve > ollama.log 2>&1 &
  sleep 3
fi

# ---- Pull model ----
echo "[*] Pulling model qwen2.5:0.5b (once)"
ollama pull qwen2.5:0.5b

# ---- Python app ----
echo "[*] Setting up Python environment"
if [ ! -d venv ]; then
  python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install fastapi uvicorn ollama wikipedia-api requests

# ---- Run app ----
echo "[*] Starting FastAPI app"
echo "[*] Access at: http://$(curl -s ifconfig.me):8000"
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
