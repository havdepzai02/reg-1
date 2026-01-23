#!/bin/bash
echo "=== BẮT ĐẦU CHẠY TỰ ĐỘNG ==="
echo "Codespace: $(hostname)"
echo "Thời gian: $(date)"

# Cài đặt requirements nếu có
if [ -f "1.txt" ]; then
    pip install -r 1.txt
fi

# Chạy 1.py với input tự động
echo "Đang chạy 1.py với input tự động..."
(
  sleep 1.5 && echo "1"
  sleep 1.5 && echo "VN" 
  sleep 1.5 && echo "10000"
  sleep 1.5 && echo "hav"
  sleep 1.5 && echo "hav"
  sleep 1.5 && echo "2"
  sleep 1.5 && echo "50"
) | python 1.py

echo "=== KẾT THÚC ==="
