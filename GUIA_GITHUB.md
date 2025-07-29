# 🚀 Guia Completo: Como Subir para o GitHub e Gerar APK

## 📋 Pré-requisitos

1. **Conta no GitHub**: Crie em https://github.com se não tiver
2. **Git instalado** no Windows: Baixe em https://git-scm.com/download/win

## 🔧 Passo 1: Instalar Git (se não tiver)

1. Baixe o Git para Windows
2. Instale com as configurações padrão
3. Reinicie o VS Code

## 📁 Passo 2: Criar Repositório no GitHub

1. Acesse https://github.com
2. Clique em **"New repository"** (botão verde)
3. Configure:
   - **Repository name**: `lista-compras-android`
   - **Description**: `Aplicativo de lista de compras para Android`
   - ✅ **Public** (para usar GitHub Actions grátis)
   - ❌ **Add a README file** (já temos um)
   - ❌ **Add .gitignore** (já temos um)
   - ✅ **Choose a license**: MIT
4. Clique em **"Create repository"**

## 💻 Passo 3: Configurar Git Local (no VS Code Terminal)

```bash
# Navegue para a pasta do projeto
cd "c:\Users\Henrique\OneDrive - COPASA\PYTHON\PROGRAMA LISTA DE COMPRAS"

# Configure seu nome e email (primeira vez)
git config --global user.name "Seu Nome"
git config --global user.email "seu.email@exemplo.com"

# Inicializar repositório Git
git init

# Adicionar todos os arquivos
git add .

# Primeiro commit
git commit -m "Primeira versão do aplicativo Lista de Compras"

# Conectar com o repositório do GitHub (substitua SEU-USUARIO)
git remote add origin https://github.com/SEU-USUARIO/lista-compras-android.git

# Enviar para o GitHub
git push -u origin main
```

## 🔄 Passo 4: Aguardar o Build Automático

1. **Acesse seu repositório** no GitHub
2. **Clique na aba "Actions"**
3. **Aguarde o build** (pode demorar 10-20 minutos)
4. **Quando terminar** (✅ verde), clique no build
5. **Role para baixo** até "Artifacts"
6. **Baixe** o arquivo `lista-compras-apk.zip`

## 📱 Passo 5: Instalar no Android

1. **Extraia o arquivo ZIP** baixado
2. **Encontre o arquivo .apk**
3. **Transfira para o celular** (cabo USB, WhatsApp, etc.)
4. **No celular**:
   - Configurações > Segurança > Fontes desconhecidas (✅)
   - Abra o arquivo .apk
   - Toque em "Instalar"

## 🔧 Comandos Úteis para Atualizações

Quando você fizer mudanças no código:

```bash
# Adicionar mudanças
git add .

# Commit com mensagem
git commit -m "Descrição da mudança"

# Enviar para GitHub (dispara novo build)
git push
```

## ❗ Possíveis Problemas e Soluções

### Problema: Git não reconhecido
**Solução**: Instale Git for Windows e reinicie o terminal

### Problema: Build falha no GitHub
**Solução**: Verifique os logs na aba Actions

### Problema: APK não instala
**Solução**: 
- Ative "Fontes desconhecidas"
- Ative "Opções do desenvolvedor"

### Problema: Erro de permissão
**Solução**: Use token do GitHub em vez de senha

## 🎯 Próximos Passos

1. **Execute os comandos** do Passo 3
2. **Aguarde o build** no GitHub Actions
3. **Baixe e teste** o APK
4. **Compartilhe** o link do repositório!

## 📞 Suporte

Se tiver problemas:
1. Verifique os logs no GitHub Actions
2. Copie a mensagem de erro
3. Pesquise no Google ou Stack Overflow

---

**✨ Parabéns! Seu app estará disponível para download em poucos minutos!**
