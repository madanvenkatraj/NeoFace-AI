#!/bin/bash
# download_models.sh
# Fetches required models for NeoFace AI

mkdir -p ./models
cd ./models

echo "Downloading Inswapper 128 ONNX..."
wget -qnc https://huggingface.co/ezioruan/inswapper_128.onnx/resolve/main/inswapper_128.onnx -O inswapper_128.onnx

echo "Downloading GFPGANv1.4..."
wget -qnc https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth -O GFPGANv1.4.pth

echo "Downloading InsightFace buffalo_l models..."
mkdir -p buffalo_l
cd buffalo_l
wget -qnc https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip
unzip -o buffalo_l.zip
rm buffalo_l.zip
cd ..

echo "All models downloaded successfully!"
