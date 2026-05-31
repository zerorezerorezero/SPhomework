#!/bin/bash
# NL 語言解釋器 - 快速啟動腳本

echo "=================================="
echo "NL 編程語言解釋器"
echo "=================================="
echo ""

# 檢查 Python 版本
if ! command -v python3 &> /dev/null; then
    echo "錯誤: 需要安裝 Python 3"
    exit 1
fi

echo "✓ Python 版本: $(python3 --version)"
echo ""

# 如果有參數，執行指定文件
if [ $# -gt 0 ]; then
    echo "執行程序: $1"
    python3 main.py "$1"
else
    echo "启动交互式模式..."
    echo "輸入 '.help' 查看幫助"
    python3 main.py
fi
