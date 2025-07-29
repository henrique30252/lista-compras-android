# Dockerfile para gerar APK em ambiente controlado
FROM ubuntu:22.04

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    openjdk-17-jdk \
    build-essential \
    ccache \
    libncurses5:i386 \
    libstdc++6:i386 \
    libgtk2.0-0:i386 \
    libpangox-1.0-0:i386 \
    libpangoxft-1.0-0:i386 \
    libidn11:i386 \
    python3-setuptools \
    libc6-dev \
    libncurses5-dev:i386 \
    libstdc++6-dev:i386 \
    libgtk2.0-dev:i386 \
    libgconf2-dev:i386 \
    libxss1:i386 \
    libgconf-2-4:i386 \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

# Configurar variáveis de ambiente
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

# Criar diretório de trabalho
WORKDIR /app

# Copiar arquivos do projeto
COPY . .

# Criar ambiente virtual e instalar dependências
RUN python3 -m venv venv && \
    . venv/bin/activate && \
    pip install --upgrade pip && \
    pip install buildozer python-for-android kivymd==2.0.1.dev0 kivy[base]==2.3.1

# Comando para executar o build
CMD ["/bin/bash", "-c", ". venv/bin/activate && buildozer android debug"]
