#!/bin/bash
set -e

echo "=== BẮT ĐẦU CHẠY TỰ ĐỘNG ==="
echo "Codespace: $(hostname)"
echo "Thời gian: $(date)"

# Cài requirements nếu có
if [ -f "1.txt" ]; then
    pip install -r 1.txt
fi

echo "Đang chạy 1.py với input tự động..."

(
  sleep 1.5 && echo "1"
  sleep 1.5 && echo "VN"
  sleep 1.5 && echo "10000"
  sleep 1.5 && echo "hav"
  sleep 1.5 && echo "hav"
  sleep 1.5 && echo "2"
  sleep 1.5 && echo "50"
) | python 1.py > run.log 2>&1 &

PY_PID=$!
START_TIME=$(date +%s)

echo "Python PID: $PY_PID"
echo "Keep-alive: 30 phút"

# ===== GIỮ SỐNG 30 PHÚT =====
while kill -0 $PY_PID 2>/dev/null; do
    NOW=$(date +%s)
    ELAPSED=$((NOW - START_TIME))

    if [ $ELAPSED -ge 1800 ]; then
        echo "[TIMEOUT] Đủ 30 phút, dừng keep-alive"
        break
    fi

    echo "[KEEPALIVE] $(date) - ${ELAPSED}s" >> keepalive.log
    sleep 300   # 5 phút
done

echo "=== KẾT THÚC ==="
