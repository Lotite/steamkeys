#!/bin/bash

echo "=== Instalando Google Chrome estable ==="

# Descargar Chrome
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

# Instalar Chrome
sudo apt install -y ./google-chrome-stable_current_amd64.deb

# Limpiar
rm google-chrome-stable_current_amd64.deb

echo "=== Chrome instalado ==="
google-chrome --version

echo "=== Buscando ruta real de Chrome ==="
CHROME_PATH=$(sudo find /opt/google/chrome -type f -name "google-chrome" 2>/dev/null)

if [ -z "$CHROME_PATH" ]; then
    echo "❌ No se encontró Chrome en /opt/google/chrome"
    exit 1
fi

echo "Chrome encontrado en: $CHROME_PATH"

echo "=== Creando enlace simbólico en /usr/bin ==="
sudo ln -sf "$CHROME_PATH" /usr/bin/google-chrome

echo "=== Verificando PATH ==="
which google-chrome

echo "=== Instalando unzip (si no existe) ==="
sudo apt install -y unzip

echo "=== Instalación completada ==="
echo "Chrome está listo para usarse con undetected-chromedriver."