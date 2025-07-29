# Instruções para gerar APK usando serviços online

## MÉTODO 1: GitHub Actions (Recomendado)

1. Criar repositório no GitHub com seu código
2. Adicionar arquivo `.github/workflows/build-apk.yml`:

```yml
name: Build APK

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
        
    - name: Install system dependencies
      run: |
        sudo apt update
        sudo apt install -y openjdk-17-jdk
        
    - name: Install Python dependencies
      run: |
        python -m pip install --upgrade pip
        pip install buildozer python-for-android kivymd==2.0.1.dev0
        
    - name: Build APK
      run: |
        buildozer android debug
        
    - name: Upload APK
      uses: actions/upload-artifact@v3
      with:
        name: apk
        path: bin/*.apk
```

## MÉTODO 2: GitPod (Online IDE)

1. Acesse https://gitpod.io
2. Abra seu repositório GitHub no GitPod
3. Execute os comandos Linux do script build_apk_linux.sh

## MÉTODO 3: Replit (Alternativa simples)

1. Acesse https://replit.com
2. Crie um novo projeto Python
3. Faça upload dos arquivos
4. Execute o build (pode ter limitações)

## MÉTODO 4: Kivy.org Build Service (Pago)

- https://kivymd.readthedocs.io/en/latest/getting-started/
- Serviço oficial para builds em cloud

## Como usar o GitHub Actions:

1. Crie repositório no GitHub
2. Faça push do código
3. Adicione o workflow file
4. O APK será gerado automaticamente
5. Baixe o APK dos artifacts
