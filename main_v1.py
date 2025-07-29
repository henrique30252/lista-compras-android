#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lista de Compras - Versão compatível com KivyMD 1.2.0
Aplicativo Android para gerenciamento de listas de compras
"""

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.list import OneLineListItem, TwoLineListItem, MDList, OneLineIconListItem
from kivymd.uix.divider import MDDivider  
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.bottomsheet import MDBottomSheet
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.navigationdrawer import (
    MDNavigationLayout, MDNavigationDrawer, MDNavigationDrawerItem
)

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.logger import Logger
from datetime import datetime
import sqlite3
import os
import sys

# Importar módulo de banco de dados compatível
try:
    from database_apk import DatabaseManager
except ImportError:
    from database import DatabaseManager

class ListaComprasApp(MDApp):
    """Aplicativo principal - Lista de Compras"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Lista de Compras"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        
        # Inicializar banco de dados
        self.db = DatabaseManager()
        
        # Histórico de navegação para sistema de voltar
        self.historico_navegacao = []
        self.loading_snackbar = None
        
        Logger.info("ListaCompras: App inicializado")
    
    def build(self):
        """Construir interface do aplicativo"""
        try:
            # Screen Manager
            self.screen_manager = MDScreenManager()
            
            # Tela principal
            self.tela_principal = self.criar_tela_principal()
            self.screen_manager.add_widget(self.tela_principal)
            
            # Outras telas
            self.criar_demais_telas()
            
            Logger.info("ListaCompras: Interface construída com sucesso")
            return self.screen_manager
            
        except Exception as e:
            Logger.error(f"ListaCompras: Erro ao construir interface: {e}")
            return MDLabel(text=f"Erro ao inicializar: {e}")
    
    def criar_tela_principal(self):
        """Criar tela principal do aplicativo"""
        screen = MDScreen(name="menu_principal")
        
        # Layout principal
        layout = MDBoxLayout(
            orientation="vertical",
            md_bg_color=self.theme_cls.bg_light
        )
        
        # TopAppBar
        toolbar = MDTopAppBar(
            title="Lista de Compras",
            elevation=4
        )
        layout.add_widget(toolbar)
        
        # Conteúdo principal
        content = self.criar_menu_principal()
        layout.add_widget(content)
        
        screen.add_widget(layout)
        return screen
    
    def criar_menu_principal(self):
        """Criar menu principal com opções"""
        scroll = MDScrollView()
        
        lista = MDList()
        
        # Opções do menu
        opcoes = [
            ("Produtos", "shopping", self.ir_para_produtos),
            ("Categorias", "tag", self.ir_para_categorias),
            ("Listas de Compras", "format-list-bulleted", self.ir_para_listas),
            ("Lixeira", "delete", self.ir_para_lixeira),
        ]
        
        for titulo, icone, callback in opcoes:
            item = OneLineIconListItem(
                text=titulo,
                on_release=callback
            )
            lista.add_widget(item)
        
        scroll.add_widget(lista)
        return scroll
    
    def criar_demais_telas(self):
        """Criar outras telas do aplicativo"""
        # Tela de produtos
        self.screen_manager.add_widget(self.criar_tela_produtos())
        
        # Tela de categorias
        self.screen_manager.add_widget(self.criar_tela_categorias())
        
        # Tela de listas
        self.screen_manager.add_widget(self.criar_tela_listas())
        
        # Tela de lixeira
        self.screen_manager.add_widget(self.criar_tela_lixeira())
    
    def criar_tela_produtos(self):
        """Criar tela de produtos"""
        screen = MDScreen(name="produtos")
        
        layout = MDBoxLayout(orientation="vertical")
        
        # Toolbar
        toolbar = MDTopAppBar(
            title="Produtos",
            left_action_items=[["arrow-left", lambda x: self.voltar_tela()]],
            right_action_items=[["plus", lambda x: self.adicionar_produto()]]
        )
        layout.add_widget(toolbar)
        
        # Lista de produtos
        self.scroll_produtos = MDScrollView()
        self.lista_produtos = MDList()
        self.scroll_produtos.add_widget(self.lista_produtos)
        layout.add_widget(self.scroll_produtos)
        
        screen.add_widget(layout)
        return screen
    
    def criar_tela_categorias(self):
        """Criar tela de categorias"""
        screen = MDScreen(name="categorias")
        
        layout = MDBoxLayout(orientation="vertical")
        
        # Toolbar
        toolbar = MDTopAppBar(
            title="Categorias",
            left_action_items=[["arrow-left", lambda x: self.voltar_tela()]],
            right_action_items=[["plus", lambda x: self.adicionar_categoria()]]
        )
        layout.add_widget(toolbar)
        
        # Lista de categorias
        self.scroll_categorias = MDScrollView()
        self.lista_categorias = MDList()
        self.scroll_categorias.add_widget(self.lista_categorias)
        layout.add_widget(self.scroll_categorias)
        
        screen.add_widget(layout)
        return screen
    
    def criar_tela_listas(self):
        """Criar tela de listas de compras"""
        screen = MDScreen(name="listas")
        
        layout = MDBoxLayout(orientation="vertical")
        
        # Toolbar
        toolbar = MDTopAppBar(
            title="Listas de Compras",
            left_action_items=[["arrow-left", lambda x: self.voltar_tela()]],
            right_action_items=[["plus", lambda x: self.criar_lista()]]
        )
        layout.add_widget(toolbar)
        
        # Lista de listas
        self.scroll_listas = MDScrollView()
        self.lista_listas = MDList()
        self.scroll_listas.add_widget(self.lista_listas)
        layout.add_widget(self.scroll_listas)
        
        screen.add_widget(layout)
        return screen
    
    def criar_tela_lixeira(self):
        """Criar tela de lixeira"""
        screen = MDScreen(name="lixeira")
        
        layout = MDBoxLayout(orientation="vertical")
        
        # Toolbar
        toolbar = MDTopAppBar(
            title="Lixeira",
            left_action_items=[["arrow-left", lambda x: self.voltar_tela()]],
            right_action_items=[["delete-sweep", lambda x: self.limpar_lixeira()]]
        )
        layout.add_widget(toolbar)
        
        # Lista da lixeira
        self.scroll_lixeira = MDScrollView()
        self.lista_lixeira = MDList()
        self.scroll_lixeira.add_widget(self.lista_lixeira)
        layout.add_widget(self.scroll_lixeira)
        
        screen.add_widget(layout)
        return screen
    
    # Métodos de navegação
    def ir_para_produtos(self, *args):
        """Navegar para tela de produtos"""
        self.navegacao_com_historico("produtos", "Produtos")
        self.carregar_produtos()
    
    def ir_para_categorias(self, *args):
        """Navegar para tela de categorias"""
        self.navegacao_com_historico("categorias", "Categorias")
        self.carregar_categorias()
    
    def ir_para_listas(self, *args):
        """Navegar para tela de listas"""
        self.navegacao_com_historico("listas", "Listas de Compras")
        self.carregar_listas()
    
    def ir_para_lixeira(self, *args):
        """Navegar para tela de lixeira"""
        self.navegacao_com_historico("lixeira", "Lixeira")
        self.carregar_lixeira()
    
    def navegacao_com_historico(self, tela, titulo):
        """Navegar mantendo histórico"""
        # Adicionar tela atual ao histórico
        tela_atual = self.screen_manager.current
        if tela_atual != tela:  # Evitar duplicatas
            self.historico_navegacao.append(tela_atual)
            # Manter histórico limitado
            if len(self.historico_navegacao) > 10:
                self.historico_navegacao.pop(0)
        
        self.screen_manager.current = tela
        Logger.info(f"ListaCompras: Navegando para {tela} - {titulo}")
    
    def voltar_tela(self, *args):
        """Voltar para tela anterior usando histórico"""
        if self.historico_navegacao:
            tela_anterior = self.historico_navegacao.pop()
            self.screen_manager.current = tela_anterior
            Logger.info(f"ListaCompras: Voltando para {tela_anterior}")
        else:
            self.screen_manager.current = "menu_principal"
            Logger.info("ListaCompras: Voltando para menu principal")
    
    # Métodos de carregamento de dados
    def carregar_produtos(self):
        """Carregar lista de produtos"""
        self.mostrar_loading("Carregando produtos...")
        
        try:
            produtos = self.db.obter_produtos()
            self.lista_produtos.clear_widgets()
            
            for produto in produtos:
                item = TwoLineListItem(
                    text=produto['nome'],
                    secondary_text=f"Categoria: {produto.get('categoria', 'Sem categoria')}"
                )
                self.lista_produtos.add_widget(item)
            
            self.ocultar_loading()
            self.mostrar_sucesso(f"{len(produtos)} produtos carregados")
            
        except Exception as e:
            self.ocultar_loading()
            self.mostrar_erro(f"Erro ao carregar produtos: {e}")
            Logger.error(f"ListaCompras: Erro ao carregar produtos: {e}")
    
    def carregar_categorias(self):
        """Carregar lista de categorias"""
        self.mostrar_loading("Carregando categorias...")
        
        try:
            categorias = self.db.obter_categorias()
            self.lista_categorias.clear_widgets()
            
            for categoria in categorias:
                item = OneLineListItem(text=categoria['nome'])
                self.lista_categorias.add_widget(item)
            
            self.ocultar_loading()
            self.mostrar_sucesso(f"{len(categorias)} categorias carregadas")
            
        except Exception as e:
            self.ocultar_loading()
            self.mostrar_erro(f"Erro ao carregar categorias: {e}")
            Logger.error(f"ListaCompras: Erro ao carregar categorias: {e}")
    
    def carregar_listas(self):
        """Carregar listas de compras"""
        self.mostrar_loading("Carregando listas...")
        
        try:
            listas = self.db.obter_listas_compras()
            self.lista_listas.clear_widgets()
            
            for lista in listas:
                item = TwoLineListItem(
                    text=lista['nome'],
                    secondary_text=f"Criada em: {lista.get('data_criacao', 'N/A')}"
                )
                self.lista_listas.add_widget(item)
            
            self.ocultar_loading()
            self.mostrar_sucesso(f"{len(listas)} listas carregadas")
            
        except Exception as e:
            self.ocultar_loading()
            self.mostrar_erro(f"Erro ao carregar listas: {e}")
            Logger.error(f"ListaCompras: Erro ao carregar listas: {e}")
    
    def carregar_lixeira(self):
        """Carregar itens da lixeira"""
        self.mostrar_loading("Carregando lixeira...")
        
        try:
            itens = self.db.obter_itens_lixeira()
            self.lista_lixeira.clear_widgets()
            
            for item in itens:
                list_item = TwoLineListItem(
                    text=item['nome'],
                    secondary_text=f"Excluído em: {item.get('data_exclusao', 'N/A')}"
                )
                self.lista_lixeira.add_widget(list_item)
            
            self.ocultar_loading()
            self.mostrar_sucesso(f"{len(itens)} itens na lixeira")
            
        except Exception as e:
            self.ocultar_loading()
            self.mostrar_erro(f"Erro ao carregar lixeira: {e}")
            Logger.error(f"ListaCompras: Erro ao carregar lixeira: {e}")
    
    # Métodos de feedback para o usuário
    def mostrar_snackbar(self, texto, duracao=2):
        """Mostrar snackbar básico"""
        try:
            snackbar = Snackbar(text=texto, duration=duracao)
            snackbar.open()
        except Exception as e:
            Logger.error(f"ListaCompras: Erro ao mostrar snackbar: {e}")
    
    def mostrar_sucesso(self, texto):
        """Mostrar notificação de sucesso"""
        self.mostrar_snackbar(f"✅ {texto}", 2)
        Logger.info(f"ListaCompras: Sucesso - {texto}")
    
    def mostrar_erro(self, texto):
        """Mostrar notificação de erro"""
        self.mostrar_snackbar(f"❌ {texto}", 4)
        Logger.error(f"ListaCompras: Erro - {texto}")
    
    def mostrar_aviso(self, texto):
        """Mostrar notificação de aviso"""
        self.mostrar_snackbar(f"⚠️ {texto}", 3)
        Logger.warning(f"ListaCompras: Aviso - {texto}")
    
    def mostrar_info(self, texto):
        """Mostrar notificação informativa"""
        self.mostrar_snackbar(f"ℹ️ {texto}", 2)
        Logger.info(f"ListaCompras: Info - {texto}")
    
    def mostrar_loading(self, texto="Carregando..."):
        """Mostrar indicador de carregamento"""
        try:
            # Remover loading anterior se existir
            if self.loading_snackbar:
                self.loading_snackbar.dismiss()
            
            self.loading_snackbar = Snackbar(
                text=f"⏳ {texto}",
                duration=-1  # Permanente até ser removido
            )
            self.loading_snackbar.open()
            
        except Exception as e:
            Logger.error(f"ListaCompras: Erro ao mostrar loading: {e}")
    
    def ocultar_loading(self):
        """Ocultar indicador de carregamento"""
        try:
            if self.loading_snackbar:
                self.loading_snackbar.dismiss()
                self.loading_snackbar = None
        except Exception as e:
            Logger.error(f"ListaCompras: Erro ao ocultar loading: {e}")
    
    # Métodos de ação (placeholders para funcionalidades futuras)
    def adicionar_produto(self, *args):
        """Adicionar novo produto"""
        self.mostrar_info("Funcionalidade em desenvolvimento")
    
    def adicionar_categoria(self, *args):
        """Adicionar nova categoria"""
        self.mostrar_info("Funcionalidade em desenvolvimento")
    
    def criar_lista(self, *args):
        """Criar nova lista de compras"""
        self.mostrar_info("Funcionalidade em desenvolvimento")
    
    def limpar_lixeira(self, *args):
        """Limpar todos os itens da lixeira"""
        self.mostrar_info("Funcionalidade em desenvolvimento")

def main():
    """Função principal para executar o aplicativo"""
    try:
        Logger.info("ListaCompras: Iniciando aplicativo...")
        app = ListaComprasApp()
        app.run()
    except Exception as e:
        Logger.error(f"ListaCompras: Erro crítico ao iniciar: {e}")
        print(f"Erro ao iniciar aplicativo: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
