# ⚡ INSTRUÇÕES RÁPIDAS - GERAR APK

## 🎯 O que você precisa fazer AGORA:

### 1️⃣ **Instalar Git** (se não tiver):
- Baixe: https://git-scm.com/download/win
- Instale com configurações padrão
- Reinicie o VS Code

### 2️⃣ **Criar repositório GitHub**:
- Acesse: https://github.com
- Clique "New repository"
- Nome: `lista-compras-android`
- Público ✅
- Create repository

### 3️⃣ **Executar comandos no terminal VS Code**:
```bash
cd "c:\Users\Henrique\OneDrive - COPASA\PYTHON\PROGRAMA LISTA DE COMPRAS"
git config --global user.name "Seu Nome Aqui"
git config --global user.email "seuemail@exemplo.com"
git init
git add .
git commit -m "Primeira versão do app"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/lista-compras-android.git
git push -u origin main
```

### 4️⃣ **Aguardar build no GitHub**:
- Vá na aba "Actions" do seu repositório
- Aguarde build terminar (✅ verde)
- Baixe o APK dos "Artifacts"

### 5️⃣ **Instalar no celular**:
- Ative "Fontes desconhecidas" no Android
- Instale o arquivo .apk

---

## ✅ **ARQUIVOS PRONTOS**:
- ✅ main.py (ponto de entrada)
- ✅ buildozer.spec (configuração Android)
- ✅ .github/workflows/build-apk.yml (automação)
- ✅ README.md (documentação)
- ✅ requirements.txt (dependências)
- ✅ .gitignore (arquivos ignorados)

## 🚀 **RESULTADO**: 
Em 20-30 minutos você terá um APK funcionando!

---

**Dúvidas? Leia o GUIA_GITHUB.md completo**
