# 🛒 Lista de Compras - Aplicativo Android

Um aplicativo completo de lista de compras desenvolvido em Python com KivyMD, incluindo sistema de lixeira, gerenciamento de produtos, supermercados e carrinhos de compras.

## 📱 Funcionalidades

- ✅ **Gerenciamento de Produtos**: Cadastro completo com tipos, categorias e subcategorias
- ✅ **Supermercados**: Organização por estabelecimentos e bairros
- ✅ **Listas de Compras**: Criação e gestão de múltiplas listas
- ✅ **Carrinhos de Compras**: Associação de listas com supermercados
- ✅ **Sistema de Lixeira**: Recuperação de itens excluídos
- ✅ **Interface Material Design**: Design moderno e intuitivo
- ✅ **Banco de Dados SQLite**: Armazenamento local dos dados

## 🚀 Download do APK

O APK é gerado automaticamente pelo GitHub Actions sempre que há uma atualização no código.

### Como baixar:

1. Vá para a aba **Actions** deste repositório
2. Clique no build mais recente (com ✅)
3. Role para baixo até **Artifacts**
4. Baixe o arquivo `lista-compras-apk`
5. Extraia o arquivo ZIP para obter o APK

### Como instalar no Android:

1. **Ative as Opções do Desenvolvedor**:
   - Vá em Configurações > Sobre o telefone
   - Toque 7 vezes em "Número da versão"

2. **Permita instalação de fontes desconhecidas**:
   - Configurações > Segurança > Fontes desconhecidas (Android antigo)
   - Configurações > Apps > Acesso especial > Instalar apps desconhecidos (Android novo)

3. **Instale o APK**:
   - Transfira o arquivo `.apk` para o celular
   - Toque no arquivo para instalar
   - Confirme a instalação

## 🔧 Desenvolvimento

### Pré-requisitos
- Python 3.10+
- KivyMD 2.0.1.dev0
- Kivy 2.3.1

### Estrutura do Projeto
```
├── apk.py              # Aplicação principal
├── main.py             # Ponto de entrada
├── database_*.py       # Módulos de banco de dados
├── buildozer.spec      # Configuração para build Android
├── compras.db          # Banco de dados SQLite
└── .github/workflows/  # Automação GitHub Actions
```

### Como executar localmente:
```bash
python main.py
```

## 📦 Build Manual

### Linux/macOS:
```bash
chmod +x build_apk_linux.sh
./build_apk_linux.sh
```

### Docker:
```bash
docker build -t lista-compras .
docker run -v $(pwd)/bin:/app/bin lista-compras
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🏗️ Status do Build

![Build Status](https://github.com/[SEU-USUARIO]/[NOME-DO-REPO]/workflows/Build%20Android%20APK/badge.svg)

---

**Desenvolvido com ❤️ usando Python + KivyMD**
