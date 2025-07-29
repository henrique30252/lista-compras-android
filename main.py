#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arquivo principal para executar a aplicação Lista de Compras
Este arquivo serve como ponto de entrada para o Buildozer criar o APK
Versão compatível com KivyMD 1.2.0
"""

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout

class ListaComprasApp(MDApp):
    def build(self):
        self.title = "Lista de Compras"
        self.theme_cls.primary_palette = "Blue"
        
        # Layout principal
        screen = MDScreen()
        layout = MDBoxLayout(
            orientation="vertical",
            padding="20dp",
            spacing="20dp"
        )
        
        # Título
        titulo = MDLabel(
            text="Lista de Compras",
            theme_text_color="Primary",
            size_hint_y=None,
            height="48dp",
            halign="center"
        )
        
        # Mensagem
        mensagem = MDLabel(
            text="Aplicativo funcionando!\nVersão compatível com KivyMD 1.2.0\nEm breve, mais funcionalidades...",
            theme_text_color="Secondary",
            halign="center"
        )
        
        layout.add_widget(titulo)
        layout.add_widget(mensagem)
        screen.add_widget(layout)
        
        return screen

def main():
    """Função principal"""
    ListaComprasApp().run()

if __name__ == "__main__":
    main()
