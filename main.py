#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arquivo principal para executar a aplicação Lista de Compras
Este arquivo serve como ponto de entrada para o Buildozer criar o APK
"""

if __name__ == '__main__':
    # Importa e executa a aplicação principal
    from apk import Example
    
    # Cria e executa a aplicação
    app = Example()
    app.run()
