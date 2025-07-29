#!/bin/bash
# Script para gerar APK no Linux (usar no GitHub Codespaces ou Ubuntu)

echo "=== Script para gerar APK do Lista de Compras ==="
echo ""

# Instalar dependências do sistema
echo "1. Instalando dependências do sistema..."
sudo apt update
sudo apt install -y python3-pip python3-venv git openjdk-17-jdk
sudo apt install -y build-essential ccache git libncurses5:i386 libstdc++6:i386 libgtk2.0-0:i386
sudo apt install -y libpangox-1.0-0:i386 libpangoxft-1.0-0:i386 libidn11:i386 python3-setuptools
sudo apt install -y libc6-dev libncurses5-dev:i386 libstdc++6-dev:i386 libgtk2.0-dev:i386
sudo apt install -y libgconf2-dev:i386 libxss1:i386 libgconf-2-4:i386 libxml2-dev libxslt1-dev

# Criar ambiente virtual
echo "2. Criando ambiente virtual..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependências Python
echo "3. Instalando dependências Python..."
pip install --upgrade pip
pip install buildozer
pip install python-for-android
pip install kivymd==2.0.1.dev0
pip install kivy[base]==2.3.1

# Configurar variáveis de ambiente
echo "4. Configurando variáveis de ambiente..."
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH
export ANDROID_HOME=$HOME/.buildozer/android/platform/android-sdk
export PATH=$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools:$PATH

# Executar build do APK
echo "5. Executando build do APK..."
buildozer android debug

echo ""
echo "=== Build concluído! ==="
echo "O arquivo APK será gerado em: bin/listacompras-1.0-debug.apk"
echo ""
echo "Para instalar no celular:"
echo "1. Ative 'Opções do desenvolvedor' no Android"
echo "2. Ative 'Instalação de apps desconhecidos'"
echo "3. Transfira o APK para o celular"
echo "4. Instale tocando no arquivo APK"
