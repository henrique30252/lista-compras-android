from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.navigationdrawer import (
    MDNavigationLayout, MDNavigationDrawer, MDNavigationDrawerMenu,
    MDNavigationDrawerLabel, MDNavigationDrawerItem, MDNavigationDrawerItemLeadingIcon,
    MDNavigationDrawerItemText, MDNavigationDrawerDivider
)
from kivymd.uix.appbar import (
    MDTopAppBar, MDTopAppBarLeadingButtonContainer, MDActionTopAppBarButton,
    MDTopAppBarTitle, MDTopAppBarTrailingButtonContainer
)
from kivymd.uix.list import MDListItem, MDListItemHeadlineText, MDListItemSupportingText, MDList
from kivymd.uix.divider import MDDivider
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dropdownitem import MDDropDownItem, MDDropDownItemText
from kivymd.uix.bottomsheet import MDBottomSheet
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogSupportingText, MDDialogButtonContainer
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.card import MDCard

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.animation import Animation

# Imports padrão do Python
import json
import logging
import sys
import time
import unicodedata
from datetime import datetime

from database_apk import (
    listar_produtos_apk, excluir_produto_apk, listar_historico_precos_apk,
    listar_supermercados_apk, excluir_supermercado_apk, cadastrar_supermercado_apk,
    listar_categorias_apk, listar_subcategorias_apk, alterar_supermercado_apk,
    cadastrar_lista_apk, listar_listas_apk, alterar_lista_apk, excluir_lista_apk,
    listar_itens_lista_apk, adicionar_item_lista_apk, editar_item_lista_apk, excluir_item_lista_apk,
    listar_tipos_produto_apk, cadastrar_tipo_produto_apk, cadastrar_produto_apk, alterar_produto_apk,
    listar_carrinhos_apk, cadastrar_carrinho_apk, alterar_carrinho_apk, excluir_carrinho_apk,
    alterar_tipo_produto_apk, excluir_tipo_produto_apk,
    listar_itens_carrinho_apk, adicionar_item_carrinho_apk, editar_item_carrinho_apk, excluir_item_carrinho_apk
)

# Configurações da aplicação
class Config:
    CACHE_TIMEOUT = 300  # 5 minutos
    MAX_ITEMS_POR_PAGINA = 100
    TIMEOUT_SNACKBAR = 3

# Índices dos campos no banco de dados
class DatabaseFields:
    PRODUTO_ID = 0
    PRODUTO_TIPO_ID = 1
    PRODUTO_NOME = 2
    PRODUTO_MARCA = 3
    PRODUTO_QUANTIDADE_EMBALAGEM = 4
    PRODUTO_CODIGO_BARRAS = 5
    PRODUTO_CATEGORIA_ID = 6
    PRODUTO_SUBCATEGORIA_ID = 7
    PRODUTO_IMAGEM = 8

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Classe customizada para itens com swipe usando MDListItem
class SwipeableListItem(MDListItem):
    """Item de lista com funcionalidade de swipe"""
    
    def __init__(self, *args, item_data=None, on_swipe_left=None, on_swipe_right=None, **kwargs):
        # Extrai parâmetros específicos do swipe
        self.item_data = item_data
        self.on_swipe_left = on_swipe_left
        self.on_swipe_right = on_swipe_right
        
        # Chama construtor pai com argumentos restantes
        super().__init__(*args, **kwargs)
        
        # Configurações de swipe otimizadas
        self.swipe_threshold = dp(50)  # Reduzido de 80 para 50
        self.touch_start_x = 0
        self.touch_start_time = 0  # Para detectar toque rápido
        self.is_swiping = False
        self.original_x = 0
        
        # Cores de feedback mais suaves
        self.left_action_color = [1, 0.3, 0.3, 0.7]   # Vermelho
        self.right_action_color = [0.3, 1, 0.3, 0.7]  # Verde
        
        logger.info(f"SwipeableListItem criado para {item_data.get('tipo_nome', 'Unknown') if item_data else 'Unknown'}")
        
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # Verifica se o toque foi em um checkbox
            for child in self.walk():
                if hasattr(child, '__class__') and child.__class__.__name__ == 'MDCheckbox':
                    if child.collide_point(*touch.pos):
                        # Permite que o checkbox processe o evento
                        logger.info(f"Touch no checkbox de: {self.item_data.get('tipo_nome', 'Unknown') if self.item_data else 'Unknown'}")
                        return super().on_touch_down(touch)
            
            # Se não foi no checkbox, inicia o swipe
            logger.info(f"Touch down em: {self.item_data.get('tipo_nome', 'Unknown') if self.item_data else 'Unknown'}")
            self.touch_start_x = touch.x
            self.touch_start_time = time.time()  # Marca tempo do toque
            self.original_x = self.x
            self.is_swiping = True
            touch.grab(self)
            return True
        return super().on_touch_down(touch)
    
    def on_touch_move(self, touch):
        if touch.grab_current is self and self.is_swiping:
            dx = touch.x - self.touch_start_x
            
            # Só ativa swipe após movimento mínimo (evita ativação acidental)
            if abs(dx) < dp(10):
                return True
                
            logger.info(f"Swipe detectado: dx={dx}")
            
            # Limita movimento para 20% da largura
            max_swipe = self.width * 0.2
            dx = max(-max_swipe, min(max_swipe, dx))
            
            # Move o item
            self.x = self.original_x + dx
            
            # Feedback visual mais responsivo
            threshold_visual = self.swipe_threshold * 0.3  # 30% do threshold para feedback
            if dx < -threshold_visual:
                self.md_bg_color = self.left_action_color
            elif dx > threshold_visual:
                self.md_bg_color = self.right_action_color
            else:
                self.md_bg_color = [0, 0, 0, 0]
            
            return True
        return super().on_touch_move(touch)
    
    def on_touch_up(self, touch):
        if touch.grab_current is self and self.is_swiping:
            dx = touch.x - self.touch_start_x
            touch_duration = time.time() - self.touch_start_time
            
            logger.info(f"Touch up: dx={dx}, duration={touch_duration:.2f}s, threshold={self.swipe_threshold}")
            
            # Ações de swipe com threshold reduzido
            action_executed = False
            if dx < -self.swipe_threshold and self.on_swipe_left:
                logger.info("Executando SWIPE LEFT (excluir)")
                self.on_swipe_left(self.item_data)
                action_executed = True
            elif dx > self.swipe_threshold and self.on_swipe_right:
                logger.info("Executando SWIPE RIGHT (editar)")
                self.on_swipe_right(self.item_data)
                action_executed = True
            
            if not action_executed:
                logger.info(f"Swipe insuficiente (threshold: {self.swipe_threshold}dp)")
            
            # Animação mais rápida de retorno
            anim = Animation(
                x=self.original_x, 
                md_bg_color=[0, 0, 0, 0], 
                duration=0.15  # Reduzido de 0.2 para 0.15
            )
            anim.start(self)
            
            self.is_swiping = False
            touch.ungrab(self)
            return True
        return super().on_touch_up(touch)

class Example(MDApp):
    def __init__(self):
        super().__init__()
        self.filtro_ativo = False
        # Cache inteligente
        self._cache_produtos = {}
        self._cache_timestamp = {}
        self._cache_timeout = Config.CACHE_TIMEOUT
        # Referencias de checkbox mais robustas
        self.checkbox_refs = []
        self.super_checkbox_refs = []
        self.listas_checkbox_refs = []
        self.itens_checkbox_refs = []
        self.carrinhos_checkbox_refs = []
        self.tipos_checkbox_refs = []

    def build(self):
        logger.info("Iniciando aplicação Lista de Compras")
        
        # Inicializa sistema de lixeira
        self.inicializar_lixeira()
        
        # Executa migrações necessárias
        self.executar_migracoes()
        
        # --- Telas principais ---
        main_layout_produtos = self.criar_tela_produtos()
        main_layout_supermercados = self.criar_tela_supermercados()
        main_layout_listas = self.criar_tela_listas()
        main_layout_carrinhos = self.criar_tela_carrinhos()
        main_layout_categorias = self.criar_tela_categorias_tipos()

        # --- ScreenManager com as telas principais ---
        self.screen_manager = MDScreenManager(
            self.criar_tela_inicial(),
            MDScreen(main_layout_produtos, name="produtos"),
            MDScreen(main_layout_supermercados, name="supermercados"),
            MDScreen(main_layout_listas, name="listas"),
            MDScreen(main_layout_carrinhos, name="carrinhos"),
            MDScreen(main_layout_categorias, name="categorias"),
        )
        self.screen_manager.current = "inicial"

        # --- Menu lateral (Navigation Drawer) ---
        nav_drawer = self.criar_menu_lateral()

        # --- Retorno da tela principal ---
        return MDScreen(
            MDNavigationLayout(
                self.screen_manager,
                nav_drawer,
            ),
            md_bg_color=self.theme_cls.secondaryContainerColor,
        )

    # --- Cache inteligente ---
    def get_produtos_cached(self):
        """Cache inteligente para produtos"""
        current_time = time.time()
        
        if ('produtos' not in self._cache_produtos or 
            current_time - self._cache_timestamp.get('produtos', 0) > self._cache_timeout):
            
            logger.info("Atualizando cache de produtos")
            self._cache_produtos['produtos'] = listar_produtos_apk()
            self._cache_timestamp['produtos'] = current_time
        
        return self._cache_produtos['produtos']

    def invalidar_cache(self, tipo=None):
        """Invalida cache quando dados são alterados"""
        if tipo:
            self._cache_produtos.pop(tipo, None)
            self._cache_timestamp.pop(tipo, None)
            logger.info(f"Cache invalidado para: {tipo}")
        else:
            self._cache_produtos.clear()
            self._cache_timestamp.clear()
            logger.info("Cache completo invalidado")

    def produto_existe(self, produto_id):
        """Verifica se produto existe no banco"""
        try:
            produtos = self.get_produtos_cached()
            return any(p[DatabaseFields.PRODUTO_ID] == produto_id for p in produtos)
        except Exception as e:
            logger.error(f"Erro ao verificar existência do produto {produto_id}: {e}")
            return False

    def produto_match_filtro(self, produto, filtro_norm):
        """Verifica se produto corresponde ao filtro - busca em todos os campos"""
        # Busca nos campos diretos do produto (todos os campos)
        for campo in produto:
            if campo is not None and filtro_norm in self.normalizar_texto(str(campo)):
                return True
        return False

    # --- Gerenciamento robusto de referências ---
    def limpar_referencias_checkbox(self, tipo_lista='produtos'):
        """Limpa referências órfãs de checkboxes"""
        try:
            if tipo_lista == 'produtos':
                lista_refs = self.checkbox_refs
            elif tipo_lista == 'supermercados':
                lista_refs = self.super_checkbox_refs
            elif tipo_lista == 'listas':
                lista_refs = self.listas_checkbox_refs
            elif tipo_lista == 'itens':
                lista_refs = self.itens_checkbox_refs
            elif tipo_lista == 'carrinhos':
                lista_refs = self.carrinhos_checkbox_refs
            elif tipo_lista == 'tipos':
                lista_refs = self.tipos_checkbox_refs
            elif tipo_lista == 'lixeira':
                lista_refs = getattr(self, 'lixeira_checkbox_refs', [])
            else:
                return

            refs_validas = []
            
            # Trata especificamente a lixeira que tem 3 elementos por referência
            if tipo_lista == 'lixeira':
                for checkbox, item_id, tipo_item in lista_refs:
                    if checkbox.parent:  # Só mantém se ainda está na tela
                        refs_validas.append((checkbox, item_id, tipo_item))
            else:
                for checkbox, item_id in lista_refs:
                    if checkbox.parent:  # Só mantém se ainda está na tela
                        refs_validas.append((checkbox, item_id))
            
            if tipo_lista == 'produtos':
                self.checkbox_refs = refs_validas
            elif tipo_lista == 'supermercados':
                self.super_checkbox_refs = refs_validas
            elif tipo_lista == 'listas':
                self.listas_checkbox_refs = refs_validas
            elif tipo_lista == 'itens':
                self.itens_checkbox_refs = refs_validas
            elif tipo_lista == 'carrinhos':
                self.carrinhos_checkbox_refs = refs_validas
            elif tipo_lista == 'tipos':
                self.tipos_checkbox_refs = refs_validas
            elif tipo_lista == 'lixeira':
                self.lixeira_checkbox_refs = refs_validas

        except Exception as e:
            logger.error(f"Erro ao limpar referências de {tipo_lista}: {e}")

    def remover_tela_segura(self, screen_name):
        """Remove tela de forma segura"""
        try:
            if self.screen_manager.has_screen(screen_name):
                screen = self.screen_manager.get_screen(screen_name)
                self.screen_manager.remove_widget(screen)
                # Limpa referências se necessário
                if hasattr(screen, 'cleanup'):
                    screen.cleanup()
                logger.info(f"Tela {screen_name} removida com sucesso")
        except Exception as e:
            logger.error(f"Erro ao remover tela {screen_name}: {e}")

    # --- Tela inicial ---
    def criar_tela_inicial(self):
        appbar = MDTopAppBar(
            MDTopAppBarLeadingButtonContainer(
                MDActionTopAppBarButton(
                    icon="menu",
                    on_release=lambda x: self.root.get_ids().nav_drawer.set_state("toggle"),
                ),
            ),
            MDTopAppBarTitle(
                text="Bem-vindo!",
                halign="center",
            ),
            type="small",
            size_hint_y=None,
            height=dp(64),
        )
        label = MDLabel(
            text="Bem-vindo ao aplicativo Lista de Compras!\nSelecione uma opção no menu lateral.",
            halign="center",
            theme_text_color="Primary",
            size_hint_y=1,
            padding=(dp(16), dp(16)),
        )
        layout = BoxLayout(orientation="vertical")
        layout.add_widget(appbar)
        layout.add_widget(label)
        return MDScreen(layout, name="inicial")

    # --- Tela de Produtos ---
    def criar_tela_produtos(self):
        # Inicializa lista e referências de checkboxes
        self.md_list = MDList()
        self.checkbox_refs = []

        # --- Barra de filtro ---
        filtro_box = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(56),
            padding=(dp(16), dp(8), dp(16), dp(8)),
            spacing=dp(8)
        )
        
        self.filtro_texto_produto = MDTextField(
            hint_text="Filtrar produtos",
            size_hint_x=0.7,
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            pos_hint={"center_y": 0.5},
            on_text_validate=self.aplicar_filtro_texto_produto
        )
        
        btn_filtrar = MDActionTopAppBarButton(
            icon="filter",
            on_release=self.aplicar_filtro_texto_produto,
            size_hint_y=None,
            height=dp(40),
        )
        btn_limpar = MDActionTopAppBarButton(
            icon="close",
            on_release=self.limpar_filtro_texto_produto,
            size_hint_y=None,
            height=dp(40),
        )
        self.btn_exibir_selecionados = MDActionTopAppBarButton(
            icon="eye",
            on_release=self.exibir_selecionados_produtos,
            size_hint_y=None,
            height=dp(40),
        )
        self.btn_limpar_selecao = MDActionTopAppBarButton(
            icon="selection-remove",
            on_release=self.limpar_selecao_produtos,
            size_hint_y=None,
            height=dp(40),
        )
        
        filtro_box.add_widget(self.filtro_texto_produto)
        filtro_box.add_widget(btn_filtrar)
        filtro_box.add_widget(btn_limpar)
        filtro_box.add_widget(self.btn_exibir_selecionados)
        filtro_box.add_widget(self.btn_limpar_selecao)

        # --- AppBar (barra superior) ---
        appbar_produtos = MDTopAppBar(
            MDTopAppBarLeadingButtonContainer(
                MDActionTopAppBarButton(
                    icon="menu",
                    on_release=lambda x: self.root.get_ids().nav_drawer.set_state("toggle"),
                ),
            ),
            MDTopAppBarTitle(
                text="Produtos",
                halign="center",
            ),
            MDTopAppBarTrailingButtonContainer(
                MDActionTopAppBarButton(
                    icon="plus",
                    on_release=self.show_cadastro_produto_dialog,
                ),
                MDActionTopAppBarButton(
                    icon="pencil",
                    on_release=self.show_editar_produto_screen,
                ),
                MDActionTopAppBarButton(
                    icon="delete",
                    on_release=self.excluir_produto,
                ),
                MDActionTopAppBarButton(
                    icon="chart-line",
                    on_release=self.show_historico_precos_screen
                ),
            ),
            type="small",
            size_hint_y=None,
            height=dp(64),
        )

        # --- Preenche a lista de produtos ---
        self.atualizar_lista_produtos()

        # --- Scroll para lista ---
        scroll = MDScrollView()
        scroll.add_widget(self.md_list)

        # --- Layout vertical final ---
        layout = BoxLayout(orientation="vertical")
        layout.add_widget(appbar_produtos)
        layout.add_widget(filtro_box)
        layout.add_widget(scroll)
        return layout

    # --- Função para normalizar texto (remove acentos e converte para maiúsculas) ---
    def normalizar_texto(self, texto):
        """Remove acentos e converte para maiúsculas"""
        try:
            if not isinstance(texto, str):
                texto = str(texto)
            return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII').upper()
        except Exception as e:
            logger.error(f"Erro ao normalizar texto '{texto}': {e}")
            return str(texto).upper()

    # --- Atualiza a lista de produtos, aplicando filtro se necessário ---
    def atualizar_lista_produtos(self, filtro_texto="", ids_filtrados=None):
        """Atualiza lista de produtos com limpeza adequada de checkboxes"""
        try:
            self.md_list.clear_widgets()
            self.limpar_referencias_checkbox('produtos')
            
            produtos = listar_produtos_apk()
            # Invalida cache ao atualizar
            self.invalidar_cache('produtos')
            
            if ids_filtrados is not None:
                produtos = [p for p in produtos if p[0] in ids_filtrados]
            categorias = listar_categorias_apk()
            categorias_dict = {c[0]: c[1] for c in categorias}
            subcategorias_dict_total = {}
            for cat in categorias:
                subcats = listar_subcategorias_apk(cat[0])
                for sub in subcats:
                    subcategorias_dict_total[sub[0]] = sub[1]

            # --- Filtro: busca em todos os campos do produto, categoria e subcategoria ---
            if filtro_texto:
                filtro_normalizado = self.normalizar_texto(filtro_texto)
                produtos_filtrados = []
                
                for produto in produtos:
                    # Busca em todos os campos do produto
                    match_produto = self.produto_match_filtro(produto, filtro_normalizado)
                    
                    # Busca no nome da categoria
                    categoria_id = produto[6]  # índice da categoria
                    categoria_nome = categorias_dict.get(categoria_id, "")
                    match_categoria = filtro_normalizado in self.normalizar_texto(str(categoria_nome))
                    
                    # Busca no nome da subcategoria
                    subcategoria_id = produto[7]  # índice da subcategoria
                    subcategoria_nome = subcategorias_dict_total.get(subcategoria_id, "")
                    match_subcategoria = filtro_normalizado in self.normalizar_texto(str(subcategoria_nome))
                    
                    # Inclui o produto se encontrou match em qualquer campo
                    if match_produto or match_categoria or match_subcategoria:
                        produtos_filtrados.append(produto)
                
                produtos = produtos_filtrados
                
            produtos = sorted(produtos, key=lambda x: self.normalizar_texto(x[2]))

            # --- Adiciona cada produto à lista ---
            for produto in produtos:
                produto_id, tipo_id, nome, marca, quantidade_embalagem, codigo_barras, categoria_id, subcategoria_id, imagem = produto
                checkbox = MDCheckbox()
                self.checkbox_refs.append((checkbox, produto_id))
                categoria_nome = categorias_dict.get(categoria_id, "") if categoria_id else ""
                subcategoria_nome = subcategorias_dict_total.get(subcategoria_id, "") if subcategoria_id else ""

                # Busca o preço mais atual do histórico, se existir
                historico = listar_historico_precos_apk(produto_id)
                preco_atual = None
                if historico:
                    # Assume que o histórico está ordenado por data (mais recente por último)
                    preco_atual = historico[-1][3]  # campo preço

                # Primeira linha: apenas o nome do produto
                headline = MDListItemHeadlineText(text=f"{str(nome).upper()}")

                # Segunda linha: marca, quantidade e preço (se houver)
                supporting_text = f"Marca: {str(marca).upper()} | Quantidade: {str(quantidade_embalagem).upper()}"
                if preco_atual is not None:
                    supporting_text += f" | Último preço: R$ {preco_atual:.2f}"

                item = MDListItem(
                    checkbox,
                    headline,
                    MDListItemSupportingText(text=supporting_text),
                    MDListItemSupportingText(text=f"Categoria: {str(categoria_nome).upper()} | Subcategoria: {str(subcategoria_nome).upper()}"),
                    padding=(dp(8), dp(8), dp(8), dp(8)),
                )
                self.md_list.add_widget(item)
            
            logger.info(f"Lista de produtos atualizada com {len(produtos)} itens")
            
        except Exception as e:
            logger.error(f"Erro ao atualizar lista de produtos: {e}")
            self.mostrar_snackbar("Erro ao carregar produtos.")
            self.md_list.add_widget(item)

    # --- Tela de Supermercados ---
    def criar_tela_supermercados(self):
        self.super_list = MDList()
        self.super_checkbox_refs = []
        self.atualizar_lista_supermercados()
        super_scroll = MDScrollView()
        super_scroll.add_widget(self.super_list)
        
        appbar_supermercados = MDTopAppBar(
            MDTopAppBarLeadingButtonContainer(
                MDActionTopAppBarButton(
                    icon="menu",
                    on_release=lambda x: self.root.get_ids().nav_drawer.set_state("toggle"),
                ),
            ),
            MDTopAppBarTitle(
                text="Supermercados",
                halign="center",
            ),
            MDTopAppBarTrailingButtonContainer(
                MDActionTopAppBarButton(
                    icon="plus",
                    on_release=self.show_cadastro_supermercado_screen,
                ),
                MDActionTopAppBarButton(
                    icon="pencil",
                    on_release=self.show_editar_supermercado_screen,
                ),
                MDActionTopAppBarButton(
                    icon="delete",
                    on_release=self.excluir_supermercado,
                ),
            ),
            type="small",
            size_hint_y=None,
            height=dp(64),
        )
        layout = BoxLayout(orientation="vertical")
        layout.add_widget(appbar_supermercados)
        layout.add_widget(super_scroll)
        return layout

    # --- Tela de Listas de Compras ---
    def criar_tela_listas(self):
        self.listas_list = MDList()
        self.listas_checkbox_refs = []
        self.atualizar_lista_compras()
        listas_scroll = MDScrollView()
        listas_scroll.add_widget(self.listas_list)
        
        appbar_listas = MDTopAppBar(
            MDTopAppBarLeadingButtonContainer(
                MDActionTopAppBarButton(
                    icon="menu",
                    on_release=lambda x: self.root.get_ids().nav_drawer.set_state("toggle"),
                ),
            ),
            MDTopAppBarTitle(
                text="Listas de Compras",
                halign="center",
            ),
            MDTopAppBarTrailingButtonContainer(
                MDActionTopAppBarButton(
                    icon="plus",
                    on_release=self.show_cadastro_lista_screen,
                ),
                MDActionTopAppBarButton(
                    icon="pencil",
                    on_release=self.show_editar_lista_screen,
                ),
                MDActionTopAppBarButton(
                    icon="delete",
                    on_release=self.excluir_lista,
                ),
                MDActionTopAppBarButton(
                    icon="eye",
                    on_release=self.show_itens_lista_screen,
                ),
            ),
            type="small",
            size_hint_y=None,
            height=dp(64),
        )
        layout = BoxLayout(orientation="vertical")
        layout.add_widget(appbar_listas)
        layout.add_widget(listas_scroll)
        return layout

    # --- Tela de Carrinhos ---
    def criar_tela_carrinhos(self):
        self.carrinhos_list = MDList()
        self.carrinhos_checkbox_refs = []
        self.atualizar_lista_carrinhos()
        carrinhos_scroll = MDScrollView()
        carrinhos_scroll.add_widget(self.carrinhos_list)
        
        appbar_carrinhos = MDTopAppBar(
            MDTopAppBarLeadingButtonContainer(
                MDActionTopAppBarButton(
                    icon="menu",
                    on_release=lambda x: self.root.get_ids().nav_drawer.set_state("toggle"),
                ),
            ),
            MDTopAppBarTitle(
                text="Carrinhos",
                halign="center",
            ),
            MDTopAppBarTrailingButtonContainer(
                MDActionTopAppBarButton(
                    icon="plus",
                    on_release=self.show_cadastro_carrinho_screen,
                ),
                MDActionTopAppBarButton(
                    icon="pencil",
                    on_release=self.show_editar_carrinho_screen,
                ),
                MDActionTopAppBarButton(
                    icon="delete",
                    on_release=self.excluir_carrinho,
                ),
                MDActionTopAppBarButton(
                    icon="eye",
                    on_release=self.show_itens_carrinho_screen,
                ),
            ),
            type="small",
            size_hint_y=None,
            height=dp(64),
        )
        layout = BoxLayout(orientation="vertical")
        layout.add_widget(appbar_carrinhos)
        layout.add_widget(carrinhos_scroll)
        return layout

    # --- Tela de Categorias e Tipos ---
    def criar_tela_categorias_tipos(self):
        # Cria abas para organizar os conteúdos
        self.tipos_list = MDList()
        self.tipos_checkbox_refs = []
        self.atualizar_lista_tipos_produto()
        tipos_scroll = MDScrollView()
        tipos_scroll.add_widget(self.tipos_list)
        
        appbar_categorias = MDTopAppBar(
            MDTopAppBarLeadingButtonContainer(
                MDActionTopAppBarButton(
                    icon="menu",
                    on_release=lambda x: self.root.get_ids().nav_drawer.set_state("toggle"),
                ),
            ),
            MDTopAppBarTitle(
                text="Categorias e Tipos",
                halign="center",
            ),
            MDTopAppBarTrailingButtonContainer(
                MDActionTopAppBarButton(
                    icon="plus",
                    on_release=self.show_cadastro_tipo_produto_screen,
                ),
                MDActionTopAppBarButton(
                    icon="pencil",
                    on_release=self.show_editar_tipo_produto_screen,
                ),
                MDActionTopAppBarButton(
                    icon="delete",
                    on_release=self.excluir_tipo_produto,
                ),
            ),
            type="small",
            size_hint_y=None,
            height=dp(64),
        )
        layout = BoxLayout(orientation="vertical")
        layout.add_widget(appbar_categorias)
        layout.add_widget(tipos_scroll)
        return layout

    # --- Menu lateral (Navigation Drawer) ---
    def criar_menu_lateral(self):
        return MDNavigationDrawer(
            MDNavigationDrawerMenu(
                MDNavigationDrawerLabel(text="Menu"),
                MDNavigationDrawerItem(
                    MDNavigationDrawerItemLeadingIcon(icon="shopping"),
                    MDNavigationDrawerItemText(text="Produtos"),
                    on_release=lambda x: (
                        self.atualizar_lista_produtos(),
                        setattr(self.screen_manager, "current", "produtos"),
                        self.root.get_ids().nav_drawer.set_state("close")
                    ),
                ),
                MDNavigationDrawerItem(
                    MDNavigationDrawerItemLeadingIcon(icon="store"),
                    MDNavigationDrawerItemText(text="Supermercados"),
                    on_release=lambda x: (
                        self.atualizar_lista_supermercados(),
                        setattr(self.screen_manager, "current", "supermercados"),
                        self.root.get_ids().nav_drawer.set_state("close")
                    ),
                ),
                MDNavigationDrawerItem(
                    MDNavigationDrawerItemLeadingIcon(icon="clipboard-list"),
                    MDNavigationDrawerItemText(text="Listas de Compras"),
                    on_release=lambda x: (
                        self.atualizar_lista_compras(),
                        setattr(self.screen_manager, "current", "listas"),
                        self.root.get_ids().nav_drawer.set_state("close")
                    ),
                ),
                MDNavigationDrawerItem(
                    MDNavigationDrawerItemLeadingIcon(icon="cart"),
                    MDNavigationDrawerItemText(text="Carrinhos"),
                    on_release=lambda x: (
                        self.atualizar_lista_carrinhos(),
                        setattr(self.screen_manager, "current", "carrinhos"),
                        self.root.get_ids().nav_drawer.set_state("close")
                    ),
                ),
                MDNavigationDrawerItem(
                    MDNavigationDrawerItemLeadingIcon(icon="shape"),
                    MDNavigationDrawerItemText(text="Categorias e Tipos"),
                    on_release=lambda x: (
                        self.atualizar_lista_tipos_produto(),
                        setattr(self.screen_manager, "current", "categorias"),
                        self.root.get_ids().nav_drawer.set_state("close")
                    ),
                ),
                MDNavigationDrawerItem(
                    MDNavigationDrawerItemLeadingIcon(icon="logout"),
                    MDNavigationDrawerItemText(text="Sair"),
                    on_release=lambda x: sys.exit(0),
                ),
                MDNavigationDrawerDivider(),
            ),
            id="nav_drawer",
            radius=(0, dp(16), dp(16), 0),
        )

    # --- Atualização otimizada de listas ---
    def atualizar_lista_produtos_otimizada(self, filtro_texto="", ids_filtrados=None):
        """Versão otimizada da atualização de produtos"""
        try:
            logger.info("Iniciando atualização otimizada da lista de produtos")
            self.md_list.clear_widgets()
            self.limpar_referencias_checkbox('produtos')
            
            # Usa cache inteligente
            produtos = self.get_produtos_cached()
            
            if ids_filtrados:
                produtos = [p for p in produtos if p[DatabaseFields.PRODUTO_ID] in ids_filtrados]
                logger.info(f"Filtro por IDs aplicado: {len(produtos)} produtos")
            
            # Cache para categorias e subcategorias
            if 'categorias' not in self._cache_produtos:
                self._cache_produtos['categorias'] = listar_categorias_apk()
                self._cache_produtos['subcategorias'] = self._get_todas_subcategorias()
            
            categorias_dict = {c[0]: c[1] for c in self._cache_produtos['categorias']}
            subcategorias_dict_total = self._cache_produtos['subcategorias']

            # Filtro em memória é mais rápido - busca em todos os campos
            if filtro_texto:
                filtro_norm = self.normalizar_texto(filtro_texto)
                produtos_filtrados = []
                
                for produto in produtos:
                    # Busca em todos os campos do produto
                    match_produto = self.produto_match_filtro(produto, filtro_norm)
                    
                    # Busca no nome da categoria
                    categoria_id = produto[DatabaseFields.PRODUTO_CATEGORIA_ID]
                    categoria_nome = categorias_dict.get(categoria_id, "")
                    match_categoria = filtro_norm in self.normalizar_texto(str(categoria_nome))
                    
                    # Busca no nome da subcategoria
                    subcategoria_id = produto[DatabaseFields.PRODUTO_SUBCATEGORIA_ID]
                    subcategoria_nome = subcategorias_dict_total.get(subcategoria_id, "")
                    match_subcategoria = filtro_norm in self.normalizar_texto(str(subcategoria_nome))
                    
                    # Inclui o produto se encontrou match em qualquer campo
                    if match_produto or match_categoria or match_subcategoria:
                        produtos_filtrados.append(produto)
                
                produtos = produtos_filtrados
                logger.info(f"Filtro de texto aplicado: {len(produtos)} produtos")

            # Ordena uma vez só
            produtos.sort(key=lambda x: self.normalizar_texto(x[DatabaseFields.PRODUTO_NOME]))

            # Adiciona produtos otimizado
            for produto in produtos:
                self.adicionar_item_produto_lista_otimizado(produto, categorias_dict, subcategorias_dict_total)
            
            logger.info(f"Lista de produtos atualizada com {len(produtos)} itens")
                
        except Exception as e:
            logger.error(f"Erro ao atualizar lista de produtos: {e}")
            self.mostrar_snackbar("Erro ao carregar produtos.")

    def _get_todas_subcategorias(self):
        """Pré-carrega todas as subcategorias"""
        subcategorias_dict = {}
        for cat in self._cache_produtos['categorias']:
            subcats = listar_subcategorias_apk(cat[0])
            for sub in subcats:
                subcategorias_dict[sub[0]] = sub[1]
        return subcategorias_dict

    def adicionar_item_produto_lista_otimizada(self, produto, categorias_dict, subcategorias_dict_total):
        """Adiciona item de produto de forma otimizada"""
        try:
            produto_id = produto[DatabaseFields.PRODUTO_ID]
            tipo_id = produto[DatabaseFields.PRODUTO_TIPO_ID]
            nome = produto[DatabaseFields.PRODUTO_NOME]
            marca = produto[DatabaseFields.PRODUTO_MARCA]
            quantidade_embalagem = produto[DatabaseFields.PRODUTO_QUANTIDADE_EMBALAGEM]
            categoria_id = produto[DatabaseFields.PRODUTO_CATEGORIA_ID]
            subcategoria_id = produto[DatabaseFields.PRODUTO_SUBCATEGORIA_ID]

            checkbox = MDCheckbox()
            self.checkbox_refs.append((checkbox, produto_id))
            
            categoria_nome = categorias_dict.get(categoria_id, "") if categoria_id else ""
            subcategoria_nome = subcategorias_dict_total.get(subcategoria_id, "") if subcategoria_id else ""

            # Busca preço mais atual com cache
            preco_atual = self._get_preco_atual_cached(produto_id)

            # Primeira linha: apenas o nome do produto
            headline = MDListItemHeadlineText(text=str(nome).upper())

            # Segunda linha: marca, embalagem e preço (se houver)
            supporting_text = f"Marca: {str(marca).upper()} | Embalagem: {str(quantidade_embalagem).upper()}"
            if preco_atual is not None:
                supporting_text += f" | Preço atual: R$ {preco_atual:.2f}"

            item = MDListItem(
                checkbox,
                headline,
                MDListItemSupportingText(text=supporting_text),
                MDListItemSupportingText(text=f"Categoria: {str(categoria_nome).upper()} | Subcategoria: {str(subcategoria_nome).upper()}"),
                padding=(dp(8), dp(8), dp(8), dp(8)),
            )
            self.md_list.add_widget(item)

        except Exception as e:
            logger.error(f"Erro ao adicionar item de produto {produto_id}: {e}")

    def _get_preco_atual_cached(self, produto_id):
        """Busca preço atual com cache básico"""
        try:
            cache_key = f"preco_{produto_id}"
            if cache_key in self._cache_produtos:
                return self._cache_produtos[cache_key]
            
            historico = listar_historico_precos_apk(produto_id)
            if historico:
                preco_atual = historico[-1][3]  # Assume ordenação por data
                self._cache_produtos[cache_key] = preco_atual
                return preco_atual
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar preço para produto {produto_id}: {e}")
            return None

    def adicionar_item_produto_lista_otimizado(self, produto, categorias_dict, subcategorias_dict_total):
        """Adiciona item de produto de forma otimizada à lista"""
        try:
            produto_id = produto[DatabaseFields.PRODUTO_ID]
            tipo_id = produto[DatabaseFields.PRODUTO_TIPO_ID]
            nome = produto[DatabaseFields.PRODUTO_NOME]
            marca = produto[DatabaseFields.PRODUTO_MARCA]
            quantidade_embalagem = produto[DatabaseFields.PRODUTO_QUANTIDADE_EMBALAGEM]
            categoria_id = produto[DatabaseFields.PRODUTO_CATEGORIA_ID]
            subcategoria_id = produto[DatabaseFields.PRODUTO_SUBCATEGORIA_ID]

            checkbox = MDCheckbox()
            self.checkbox_refs.append((checkbox, produto_id))
            
            categoria_nome = categorias_dict.get(categoria_id, "") if categoria_id else ""
            subcategoria_nome = subcategorias_dict_total.get(subcategoria_id, "") if subcategoria_id else ""

            # Busca preço mais atual com cache
            preco_atual = self._get_preco_atual_cached(produto_id)

            # Primeira linha: apenas o nome do produto
            headline = MDListItemHeadlineText(text=str(nome).upper())

            # Segunda linha: marca, embalagem e preço (se houver)
            supporting_text = f"Marca: {str(marca).upper()} | Embalagem: {str(quantidade_embalagem).upper()}"
            if preco_atual is not None:
                supporting_text += f" | Preço atual: R$ {preco_atual:.2f}"

            item = MDListItem(
                checkbox,
                headline,
                MDListItemSupportingText(text=supporting_text),
                MDListItemSupportingText(text=f"Categoria: {str(categoria_nome).upper()} | Subcategoria: {str(subcategoria_nome).upper()}"),
                padding=(dp(8), dp(8), dp(8), dp(8)),
            )
            self.md_list.add_widget(item)

        except Exception as e:
            logger.error(f"Erro ao adicionar item de produto {produto_id}: {e}")

    # Mantém compatibilidade com método original
    def atualizar_lista_produtos(self, filtro_texto="", ids_filtrados=None):
        """Atualiza lista de produtos com limpeza adequada de checkboxes"""
        try:
            self.md_list.clear_widgets()
            self.limpar_referencias_checkbox('produtos')
            
            # Limpeza adicional para evitar checkboxes órfãos após restauração
            self.checkbox_refs = []
            
            produtos = listar_produtos_apk()
            # Invalida cache ao atualizar
            self.invalidar_cache('produtos')
            
            if ids_filtrados is not None:
                produtos = [p for p in produtos if p[0] in ids_filtrados]
            categorias = listar_categorias_apk()
            categorias_dict = {c[0]: c[1] for c in categorias}
            subcategorias_dict_total = {}
            for cat in categorias:
                subcats = listar_subcategorias_apk(cat[0])
                for sub in subcats:
                    subcategorias_dict_total[sub[0]] = sub[1]

            # --- Filtro: busca em todos os campos do produto, categoria e subcategoria ---
            if filtro_texto:
                filtro_normalizado = self.normalizar_texto(filtro_texto)
                produtos_filtrados = []
                
                for produto in produtos:
                    # Busca em todos os campos do produto
                    match_produto = self.produto_match_filtro(produto, filtro_normalizado)
                    
                    # Busca no nome da categoria
                    categoria_id = produto[6]  # índice da categoria
                    categoria_nome = categorias_dict.get(categoria_id, "")
                    match_categoria = filtro_normalizado in self.normalizar_texto(str(categoria_nome))
                    
                    # Busca no nome da subcategoria
                    subcategoria_id = produto[7]  # índice da subcategoria
                    subcategoria_nome = subcategorias_dict_total.get(subcategoria_id, "")
                    match_subcategoria = filtro_normalizado in self.normalizar_texto(str(subcategoria_nome))
                    
                    # Inclui o produto se encontrou match em qualquer campo
                    if match_produto or match_categoria or match_subcategoria:
                        produtos_filtrados.append(produto)
                
                produtos = produtos_filtrados
                
            produtos = sorted(produtos, key=lambda x: self.normalizar_texto(x[2]))

            # --- Adiciona cada produto à lista ---
            for produto in produtos:
                produto_id, tipo_id, nome, marca, quantidade_embalagem, codigo_barras, categoria_id, subcategoria_id, imagem = produto
                checkbox = MDCheckbox()
                self.checkbox_refs.append((checkbox, produto_id))
                categoria_nome = categorias_dict.get(categoria_id, "") if categoria_id else ""
                subcategoria_nome = subcategorias_dict_total.get(subcategoria_id, "") if subcategoria_id else ""

                # Busca o preço mais atual do histórico, se existir
                historico = listar_historico_precos_apk(produto_id)
                preco_atual = None
                if historico:
                    # Assume que o histórico está ordenado por data (mais recente por último)
                    preco_atual = historico[-1][3]  # campo preço

                # Primeira linha: apenas o nome do produto
                headline = MDListItemHeadlineText(text=f"{str(nome).upper()}")

                # Segunda linha: marca, quantidade e preço (se houver)
                supporting_text = f"Marca: {str(marca).upper()} | Quantidade: {str(quantidade_embalagem).upper()}"
                if preco_atual is not None:
                    supporting_text += f" | Último preço: R$ {preco_atual:.2f}"

                item = MDListItem(
                    checkbox,
                    headline,
                    MDListItemSupportingText(text=supporting_text),
                    MDListItemSupportingText(text=f"Categoria: {str(categoria_nome).upper()} | Subcategoria: {str(subcategoria_nome).upper()}"),
                    padding=(dp(8), dp(8), dp(8), dp(8)),
                )
                self.md_list.add_widget(item)
            
            logger.info(f"Lista de produtos atualizada com {len(produtos)} itens")
            
        except Exception as e:
            logger.error(f"Erro ao atualizar lista de produtos: {e}")
            self.mostrar_snackbar("Erro ao carregar produtos.")

    # --- Funções auxiliares melhoradas ---
    def mostrar_snackbar(self, mensagem):
        """Mostra snackbar com tratamento de erro"""
        try:
            MDSnackbar(
                MDSnackbarText(text=mensagem),
                y=dp(24),
                pos_hint={"center_x": 0.5},
                size_hint_x=0.5,
            ).open()
            logger.info(f"Snackbar exibido: {mensagem}")
        except Exception as e:
            logger.error(f"Erro ao exibir snackbar: {e}")

    def forcar_maiusculas(self, instance, text):
        """Força texto em maiúsculas nos campos - corrigido para aceitar 2 argumentos"""
        try:
            instance.text = text.upper()
        except Exception as e:
            logger.error(f"Erro ao forçar maiúsculas: {e}")

    # --- Métodos de seleção e filtros otimizados ---
    def exibir_selecionados_produtos(self, *args):
        """Exibe apenas produtos selecionados com validação"""
        try:
            selecionados = [produto_id for checkbox, produto_id in self.checkbox_refs if checkbox.active]
            if not selecionados:
                self.mostrar_snackbar("Nenhum produto selecionado.")
                return
            
            logger.info(f"Exibindo {len(selecionados)} produtos selecionados")
            self.atualizar_lista_produtos(ids_filtrados=selecionados)
            self.filtro_ativo = True
        except Exception as e:
            logger.error(f"Erro ao exibir produtos selecionados: {e}")
            self.mostrar_snackbar("Erro ao filtrar produtos selecionados.")

    def limpar_selecao_produtos(self, *args):
        """Limpa seleção de produtos com feedback"""
        try:
            count = 0
            for checkbox, _ in self.checkbox_refs:
                if checkbox.active:
                    checkbox.active = False
                    count += 1
            
            if self.filtro_ativo:
                self.atualizar_lista_produtos()
                self.filtro_ativo = False
            
            logger.info(f"Limpou seleção de {count} produtos")
            if count > 0:
                self.mostrar_snackbar(f"{count} produto(s) desmarcado(s).")
        except Exception as e:
            logger.error(f"Erro ao limpar seleção: {e}")

    def aplicar_filtro_texto_produto(self, *args):
        """Aplica filtro de texto otimizado"""
        try:
            filtro_texto = self.filtro_texto_produto.text.strip()
            if filtro_texto:
                self.filtro_ativo = True
                logger.info(f"Aplicando filtro: '{filtro_texto}'")
            else:
                self.filtro_ativo = False
                logger.info("Filtro removido")
            
            self.atualizar_lista_produtos(filtro_texto=filtro_texto)
        except Exception as e:
            logger.error(f"Erro ao aplicar filtro: {e}")
            self.mostrar_snackbar("Erro ao aplicar filtro.")

    def limpar_filtro_texto_produto(self, *args):
        """Limpa filtro de texto"""
        try:
            self.filtro_texto_produto.text = ""
            self.filtro_ativo = False
            self.atualizar_lista_produtos()
            logger.info("Filtro de texto limpo")
        except Exception as e:
            logger.error(f"Erro ao limpar filtro: {e}")

    # --- Atualização otimizada de listas ---
    def atualizar_lista_supermercados(self):
        """Atualiza lista de supermercados com tratamento de erro"""
        try:
            self.super_list.clear_widgets()
            self.limpar_referencias_checkbox('supermercados')
            
            # Limpeza adicional para evitar checkboxes órfãos
            self.super_checkbox_refs = []
            
            supermercados = listar_supermercados_apk()
            for supermercado in supermercados:
                super_id, nome, bairro = supermercado
                checkbox = MDCheckbox()
                self.super_checkbox_refs.append((checkbox, super_id))
                item = MDListItem(
                    checkbox,
                    MDListItemHeadlineText(text=str(nome).upper()),
                    MDListItemSupportingText(text=f"Bairro: {str(bairro).upper()}"),
                    padding=(dp(8), dp(8), dp(8), dp(8)),
                )
                self.super_list.add_widget(item)
            
            logger.info(f"Lista de supermercados atualizada com {len(supermercados)} itens")
        except Exception as e:
            logger.error(f"Erro ao atualizar lista de supermercados: {e}")
            self.mostrar_snackbar("Erro ao carregar supermercados.")

    def atualizar_lista_compras(self):
        """Atualiza lista de compras com tratamento de erro"""
        try:
            self.listas_list.clear_widgets()
            self.limpar_referencias_checkbox('listas')
            
            # Limpeza adicional para evitar checkboxes órfãos
            self.listas_checkbox_refs = []
            
            listas = listar_listas_apk()
            for lista in listas:
                lista_id, nome, data_criacao = lista
                checkbox = MDCheckbox()
                self.listas_checkbox_refs.append((checkbox, lista_id))
                item = MDListItem(
                    checkbox,
                    MDListItemHeadlineText(text=str(nome).upper()),
                    MDListItemSupportingText(text=f"Data: {data_criacao}"),
                    padding=(dp(8), dp(8), dp(8), dp(8)),
                )
                self.listas_list.add_widget(item)
            
            logger.info(f"Lista de compras atualizada com {len(listas)} itens")
        except Exception as e:
            logger.error(f"Erro ao atualizar lista de compras: {e}")
            self.mostrar_snackbar("Erro ao carregar listas.")

    def atualizar_lista_carrinhos(self):
        """Atualiza lista de carrinhos com tratamento de erro"""
        try:
            self.carrinhos_list.clear_widgets()
            self.limpar_referencias_checkbox('carrinhos')
            
            # Limpeza adicional para evitar checkboxes órfãos
            self.carrinhos_checkbox_refs = []
            
            carrinhos = listar_carrinhos_apk()
            supermercados = listar_supermercados_apk()
            listas = listar_listas_apk()
            
            # Dicionários para lookup
            supermercados_dict = {s[0]: (s[1], s[2]) for s in supermercados}  # {id: (nome, bairro)}
            listas_dict = {l[0]: l[1] for l in listas}
            
            # Separar carrinhos finalizados e abertos
            carrinhos_abertos = []
            carrinhos_finalizados = []
            
            for carrinho in carrinhos:
                carrinho_id, nome, supermercado_id, lista_id, data_criacao, finalizado, data_finalizacao = carrinho
                if finalizado:
                    carrinhos_finalizados.append(carrinho)
                else:
                    carrinhos_abertos.append(carrinho)
            
            # Função helper para criar item de carrinho
            def criar_item_carrinho(carrinho, is_finalizado=False):
                carrinho_id, nome, supermercado_id, lista_id, data_criacao, finalizado, data_finalizacao = carrinho
                checkbox = MDCheckbox()
                self.carrinhos_checkbox_refs.append((checkbox, carrinho_id))
                
                # Busca informações do supermercado
                supermercado_info = supermercados_dict.get(supermercado_id, ("Supermercado não encontrado", ""))
                supermercado_nome = supermercado_info[0]
                supermercado_bairro = supermercado_info[1]
                
                lista_nome = listas_dict.get(lista_id, "Lista não encontrada")
                
                # Formatar data de criação
                data_formatada = data_criacao
                try:
                    data_obj = datetime.strptime(data_criacao, "%Y-%m-%d")
                    data_formatada = data_obj.strftime("%d/%m/%y")
                except:
                    pass
                
                # Formatar data de finalização se existir
                data_finalizacao_formatada = ""
                if data_finalizacao:
                    try:
                        data_obj = datetime.strptime(data_finalizacao, "%Y-%m-%d %H:%M:%S")
                        data_finalizacao_formatada = f" | Finalizado: {data_obj.strftime('%d/%m/%y %H:%M')}"
                    except:
                        data_finalizacao_formatada = f" | Finalizado: {data_finalizacao}"
                
                # Calcula total do carrinho
                total_carrinho = self.calcular_total_carrinho(carrinho_id)
                total_texto = f"R$ {total_carrinho:.2f}" if total_carrinho > 0 else "R$ 0,00"
                
                # Status visual
                status_text = "FINALIZADO" if is_finalizado else "EM ABERTO"
                nome_display = f"{str(nome).upper()} - {total_texto}"
                
                supporting_text = f"{str(supermercado_nome).upper()} - {str(supermercado_bairro).upper()}"
                third_line = f"Lista: {str(lista_nome).upper()} | Criado: {data_formatada}{data_finalizacao_formatada}"
                
                item = MDListItem(
                    checkbox,
                    MDListItemHeadlineText(text=nome_display),
                    MDListItemSupportingText(text=supporting_text),
                    MDListItemSupportingText(text=third_line),
                    padding=(dp(8), dp(8), dp(8), dp(8)),
                )
                return item
            
            # Adicionar seção de carrinhos abertos
            if carrinhos_abertos:
                # Cabeçalho para carrinhos abertos
                header_abertos = MDListItem(
                    MDListItemHeadlineText(
                        text="CARRINHOS EM ABERTO",
                        theme_text_color="Primary",
                        font_style="Title"
                    ),
                    padding=(dp(16), dp(12), dp(16), dp(8)),
                    height=dp(56)
                )
                header_abertos.md_bg_color = (0.2, 0.6, 1.0, 0.1)  # Azul claro
                self.carrinhos_list.add_widget(header_abertos)
                
                for carrinho in carrinhos_abertos:
                    item = criar_item_carrinho(carrinho, False)
                    # Adiciona indentação visual
                    item.padding = (dp(24), dp(8), dp(8), dp(8))
                    self.carrinhos_list.add_widget(item)
            
            # Adicionar seção de carrinhos finalizados
            if carrinhos_finalizados:
                # Cabeçalho para carrinhos finalizados
                header_finalizados = MDListItem(
                    MDListItemHeadlineText(
                        text="CARRINHOS FINALIZADOS",
                        theme_text_color="Primary",
                        font_style="Title"
                    ),
                    padding=(dp(16), dp(12), dp(16), dp(8)),
                    height=dp(56)
                )
                header_finalizados.md_bg_color = (0.2, 0.8, 0.2, 0.1)  # Verde claro
                self.carrinhos_list.add_widget(header_finalizados)
                
                for carrinho in carrinhos_finalizados:
                    item = criar_item_carrinho(carrinho, True)
                    # Adiciona indentação visual
                    item.padding = (dp(24), dp(8), dp(8), dp(8))
                    self.carrinhos_list.add_widget(item)
            
            logger.info(f"Lista de carrinhos atualizada - {len(carrinhos_abertos)} abertos, {len(carrinhos_finalizados)} finalizados")
        except Exception as e:
            logger.error(f"Erro ao atualizar lista de carrinhos: {e}")
            self.mostrar_snackbar("Erro ao carregar carrinhos.")

    def calcular_total_carrinho(self, carrinho_id):
        """Calcula o total do carrinho baseado nos itens cadastrados"""
        try:
            # Busca itens do carrinho
            itens = listar_itens_carrinho_apk(carrinho_id)
            if not itens:
                return 0.0
            
            total = 0.0
            for item in itens:
                # Estrutura do item: (item_id, carrinho_id, produto_id, quantidade, preco_unit, nome_produto, marca, quantidade_embalagem)
                quantidade = item[3]  # quantidade
                preco_unit = item[4]  # preco_unit
                
                if quantidade is not None and preco_unit is not None:
                    total += quantidade * preco_unit
            
            return total
            
        except Exception as e:
            logger.error(f"Erro ao calcular total do carrinho {carrinho_id}: {e}")
            return 0.0

    def atualizar_lista_tipos_produto(self):
        """Atualiza lista de tipos de produto com tratamento de erro"""
        try:
            self.tipos_list.clear_widgets()
            self.limpar_referencias_checkbox('tipos')
            
            # Limpeza adicional para evitar checkboxes órfãos
            self.tipos_checkbox_refs = []
            
            tipos = listar_tipos_produto_apk()
            categorias = listar_categorias_apk()
            
            # Dicionário para lookup de categorias
            categorias_dict = {c[0]: c[1] for c in categorias}
            
            # Dicionário para lookup de subcategorias
            subcategorias_dict = {}
            for cat in categorias:
                subcats = listar_subcategorias_apk(cat[0])
                for sub in subcats:
                    subcategorias_dict[sub[0]] = sub[1]
            
            for tipo in tipos:
                tipo_id, nome, categoria_id, subcategoria_id = tipo
                checkbox = MDCheckbox()
                self.tipos_checkbox_refs.append((checkbox, tipo_id))
                
                categoria_nome = categorias_dict.get(categoria_id, "Categoria não encontrada")
                subcategoria_nome = subcategorias_dict.get(subcategoria_id, "Subcategoria não encontrada")
                
                item = MDListItem(
                    checkbox,
                    MDListItemHeadlineText(text=str(nome).upper()),
                    MDListItemSupportingText(text=f"Categoria: {str(categoria_nome).upper()}"),
                    MDListItemSupportingText(text=f"Subcategoria: {str(subcategoria_nome).upper()}"),
                    padding=(dp(8), dp(8), dp(8), dp(8)),
                )
                self.tipos_list.add_widget(item)
            
            logger.info(f"Lista de tipos de produto atualizada com {len(tipos)} itens")
        except Exception as e:
            logger.error(f"Erro ao atualizar lista de tipos de produto: {e}")
            self.mostrar_snackbar("Erro ao carregar tipos de produto.")

    def atualizar_lista_compras_itens(self, lista_id, filtro_texto=""):
        """Atualiza itens da lista com tratamento de erro e organização por categorias usando dividers"""
        try:
            itens = listar_itens_lista_apk(lista_id)
            self.limpar_referencias_checkbox('itens')
            self.itens_list.clear_widgets()
            
            # Organiza itens por categoria
            categorias_dict = {}
            for item in itens:
                item_id = item[0]
                tipo_nome = item[7]
                quantidade = item[5]
                categoria_nome = item[8]
                subcategoria_nome = item[9]
                # Removed comprado field as it doesn't exist in database schema
                
                # Aplica filtro se fornecido
                if filtro_texto:
                    filtro_norm = self.normalizar_texto(filtro_texto)
                    item_match = False
                    
                    # Busca em todos os campos do item
                    campos_busca = [tipo_nome, categoria_nome, subcategoria_nome, str(quantidade)]
                    for campo in campos_busca:
                        if filtro_norm in self.normalizar_texto(str(campo)):
                            item_match = True
                            break
                    
                    if not item_match:
                        continue
                
                # Agrupa por categoria
                if categoria_nome not in categorias_dict:
                    categorias_dict[categoria_nome] = []
                
                categorias_dict[categoria_nome].append({
                    'item_id': item_id,
                    'tipo_nome': tipo_nome,
                    'quantidade': quantidade,
                    'categoria_nome': categoria_nome,
                    'subcategoria_nome': subcategoria_nome
                })
            
            # Exibe itens organizados por categoria com dividers
            if not categorias_dict and filtro_texto:
                # Se não há resultados com filtro, mostra mensagem
                label_vazio = MDLabel(
                    text=f"Nenhum item encontrado para '{filtro_texto}'.",
                    halign="center",
                    theme_text_color="Primary",
                    size_hint_y=None,
                    height=dp(100),
                    padding=(dp(16), dp(16)),
                )
                self.itens_list.add_widget(label_vazio)
            elif not categorias_dict:
                # Se não há itens na lista
                label_vazio = MDLabel(
                    text="Esta lista não possui itens.\nUse o botão '+' para adicionar itens.",
                    halign="center",
                    theme_text_color="Primary",
                    size_hint_y=None,
                    height=dp(100),
                    padding=(dp(16), dp(16)),
                )
                self.itens_list.add_widget(label_vazio)
            else:
                # Cria seções para categorias com dividers e labels
                for categoria_nome in sorted(categorias_dict.keys()):
                    itens_categoria = categorias_dict[categoria_nome]
                    self.criar_secao_categoria_com_divider(categoria_nome, itens_categoria)
            
            logger.info(f"Lista de itens atualizada com {len(itens)} itens para lista {lista_id}")
        except Exception as e:
            logger.error(f"Erro ao atualizar itens da lista {lista_id}: {e}")
            self.mostrar_snackbar("Erro ao carregar itens da lista.")

    def criar_secao_categoria_com_divider(self, categoria_nome, itens_categoria):
        """Cria seção de categoria com divider e label ao invés de expansion panel"""
        try:
            # Conta total de itens na categoria
            total_itens = len(itens_categoria)
            
            # Cria título com informações da categoria (sem contagem de comprados)
            titulo_categoria = f"{str(categoria_nome).upper()} ({total_itens} {'item' if total_itens == 1 else 'itens'})"
            
            # Adiciona label da categoria com espaçamento reduzido (sem dividers)
            categoria_label = MDLabel(
                text=titulo_categoria,
                theme_text_color="Primary",
                size_hint_y=None,
                height=dp(32),  # Altura reduzida de 48 para 32
                padding=(dp(16), dp(4)),  # Padding reduzido de (16,8) para (16,4)
                bold=True,
            )
            self.itens_list.add_widget(categoria_label)
            
            # Ordena itens por nome do tipo
            itens_ordenados = sorted(itens_categoria, key=lambda x: self.normalizar_texto(x['tipo_nome']))
            
            # Adiciona cada item da categoria com funcionalidade de swipe
            for item in itens_ordenados:
                # Checkbox para seleção
                checkbox = MDCheckbox(active=False)
                self.itens_checkbox_refs.append((checkbox, item['item_id']))
                
                # Destaca a quantidade em negrito
                quantidade_destaque = f"[b]Qtd: {item['quantidade']}[/b]"
                
                # Cria item swipeável usando MDListItem
                item_widget = SwipeableListItem(
                    checkbox,
                    MDListItemHeadlineText(text=str(item['tipo_nome']).upper()),
                    MDListItemSupportingText(
                        text=f"{quantidade_destaque} | Subcategoria: {str(item['subcategoria_nome']).upper()}",
                        markup=True
                    ),
                    item_data=item,
                    on_swipe_left=self.swipe_excluir_item,
                    on_swipe_right=self.swipe_editar_item,
                    padding=(dp(4), dp(4), dp(4), dp(4)),
                    size_hint_y=None,
                    height=dp(56),
                )
                
                self.itens_list.add_widget(item_widget)
            
            # Adiciona espaçamento mínimo após categoria
            espacador = BoxLayout(size_hint_y=None, height=dp(4))  # Reduzido de 8 para 4
            self.itens_list.add_widget(espacador)
            
            logger.info(f"Seção da categoria criada para: {titulo_categoria}")
            
        except Exception as e:
            logger.error(f"Erro ao criar seção da categoria {categoria_nome}: {e}")
            # Fallback: adiciona apenas os itens sem organização usando método original
            for item in itens_categoria:
                try:
                    # Checkbox para SELEÇÃO do item (para editar, excluir ou adicionar ao carrinho)
                    checkbox = MDCheckbox(active=False)
                    self.itens_checkbox_refs.append((checkbox, item['item_id']))
                    
                    # Destaca a quantidade em negrito
                    quantidade_destaque = f"[b]Qtd: {item['quantidade']}[/b]"
                    
                    item_widget = MDListItem(
                        checkbox,
                        MDListItemHeadlineText(text=str(item['tipo_nome']).upper()),
                        MDListItemSupportingText(
                            text=f"{quantidade_destaque} | Subcategoria: {str(item['subcategoria_nome']).upper()}",
                            markup=True
                        ),
                        padding=(dp(4), dp(4), dp(4), dp(4)),
                        size_hint_y=None,
                        height=dp(56),
                    )
                    self.itens_list.add_widget(item_widget)
                except Exception as item_error:
                    logger.error(f"Erro ao adicionar item {item.get('item_id', 'desconhecido')}: {item_error}")
                    continue

    # Métodos de callback para ações de swipe
    def swipe_excluir_item(self, item_data):
        """Callback para swipe esquerda - exclui item da lista"""
        try:
            item_id = item_data['item_id']
            tipo_nome = item_data['tipo_nome']
            
            # Confirma exclusão com snackbar
            self.mostrar_snackbar(f"{tipo_nome.upper()} será excluído da lista!")
            
            # Exclui o item
            sucesso = excluir_item_lista_apk(item_id)
            
            if sucesso:
                # Atualiza a tela
                if hasattr(self, 'lista_atual_visualizada_id'):
                    self.atualizar_lista_compras_itens(self.lista_atual_visualizada_id)
                    self.atualizar_titulo_appbar_lista()
                
                self.mostrar_snackbar(f"{tipo_nome.upper()} excluído com sucesso!")
                logger.info(f"Item {item_id} excluído via swipe")
            else:
                self.mostrar_snackbar("Erro ao excluir item.")
                
        except Exception as e:
            logger.error(f"Erro ao excluir item via swipe: {e}")
            self.mostrar_snackbar("Erro ao excluir item.")

    def swipe_editar_item(self, item_data):
        """Callback para swipe direita - edita item da lista"""
        try:
            item_id = item_data['item_id']
            
            # Limpa seleções anteriores
            for checkbox, _ in self.itens_checkbox_refs:
                checkbox.active = False
            
            # Marca apenas este item como selecionado
            for checkbox, checkbox_item_id in self.itens_checkbox_refs:
                if checkbox_item_id == item_id:
                    checkbox.active = True
                    break
            
            # Abre tela de edição
            if hasattr(self, 'lista_atual_visualizada_id'):
                self.show_editar_item_lista_screen(self.lista_atual_visualizada_id)
                logger.info(f"Editando item {item_id} via swipe")
            else:
                self.mostrar_snackbar("Erro: lista não identificada.")
                
        except Exception as e:
            logger.error(f"Erro ao editar item via swipe: {e}")
            self.mostrar_snackbar("Erro ao editar item.")
    
    def aplicar_filtro_itens_lista(self, *args):
        """Aplica filtro nos itens da lista com sugestões de produtos não adicionados"""
        try:
            if not hasattr(self, 'lista_atual_visualizada_id'):
                return
                
            filtro_texto = self.filtro_texto_itens_lista.text.strip()
            self.atualizar_lista_compras_itens(self.lista_atual_visualizada_id, filtro_texto)
            
            # Se há filtro, mostra sugestões de produtos não adicionados
            if filtro_texto:
                self.mostrar_sugestoes_produtos_nao_adicionados(filtro_texto)
                logger.info(f"Filtro aplicado nos itens da lista com sugestões: '{filtro_texto}'")
            
        except Exception as e:
            logger.error(f"Erro ao aplicar filtro nos itens: {e}")
            self.mostrar_snackbar("Erro ao aplicar filtro.")

    def limpar_filtro_itens_lista(self, *args):
        """Limpa filtro dos itens da lista"""
        try:
            if not hasattr(self, 'lista_atual_visualizada_id'):
                return
                
            tinha_filtro = bool(self.filtro_texto_itens_lista.text.strip())
            self.filtro_texto_itens_lista.text = ""
            self.atualizar_lista_compras_itens(self.lista_atual_visualizada_id)
            
            if tinha_filtro:
                Clock.schedule_once(lambda dt: self.mostrar_snackbar("Filtro removido"), 0.1)
                
            logger.info("Filtro de itens da lista limpo")
            
        except Exception as e:
            logger.error(f"Erro ao limpar filtro dos itens: {e}")

    def filtro_tempo_real_itens_lista(self, instance, text):
        """Aplica filtro em tempo real conforme usuário digita"""
        try:
            # Cancela agendamento anterior se existir
            if hasattr(self, '_filtro_timer'):
                self._filtro_timer.cancel()
            
            # Agenda aplicação do filtro com delay de 0.5 segundos
            self._filtro_timer = Clock.schedule_once(
                lambda dt: self.aplicar_filtro_itens_lista(), 0.5
            )
            
        except Exception as e:
            logger.error(f"Erro no filtro em tempo real: {e}")

    def mostrar_sugestoes_produtos_nao_adicionados(self, filtro_texto):
        """Mostra sugestões de tipos de produtos do banco que não estão na lista"""
        try:
            if not filtro_texto.strip():
                return
                
            # Busca tipos de produtos que correspondem ao filtro
            todos_tipos = listar_tipos_produto_apk()
            filtro_norm = self.normalizar_texto(filtro_texto)
            
            # Tipos que já estão na lista atual
            itens_na_lista = listar_itens_lista_apk(self.lista_atual_visualizada_id)
            tipos_na_lista = {item[1] for item in itens_na_lista}  # tipo_produto_id está no índice 1
            
            # Busca tipos que não estão na lista mas correspondem ao filtro
            sugestoes = []
            categorias_dict = {c[0]: c[1] for c in listar_categorias_apk()}
            
            for tipo in todos_tipos:
                tipo_id = tipo[0]  # id do tipo
                nome_tipo = tipo[1]  # nome do tipo
                categoria_id = tipo[2]  # categoria_id do tipo
                categoria_nome = categorias_dict.get(categoria_id, "")
                
                # Se tipo não está na lista e corresponde ao filtro
                if (tipo_id not in tipos_na_lista and 
                    (filtro_norm in self.normalizar_texto(str(nome_tipo)) or
                     filtro_norm in self.normalizar_texto(str(categoria_nome)))):
                    sugestoes.append(tipo)
            
            # Limita a 5 sugestões e ordena por relevância (nome primeiro)
            sugestoes = sorted(sugestoes, key=lambda x: self.normalizar_texto(x[1]))[:5]
            
            # Adiciona seção de sugestões se houver
            if sugestoes:
                self.adicionar_secao_sugestoes_tipos(sugestoes, categorias_dict)
                logger.info(f"Exibindo {len(sugestoes)} sugestões de tipos para adicionar")
                
        except Exception as e:
            logger.error(f"Erro ao buscar sugestões de tipos: {e}")

    def adicionar_secao_sugestoes_tipos(self, sugestoes, categorias_dict):
        """Adiciona seção de sugestões de tipos de produtos para adicionar à lista"""
        try:
            # Separador visual antes das sugestões
            separador = BoxLayout(size_hint_y=None, height=dp(8))
            self.itens_list.add_widget(separador)
            
            # Label da seção de sugestões
            sugestoes_label = MDLabel(
                text=f"TIPOS DISPONÍVEIS PARA ADICIONAR ({len(sugestoes)})",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(28),  # Menor que categoria normal
                padding=(dp(16), dp(2)),
                bold=True,
            )
            self.itens_list.add_widget(sugestoes_label)
            
            # Adiciona cada sugestão com botão de +
            for tipo in sugestoes:
                tipo_id = tipo[0]
                nome_tipo = tipo[1]
                categoria_id = tipo[2]
                categoria_nome = categorias_dict.get(categoria_id, "")
                
                # Botão de adicionar (+)
                btn_adicionar = MDActionTopAppBarButton(
                    icon="plus-circle",
                    theme_icon_color="Custom",
                    icon_color="green",
                    on_release=lambda x, tid=tipo_id: self.adicionar_tipo_sugerido_lista(tid)
                )
                
                # Item da sugestão com altura menor
                item_sugestao = MDListItem(
                    btn_adicionar,
                    MDListItemHeadlineText(text=str(nome_tipo).upper()),
                    MDListItemSupportingText(
                        text=f"Categoria: {str(categoria_nome).upper()}"
                    ),
                    padding=(dp(4), dp(2), dp(4), dp(2)),  # Padding ainda menor
                    size_hint_y=None,
                    height=dp(48),  # Altura menor que itens normais
                )
                self.itens_list.add_widget(item_sugestao)
                
        except Exception as e:
            logger.error(f"Erro ao adicionar seção de sugestões de tipos: {e}")

    def adicionar_tipo_sugerido_lista(self, tipo_id):
        """Adiciona tipo sugerido à lista atual"""
        try:
            if not hasattr(self, 'lista_atual_visualizada_id'):
                return
                
            # Abre dialog para definir quantidade
            self.tipo_sugerido_id = tipo_id
            self.show_dialog_quantidade_tipo_sugerido()
                
        except Exception as e:
            logger.error(f"Erro ao adicionar tipo sugerido {tipo_id}: {e}")
            self.mostrar_snackbar("Erro ao adicionar tipo.")

    def show_dialog_quantidade_tipo_sugerido(self):
        """Mostra dialog para definir quantidade do tipo sugerido"""
        try:
            # Busca nome do tipo
            tipos = listar_tipos_produto_apk()
            tipo = next((t for t in tipos if t[0] == self.tipo_sugerido_id), None)
            nome_tipo = tipo[1] if tipo else "Tipo"
            
            # Campo de quantidade
            self.campo_quantidade_sugerido = MDTextField(
                hint_text="Quantidade",
                text="1",
                multiline=False,
                size_hint_y=None,
                height=dp(56),
                input_filter="int"  # Apenas números inteiros
            )
            
            # Card container
            card = MDCard(
                orientation="vertical",
                padding=dp(16),
                spacing=dp(16),
                size_hint_y=None,
                height=dp(200),
                elevation=0,
            )
            
            # Título
            titulo = MDLabel(
                text=f"Adicionar '{str(nome_tipo).upper()}' à lista:",
                theme_text_color="Primary",
                size_hint_y=None,
                height=dp(32),
                halign="center"
            )
            
            # Botões
            botoes_box = BoxLayout(
                orientation="horizontal",
                spacing=dp(16),
                size_hint_y=None,
                height=dp(40),
            )
            
            btn_cancelar = MDButton(
                MDButtonText(text="CANCELAR"),
                style="text",
                on_release=self.fechar_bottomsheet_quantidade,
                size_hint_x=0.5,
            )
            
            btn_adicionar = MDButton(
                MDButtonText(text="ADICIONAR"),
                style="filled",  
                on_release=self.confirmar_adicao_tipo_sugerido,
                size_hint_x=0.5,
            )
            
            botoes_box.add_widget(btn_cancelar)
            botoes_box.add_widget(btn_adicionar)
            
            card.add_widget(titulo)
            card.add_widget(self.campo_quantidade_sugerido)
            card.add_widget(botoes_box)
            
            self.bottomsheet_quantidade = MDBottomSheet()
            self.bottomsheet_quantidade.add_widget(card)
            self.bottomsheet_quantidade.set_state("open")
            
        except Exception as e:
            logger.error(f"Erro ao mostrar dialog de quantidade: {e}")
            self.mostrar_snackbar("Erro ao abrir dialog.")

    def fechar_bottomsheet_quantidade(self, *args):
        """Fecha bottomsheet de quantidade"""
        try:
            self.bottomsheet_quantidade.set_state("close")
        except Exception as e:
            logger.error(f"Erro ao fechar bottomsheet: {e}")

    def confirmar_adicao_tipo_sugerido(self, *args):
        """Confirma adição do tipo sugerido com quantidade"""
        try:
            quantidade_text = self.campo_quantidade_sugerido.text.strip()
            if not quantidade_text or not quantidade_text.isdigit():
                self.mostrar_snackbar("Digite uma quantidade válida.")
                return
                
            quantidade = int(quantidade_text)
            if quantidade <= 0:
                self.mostrar_snackbar("Quantidade deve ser maior que zero.")
                return
            
            # Busca categoria e subcategoria do tipo para adicionar corretamente
            tipos = listar_tipos_produto_apk()
            tipo_info = next((t for t in tipos if t[0] == self.tipo_sugerido_id), None)
            
            if not tipo_info:
                self.mostrar_snackbar("Tipo de produto não encontrado.")
                return
            
            categoria_id = tipo_info[2] if len(tipo_info) > 2 else None
            subcategoria_id = tipo_info[3] if len(tipo_info) > 3 else None
            
            if not categoria_id or not subcategoria_id:
                self.mostrar_snackbar("Categoria ou subcategoria do tipo não encontrada.")
                return
            
            # Data atual para o item
            data_adicao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Adiciona item à lista com todos os parâmetros necessários
            sucesso = adicionar_item_lista_apk(
                self.lista_atual_visualizada_id,
                self.tipo_sugerido_id,
                categoria_id,
                subcategoria_id,
                quantidade,
                data_adicao
            )
            
            if sucesso:
                self.bottomsheet_quantidade.set_state("close")
                # Reaplica o filtro para atualizar a lista
                filtro_texto = self.filtro_texto_itens_lista.text.strip()
                self.atualizar_lista_compras_itens(self.lista_atual_visualizada_id, filtro_texto)
                # Atualiza o título da AppBar com novo total
                self.atualizar_titulo_appbar_lista()
                self.mostrar_snackbar("Tipo adicionado com sucesso!")
                logger.info(f"Tipo {self.tipo_sugerido_id} adicionado à lista com quantidade {quantidade}")
            else:
                self.mostrar_snackbar("Erro ao adicionar tipo à lista.")
                
        except Exception as e:
            logger.error(f"Erro ao confirmar adição do tipo: {e}")
            self.mostrar_snackbar("Erro ao adicionar tipo.")

    def atualizar_titulo_appbar_lista(self):
        """Atualiza o título da AppBar com o total de itens da lista"""
        try:
            if not hasattr(self, 'lista_atual_visualizada_id'):
                return
                
            # Busca informações da lista
            listas = listar_listas_apk()
            lista_info = next((l for l in listas if l[0] == self.lista_atual_visualizada_id), None)
            nome_lista = lista_info[1] if lista_info else f"Lista {self.lista_atual_visualizada_id}"
            
            # Conta total de itens na lista
            itens = listar_itens_lista_apk(self.lista_atual_visualizada_id)
            total_itens = len(itens)
            titulo_com_total = f"{nome_lista} ({total_itens} {'item' if total_itens == 1 else 'itens'})"
            
            # Encontra a tela atual e atualiza o título da AppBar
            screen_name = f"itens_lista_{self.lista_atual_visualizada_id}"
            if self.screen_manager.has_screen(screen_name):
                screen = self.screen_manager.get_screen(screen_name)
                # Encontra o primeiro widget BoxLayout (layout principal da tela)
                if hasattr(screen, 'children') and screen.children:
                    main_layout = screen.children[0]
                    # Encontra a AppBar (primeiro widget do layout)
                    if hasattr(main_layout, 'children') and main_layout.children:
                        appbar = main_layout.children[-1]  # AppBar é adicionada primeiro, então está no final da lista
                        if hasattr(appbar, 'children') and len(appbar.children) >= 2:
                            # O título está no meio da AppBar
                            title_container = appbar.children[1]  # Segundo elemento é o título
                            if hasattr(title_container, 'children') and title_container.children:
                                title_widget = title_container.children[0]
                                if hasattr(title_widget, 'text'):
                                    title_widget.text = titulo_com_total
                                    logger.info(f"Título da AppBar atualizado: {titulo_com_total}")
                                    
        except Exception as e:
            logger.error(f"Erro ao atualizar título da AppBar: {e}")

    # --- Telas de visualização melhoradas ---
    def show_itens_lista_screen(self, *args):
        """Exibe tela de itens da lista selecionada"""
        try:
            selecionados = [lista_id for checkbox, lista_id in self.listas_checkbox_refs if checkbox.active]
            if len(selecionados) != 1:
                self.mostrar_snackbar("Selecione apenas uma lista para ver os itens.")
                return
            
            lista_id = selecionados[0]
            screen_name = f"itens_lista_{lista_id}"
            
            # Remove tela antiga se existir
            self.remover_tela_segura(screen_name)
            
            tela = self.criar_tela_itens_lista(lista_id)
            self.screen_manager.add_widget(tela)
            self.screen_manager.current = screen_name
            
            logger.info(f"Exibindo itens da lista {lista_id}")
        except Exception as e:
            logger.error(f"Erro ao exibir itens da lista: {e}")
            self.mostrar_snackbar("Erro ao abrir lista de itens.")

    def criar_tela_itens_lista(self, lista_id):
        """Cria tela de itens da lista com controles melhorados e filtro"""
        try:
            # Armazena o ID da lista para uso posterior
            self.lista_atual_visualizada_id = lista_id
            
            self.itens_list = MDList()
            self.atualizar_lista_compras_itens(lista_id)

            def voltar_para_listas(x):
                """Volta para tela de listas de forma segura"""
                try:
                    self.screen_manager.current = "listas"
                    screen_name = f"itens_lista_{lista_id}"
                    self.remover_tela_segura(screen_name)
                except Exception as e:
                    logger.error(f"Erro ao voltar para listas: {e}")

            # Busca nome da lista para o título
            try:
                listas = listar_listas_apk()
                lista_info = next((l for l in listas if l[0] == lista_id), None)
                nome_lista = lista_info[1] if lista_info else f"Lista {lista_id}"
                
                # Conta total de itens na lista
                itens = listar_itens_lista_apk(lista_id)
                total_itens = len(itens)
                titulo_com_total = f"{nome_lista} ({total_itens} {'item' if total_itens == 1 else 'itens'})"
            except:
                nome_lista = f"Lista {lista_id}"
                titulo_com_total = nome_lista

            # === APPBAR ===
            appbar = MDTopAppBar(
                MDTopAppBarLeadingButtonContainer(
                    MDActionTopAppBarButton(
                        icon="arrow-left",
                        on_release=voltar_para_listas,
                    ),
                ),
                MDTopAppBarTitle(
                    text=titulo_com_total,
                    halign="center",
                ),
                MDTopAppBarTrailingButtonContainer(
                    MDActionTopAppBarButton(
                        icon="plus",
                        on_release=lambda x: self.show_adicionar_item_lista_screen(lista_id),
                    ),
                    MDActionTopAppBarButton(
                        icon="pencil",
                        on_release=lambda x: self.show_editar_item_lista_screen(lista_id),
                    ),
                    MDActionTopAppBarButton(
                        icon="delete",
                        on_release=lambda x: self.excluir_item_lista(lista_id),
                    ),
                ),
                type="small",
                size_hint_y=None,
                height=dp(64),
            )

            # === BARRA DE FILTRO ===
            filtro_box = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(56),
                padding=(dp(16), dp(8), dp(16), dp(8)),
                spacing=dp(8)
            )
            
            self.filtro_texto_itens_lista = MDTextField(
                hint_text="Filtrar itens da lista",
                size_hint_x=0.8,
                multiline=False,
                size_hint_y=None,
                height=dp(40),
                pos_hint={"center_y": 0.5},
                on_text_validate=self.aplicar_filtro_itens_lista,
                on_text=self.filtro_tempo_real_itens_lista  # Filtro em tempo real
            )
            
            btn_filtrar_itens = MDActionTopAppBarButton(
                icon="filter",
                on_release=self.aplicar_filtro_itens_lista,
                size_hint_y=None,
                height=dp(40),
                size_hint_x=0.1
            )
            
            btn_limpar_filtro_itens = MDActionTopAppBarButton(
                icon="close",
                on_release=self.limpar_filtro_itens_lista,
                size_hint_y=None,
                height=dp(40),
                size_hint_x=0.1
            )
            
            filtro_box.add_widget(self.filtro_texto_itens_lista)
            filtro_box.add_widget(btn_filtrar_itens)
            filtro_box.add_widget(btn_limpar_filtro_itens)

            # === SCROLL PARA LISTA ===
            scroll = MDScrollView()
            scroll.add_widget(self.itens_list)

            # === LAYOUT PRINCIPAL ===
            layout = BoxLayout(orientation="vertical")
            layout.add_widget(appbar)
            layout.add_widget(filtro_box)  # Adiciona filtro abaixo da AppBar
            layout.add_widget(scroll)
            
            return MDScreen(layout, name=f"itens_lista_{lista_id}")
            
        except Exception as e:
            logger.error(f"Erro ao criar tela de itens da lista {lista_id}: {e}")
            return None

    def show_historico_precos_screen(self, *args):
        """Exibe histórico de preços do produto selecionado"""
        try:
            selecionados = [produto_id for checkbox, produto_id in self.checkbox_refs if checkbox.active]
            if len(selecionados) != 1:
                self.mostrar_snackbar("Selecione apenas um produto para ver o histórico.")
                return
            
            produto_id = selecionados[0]
            screen_name = f"historico_precos_{produto_id}"
            
            # Remove tela antiga se existir
            self.remover_tela_segura(screen_name)
            
            tela = self.criar_tela_historico_precos(produto_id)
            if tela:
                self.screen_manager.add_widget(tela)
                self.screen_manager.current = screen_name
                logger.info(f"Exibindo histórico de preços do produto {produto_id}")
            
        except Exception as e:
            logger.error(f"Erro ao exibir histórico de preços: {e}")
            self.mostrar_snackbar("Erro ao abrir histórico de preços.")

    def criar_tela_historico_precos(self, produto_id):
        """Cria tela de histórico de preços com tratamento completo"""
        try:
            historico = listar_historico_precos_apk(produto_id)
            supermercados = {s[0]: s[1] for s in listar_supermercados_apk()}

            # Busca nome do produto para título
            produtos = self.get_produtos_cached()
            produto = next((p for p in produtos if p[DatabaseFields.PRODUTO_ID] == produto_id), None)
            nome_produto = produto[DatabaseFields.PRODUTO_NOME] if produto else f"Produto {produto_id}"

            def voltar_para_produtos(x):
                """Volta para produtos de forma segura"""
                try:
                    self.screen_manager.current = "produtos"
                    screen_name = f"historico_precos_{produto_id}"
                    self.remover_tela_segura(screen_name)
                except Exception as e:
                    logger.error(f"Erro ao voltar para produtos: {e}")

            appbar = MDTopAppBar(
                MDTopAppBarLeadingButtonContainer(
                    MDActionTopAppBarButton(
                        icon="arrow-left",
                        on_release=voltar_para_produtos,
                    ),
                ),
                MDTopAppBarTitle(
                    text=str(nome_produto).upper(),
                    halign="center",
                ),
                type="small",
                size_hint_y=None,
                height=dp(64),
            )

            layout = BoxLayout(orientation="vertical")
            layout.add_widget(appbar)

            # Se não há histórico, mostra mensagem
            if not historico:
                label_vazio = MDLabel(
                    text="Nenhum registro de preço encontrado para este produto.",
                    halign="center",
                    theme_text_color="Primary",
                    size_hint_y=1,
                    padding=(dp(16), dp(16)),
                )
                layout.add_widget(label_vazio)
                Clock.schedule_once(lambda dt: self.mostrar_snackbar("Não há registro de preços para este produto."), 0.1)
            else:
                # Cria lista de histórico
                historico_list = MDList()
                
                # Ordena por data (mais recente primeiro)
                historico_ordenado = sorted(historico, key=lambda x: x[4], reverse=True)
                
                for registro in historico_ordenado:
                    _, _, supermercado_id, preco, data = registro
                    super_nome = supermercados.get(supermercado_id, f"Supermercado {supermercado_id}")
                    
                    item = MDListItem(
                        MDListItemHeadlineText(text=str(super_nome).upper()),
                        MDListItemSupportingText(text=f"R$ {preco:.2f}"),
                        MDListItemSupportingText(text=f"Data: {data}"),
                        padding=(dp(8), dp(8), dp(8), dp(8)),
                    )
                    historico_list.add_widget(item)
                
                scroll = MDScrollView()
                scroll.add_widget(historico_list)
                layout.add_widget(scroll)

            return MDScreen(layout, name=f"historico_precos_{produto_id}")
            
        except Exception as e:
            logger.error(f"Erro ao criar tela de histórico para produto {produto_id}: {e}")
            return None

    # --- Métodos de edição melhorados ---
    def show_editar_lista_screen(self, *args):
        """Exibe tela de edição de lista com validação"""
        try:
            selecionados = [lista_id for checkbox, lista_id in self.listas_checkbox_refs if checkbox.active]
            if len(selecionados) != 1:
                self.mostrar_snackbar("Selecione apenas uma lista para editar.")
                return
            
            lista_id = selecionados[0]
            screen_name = "editar_lista"
            
            # Remove tela antiga se existir
            self.remover_tela_segura(screen_name)
            
            tela = self.criar_tela_editar_lista(lista_id)
            if tela:
                self.screen_manager.add_widget(tela)
                self.screen_manager.current = screen_name
                logger.info(f"Editando lista {lista_id}")
                
        except Exception as e:
            logger.error(f"Erro ao abrir edição de lista: {e}")
            self.mostrar_snackbar("Erro ao abrir edição da lista.")

    def criar_tela_editar_lista(self, lista_id):
        """Cria tela de edição de lista com validação"""
        try:
            listas = listar_listas_apk()
            dados = next((l for l in listas if l[0] == lista_id), None)
            if not dados:
                logger.error(f"Lista {lista_id} não encontrada")
                self.mostrar_snackbar("Lista não encontrada.")
                return None

            _, nome, data_criacao = dados

            self.edit_nome_lista = MDTextField(
                text=nome, 
                hint_text="Digite o nome da lista"
            )
            self.edit_nome_lista.bind(text=self.forcar_maiusculas)
            
            self.edit_data_criacao_lista = MDTextField(
                text=data_criacao, 
                hint_text="Data de criação (AAAA-MM-DD)"
            )

            content = BoxLayout(
                orientation="vertical",
                spacing=dp(10),
                padding=dp(20),
                size_hint_y=None,
            )
            content.bind(minimum_height=content.setter("height"))

            content.add_widget(MDLabel(text="Nome", halign="left", theme_text_color="Primary"))
            content.add_widget(self.edit_nome_lista)
            content.add_widget(MDLabel(text="Data de Criação", halign="left", theme_text_color="Primary"))
            content.add_widget(self.edit_data_criacao_lista)

            scroll = MDScrollView()
            scroll.add_widget(content)

            appbar = MDTopAppBar(
                MDTopAppBarLeadingButtonContainer(
                    MDActionTopAppBarButton(
                        icon="arrow-left",
                        on_release=lambda x: self.voltar_para_listas_seguro(),
                    ),
                ),
                MDTopAppBarTitle(
                    text="Editar Lista",
                    halign="center",
                ),
                MDTopAppBarTrailingButtonContainer(
                    MDActionTopAppBarButton(
                        icon="content-save",
                        on_release=lambda x: self.salvar_edicao_lista(lista_id),
                    ),
                ),
                type="small",
                size_hint_y=None,
                height=dp(64),
            )

            layout = BoxLayout(orientation="vertical")
            layout.add_widget(appbar)
            layout.add_widget(scroll)

            return MDScreen(layout, name="editar_lista")
            
        except Exception as e:
            logger.error(f"Erro ao criar tela de edição de lista {lista_id}: {e}")
            return None

    def voltar_para_listas_seguro(self):
        """Volta para tela de listas de forma segura"""
        try:
            self.remover_tela_segura("editar_lista")
            self.screen_manager.current = "listas"
        except Exception as e:
            logger.error(f"Erro ao voltar para listas: {e}")

    def salvar_edicao_lista(self, lista_id):
        """Salva edição da lista com validação"""
        try:
            novo_nome = self.edit_nome_lista.text.strip()
            nova_data_criacao = self.edit_data_criacao_lista.text.strip()
            
            if not novo_nome:
                self.mostrar_snackbar("Nome da lista é obrigatório!")
                return
            
            alterar_lista_apk(lista_id, novo_nome, nova_data_criacao)
            self.invalidar_cache('listas')
            
            self.remover_tela_segura("editar_lista")
            self.screen_manager.current = "listas"
            self.mostrar_snackbar("Lista editada com sucesso!")
            
            # Atualiza lista de compras
            self.atualizar_lista_compras()
            logger.info(f"Lista {lista_id} editada com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao salvar edição da lista {lista_id}: {e}")
            self.mostrar_snackbar("Erro ao salvar alterações da lista.")

    # --- Métodos de exclusão otimizados ---
    def excluir_produto(self, *args):
        """Exclui produtos selecionados com confirmação e sistema de lixeira"""
        try:
            selecionados = [produto_id for checkbox, produto_id in self.checkbox_refs if checkbox.active]
            
            if not selecionados:
                # Se nenhum item está selecionado, abre a lixeira específica de produtos
                self.visualizar_lixeira('produto')
                return
            
            # Usa sistema genérico de confirmação
            self.criar_popup_confirmacao_exclusao_generico(
                selecionados, "produto", self.confirmar_exclusao_produtos
            )
                
        except Exception as e:
            logger.error(f"Erro ao iniciar exclusão de produtos: {e}")
            self.mostrar_snackbar("Erro ao excluir produtos.")

    def confirmar_exclusao_produtos(self, produtos_ids):
        """Confirma e executa exclusão dos produtos com sistema de lixeira"""
        try:
            produtos = listar_produtos_apk()
            excluidos = []
            refs_para_remover = []
            
            for produto_id in produtos_ids:
                try:
                    # Busca dados do produto para mover para lixeira
                    produto_data = next((p for p in produtos if p[0] == produto_id), None)
                    if produto_data:
                        # Prepara dados para lixeira (produto_data order: id, tipo_id, nome, marca, quantidade_embalagem, codigo_barras, categoria_id, subcategoria_id, imagem)
                        dados_produto = {
                            'id': produto_data[0],              # id
                            'tipo_produto_id': produto_data[1], # tipo_id
                            'nome': produto_data[2],            # nome
                            'marca': produto_data[3],           # marca
                            'quantidade': produto_data[4],      # quantidade_embalagem
                            'codigo_barras': produto_data[5],   # codigo_barras
                            'categoria_id': produto_data[6],    # categoria_id
                            'subcategoria_id': produto_data[7]  # subcategoria_id
                        }
                        
                        # Move para lixeira primeiro
                        if self.mover_para_lixeira(produto_id, 'produto', dados_produto):
                            # Depois exclui do banco principal
                            excluir_produto_apk(produto_id)
                            excluidos.append(produto_id)
                            # Encontra referência para remover
                            for checkbox, pid in self.checkbox_refs:
                                if pid == produto_id:
                                    refs_para_remover.append((checkbox, pid))
                                    break
                            logger.info(f"Produto {produto_id} movido para lixeira e excluído")
                        
                except Exception as e:
                    logger.error(f"Erro ao excluir produto {produto_id}: {e}")
            
            # Remove referências dos produtos excluídos
            for ref in refs_para_remover:
                checkbox, produto_id = ref
                # Limpa o estado visual do checkbox
                checkbox.active = False
                if ref in self.checkbox_refs:
                    self.checkbox_refs.remove(ref)
            
            # Invalida cache
            self.invalidar_cache('produtos')
            
            # Fecha popup e mostra resultado
            self.fechar_popup_confirmacao()
            
            if excluidos:
                self.mostrar_snackbar(f"{len(excluidos)} produto(s) excluído(s) e movido(s) para lixeira!")
                # Atualiza a lista
                self.atualizar_lista_produtos()
            else:
                self.mostrar_snackbar("Nenhum produto foi excluído.")
                
        except Exception as e:
            logger.error(f"Erro na confirmação de exclusão: {e}")
            self.mostrar_snackbar("Erro ao excluir produtos.")

    def excluir_supermercado(self, *args):
        """Exclui supermercados selecionados com confirmação e sistema de lixeira"""
        try:
            selecionados = [super_id for checkbox, super_id in self.super_checkbox_refs if checkbox.active]
            
            if not selecionados:
                # Se nenhum item está selecionado, abre a lixeira específica de supermercados
                self.visualizar_lixeira('supermercado')
                return
            
            # Usa sistema genérico de confirmação
            self.criar_popup_confirmacao_exclusao_generico(
                selecionados, "supermercado", self.confirmar_exclusao_supermercados
            )
                
        except Exception as e:
            logger.error(f"Erro ao iniciar exclusão de supermercados: {e}")
            self.mostrar_snackbar("Erro ao excluir supermercados.")

    def confirmar_exclusao_supermercados(self, supermercados_ids):
        """Confirma e executa exclusão dos supermercados com sistema de lixeira"""
        try:
            supermercados = listar_supermercados_apk()
            excluidos = []
            refs_para_remover = []
            
            for super_id in supermercados_ids:
                try:
                    # Busca dados do supermercado para mover para lixeira
                    super_data = next((s for s in supermercados if s[0] == super_id), None)
                    if super_data:
                        # Prepara dados para lixeira
                        dados_supermercado = {
                            'id': super_data[0],
                            'nome': super_data[1],
                            'bairro': super_data[2]
                        }
                        
                        # Move para lixeira primeiro
                        if self.mover_para_lixeira(super_id, 'supermercado', dados_supermercado):
                            # Depois exclui do banco principal
                            excluir_supermercado_apk(super_id)
                            excluidos.append(super_id)
                            # Encontra referência para remover
                            for checkbox, sid in self.super_checkbox_refs:
                                if sid == super_id:
                                    refs_para_remover.append((checkbox, sid))
                                    break
                            logger.info(f"Supermercado {super_id} movido para lixeira e excluído")
                        
                except Exception as e:
                    logger.error(f"Erro ao excluir supermercado {super_id}: {e}")
            
            # Remove referências
            for ref in refs_para_remover:
                checkbox, super_id = ref
                # Limpa o estado visual do checkbox
                checkbox.active = False
                if ref in self.super_checkbox_refs:
                    self.super_checkbox_refs.remove(ref)
            
            # Fecha popup e mostra resultado
            self.fechar_popup_confirmacao()
            
            if excluidos:
                self.mostrar_snackbar(f"{len(excluidos)} supermercado(s) excluído(s) e movido(s) para lixeira!")
                # Atualiza a lista
                self.atualizar_lista_supermercados()
            else:
                self.mostrar_snackbar("Nenhum supermercado foi excluído.")
                
        except Exception as e:
            logger.error(f"Erro na confirmação de exclusão: {e}")
            self.mostrar_snackbar("Erro ao excluir supermercados.")

    def excluir_lista(self, *args):
        """Exclui listas selecionadas com confirmação e sistema de lixeira"""
        try:
            selecionados = [lista_id for checkbox, lista_id in self.listas_checkbox_refs if checkbox.active]
            
            if not selecionados:
                # Se nenhum item está selecionado, abre a lixeira específica de listas
                self.visualizar_lixeira('lista')
                return
            
            # Usa sistema genérico de confirmação
            self.criar_popup_confirmacao_exclusao_generico(
                selecionados, "lista", self.confirmar_exclusao_listas
            )
                
        except Exception as e:
            logger.error(f"Erro ao iniciar exclusão de listas: {e}")
            self.mostrar_snackbar("Erro ao excluir listas.")

    def confirmar_exclusao_listas(self, listas_ids):
        """Confirma e executa exclusão das listas com sistema de lixeira"""
        try:
            listas = listar_listas_apk()
            excluidos = []
            refs_para_remover = []
            
            for lista_id in listas_ids:
                try:
                    # Busca dados da lista para mover para lixeira
                    lista_data = next((l for l in listas if l[0] == lista_id), None)
                    if lista_data:
                        # Prepara dados para lixeira
                        dados_lista = {
                            'id': lista_data[0],
                            'nome': lista_data[1],
                            'data_criacao': lista_data[2]
                        }
                        
                        # Move para lixeira primeiro
                        if self.mover_para_lixeira(lista_id, 'lista', dados_lista):
                            # Depois exclui do banco principal
                            excluir_lista_apk(lista_id)
                            excluidos.append(lista_id)
                            # Encontra referência para remover
                            for checkbox, lid in self.listas_checkbox_refs:
                                if lid == lista_id:
                                    refs_para_remover.append((checkbox, lid))
                                    break
                            logger.info(f"Lista {lista_id} movida para lixeira e excluída")
                        
                except Exception as e:
                    logger.error(f"Erro ao excluir lista {lista_id}: {e}")
            
            # Remove referências
            for ref in refs_para_remover:
                checkbox, lista_id = ref
                # Limpa o estado visual do checkbox
                checkbox.active = False
                if ref in self.listas_checkbox_refs:
                    self.listas_checkbox_refs.remove(ref)
            
            # Fecha popup e mostra resultado
            self.fechar_popup_confirmacao()
            
            if excluidos:
                self.mostrar_snackbar(f"{len(excluidos)} lista(s) excluída(s) e movida(s) para lixeira!")
                # Atualiza a lista
                self.atualizar_lista_compras()
            else:
                self.mostrar_snackbar("Nenhuma lista foi excluída.")
                
        except Exception as e:
            logger.error(f"Erro na confirmação de exclusão: {e}")
            self.mostrar_snackbar("Erro ao excluir listas.")
            
            if excluidos:
                self.mostrar_snackbar(f"{len(excluidos)} lista(s) excluída(s)!")
            else:
                self.mostrar_snackbar("Nenhuma lista selecionada para exclusão.")
                
        except Exception as e:
            logger.error(f"Erro geral na exclusão de listas: {e}")
            self.mostrar_snackbar("Erro ao excluir listas.")

    def excluir_item_lista(self, lista_id):
        """Exclui itens da lista selecionados"""
        try:
            excluidos = []
            refs_para_remover = []
            
            for checkbox, item_id in self.itens_checkbox_refs:
                if checkbox.active:
                    try:
                        excluir_item_lista_apk(item_id)
                        parent = checkbox.parent
                        if parent and parent.parent:
                            parent.parent.remove_widget(parent)
                        excluidos.append(item_id)
                        refs_para_remover.append((checkbox, item_id))
                        logger.info(f"Item {item_id} excluído da lista {lista_id}")
                    except Exception as e:
                        logger.error(f"Erro ao excluir item {item_id}: {e}")
            
            # Remove referências
            for ref in refs_para_remover:
                if ref in self.itens_checkbox_refs:
                    self.itens_checkbox_refs.remove(ref)
            
            if excluidos:
                # Atualiza o título da AppBar com novo total
                self.atualizar_titulo_appbar_lista()
                self.mostrar_snackbar(f"{len(excluidos)} item(ns) excluído(s)!")
            else:
                self.mostrar_snackbar("Nenhum item selecionado para exclusão.")
                
        except Exception as e:
            logger.error(f"Erro geral na exclusão de itens da lista {lista_id}: {e}")
            self.mostrar_snackbar("Erro ao excluir itens da lista.")

    # --- Métodos auxiliares para telas de itens ---
    def show_adicionar_item_lista_screen(self, lista_id):
        """Exibe tela para adicionar item à lista"""
        try:
            self.show_form_adicionar_item_lista(lista_id)
            logger.info(f"Tela de adicionar item à lista {lista_id} aberta")
        except Exception as e:
            logger.error(f"Erro ao abrir adição de item: {e}")
            self.mostrar_snackbar("Erro ao abrir formulário de item.")

    def show_editar_item_lista_screen(self, lista_id):
        """Exibe tela para editar item da lista"""
        try:
            selecionados = [item_id for checkbox, item_id in self.itens_checkbox_refs if checkbox.active]
            if len(selecionados) != 1:
                self.mostrar_snackbar("Selecione apenas um item para editar.")
                return
            
            item_id = selecionados[0]
            self.show_form_editar_item_lista(lista_id, item_id)
            logger.info(f"Tela de editar item {item_id} da lista {lista_id} aberta")
        except Exception as e:
            logger.error(f"Erro ao abrir edição de item: {e}")
            self.mostrar_snackbar("Erro ao abrir edição do item.")

    # === SISTEMA UNIFICADO PARA ADICIONAR ITENS À LISTA ===
    def show_form_adicionar_item_lista(self, lista_id):
        """Exibe formulário para adicionar item à lista de compras"""
        try:
            
            # Armazena ID da lista para uso posterior
            self.lista_atual_id = lista_id
            
            # Busca informações da lista para exibir no título
            listas = listar_listas_apk()
            lista_info = next((l for l in listas if l[0] == lista_id), None)
            nome_lista = lista_info[1] if lista_info else f"Lista {lista_id}"
            
            # === CAMPOS DO FORMULÁRIO ===
            # Campo para Tipo de Produto (BottomSheet) - obrigatório
            self.campo_tipo_item_lista = MDTextField(
                text="Selecione o tipo de produto",
                readonly=True,
                hint_text="Tipo de produto"
            )
            tipos_produto = listar_tipos_produto_apk()
            self.campo_tipo_item_lista.bind(on_touch_down=lambda instance, touch: self._handle_tipo_item_lista_touch(instance, touch, tipos_produto))
            
            # Campo para Quantidade - editável
            self.campo_quantidade_item_lista = MDTextField(
                hint_text="Quantidade do item",
                text="1",  # Valor padrão
                on_text_validate=lambda instance: setattr(self.campo_quantidade_item_lista, 'focus', False)
            )
            
            # Campos informativos (preenchidos automaticamente ao selecionar tipo)
            self.campo_categoria_item_lista = MDTextField(
                text="Categoria será definida automaticamente",
                readonly=True,
                hint_text="Categoria",
                disabled=True
            )
            
            self.campo_subcategoria_item_lista = MDTextField(
                text="Subcategoria será definida automaticamente", 
                readonly=True,
                hint_text="Subcategoria",
                disabled=True
            )
            
            # Variáveis para armazenar dados selecionados
            self.tipo_item_lista_selecionado_id = None
            self.categoria_item_lista_id = None
            self.subcategoria_item_lista_id = None
            
            # === LAYOUT DO FORMULÁRIO ===
            content = BoxLayout(
                orientation="vertical",
                spacing=dp(15),
                padding=dp(20),
                size_hint_y=None,
            )
            content.bind(minimum_height=content.setter("height"))
            
            content.add_widget(MDLabel(text="Tipo de Produto", theme_text_color="Primary"))
            content.add_widget(self.campo_tipo_item_lista)
            content.add_widget(MDLabel(text="Quantidade", theme_text_color="Primary"))
            content.add_widget(self.campo_quantidade_item_lista)
            content.add_widget(MDLabel(text="Categoria (Automática)", theme_text_color="Primary"))
            content.add_widget(self.campo_categoria_item_lista)
            content.add_widget(MDLabel(text="Subcategoria (Automática)", theme_text_color="Primary"))
            content.add_widget(self.campo_subcategoria_item_lista)

            scroll = MDScrollView()
            scroll.add_widget(content)

            # === APPBAR ===
            appbar = MDTopAppBar(
                MDTopAppBarLeadingButtonContainer(
                    MDActionTopAppBarButton(
                        icon="arrow-left",
                        on_release=lambda x: self.voltar_para_itens_lista_seguro(),
                    ),
                ),
                MDTopAppBarTitle(
                    text=f"Adicionar Item - {nome_lista}",
                    halign="center",
                ),
                MDTopAppBarTrailingButtonContainer(
                    MDActionTopAppBarButton(
                        icon="content-save",
                        on_release=lambda x: self.salvar_item_lista(),
                    ),
                ),
                type="small",
                size_hint_y=None,
                height=dp(64),
            )

            layout = BoxLayout(orientation="vertical")
            layout.add_widget(appbar)
            layout.add_widget(scroll)

            # === GERENCIAMENTO DE TELA ===
            screen_name = "adicionar_item_lista"
            
            # Remove tela antiga se existir
            self.remover_tela_segura(screen_name)
            
            # Cria a tela
            tela = MDScreen(layout, name=screen_name)
            
            # Adiciona ao screen manager e faz a transição
            self.screen_manager.add_widget(tela)
            self.screen_manager.current = screen_name
            
            # Define foco inicial no tipo de produto
            Clock.schedule_once(lambda dt: setattr(self.campo_tipo_item_lista, 'focus', True), 0.2)
            
            logger.info(f"Formulário de adicionar item à lista {lista_id} criado")
            
        except Exception as e:
            logger.error(f"Erro ao criar formulário de item: {e}")
            self.mostrar_snackbar("Erro ao abrir formulário de item.")

    def _handle_tipo_item_lista_touch(self, instance, touch, tipos_produto):
        """Handler para evento de toque no campo tipo de produto do item"""
        if instance.collide_point(*touch.pos):
            self.abrir_bottomsheet_tipo_item_lista(tipos_produto)
            return True
        return False

    def abrir_bottomsheet_tipo_item_lista(self, tipos_produto):
        """Abre BottomSheet para seleção de tipo de produto para item da lista"""
        try:
            # Container principal
            container = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(16))
            
            # Container horizontal para filtro e botão
            filtro_container = BoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(56))
            
            # Campo de filtro
            self.filtro_tipo_item_lista = MDTextField(
                hint_text="Digite para filtrar tipos...",
                size_hint_x=0.8
            )
            self.filtro_tipo_item_lista.bind(text=lambda instance, text: self.filtrar_tipos_item_lista_bottomsheet(text))
            filtro_container.add_widget(self.filtro_tipo_item_lista)
            
            # Botão para adicionar novo tipo
            botao_novo_tipo_item = MDActionTopAppBarButton(
                icon="plus",
                theme_icon_color="Custom",
                icon_color="green",
                size_hint_x=0.2,
                on_release=lambda x: self.abrir_dialog_novo_tipo_item_lista()
            )
            filtro_container.add_widget(botao_novo_tipo_item)
            
            container.add_widget(filtro_container)
            
            # Lista de tipos
            self.lista_tipos_item_lista_filtrada = MDList()
            self.tipos_item_lista_dados = tipos_produto  # Armazena para uso nos filtros
            self.carregar_tipos_item_lista_bottomsheet(tipos_produto)
            
            # ScrollView para a lista
            scroll = MDScrollView()
            scroll.add_widget(self.lista_tipos_item_lista_filtrada)
            container.add_widget(scroll)
            
            # Cria e configura o BottomSheet
            self.bottomsheet_tipo_item_lista = MDBottomSheet()
            self.bottomsheet_tipo_item_lista.add_widget(container)
            
            # Adiciona ao root para exibir
            self.root.add_widget(self.bottomsheet_tipo_item_lista)
            self.bottomsheet_tipo_item_lista.set_state("open")
            
            # Foca no campo de filtro
            Clock.schedule_once(lambda dt: setattr(self.filtro_tipo_item_lista, 'focus', True), 0.2)
            
        except Exception as e:
            logger.error(f"Erro ao abrir BottomSheet de tipos para item: {e}")
            self.mostrar_snackbar("Erro ao abrir seleção de tipos.")

    def carregar_tipos_item_lista_bottomsheet(self, tipos_produto, filtro=""):
        """Carrega tipos no BottomSheet com filtro opcional e ordenação alfabética"""
        try:
            self.lista_tipos_item_lista_filtrada.clear_widgets()
            
            # Filtra e ordena alfabeticamente
            tipos_filtrados = []
            for tipo in tipos_produto:
                tipo_nome = str(tipo[1]).upper()
                # Aplica filtro se fornecido
                if not filtro or filtro.upper() in tipo_nome:
                    tipos_filtrados.append((tipo[0], tipo_nome, tipo[1], tipo[2], tipo[3]))  # id, nome_upper, nome_original, categoria_id, subcategoria_id
            
            # Ordena alfabeticamente pelo nome
            tipos_filtrados.sort(key=lambda x: x[1])
            
            # Adiciona itens ordenados à lista
            for tipo_id, tipo_nome_upper, tipo_nome_original, categoria_id, subcategoria_id in tipos_filtrados:
                item = MDListItem(
                    MDListItemHeadlineText(text=tipo_nome_upper),
                    on_release=lambda x, t_id=tipo_id, nome=tipo_nome_original, cat_id=categoria_id, sub_id=subcategoria_id: self.selecionar_tipo_item_lista_bottomsheet(t_id, nome, cat_id, sub_id)
                )
                self.lista_tipos_item_lista_filtrada.add_widget(item)
                    
        except Exception as e:
            logger.error(f"Erro ao carregar tipos filtrados para item: {e}")

    def filtrar_tipos_item_lista_bottomsheet(self, filtro):
        """Filtra tipos no BottomSheet"""
        try:
            self.carregar_tipos_item_lista_bottomsheet(self.tipos_item_lista_dados, filtro)
        except Exception as e:
            logger.error(f"Erro ao filtrar tipos para item: {e}")

    def selecionar_tipo_item_lista_bottomsheet(self, tipo_id, tipo_nome, categoria_id, subcategoria_id):
        """Seleciona tipo de produto para item da lista via BottomSheet"""
        try:
            # Armazena dados selecionados
            self.tipo_item_lista_selecionado_id = tipo_id
            self.categoria_item_lista_id = categoria_id
            self.subcategoria_item_lista_id = subcategoria_id
            
            # Atualiza campos de exibição
            self.campo_tipo_item_lista.text = str(tipo_nome).upper()
            
            # Busca e exibe categoria e subcategoria
            categorias = listar_categorias_apk()
            subcategorias_todas = []
            for cat in listar_categorias_apk():
                subcategorias_todas.extend(listar_subcategorias_apk(cat[0]))
            
            categoria_nome = next((c[1] for c in categorias if c[0] == categoria_id), "Categoria não encontrada")
            subcategoria_nome = next((s[1] for s in subcategorias_todas if s[0] == subcategoria_id), "Subcategoria não encontrada")
            
            self.campo_categoria_item_lista.text = str(categoria_nome).upper()
            self.campo_subcategoria_item_lista.text = str(subcategoria_nome).upper()
            
            # Fecha o BottomSheet
            self.bottomsheet_tipo_item_lista.set_state("close")
            if self.bottomsheet_tipo_item_lista.parent:
                self.bottomsheet_tipo_item_lista.parent.remove_widget(self.bottomsheet_tipo_item_lista)
            
            # Foca no campo quantidade após seleção
            Clock.schedule_once(lambda dt: setattr(self.campo_quantidade_item_lista, 'focus', True), 0.1)
            
            logger.info(f"Tipo selecionado para item: {tipo_id} - {tipo_nome}")
            
        except Exception as e:
            logger.error(f"Erro ao selecionar tipo para item: {e}")

    def abrir_dialog_novo_tipo_item_lista(self):
        """Abre dialog para criar novo tipo de produto a partir do contexto de item da lista"""
        try:
            # Captura o valor do filtro atual (se houver)
            valor_filtro = ""
            if hasattr(self, 'filtro_tipo_item_lista') and self.filtro_tipo_item_lista.text:
                valor_filtro = self.filtro_tipo_item_lista.text.strip().upper()
                
            # Fecha o BottomSheet atual
            if hasattr(self, 'bottomsheet_tipo_item_lista') and self.bottomsheet_tipo_item_lista.parent:
                self.bottomsheet_tipo_item_lista.set_state("close")
                self.bottomsheet_tipo_item_lista.parent.remove_widget(self.bottomsheet_tipo_item_lista)
            
            # Cria tela de cadastro de novo tipo com pré-preenchimento
            # Marca que veio do contexto de item da lista
            self.contexto_novo_tipo = "item_lista"
            self.criar_tela_novo_tipo_produto(valor_preenchimento=valor_filtro)
            
        except Exception as e:
            logger.error(f"Erro ao abrir dialog de novo tipo a partir de item: {e}")

    def salvar_item_lista(self):
        """Salva o item na lista de compras"""
        try:
            
            # Validações
            if not self.tipo_item_lista_selecionado_id:
                self.mostrar_snackbar("Selecione um tipo de produto!")
                return
                
            quantidade = self.campo_quantidade_item_lista.text.strip()
            if not quantidade:
                self.mostrar_snackbar("Quantidade é obrigatória!")
                return
                
            try:
                quantidade_num = float(quantidade)
                if quantidade_num <= 0:
                    self.mostrar_snackbar("Quantidade deve ser maior que zero!")
                    return
            except ValueError:
                self.mostrar_snackbar("Quantidade deve ser um número válido!")
                return
            
            # Salva no banco de dados
            data_adicao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sucesso = adicionar_item_lista_apk(
                self.lista_atual_id,
                self.tipo_item_lista_selecionado_id,
                self.categoria_item_lista_id,
                self.subcategoria_item_lista_id,
                quantidade,
                data_adicao
            )
            
            if sucesso:
                self.mostrar_snackbar("Item adicionado à lista com sucesso!")
                
                # Volta para a tela de itens da lista
                self.voltar_para_itens_lista_seguro()
                
                # Atualiza o título da AppBar com novo total
                self.atualizar_titulo_appbar_lista()
                
                logger.info(f"Item adicionado à lista {self.lista_atual_id}: tipo {self.tipo_item_lista_selecionado_id}, qtd {quantidade}")
            else:
                self.mostrar_snackbar("Erro ao salvar item na lista.")
                
        except Exception as e:
            logger.error(f"Erro ao salvar item na lista: {e}")
            self.mostrar_snackbar("Erro ao salvar item na lista.")

    def voltar_para_itens_lista_seguro(self):
        """Volta para tela de itens da lista de forma segura"""
        try:
            # Remove a tela atual
            self.remover_tela_segura("adicionar_item_lista")
            self.remover_tela_segura("editar_item_lista")
            
            # Volta para a tela de itens da lista
            screen_name = f"itens_lista_{self.lista_atual_id}"
            if self.screen_manager.has_screen(screen_name):
                self.screen_manager.current = screen_name
                # Atualiza a lista de itens mantendo filtro se houver
                if hasattr(self, 'itens_list'):
                    filtro_atual = ""
                    if hasattr(self, 'filtro_texto_itens_lista') and self.filtro_texto_itens_lista.text:
                        filtro_atual = self.filtro_texto_itens_lista.text.strip()
                    self.atualizar_lista_compras_itens(self.lista_atual_id, filtro_atual)
            else:
                # Se a tela não existir, recria ela
                self.show_itens_lista_screen()
                
        except Exception as e:
            logger.error(f"Erro ao voltar para itens da lista: {e}")
            # Em caso de erro, volta para listas como fallback
            self.screen_manager.current = "listas"

    # === MÉTODOS AUXILIARES PARA NOVO TIPO NO CONTEXTO DE ITEM ===

    def show_form_editar_item_lista(self, lista_id, item_id):
        """Exibe formulário para editar item da lista de compras"""
        try:
            # Armazena IDs para uso posterior
            self.lista_atual_id = lista_id
            self.item_atual_id = item_id
            
            # Busca dados do item atual
            itens = listar_itens_lista_apk(lista_id)
            item_atual = next((item for item in itens if item[0] == item_id), None)
            
            if not item_atual:
                self.mostrar_snackbar("Item não encontrado.")
                return
            
            # Extrai dados do item: [id, lista_id, tipo_id, categoria_id, subcategoria_id, quantidade, data_adicao, tipo_nome, categoria_nome, subcategoria_nome]
            _, _, tipo_id_atual, categoria_id_atual, subcategoria_id_atual, quantidade_atual, _, tipo_nome_atual, categoria_nome_atual, subcategoria_nome_atual = item_atual
            
            # Busca informações da lista para exibir no título
            listas = listar_listas_apk()
            lista_info = next((l for l in listas if l[0] == lista_id), None)
            nome_lista = lista_info[1] if lista_info else f"Lista {lista_id}"
            
            # === CAMPOS DO FORMULÁRIO ===
            # Campo para Tipo de Produto (BottomSheet) - editável
            self.campo_tipo_item_lista_edit = MDTextField(
                text=str(tipo_nome_atual).upper(),
                readonly=True,
                hint_text="Tipo de produto"
            )
            tipos_produto = listar_tipos_produto_apk()
            self.campo_tipo_item_lista_edit.bind(on_touch_down=lambda instance, touch: self._handle_tipo_item_lista_edit_touch(instance, touch, tipos_produto))
            
            # Campo para Quantidade - editável
            self.campo_quantidade_item_lista_edit = MDTextField(
                hint_text="Quantidade do item",
                text=str(quantidade_atual),
                on_text_validate=lambda instance: setattr(self.campo_quantidade_item_lista_edit, 'focus', False)
            )
            
            # Campos informativos (preenchidos automaticamente ao selecionar tipo)
            self.campo_categoria_item_lista_edit = MDTextField(
                text=str(categoria_nome_atual).upper(),
                readonly=True,
                hint_text="Categoria",
                disabled=True
            )
            
            self.campo_subcategoria_item_lista_edit = MDTextField(
                text=str(subcategoria_nome_atual).upper(),
                readonly=True,
                hint_text="Subcategoria", 
                disabled=True
            )
            
            # Variáveis para armazenar dados selecionados (inicializa com valores atuais)
            self.tipo_item_lista_edit_selecionado_id = tipo_id_atual
            self.categoria_item_lista_edit_id = categoria_id_atual
            self.subcategoria_item_lista_edit_id = subcategoria_id_atual
            
            # Guarda os IDs originais para comparação
            self.tipo_item_lista_original_id = tipo_id_atual
            
            # === LAYOUT DO FORMULÁRIO ===
            content = BoxLayout(
                orientation="vertical",
                spacing=dp(15),
                padding=dp(20),
                size_hint_y=None,
            )
            content.bind(minimum_height=content.setter("height"))
            
            content.add_widget(MDLabel(text="Tipo de Produto", theme_text_color="Primary"))
            content.add_widget(self.campo_tipo_item_lista_edit)
            content.add_widget(MDLabel(text="Quantidade", theme_text_color="Primary"))
            content.add_widget(self.campo_quantidade_item_lista_edit)
            content.add_widget(MDLabel(text="Categoria (Automática)", theme_text_color="Primary"))
            content.add_widget(self.campo_categoria_item_lista_edit)
            content.add_widget(MDLabel(text="Subcategoria (Automática)", theme_text_color="Primary"))
            content.add_widget(self.campo_subcategoria_item_lista_edit)

            scroll = MDScrollView()
            scroll.add_widget(content)

            # === APPBAR ===
            appbar = MDTopAppBar(
                MDTopAppBarLeadingButtonContainer(
                    MDActionTopAppBarButton(
                        icon="arrow-left",
                        on_release=lambda x: self.voltar_para_itens_lista_seguro(),
                    ),
                ),
                MDTopAppBarTitle(
                    text=f"Editar Item - {nome_lista}",
                    halign="center",
                ),
                MDTopAppBarTrailingButtonContainer(
                    MDActionTopAppBarButton(
                        icon="content-save",
                        on_release=lambda x: self.salvar_edicao_item_lista(),
                    ),
                ),
                type="small",
                size_hint_y=None,
                height=dp(64),
            )

            layout = BoxLayout(orientation="vertical")
            layout.add_widget(appbar)
            layout.add_widget(scroll)

            # === GERENCIAMENTO DE TELA ===
            screen_name = "editar_item_lista"
            
            # Remove tela antiga se existir
            self.remover_tela_segura(screen_name)
            
            # Cria a tela
            tela = MDScreen(layout, name=screen_name)
            
            # Adiciona ao screen manager e faz a transição
            self.screen_manager.add_widget(tela)
            self.screen_manager.current = screen_name
            
            # Define foco inicial na quantidade
            Clock.schedule_once(lambda dt: setattr(self.campo_quantidade_item_lista_edit, 'focus', True), 0.2)
            
            logger.info(f"Formulário de editar item {item_id} da lista {lista_id} criado")
            
        except Exception as e:
            logger.error(f"Erro ao criar formulário de edição de item: {e}")
            self.mostrar_snackbar("Erro ao abrir formulário de edição.")

    def _handle_tipo_item_lista_edit_touch(self, instance, touch, tipos_produto):
        """Handler para evento de toque no campo tipo de produto na edição do item"""
        if instance.collide_point(*touch.pos):
            self.abrir_bottomsheet_tipo_item_lista_edit(tipos_produto)
            return True
        return False

    def abrir_bottomsheet_tipo_item_lista_edit(self, tipos_produto):
        """Abre BottomSheet para seleção de tipo de produto na edição de item da lista"""
        try:
            # Container principal
            container = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(16))
            
            # Container horizontal para filtro e botão
            filtro_container = BoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(56))
            
            # Campo de filtro
            self.filtro_tipo_item_lista_edit = MDTextField(
                hint_text="Digite para filtrar tipos...",
                size_hint_x=0.8
            )
            self.filtro_tipo_item_lista_edit.bind(text=lambda instance, text: self.filtrar_tipos_item_lista_edit_bottomsheet(text))
            filtro_container.add_widget(self.filtro_tipo_item_lista_edit)
            
            # Botão para adicionar novo tipo
            botao_novo_tipo_item_edit = MDActionTopAppBarButton(
                icon="plus",
                theme_icon_color="Custom",
                icon_color="green",
                size_hint_x=0.2,
                on_release=lambda x: self.abrir_dialog_novo_tipo_item_lista_edit()
            )
            filtro_container.add_widget(botao_novo_tipo_item_edit)
            
            container.add_widget(filtro_container)
            
            # Lista de tipos
            self.lista_tipos_item_lista_edit_filtrada = MDList()
            self.tipos_item_lista_edit_dados = tipos_produto  # Armazena para uso nos filtros
            self.carregar_tipos_item_lista_edit_bottomsheet(tipos_produto)
            
            # ScrollView para a lista
            scroll = MDScrollView()
            scroll.add_widget(self.lista_tipos_item_lista_edit_filtrada)
            container.add_widget(scroll)
            
            # Cria e configura o BottomSheet
            self.bottomsheet_tipo_item_lista_edit = MDBottomSheet()
            self.bottomsheet_tipo_item_lista_edit.add_widget(container)
            
            # Adiciona ao root para exibir
            self.root.add_widget(self.bottomsheet_tipo_item_lista_edit)
            self.bottomsheet_tipo_item_lista_edit.set_state("open")
            
            # Foca no campo de filtro
            Clock.schedule_once(lambda dt: setattr(self.filtro_tipo_item_lista_edit, 'focus', True), 0.2)
            
        except Exception as e:
            logger.error(f"Erro ao abrir BottomSheet de tipos para edição de item: {e}")
            self.mostrar_snackbar("Erro ao abrir seleção de tipos.")

    def carregar_tipos_item_lista_edit_bottomsheet(self, tipos_produto, filtro=""):
        """Carrega tipos no BottomSheet de edição com filtro opcional e ordenação alfabética"""
        try:
            self.lista_tipos_item_lista_edit_filtrada.clear_widgets()
            
            # Filtra e ordena alfabeticamente
            tipos_filtrados = []
            for tipo in tipos_produto:
                tipo_nome = str(tipo[1]).upper()
                # Aplica filtro se fornecido
                if not filtro or filtro.upper() in tipo_nome:
                    tipos_filtrados.append((tipo[0], tipo_nome, tipo[1], tipo[2], tipo[3]))  # id, nome_upper, nome_original, categoria_id, subcategoria_id
            
            # Ordena alfabeticamente pelo nome
            tipos_filtrados.sort(key=lambda x: x[1])
            
            # Adiciona itens ordenados à lista
            for tipo_id, tipo_nome_upper, tipo_nome_original, categoria_id, subcategoria_id in tipos_filtrados:
                item = MDListItem(
                    MDListItemHeadlineText(text=tipo_nome_upper),
                    on_release=lambda x, t_id=tipo_id, nome=tipo_nome_original, cat_id=categoria_id, sub_id=subcategoria_id: self.selecionar_tipo_item_lista_edit_bottomsheet(t_id, nome, cat_id, sub_id)
                )
                self.lista_tipos_item_lista_edit_filtrada.add_widget(item)
                    
        except Exception as e:
            logger.error(f"Erro ao carregar tipos filtrados para edição de item: {e}")

    def filtrar_tipos_item_lista_edit_bottomsheet(self, filtro):
        """Filtra tipos no BottomSheet de edição"""
        try:
            self.carregar_tipos_item_lista_edit_bottomsheet(self.tipos_item_lista_edit_dados, filtro)
        except Exception as e:
            logger.error(f"Erro ao filtrar tipos para edição de item: {e}")

    def selecionar_tipo_item_lista_edit_bottomsheet(self, tipo_id, tipo_nome, categoria_id, subcategoria_id):
        """Seleciona tipo de produto para edição de item da lista via BottomSheet"""
        try:
            # Armazena dados selecionados
            self.tipo_item_lista_edit_selecionado_id = tipo_id
            self.categoria_item_lista_edit_id = categoria_id
            self.subcategoria_item_lista_edit_id = subcategoria_id
            
            # Atualiza campos de exibição
            self.campo_tipo_item_lista_edit.text = str(tipo_nome).upper()
            
            # Busca e exibe categoria e subcategoria
            categorias = listar_categorias_apk()
            subcategorias_todas = []
            for cat in listar_categorias_apk():
                subcategorias_todas.extend(listar_subcategorias_apk(cat[0]))
            
            categoria_nome = next((c[1] for c in categorias if c[0] == categoria_id), "Categoria não encontrada")
            subcategoria_nome = next((s[1] for s in subcategorias_todas if s[0] == subcategoria_id), "Subcategoria não encontrada")
            
            self.campo_categoria_item_lista_edit.text = str(categoria_nome).upper()
            self.campo_subcategoria_item_lista_edit.text = str(subcategoria_nome).upper()
            
            # Fecha o BottomSheet
            self.bottomsheet_tipo_item_lista_edit.set_state("close")
            if self.bottomsheet_tipo_item_lista_edit.parent:
                self.bottomsheet_tipo_item_lista_edit.parent.remove_widget(self.bottomsheet_tipo_item_lista_edit)
            
            # Foca no campo quantidade após seleção
            Clock.schedule_once(lambda dt: setattr(self.campo_quantidade_item_lista_edit, 'focus', True), 0.1)
            
            logger.info(f"Tipo selecionado para edição de item: {tipo_id} - {tipo_nome}")
            
        except Exception as e:
            logger.error(f"Erro ao selecionar tipo para edição de item: {e}")

    def abrir_dialog_novo_tipo_item_lista_edit(self):
        """Abre dialog para criar novo tipo de produto a partir do contexto de edição de item da lista"""
        try:
            # Captura o valor do filtro atual (se houver)
            valor_filtro = ""
            if hasattr(self, 'filtro_tipo_item_lista_edit') and self.filtro_tipo_item_lista_edit.text:
                valor_filtro = self.filtro_tipo_item_lista_edit.text.strip().upper()
                
            # Fecha o BottomSheet atual
            if hasattr(self, 'bottomsheet_tipo_item_lista_edit') and self.bottomsheet_tipo_item_lista_edit.parent:
                self.bottomsheet_tipo_item_lista_edit.set_state("close")
                self.bottomsheet_tipo_item_lista_edit.parent.remove_widget(self.bottomsheet_tipo_item_lista_edit)
            
            # Cria tela de cadastro de novo tipo com pré-preenchimento
            # Marca que veio do contexto de edição de item da lista
            self.contexto_novo_tipo = "item_lista_edit"
            self.criar_tela_novo_tipo_produto(valor_preenchimento=valor_filtro)
            
        except Exception as e:
            logger.error(f"Erro ao abrir dialog de novo tipo a partir de edição de item: {e}")

    def salvar_edicao_item_lista(self):
        """Salva as alterações do item na lista de compras"""
        try:
            # Validações
            if not self.tipo_item_lista_edit_selecionado_id:
                self.mostrar_snackbar("Selecione um tipo de produto!")
                return
                
            quantidade = self.campo_quantidade_item_lista_edit.text.strip()
            if not quantidade:
                self.mostrar_snackbar("Quantidade é obrigatória!")
                return
                
            try:
                quantidade_num = float(quantidade)
                if quantidade_num <= 0:
                    self.mostrar_snackbar("Quantidade deve ser maior que zero!")
                    return
            except ValueError:
                self.mostrar_snackbar("Quantidade deve ser um número válido!")
                return
            
            # Salva no banco de dados (usando a função de edição)
            sucesso = editar_item_lista_apk(self.item_atual_id, quantidade)
            
            # Se mudou o tipo, precisa atualizar também tipo, categoria e subcategoria
            # Como não temos função específica, vamos deletar e recriar o item
            if self.tipo_item_lista_edit_selecionado_id != self.tipo_item_lista_original_id:
                
                # Exclui item antigo
                excluir_item_lista_apk([self.item_atual_id])
                
                # Cria item novo com os dados atualizados
                data_adicao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sucesso = adicionar_item_lista_apk(
                    self.lista_atual_id,
                    self.tipo_item_lista_edit_selecionado_id,
                    self.categoria_item_lista_edit_id,
                    self.subcategoria_item_lista_edit_id,
                    quantidade,
                    data_adicao
                )
            
            if sucesso:
                self.mostrar_snackbar("Item editado com sucesso!")
                
                # Volta para a tela de itens da lista
                self.voltar_para_itens_lista_seguro()
                
                # Atualiza o título da AppBar (o total pode ter mudado se foi deletado e recriado)
                self.atualizar_titulo_appbar_lista()
                
                logger.info(f"Item {self.item_atual_id} editado na lista {self.lista_atual_id}")
            else:
                self.mostrar_snackbar("Erro ao salvar alterações do item.")
                
        except Exception as e:
            logger.error(f"Erro ao salvar alterações do item: {e}")
            self.mostrar_snackbar("Erro ao salvar alterações do item.")

    # --- Métodos faltantes para produtos ---
    # --- SISTEMA UNIFICADO DE CADASTRO/EDIÇÃO DE PRODUTOS ---
    def show_cadastro_produto_dialog(self, *args):
        """Exibe tela unificada de cadastro de produto"""
        try:
            # Verifica se há produto selecionado para pré-preenchimento
            selecionados = [produto_id for checkbox, produto_id in self.checkbox_refs if checkbox.active]
            produto_base = None
            
            if len(selecionados) == 1:
                produtos = self.get_produtos_cached()
                produto_base = next((p for p in produtos if p[DatabaseFields.PRODUTO_ID] == selecionados[0]), None)
                logger.info(f"Usando produto {selecionados[0]} como base para cadastro")
            
            self.show_form_produto_unificado(modo='cadastro', produto_base=produto_base)
                
        except Exception as e:
            logger.error(f"Erro ao abrir cadastro de produto: {e}")
            self.mostrar_snackbar("Erro ao abrir cadastro de produto.")

    def show_editar_produto_screen(self, *args):
        """Exibe tela unificada de edição de produto"""
        try:
            selecionados = [produto_id for checkbox, produto_id in self.checkbox_refs if checkbox.active]
            if len(selecionados) != 1:
                self.mostrar_snackbar("Selecione apenas um produto para editar.")
                return
            
            produto_id = selecionados[0]
            produtos = self.get_produtos_cached()
            produto = next((p for p in produtos if p[DatabaseFields.PRODUTO_ID] == produto_id), None)
            
            if not produto:
                self.mostrar_snackbar("Produto não encontrado.")
                return
            
            self.show_form_produto_unificado(modo='edicao', produto_base=produto, produto_id=produto_id)
            logger.info(f"Editando produto {produto_id}")
                
        except Exception as e:
            logger.error(f"Erro ao abrir edição de produto: {e}")
            self.mostrar_snackbar("Erro ao abrir edição do produto.")

    def show_form_produto_unificado(self, modo='cadastro', produto_base=None, produto_id=None):
        """Exibe formulário unificado para cadastro/edição de produtos"""
        try:
            # Define configurações baseadas no modo
            if modo == 'edicao':
                titulo = "Editar Produto"
                eh_edicao = True
                self.produto_edit_id = produto_id
            else:
                titulo = "Cadastrar Produto"
                eh_edicao = False
                self.produto_edit_id = None
            
            # Carrega dados necessários
            tipos_produto = listar_tipos_produto_apk()
            categorias = listar_categorias_apk()
            
            # === CAMPOS DE ENTRADA UNIFICADOS ===
            # Campo para Tipo de Produto (BottomSheet)
            self.campo_tipo_produto_form = MDTextField(
                text="Selecione o tipo",
                readonly=True,
                hint_text="Tipo do produto"
            )
            # Bind do evento de toque para abrir BottomSheet
            self.campo_tipo_produto_form.bind(on_touch_down=lambda instance, touch: self._handle_tipo_produto_touch(instance, touch, tipos_produto))
            
            self.campo_nome_produto_form = MDTextField(
                hint_text="Nome do produto",
                on_text_validate=lambda instance: self.navegar_proximo_campo("nome")
            )
            self.campo_nome_produto_form.bind(text=self.forcar_maiusculas)
            
            self.campo_marca_produto_form = MDTextField(
                hint_text="Marca do produto",
                on_text_validate=lambda instance: self.navegar_proximo_campo("marca")
            )
            self.campo_marca_produto_form.bind(text=self.forcar_maiusculas)
            
            self.campo_quantidade_produto_form = MDTextField(
                hint_text="Quantidade/Embalagem",
                on_text_validate=lambda instance: self.navegar_proximo_campo("quantidade")
            )
            self.campo_quantidade_produto_form.bind(text=self.forcar_maiusculas)
            
            self.campo_codigo_barras_produto_form = MDTextField(
                hint_text="Código de barras (opcional)",
                on_text_validate=lambda instance: self.navegar_proximo_campo("codigo_barras")
            )
            
            # Campo para Categoria (BottomSheet) - inicialmente desabilitado
            self.campo_categoria_produto_form = MDTextField(
                text="Categoria será selecionada automaticamente",
                readonly=True,
                hint_text="Categoria do produto",
                disabled=True
            )
            # Bind do evento de toque para abrir BottomSheet de categoria
            self.campo_categoria_produto_form.bind(on_touch_down=lambda instance, touch: self._handle_categoria_produto_touch(instance, touch))
            
            # Campo para Subcategoria (BottomSheet) - inicialmente desabilitado  
            self.campo_subcategoria_produto_form = MDTextField(
                text="Subcategoria será selecionada automaticamente",
                readonly=True,
                hint_text="Subcategoria do produto",
                disabled=True
            )
            # Bind do evento de toque para abrir BottomSheet de subcategoria
            self.campo_subcategoria_produto_form.bind(on_touch_down=lambda instance, touch: self._handle_subcategoria_produto_touch(instance, touch))
            
            # Variáveis para armazenar IDs selecionados
            self.tipo_produto_form_selecionado_id = None
            self.categoria_produto_form_selecionada_id = None
            self.subcategoria_produto_form_selecionada_id = None
            
            # === PRÉ-PREENCHIMENTO BASEADO NO MODO ===
            if produto_base:
                self.campo_nome_produto_form.text = str(produto_base[DatabaseFields.PRODUTO_NOME])
                self.campo_marca_produto_form.text = str(produto_base[DatabaseFields.PRODUTO_MARCA])
                self.campo_quantidade_produto_form.text = str(produto_base[DatabaseFields.PRODUTO_QUANTIDADE_EMBALAGEM])
                
                # No modo cadastro, não preenche código de barras (conforme especificado)
                if eh_edicao:
                    self.campo_codigo_barras_produto_form.text = str(produto_base[DatabaseFields.PRODUTO_CODIGO_BARRAS]) if produto_base[DatabaseFields.PRODUTO_CODIGO_BARRAS] else ""
                
                # Pré-seleciona tipo de produto
                tipo_id = produto_base[DatabaseFields.PRODUTO_TIPO_ID]
                tipo_info = next((t for t in tipos_produto if t[0] == tipo_id), None)
                if tipo_info:
                    self.tipo_produto_form_selecionado_id = tipo_id
                    self.campo_tipo_produto_form.text = str(tipo_info[1]).upper()
                    
                    if eh_edicao:
                        # Na edição, mantém categoria e subcategoria atuais e permite edição
                        self.categoria_produto_form_selecionada_id = produto_base[DatabaseFields.PRODUTO_CATEGORIA_ID]
                        self.subcategoria_produto_form_selecionada_id = produto_base[DatabaseFields.PRODUTO_SUBCATEGORIA_ID]
                        # Habilita edição de categoria e subcategoria no modo de edição
                        self.campo_categoria_produto_form.disabled = False
                        self.campo_subcategoria_produto_form.disabled = False
                        # Atualiza campos com valores atuais (deve ser DEPOIS de habilitar os campos)
                        self.atualizar_campos_categoria_subcategoria(categorias)
                    else:
                        # No cadastro, seleciona automaticamente por tipo
                        self.atualizar_categoria_subcategoria_por_tipo_form(tipo_id)
            
            # === LAYOUT DO FORMULÁRIO ===
            content = BoxLayout(
                orientation="vertical",
                spacing=dp(15),
                padding=dp(20),
                size_hint_y=None,
            )
            content.bind(minimum_height=content.setter("height"))
            
            content.add_widget(MDLabel(text="Tipo de Produto", theme_text_color="Primary"))
            content.add_widget(self.campo_tipo_produto_form)
            content.add_widget(MDLabel(text="Nome", theme_text_color="Primary"))
            content.add_widget(self.campo_nome_produto_form)
            content.add_widget(MDLabel(text="Marca", theme_text_color="Primary"))
            content.add_widget(self.campo_marca_produto_form)
            content.add_widget(MDLabel(text="Quantidade/Embalagem", theme_text_color="Primary"))
            content.add_widget(self.campo_quantidade_produto_form)
            content.add_widget(MDLabel(text="Código de Barras", theme_text_color="Primary"))
            content.add_widget(self.campo_codigo_barras_produto_form)
            content.add_widget(MDLabel(text="Categoria", theme_text_color="Primary"))
            content.add_widget(self.campo_categoria_produto_form)
            content.add_widget(MDLabel(text="Subcategoria", theme_text_color="Primary"))
            content.add_widget(self.campo_subcategoria_produto_form)

            scroll = MDScrollView()
            scroll.add_widget(content)

            # === APPBAR UNIFICADA ===
            appbar = MDTopAppBar(
                MDTopAppBarLeadingButtonContainer(
                    MDActionTopAppBarButton(
                        icon="arrow-left",
                        on_release=lambda x: self.voltar_para_produtos_seguro(),
                    ),
                ),
                MDTopAppBarTitle(
                    text=titulo,
                    halign="center",
                ),
                MDTopAppBarTrailingButtonContainer(
                    MDActionTopAppBarButton(
                        icon="content-save",
                        on_release=lambda x: self.salvar_produto_unificado(eh_edicao),
                    ),
                ),
                type="small",
                size_hint_y=None,
                height=dp(64),
            )

            layout = BoxLayout(orientation="vertical")
            layout.add_widget(appbar)
            layout.add_widget(scroll)

            # === ADICIONAR ESTAS LINHAS NO FINAL ===
            screen_name = f"{modo}_produto"
            
            # Remove tela antiga se existir
            self.remover_tela_segura(screen_name)
            
            # Cria a tela
            tela = MDScreen(layout, name=screen_name)
            
            # Adiciona ao screen manager e faz a transição
            self.screen_manager.add_widget(tela)
            self.screen_manager.current = screen_name
            
            # Define foco inicial baseado no modo
            if not produto_base:
                # Se não há produto base, foca no campo tipo
                Clock.schedule_once(lambda dt: setattr(self.campo_tipo_produto_form, 'focus', True), 0.2)
            else:
                # Se há produto base, foca no nome para edição rápida
                Clock.schedule_once(lambda dt: setattr(self.campo_nome_produto_form, 'focus', True), 0.2)
            
            logger.info(f"Tela de {modo} de produto aberta")
            
        except Exception as e:
            logger.error(f"Erro ao criar formulário de produto - Modo: {modo}: {e}")
            self.mostrar_snackbar("Erro ao abrir formulário de produto.")

    # === MÉTODOS DE SUPORTE UNIFICADOS ===
    def abrir_bottomsheet_tipo_produto(self, tipos_produto):
        """Abre BottomSheet para seleção de tipo de produto"""
        try:
            # Container principal
            container = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(16))
            
            # Container horizontal para filtro e botão
            filtro_container = BoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(56))
            
            # Campo de filtro
            self.filtro_tipo_produto = MDTextField(
                hint_text="Digite para filtrar tipos...",
                size_hint_x=0.8
            )
            self.filtro_tipo_produto.bind(text=lambda instance, text: self.filtrar_tipos_bottomsheet(text))
            filtro_container.add_widget(self.filtro_tipo_produto)
            
            # Botão para adicionar novo tipo
            botao_novo_tipo = MDActionTopAppBarButton(
                icon="plus",
                theme_icon_color="Custom",
                icon_color="green",
                size_hint_x=0.2,
                on_release=lambda x: self.abrir_dialog_novo_tipo_produto()
            )
            filtro_container.add_widget(botao_novo_tipo)
            
            container.add_widget(filtro_container)
            
            # Lista de tipos
            self.lista_tipos_filtrada = MDList()
            self.tipos_produto_dados = tipos_produto  # Armazena para uso nos filtros
            self.carregar_tipos_bottomsheet(tipos_produto)
            
            # ScrollView para a lista
            scroll = MDScrollView()
            scroll.add_widget(self.lista_tipos_filtrada)
            container.add_widget(scroll)
            
            # Cria e configura o BottomSheet
            self.bottomsheet_tipo = MDBottomSheet()
            self.bottomsheet_tipo.add_widget(container)
            
            # Adiciona ao root para exibir
            self.root.add_widget(self.bottomsheet_tipo)
            self.bottomsheet_tipo.set_state("open")
            
            # Foca no campo de filtro
            Clock.schedule_once(lambda dt: setattr(self.filtro_tipo_produto, 'focus', True), 0.2)
            
        except Exception as e:
            logger.error(f"Erro ao abrir BottomSheet de tipos de produto: {e}")
            self.mostrar_snackbar("Erro ao abrir seleção de tipos.")

    def selecionar_tipo_produto_bottomsheet(self, tipo_id, tipo_nome):
        """Seleciona tipo de produto via BottomSheet"""
        try:
            self.tipo_produto_form_selecionado_id = tipo_id
            self.campo_tipo_produto_form.text = str(tipo_nome).upper()
            self.bottomsheet_tipo.set_state("close")
            # Remove do root após fechar
            if self.bottomsheet_tipo.parent:
                self.bottomsheet_tipo.parent.remove_widget(self.bottomsheet_tipo)
            
            # Atualiza categoria e subcategoria automaticamente apenas no cadastro
            if not self.produto_edit_id:  # Se não é edição (é cadastro)
                logger.info(f"Atualizando categoria/subcategoria para tipo {tipo_id} no modo cadastro")
                self.atualizar_categoria_subcategoria_por_tipo_form(tipo_id)
            else:
                logger.info(f"Modo edição - não atualizando categoria/subcategoria automaticamente")
            
            # Navega automaticamente para o campo nome após seleção
            Clock.schedule_once(lambda dt: setattr(self.campo_nome_produto_form, 'focus', True), 0.1)
            
            logger.info(f"Tipo de produto selecionado via BottomSheet: {tipo_id} - {tipo_nome}")
            
        except Exception as e:
            logger.error(f"Erro ao selecionar tipo de produto: {e}")

    def carregar_tipos_bottomsheet(self, tipos_produto, filtro=""):
        """Carrega tipos no BottomSheet com filtro opcional e ordenação alfabética"""
        try:
            self.lista_tipos_filtrada.clear_widgets()
            
            # Filtra e ordena alfabeticamente
            tipos_filtrados = []
            for tipo in tipos_produto:
                tipo_nome = str(tipo[1]).upper()
                # Aplica filtro se fornecido
                if not filtro or filtro.upper() in tipo_nome:
                    tipos_filtrados.append((tipo[0], tipo_nome, tipo[1]))
            
            # Ordena alfabeticamente pelo nome
            tipos_filtrados.sort(key=lambda x: x[1])
            
            # Adiciona itens ordenados à lista
            for tipo_id, tipo_nome_upper, tipo_nome_original in tipos_filtrados:
                item = MDListItem(
                    MDListItemHeadlineText(text=tipo_nome_upper),
                    on_release=lambda x, t_id=tipo_id, nome=tipo_nome_original: self.selecionar_tipo_produto_bottomsheet(t_id, nome)
                )
                self.lista_tipos_filtrada.add_widget(item)
                    
        except Exception as e:
            logger.error(f"Erro ao carregar tipos filtrados: {e}")

    def filtrar_tipos_bottomsheet(self, filtro):
        """Filtra tipos no BottomSheet"""
        try:
            self.carregar_tipos_bottomsheet(self.tipos_produto_dados, filtro)
        except Exception as e:
            logger.error(f"Erro ao filtrar tipos: {e}")

    def abrir_dialog_novo_tipo_produto(self):
        """Abre dialog para criar novo tipo de produto"""
        try:
            # Captura o valor do filtro atual (se houver)
            valor_filtro = ""
            if hasattr(self, 'filtro_tipo_produto') and self.filtro_tipo_produto.text:
                valor_filtro = self.filtro_tipo_produto.text.strip().upper()
                
            # Fecha o BottomSheet atual
            if hasattr(self, 'bottomsheet_tipo') and self.bottomsheet_tipo.parent:
                self.bottomsheet_tipo.set_state("close")
                self.bottomsheet_tipo.parent.remove_widget(self.bottomsheet_tipo)
            
            # Cria tela de cadastro de novo tipo com pré-preenchimento
            self.criar_tela_novo_tipo_produto(valor_preenchimento=valor_filtro)
            
        except Exception as e:
            logger.error(f"Erro ao abrir dialog de novo tipo: {e}")

    def criar_tela_novo_tipo_produto(self, valor_preenchimento=""):
        """Cria tela para cadastrar novo tipo de produto"""
        try:
            # Campos do formulário
            self.campo_nome_novo_tipo = MDTextField(
                hint_text="Nome do novo tipo de produto",
                text=valor_preenchimento,  # Pré-preenche com valor do filtro
                on_text_validate=lambda instance: setattr(self.campo_categoria_novo_tipo, 'focus', True)
            )
            self.campo_nome_novo_tipo.bind(text=self.forcar_maiusculas)
            
            # Campo para categoria (BottomSheet)
            self.campo_categoria_novo_tipo = MDTextField(
                text="Selecione a categoria",
                readonly=True,
                hint_text="Categoria do tipo"
            )
            self.campo_categoria_novo_tipo.bind(on_touch_down=lambda instance, touch: self._handle_categoria_novo_tipo_touch(instance, touch))
            
            # Campo para subcategoria (BottomSheet) - inicialmente desabilitado
            self.campo_subcategoria_novo_tipo = MDTextField(
                text="Selecione a subcategoria",
                readonly=True,
                hint_text="Subcategoria do tipo",
                disabled=True
            )
            self.campo_subcategoria_novo_tipo.bind(on_touch_down=lambda instance, touch: self._handle_subcategoria_novo_tipo_touch(instance, touch))
            
            # Variáveis para armazenar IDs selecionados
            self.categoria_novo_tipo_selecionada_id = None
            self.subcategoria_novo_tipo_selecionada_id = None
            
            # Layout do formulário
            content = BoxLayout(
                orientation="vertical",
                spacing=dp(15),
                padding=dp(20),
                size_hint_y=None,
            )
            content.bind(minimum_height=content.setter("height"))
            
            content.add_widget(MDLabel(text="Nome do Tipo", theme_text_color="Primary"))
            content.add_widget(self.campo_nome_novo_tipo)
            content.add_widget(MDLabel(text="Categoria", theme_text_color="Primary"))
            content.add_widget(self.campo_categoria_novo_tipo)
            content.add_widget(MDLabel(text="Subcategoria", theme_text_color="Primary"))
            content.add_widget(self.campo_subcategoria_novo_tipo)

            scroll = MDScrollView()
            scroll.add_widget(content)

            # AppBar
            appbar = MDTopAppBar(
                MDTopAppBarLeadingButtonContainer(
                    MDActionTopAppBarButton(
                        icon="arrow-left",
                        on_release=lambda x: self.voltar_para_tipo_produto_bottomsheet(),
                    ),
                ),
                MDTopAppBarTitle(
                    text="Novo Tipo de Produto",
                    halign="center",
                ),
                MDTopAppBarTrailingButtonContainer(
                    MDActionTopAppBarButton(
                        icon="content-save",
                        on_release=lambda x: self.salvar_novo_tipo_produto(),
                    ),
                ),
                type="small",
                size_hint_y=None,
                height=dp(64),
            )

            layout = BoxLayout(orientation="vertical")
            layout.add_widget(appbar)
            layout.add_widget(scroll)

            # Remove tela antiga se existir
            self.remover_tela_segura("novo_tipo_produto")
            
            # Cria a tela
            tela = MDScreen(layout, name="novo_tipo_produto")
            
            # Adiciona ao screen manager e faz a transição
            self.screen_manager.add_widget(tela)
            self.screen_manager.current = "novo_tipo_produto"
            
            # Define foco inicial
            Clock.schedule_once(lambda dt: setattr(self.campo_nome_novo_tipo, 'focus', True), 0.2)
            
            logger.info("Tela de novo tipo de produto aberta")
            
        except Exception as e:
            logger.error(f"Erro ao criar tela de novo tipo: {e}")

    def _handle_categoria_novo_tipo_touch(self, instance, touch):
        """Handler para evento de toque no campo categoria do novo tipo"""
        if instance.collide_point(*touch.pos):
            self.abrir_bottomsheet_categoria_novo_tipo()
            return True
        return False

    def _handle_subcategoria_novo_tipo_touch(self, instance, touch):
        """Handler para evento de toque no campo subcategoria do novo tipo"""
        if instance.collide_point(*touch.pos) and not instance.disabled:
            self.abrir_bottomsheet_subcategoria_novo_tipo()
            return True
        return False

    def abrir_bottomsheet_categoria_novo_tipo(self):
        """Abre BottomSheet para seleção de categoria do novo tipo"""
        try:
            categorias = listar_categorias_apk()
            
            # Container principal
            container = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(16))
            
            # Container horizontal para filtro e botão
            filtro_container = BoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(56))
            
            # Campo de filtro
            filtro_categoria = MDTextField(
                hint_text="Digite para filtrar categorias...",
                size_hint_x=0.8
            )
            filtro_container.add_widget(filtro_categoria)
            
            # Botão para adicionar nova categoria  
            botao_nova_categoria_novo_tipo = MDActionTopAppBarButton(
                icon="plus",
                theme_icon_color="Custom",
                icon_color="green",
                size_hint_x=0.2,
                on_release=lambda x: self.abrir_dialog_nova_categoria_novo_tipo(filtro_categoria.text.strip().upper())
            )
            filtro_container.add_widget(botao_nova_categoria_novo_tipo)
            
            container.add_widget(filtro_container)
            
            # Lista de categorias
            lista_categorias = MDList()
            
            # Carrega categorias ordenadas
            categorias_ordenadas = sorted(categorias, key=lambda x: str(x[1]).upper())
            for categoria in categorias_ordenadas:
                item = MDListItem(
                    MDListItemHeadlineText(text=str(categoria[1]).upper()),
                    on_release=lambda x, cat_id=categoria[0], cat_nome=categoria[1]: self.selecionar_categoria_novo_tipo(cat_id, cat_nome)
                )
                lista_categorias.add_widget(item)
            
            # Filtro dinâmico
            def filtrar_categorias_novo_tipo(instance, texto):
                lista_categorias.clear_widgets()
                for categoria in categorias_ordenadas:
                    categoria_nome = str(categoria[1]).upper()
                    if not texto or texto.upper() in categoria_nome:
                        item = MDListItem(
                            MDListItemHeadlineText(text=categoria_nome),
                            on_release=lambda x, cat_id=categoria[0], cat_nome=categoria[1]: self.selecionar_categoria_novo_tipo(cat_id, cat_nome)
                        )
                        lista_categorias.add_widget(item)
            
            filtro_categoria.bind(text=filtrar_categorias_novo_tipo)
            
            # ScrollView para a lista
            scroll = MDScrollView()
            scroll.add_widget(lista_categorias)
            container.add_widget(scroll)
            
            # Cria e configura o BottomSheet
            self.bottomsheet_categoria_novo_tipo = MDBottomSheet()
            self.bottomsheet_categoria_novo_tipo.add_widget(container)
            
            # Adiciona ao root para exibir
            self.root.add_widget(self.bottomsheet_categoria_novo_tipo)
            self.bottomsheet_categoria_novo_tipo.set_state("open")
            
            # Foca no campo de filtro
            Clock.schedule_once(lambda dt: setattr(filtro_categoria, 'focus', True), 0.2)
            
        except Exception as e:
            logger.error(f"Erro ao abrir BottomSheet de categorias do novo tipo: {e}")

    def selecionar_categoria_novo_tipo(self, categoria_id, categoria_nome):
        """Seleciona categoria para o novo tipo"""
        try:
            self.categoria_novo_tipo_selecionada_id = categoria_id
            self.campo_categoria_novo_tipo.text = str(categoria_nome).upper()
            self.bottomsheet_categoria_novo_tipo.set_state("close")
            # Remove do root após fechar
            if self.bottomsheet_categoria_novo_tipo.parent:
                self.bottomsheet_categoria_novo_tipo.parent.remove_widget(self.bottomsheet_categoria_novo_tipo)
            
            # Habilita e limpa subcategoria
            self.subcategoria_novo_tipo_selecionada_id = None
            self.campo_subcategoria_novo_tipo.text = "Selecione a subcategoria"
            self.campo_subcategoria_novo_tipo.disabled = False
            
            logger.info(f"Categoria selecionada para novo tipo: {categoria_id} - {categoria_nome}")
            
        except Exception as e:
            logger.error(f"Erro ao selecionar categoria para novo tipo: {e}")

    def abrir_bottomsheet_subcategoria_novo_tipo(self):
        """Abre BottomSheet para seleção de subcategoria do novo tipo"""
        try:
            if not self.categoria_novo_tipo_selecionada_id:
                self.mostrar_snackbar("Selecione uma categoria primeiro.")
                return
                
            subcategorias = listar_subcategorias_apk(self.categoria_novo_tipo_selecionada_id)
            
            # Container principal
            container = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(16))
            
            # Container horizontal para filtro e botão
            filtro_container = BoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(56))
            
            # Campo de filtro
            filtro_subcategoria = MDTextField(
                hint_text="Digite para filtrar subcategorias...",
                size_hint_x=0.8
            )
            filtro_container.add_widget(filtro_subcategoria)
            
            # Botão para adicionar nova subcategoria
            botao_nova_subcategoria_novo_tipo = MDActionTopAppBarButton(
                icon="plus",
                theme_icon_color="Custom", 
                icon_color="green",
                size_hint_x=0.2,
                on_release=lambda x: self.abrir_dialog_nova_subcategoria_novo_tipo(filtro_subcategoria.text.strip().upper())
            )
            filtro_container.add_widget(botao_nova_subcategoria_novo_tipo)
            
            container.add_widget(filtro_container)
            
            # Lista de subcategorias
            lista_subcategorias = MDList()
            
            # Carrega subcategorias ordenadas
            subcategorias_ordenadas = sorted(subcategorias, key=lambda x: str(x[1]).upper())
            for subcategoria in subcategorias_ordenadas:
                item = MDListItem(
                    MDListItemHeadlineText(text=str(subcategoria[1]).upper()),
                    on_release=lambda x, sub_id=subcategoria[0], sub_nome=subcategoria[1]: self.selecionar_subcategoria_novo_tipo(sub_id, sub_nome)
                )
                lista_subcategorias.add_widget(item)
            
            # Filtro dinâmico
            def filtrar_subcategorias_novo_tipo(instance, texto):
                lista_subcategorias.clear_widgets()
                for subcategoria in subcategorias_ordenadas:
                    subcategoria_nome = str(subcategoria[1]).upper()
                    if not texto or texto.upper() in subcategoria_nome:
                        item = MDListItem(
                            MDListItemHeadlineText(text=subcategoria_nome),
                            on_release=lambda x, sub_id=subcategoria[0], sub_nome=subcategoria[1]: self.selecionar_subcategoria_novo_tipo(sub_id, sub_nome)
                        )
                        lista_subcategorias.add_widget(item)
            
            filtro_subcategoria.bind(text=filtrar_subcategorias_novo_tipo)
            
            # ScrollView para a lista
            scroll = MDScrollView()
            scroll.add_widget(lista_subcategorias)
            container.add_widget(scroll)
            
            # Cria e configura o BottomSheet
            self.bottomsheet_subcategoria_novo_tipo = MDBottomSheet()
            self.bottomsheet_subcategoria_novo_tipo.add_widget(container)
            
            # Adiciona ao root para exibir
            self.root.add_widget(self.bottomsheet_subcategoria_novo_tipo)
            self.bottomsheet_subcategoria_novo_tipo.set_state("open")
            
            # Foca no campo de filtro
            Clock.schedule_once(lambda dt: setattr(filtro_subcategoria, 'focus', True), 0.2)
            
        except Exception as e:
            logger.error(f"Erro ao abrir BottomSheet de subcategorias do novo tipo: {e}")

    def selecionar_subcategoria_novo_tipo(self, subcategoria_id, subcategoria_nome):
        """Seleciona subcategoria para o novo tipo"""
        try:
            self.subcategoria_novo_tipo_selecionada_id = subcategoria_id
            self.campo_subcategoria_novo_tipo.text = str(subcategoria_nome).upper()
            self.bottomsheet_subcategoria_novo_tipo.set_state("close")
            # Remove do root após fechar
            if self.bottomsheet_subcategoria_novo_tipo.parent:
                self.bottomsheet_subcategoria_novo_tipo.parent.remove_widget(self.bottomsheet_subcategoria_novo_tipo)
            
            logger.info(f"Subcategoria selecionada para novo tipo: {subcategoria_id} - {subcategoria_nome}")
            
        except Exception as e:
            logger.error(f"Erro ao selecionar subcategoria para novo tipo: {e}")

    def salvar_novo_tipo_produto(self):
        """Salva o novo tipo de produto"""
        try:
            nome = self.campo_nome_novo_tipo.text.strip()
            
            if not nome:
                self.mostrar_snackbar("Nome do tipo é obrigatório!")
                return
            
            if not self.categoria_novo_tipo_selecionada_id:
                self.mostrar_snackbar("Categoria é obrigatória!")
                return
                
            if not self.subcategoria_novo_tipo_selecionada_id:
                self.mostrar_snackbar("Subcategoria é obrigatória!")
                return
            
            # Cadastra o novo tipo
            cadastrar_tipo_produto_apk(nome, self.categoria_novo_tipo_selecionada_id, self.subcategoria_novo_tipo_selecionada_id)
            
            self.mostrar_snackbar("Novo tipo de produto cadastrado com sucesso!")
            
            # Volta para o BottomSheet de tipos atualizado
            self.voltar_para_tipo_produto_bottomsheet()
            
            logger.info(f"Novo tipo de produto cadastrado: {nome}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar novo tipo de produto: {e}")
            self.mostrar_snackbar("Erro ao salvar novo tipo de produto.")

    def voltar_para_tipo_produto_bottomsheet(self):
        """Volta para o BottomSheet de tipos de produto"""
        try:
            # Remove a tela atual
            self.remover_tela_segura("novo_tipo_produto")
            
            # Verifica o contexto de onde veio o novo tipo
            if hasattr(self, 'contexto_novo_tipo') and self.contexto_novo_tipo == "item_lista":
                # Voltando do contexto de item da lista
                self.screen_manager.current = "adicionar_item_lista"
                
                # Recarrega os tipos de produto no BottomSheet de item
                tipos_produto_atualizados = listar_tipos_produto_apk()
                self.abrir_bottomsheet_tipo_item_lista(tipos_produto_atualizados)
                
                # Limpa o contexto
                self.contexto_novo_tipo = None
            elif hasattr(self, 'contexto_novo_tipo') and self.contexto_novo_tipo == "item_lista_edit":
                # Voltando do contexto de edição de item da lista
                self.screen_manager.current = "editar_item_lista"
                
                # Recarrega os tipos de produto no BottomSheet de edição de item
                tipos_produto_atualizados = listar_tipos_produto_apk()
                self.abrir_bottomsheet_tipo_item_lista_edit(tipos_produto_atualizados)
                
                # Limpa o contexto
                self.contexto_novo_tipo = None
            else:
                # Contexto normal de produto
                screen_name = "cadastro_produto" if not hasattr(self, 'produto_edit_id') or not self.produto_edit_id else "edicao_produto"
                self.screen_manager.current = screen_name
                
                # Recarrega os tipos de produto no BottomSheet
                tipos_produto_atualizados = listar_tipos_produto_apk()
                self.abrir_bottomsheet_tipo_produto(tipos_produto_atualizados)
            
        except Exception as e:
            logger.error(f"Erro ao voltar para BottomSheet de tipos: {e}")

    # === MÉTODOS PARA CRIAR CATEGORIA/SUBCATEGORIA NO CONTEXTO DE NOVO TIPO ===
    def abrir_dialog_nova_categoria_novo_tipo(self, valor_filtro=""):
        """Abre dialog para criar nova categoria no contexto de novo tipo"""
        try:
            # Fecha o BottomSheet atual
            if hasattr(self, 'bottomsheet_categoria_novo_tipo') and self.bottomsheet_categoria_novo_tipo.parent:
                self.bottomsheet_categoria_novo_tipo.set_state("close")
                self.bottomsheet_categoria_novo_tipo.parent.remove_widget(self.bottomsheet_categoria_novo_tipo)
            
            # Cria tela de cadastro de nova categoria com pré-preenchimento
            self.criar_tela_nova_categoria_novo_tipo(valor_preenchimento=valor_filtro)
            
        except Exception as e:
            logger.error(f"Erro ao abrir dialog de nova categoria no contexto de novo tipo: {e}")

    def criar_tela_nova_categoria_novo_tipo(self, valor_preenchimento=""):
        """Cria tela para cadastrar nova categoria no contexto de novo tipo"""
        try:
            # Campo do formulário
            self.campo_nome_nova_categoria_novo_tipo = MDTextField(
                hint_text="Nome da nova categoria",
                text=valor_preenchimento,  # Pré-preenche com valor do filtro
                on_text_validate=lambda instance: setattr(self.campo_nome_nova_categoria_novo_tipo, 'focus', False)
            )
            self.campo_nome_nova_categoria_novo_tipo.bind(text=self.forcar_maiusculas)
            
            # Layout do formulário
            content = BoxLayout(
                orientation="vertical",
                spacing=dp(15),
                padding=dp(20),
                size_hint_y=None,
            )
            content.bind(minimum_height=content.setter("height"))
            
            content.add_widget(MDLabel(text="Nome da Categoria", theme_text_color="Primary"))
            content.add_widget(self.campo_nome_nova_categoria_novo_tipo)

            scroll = MDScrollView()
            scroll.add_widget(content)

            # AppBar
            appbar = MDTopAppBar(
                MDTopAppBarLeadingButtonContainer(
                    MDActionTopAppBarButton(
                        icon="arrow-left",
                        on_release=lambda x: self.voltar_para_categoria_novo_tipo_bottomsheet(),
                    ),
                ),
                MDTopAppBarTitle(
                    text="Nova Categoria",
                    halign="center",
                ),
                MDTopAppBarTrailingButtonContainer(
                    MDActionTopAppBarButton(
                        icon="content-save",
                        on_release=lambda x: self.salvar_nova_categoria_novo_tipo(),
                    ),
                ),
                type="small",
                size_hint_y=None,
                height=dp(64),
            )

            layout = BoxLayout(orientation="vertical")
            layout.add_widget(appbar)
            layout.add_widget(scroll)

            # Remove tela antiga se existir
            self.remover_tela_segura("nova_categoria_novo_tipo")
            
            # Cria a tela
            tela = MDScreen(layout, name="nova_categoria_novo_tipo")
            
            # Adiciona ao screen manager e faz a transição
            self.screen_manager.add_widget(tela)
            self.screen_manager.current = "nova_categoria_novo_tipo"
            
            # Define foco inicial
            Clock.schedule_once(lambda dt: setattr(self.campo_nome_nova_categoria_novo_tipo, 'focus', True), 0.2)
            
            logger.info("Tela de nova categoria (contexto novo tipo) aberta")
            
        except Exception as e:
            logger.error(f"Erro ao criar tela de nova categoria no contexto de novo tipo: {e}")

    def salvar_nova_categoria_novo_tipo(self):
        """Salva a nova categoria no contexto de novo tipo"""
        try:
            nome = self.campo_nome_nova_categoria_novo_tipo.text.strip()
            
            if not nome:
                self.mostrar_snackbar("Nome da categoria é obrigatório!")
                return
            
            # Cadastra a nova categoria
            from database_apk import cadastrar_categoria_apk
            cadastrar_categoria_apk(nome)
            
            self.mostrar_snackbar("Nova categoria cadastrada com sucesso!")
            
            # Volta para o BottomSheet de categorias atualizado
            self.voltar_para_categoria_novo_tipo_bottomsheet()
            
            logger.info(f"Nova categoria cadastrada no contexto de novo tipo: {nome}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar nova categoria no contexto de novo tipo: {e}")
            self.mostrar_snackbar("Erro ao salvar nova categoria.")

    def voltar_para_categoria_novo_tipo_bottomsheet(self):
        """Volta para o BottomSheet de categorias no contexto de novo tipo"""
        try:
            # Remove a tela atual
            self.remover_tela_segura("nova_categoria_novo_tipo")
            
            # Volta para a tela de novo tipo
            self.screen_manager.current = "novo_tipo_produto"
            
            # Recarrega o BottomSheet de categorias
            self.abrir_bottomsheet_categoria_novo_tipo()
            
        except Exception as e:
            logger.error(f"Erro ao voltar para BottomSheet de categorias no contexto de novo tipo: {e}")

    def abrir_dialog_nova_subcategoria_novo_tipo(self, valor_filtro=""):
        """Abre dialog para criar nova subcategoria no contexto de novo tipo"""
        try:
            # Verifica se há categoria selecionada
            if not self.categoria_novo_tipo_selecionada_id:
                self.mostrar_snackbar("Selecione uma categoria primeiro.")
                return
                
            # Fecha o BottomSheet atual
            if hasattr(self, 'bottomsheet_subcategoria_novo_tipo') and self.bottomsheet_subcategoria_novo_tipo.parent:
                self.bottomsheet_subcategoria_novo_tipo.set_state("close")
                self.bottomsheet_subcategoria_novo_tipo.parent.remove_widget(self.bottomsheet_subcategoria_novo_tipo)
            
            # Cria tela de cadastro de nova subcategoria com pré-preenchimento
            self.criar_tela_nova_subcategoria_novo_tipo(valor_preenchimento=valor_filtro)
            
        except Exception as e:
            logger.error(f"Erro ao abrir dialog de nova subcategoria no contexto de novo tipo: {e}")

    def criar_tela_nova_subcategoria_novo_tipo(self, valor_preenchimento=""):
        """Cria tela para cadastrar nova subcategoria no contexto de novo tipo"""
        try:
            # Campo do formulário
            self.campo_nome_nova_subcategoria_novo_tipo = MDTextField(
                hint_text="Nome da nova subcategoria",
                text=valor_preenchimento,  # Pré-preenche com valor do filtro
                on_text_validate=lambda instance: setattr(self.campo_nome_nova_subcategoria_novo_tipo, 'focus', False)
            )
            self.campo_nome_nova_subcategoria_novo_tipo.bind(text=self.forcar_maiusculas)
            
            # Exibe qual categoria foi selecionada
            categorias = listar_categorias_apk()
            categoria_info = next((c for c in categorias if c[0] == self.categoria_novo_tipo_selecionada_id), None)
            categoria_nome = categoria_info[1] if categoria_info else "Categoria não encontrada"
            
            # Layout do formulário
            content = BoxLayout(
                orientation="vertical",
                spacing=dp(15),
                padding=dp(20),
                size_hint_y=None,
            )
            content.bind(minimum_height=content.setter("height"))
            
            content.add_widget(MDLabel(text=f"Categoria: {str(categoria_nome).upper()}", theme_text_color="Primary"))
            content.add_widget(MDLabel(text="Nome da Subcategoria", theme_text_color="Primary"))
            content.add_widget(self.campo_nome_nova_subcategoria_novo_tipo)

            scroll = MDScrollView()
            scroll.add_widget(content)

            # AppBar
            appbar = MDTopAppBar(
                MDTopAppBarLeadingButtonContainer(
                    MDActionTopAppBarButton(
                        icon="arrow-left",
                        on_release=lambda x: self.voltar_para_subcategoria_novo_tipo_bottomsheet(),
                    ),
                ),
                MDTopAppBarTitle(
                    text="Nova Subcategoria",
                    halign="center",
                ),
                MDTopAppBarTrailingButtonContainer(
                    MDActionTopAppBarButton(
                        icon="content-save",
                        on_release=lambda x: self.salvar_nova_subcategoria_novo_tipo(),
                    ),
                ),
                type="small",
                size_hint_y=None,
                height=dp(64),
            )

            layout = BoxLayout(orientation="vertical")
            layout.add_widget(appbar)
            layout.add_widget(scroll)

            # Remove tela antiga se existir
            self.remover_tela_segura("nova_subcategoria_novo_tipo")
            
            # Cria a tela
            tela = MDScreen(layout, name="nova_subcategoria_novo_tipo")
            
            # Adiciona ao screen manager e faz a transição
            self.screen_manager.add_widget(tela)
            self.screen_manager.current = "nova_subcategoria_novo_tipo"
            
            # Define foco inicial
            Clock.schedule_once(lambda dt: setattr(self.campo_nome_nova_subcategoria_novo_tipo, 'focus', True), 0.2)
            
            logger.info("Tela de nova subcategoria (contexto novo tipo) aberta")
            
        except Exception as e:
            logger.error(f"Erro ao criar tela de nova subcategoria no contexto de novo tipo: {e}")

    def salvar_nova_subcategoria_novo_tipo(self):
        """Salva a nova subcategoria no contexto de novo tipo"""
        try:
            nome = self.campo_nome_nova_subcategoria_novo_tipo.text.strip()
            
            if not nome:
                self.mostrar_snackbar("Nome da subcategoria é obrigatório!")
                return
            
            # Cadastra a nova subcategoria
            from database_apk import cadastrar_subcategoria_apk
            cadastrar_subcategoria_apk(nome, self.categoria_novo_tipo_selecionada_id)
            
            self.mostrar_snackbar("Nova subcategoria cadastrada com sucesso!")
            
            # Volta para o BottomSheet de subcategorias atualizado
            self.voltar_para_subcategoria_novo_tipo_bottomsheet()
            
            logger.info(f"Nova subcategoria cadastrada no contexto de novo tipo: {nome}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar nova subcategoria no contexto de novo tipo: {e}")
            self.mostrar_snackbar("Erro ao salvar nova subcategoria.")

    def voltar_para_subcategoria_novo_tipo_bottomsheet(self):
        """Volta para o BottomSheet de subcategorias no contexto de novo tipo"""
        try:
            # Remove a tela atual
            self.remover_tela_segura("nova_subcategoria_novo_tipo")
            
            # Volta para a tela de novo tipo
            self.screen_manager.current = "novo_tipo_produto"
            
            # Recarrega o BottomSheet de subcategorias
            self.abrir_bottomsheet_subcategoria_novo_tipo()
            
        except Exception as e:
            logger.error(f"Erro ao voltar para BottomSheet de subcategorias no contexto de novo tipo: {e}")

    def abrir_menu_tipo_produto_form(self, tipos_produto):
        """Método mantido para compatibilidade - redireciona para BottomSheet"""
        self.abrir_bottomsheet_tipo_produto(tipos_produto)

    def _handle_tipo_produto_touch(self, instance, touch, tipos_produto):
        """Handler para evento de toque no campo tipo de produto"""
        if instance.collide_point(*touch.pos):
            self.abrir_bottomsheet_tipo_produto(tipos_produto)
            return True
        return False

    def _handle_categoria_produto_touch(self, instance, touch):
        """Handler para evento de toque no campo categoria"""
        if instance.collide_point(*touch.pos) and not instance.disabled:
            self.abrir_bottomsheet_categoria_produto()
            return True
        return False

    def _handle_subcategoria_produto_touch(self, instance, touch):
        """Handler para evento de toque no campo subcategoria"""
        if instance.collide_point(*touch.pos) and not instance.disabled:
            self.abrir_bottomsheet_subcategoria_produto()
            return True
        return False

    def abrir_bottomsheet_categoria_produto(self):
        """Abre BottomSheet para seleção de categoria"""
        try:
            categorias = listar_categorias_apk()
            
            # Container principal
            container = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(16))
            
            # Container horizontal para filtro e botão
            filtro_container = BoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(56))
            
            # Campo de filtro
            self.filtro_categoria_produto = MDTextField(
                hint_text="Digite para filtrar categorias...",
                size_hint_x=0.8
            )
            self.filtro_categoria_produto.bind(text=lambda instance, text: self.filtrar_categorias_bottomsheet(text))
            filtro_container.add_widget(self.filtro_categoria_produto)
            
            # Botão para adicionar nova categoria
            botao_nova_categoria = MDActionTopAppBarButton(
                icon="plus",
                theme_icon_color="Custom",
                icon_color="green",
                size_hint_x=0.2,
                on_release=lambda x: self.abrir_dialog_nova_categoria()
            )
            filtro_container.add_widget(botao_nova_categoria)
            
            container.add_widget(filtro_container)
            
            # Lista de categorias
            self.lista_categorias_filtrada = MDList()
            self.categorias_dados = categorias  # Armazena para uso nos filtros
            self.carregar_categorias_bottomsheet(categorias)
            
            # ScrollView para a lista
            scroll = MDScrollView()
            scroll.add_widget(self.lista_categorias_filtrada)
            container.add_widget(scroll)
            
            # Cria e configura o BottomSheet
            self.bottomsheet_categoria = MDBottomSheet()
            self.bottomsheet_categoria.add_widget(container)
            
            # Adiciona ao root para exibir
            self.root.add_widget(self.bottomsheet_categoria)
            self.bottomsheet_categoria.set_state("open")
            
            # Foca no campo de filtro
            Clock.schedule_once(lambda dt: setattr(self.filtro_categoria_produto, 'focus', True), 0.2)
            
        except Exception as e:
            logger.error(f"Erro ao abrir BottomSheet de categorias: {e}")
            self.mostrar_snackbar("Erro ao abrir seleção de categorias.")

    def selecionar_categoria_bottomsheet(self, categoria_id, categoria_nome):
        """Seleciona categoria via BottomSheet"""
        try:
            self.categoria_produto_form_selecionada_id = categoria_id
            self.campo_categoria_produto_form.text = str(categoria_nome).upper()
            self.bottomsheet_categoria.set_state("close")
            # Remove do root após fechar
            if self.bottomsheet_categoria.parent:
                self.bottomsheet_categoria.parent.remove_widget(self.bottomsheet_categoria)
            
            # Limpa subcategoria e habilita seleção
            self.subcategoria_produto_form_selecionada_id = None
            self.campo_subcategoria_produto_form.text = "Selecione a subcategoria"
            self.campo_subcategoria_produto_form.disabled = False
            
            logger.info(f"Categoria selecionada via BottomSheet: {categoria_id} - {categoria_nome}")
            
        except Exception as e:
            logger.error(f"Erro ao selecionar categoria: {e}")

    def carregar_categorias_bottomsheet(self, categorias, filtro=""):
        """Carrega categorias no BottomSheet com filtro opcional e ordenação alfabética"""
        try:
            self.lista_categorias_filtrada.clear_widgets()
            
            # Filtra e ordena alfabeticamente
            categorias_filtradas = []
            for categoria in categorias:
                categoria_nome = str(categoria[1]).upper()
                # Aplica filtro se fornecido
                if not filtro or filtro.upper() in categoria_nome:
                    categorias_filtradas.append((categoria[0], categoria_nome, categoria[1]))
            
            # Ordena alfabeticamente pelo nome
            categorias_filtradas.sort(key=lambda x: x[1])
            
            # Adiciona itens ordenados à lista
            for cat_id, cat_nome_upper, cat_nome_original in categorias_filtradas:
                item = MDListItem(
                    MDListItemHeadlineText(text=cat_nome_upper),
                    on_release=lambda x, c_id=cat_id, nome=cat_nome_original: self.selecionar_categoria_bottomsheet(c_id, nome)
                )
                self.lista_categorias_filtrada.add_widget(item)
                    
        except Exception as e:
            logger.error(f"Erro ao carregar categorias filtradas: {e}")

    def filtrar_categorias_bottomsheet(self, filtro):
        """Filtra categorias no BottomSheet"""
        try:
            self.carregar_categorias_bottomsheet(self.categorias_dados, filtro)
        except Exception as e:
            logger.error(f"Erro ao filtrar categorias: {e}")

    def abrir_bottomsheet_subcategoria_produto(self):
        """Abre BottomSheet para seleção de subcategoria"""
        try:
            if not self.categoria_produto_form_selecionada_id:
                self.mostrar_snackbar("Selecione uma categoria primeiro.")
                return
                
            subcategorias = listar_subcategorias_apk(self.categoria_produto_form_selecionada_id)
            
            # Container principal
            container = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(16))
            
            # Container horizontal para filtro e botão
            filtro_container = BoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(56))
            
            # Campo de filtro
            self.filtro_subcategoria_produto = MDTextField(
                hint_text="Digite para filtrar subcategorias...",
                size_hint_x=0.8
            )
            self.filtro_subcategoria_produto.bind(text=lambda instance, text: self.filtrar_subcategorias_bottomsheet(text))
            filtro_container.add_widget(self.filtro_subcategoria_produto)
            
            # Botão para adicionar nova subcategoria
            botao_nova_subcategoria = MDActionTopAppBarButton(
                icon="plus",
                theme_icon_color="Custom",
                icon_color="green",
                size_hint_x=0.2,
                on_release=lambda x: self.abrir_dialog_nova_subcategoria()
            )
            filtro_container.add_widget(botao_nova_subcategoria)
            
            container.add_widget(filtro_container)
            
            # Lista de subcategorias
            self.lista_subcategorias_filtrada = MDList()
            self.subcategorias_dados = subcategorias  # Armazena para uso nos filtros
            self.carregar_subcategorias_bottomsheet(subcategorias)
            
            # ScrollView para a lista
            scroll = MDScrollView()
            scroll.add_widget(self.lista_subcategorias_filtrada)
            container.add_widget(scroll)
            
            # Cria e configura o BottomSheet
            self.bottomsheet_subcategoria = MDBottomSheet()
            self.bottomsheet_subcategoria.add_widget(container)
            
            # Adiciona ao root para exibir
            self.root.add_widget(self.bottomsheet_subcategoria)
            self.bottomsheet_subcategoria.set_state("open")
            
            # Foca no campo de filtro
            Clock.schedule_once(lambda dt: setattr(self.filtro_subcategoria_produto, 'focus', True), 0.2)
            
        except Exception as e:
            logger.error(f"Erro ao abrir BottomSheet de subcategorias: {e}")
            self.mostrar_snackbar("Erro ao abrir seleção de subcategorias.")

    def selecionar_subcategoria_bottomsheet(self, subcategoria_id, subcategoria_nome):
        """Seleciona subcategoria via BottomSheet"""
        try:
            self.subcategoria_produto_form_selecionada_id = subcategoria_id
            self.campo_subcategoria_produto_form.text = str(subcategoria_nome).upper()
            self.bottomsheet_subcategoria.set_state("close")
            # Remove do root após fechar
            if self.bottomsheet_subcategoria.parent:
                self.bottomsheet_subcategoria.parent.remove_widget(self.bottomsheet_subcategoria)
            
            logger.info(f"Subcategoria selecionada via BottomSheet: {subcategoria_id} - {subcategoria_nome}")
            
        except Exception as e:
            logger.error(f"Erro ao selecionar subcategoria: {e}")

    def carregar_subcategorias_bottomsheet(self, subcategorias, filtro=""):
        """Carrega subcategorias no BottomSheet com filtro opcional e ordenação alfabética"""
        try:
            self.lista_subcategorias_filtrada.clear_widgets()
            
            # Filtra e ordena alfabeticamente
            subcategorias_filtradas = []
            for subcategoria in subcategorias:
                subcategoria_nome = str(subcategoria[1]).upper()
                # Aplica filtro se fornecido
                if not filtro or filtro.upper() in subcategoria_nome:
                    subcategorias_filtradas.append((subcategoria[0], subcategoria_nome, subcategoria[1]))
            
            # Ordena alfabeticamente pelo nome
            subcategorias_filtradas.sort(key=lambda x: x[1])
            
            # Adiciona itens ordenados à lista
            for sub_id, sub_nome_upper, sub_nome_original in subcategorias_filtradas:
                item = MDListItem(
                    MDListItemHeadlineText(text=sub_nome_upper),
                    on_release=lambda x, s_id=sub_id, nome=sub_nome_original: self.selecionar_subcategoria_bottomsheet(s_id, nome)
                )
                self.lista_subcategorias_filtrada.add_widget(item)
                    
        except Exception as e:
            logger.error(f"Erro ao carregar subcategorias filtradas: {e}")

    def filtrar_subcategorias_bottomsheet(self, filtro):
        """Filtra subcategorias no BottomSheet"""
        try:
            self.carregar_subcategorias_bottomsheet(self.subcategorias_dados, filtro)
        except Exception as e:
            logger.error(f"Erro ao filtrar subcategorias: {e}")

    # === MÉTODOS PARA CRIAR NOVA CATEGORIA ===
    def abrir_dialog_nova_categoria(self):
        """Abre dialog para criar nova categoria"""
        try:
            # Captura o valor do filtro atual (se houver)
            valor_filtro = ""
            if hasattr(self, 'filtro_categoria_produto') and self.filtro_categoria_produto.text:
                valor_filtro = self.filtro_categoria_produto.text.strip().upper()
                
            # Fecha o BottomSheet atual
            if hasattr(self, 'bottomsheet_categoria') and self.bottomsheet_categoria.parent:
                self.bottomsheet_categoria.set_state("close")
                self.bottomsheet_categoria.parent.remove_widget(self.bottomsheet_categoria)
            
            # Cria tela de cadastro de nova categoria com pré-preenchimento
            self.criar_tela_nova_categoria(valor_preenchimento=valor_filtro)
            
        except Exception as e:
            logger.error(f"Erro ao abrir dialog de nova categoria: {e}")

    def criar_tela_nova_categoria(self, valor_preenchimento=""):
        """Cria tela para cadastrar nova categoria"""
        try:
            # Campo do formulário
            self.campo_nome_nova_categoria = MDTextField(
                hint_text="Nome da nova categoria",
                text=valor_preenchimento,  # Pré-preenche com valor do filtro
                on_text_validate=lambda instance: setattr(self.campo_nome_nova_categoria, 'focus', False)
            )
            self.campo_nome_nova_categoria.bind(text=self.forcar_maiusculas)
            
            # Layout do formulário
            content = BoxLayout(
                orientation="vertical",
                spacing=dp(15),
                padding=dp(20),
                size_hint_y=None,
            )
            content.bind(minimum_height=content.setter("height"))
            
            content.add_widget(MDLabel(text="Nome da Categoria", theme_text_color="Primary"))
            content.add_widget(self.campo_nome_nova_categoria)

            scroll = MDScrollView()
            scroll.add_widget(content)

            # AppBar
            appbar = MDTopAppBar(
                MDTopAppBarLeadingButtonContainer(
                    MDActionTopAppBarButton(
                        icon="arrow-left",
                        on_release=lambda x: self.voltar_para_categoria_bottomsheet(),
                    ),
                ),
                MDTopAppBarTitle(
                    text="Nova Categoria",
                    halign="center",
                ),
                MDTopAppBarTrailingButtonContainer(
                    MDActionTopAppBarButton(
                        icon="content-save",
                        on_release=lambda x: self.salvar_nova_categoria(),
                    ),
                ),
                type="small",
                size_hint_y=None,
                height=dp(64),
            )

            layout = BoxLayout(orientation="vertical")
            layout.add_widget(appbar)
            layout.add_widget(scroll)

            # Remove tela antiga se existir
            self.remover_tela_segura("nova_categoria")
            
            # Cria a tela
            tela = MDScreen(layout, name="nova_categoria")
            
            # Adiciona ao screen manager e faz a transição
            self.screen_manager.add_widget(tela)
            self.screen_manager.current = "nova_categoria"
            
            # Define foco inicial
            Clock.schedule_once(lambda dt: setattr(self.campo_nome_nova_categoria, 'focus', True), 0.2)
            
            logger.info("Tela de nova categoria aberta")
            
        except Exception as e:
            logger.error(f"Erro ao criar tela de nova categoria: {e}")

    def salvar_nova_categoria(self):
        """Salva a nova categoria"""
        try:
            nome = self.campo_nome_nova_categoria.text.strip()
            
            if not nome:
                self.mostrar_snackbar("Nome da categoria é obrigatório!")
                return
            
            # Cadastra a nova categoria (assumindo que existe função no database_apk)
            from database_apk import cadastrar_categoria_apk
            cadastrar_categoria_apk(nome)
            
            self.mostrar_snackbar("Nova categoria cadastrada com sucesso!")
            
            # Volta para o BottomSheet de categorias atualizado
            self.voltar_para_categoria_bottomsheet()
            
            logger.info(f"Nova categoria cadastrada: {nome}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar nova categoria: {e}")
            self.mostrar_snackbar("Erro ao salvar nova categoria.")

    def voltar_para_categoria_bottomsheet(self):
        """Volta para o BottomSheet de categorias"""
        try:
            # Remove a tela atual
            self.remover_tela_segura("nova_categoria")
            
            # Volta para o formulário de produto
            screen_name = "cadastro_produto" if not hasattr(self, 'produto_edit_id') or not self.produto_edit_id else "edicao_produto"
            self.screen_manager.current = screen_name
            
            # Recarrega as categorias no BottomSheet
            self.abrir_bottomsheet_categoria_produto()
            
        except Exception as e:
            logger.error(f"Erro ao voltar para BottomSheet de categorias: {e}")

    # === MÉTODOS PARA CRIAR NOVA SUBCATEGORIA ===
    def abrir_dialog_nova_subcategoria(self):
        """Abre dialog para criar nova subcategoria"""
        try:
            # Verifica se há categoria selecionada
            if not self.categoria_produto_form_selecionada_id:
                self.mostrar_snackbar("Selecione uma categoria primeiro.")
                return
                
            # Captura o valor do filtro atual (se houver)
            valor_filtro = ""
            if hasattr(self, 'filtro_subcategoria_produto') and self.filtro_subcategoria_produto.text:
                valor_filtro = self.filtro_subcategoria_produto.text.strip().upper()
                
            # Fecha o BottomSheet atual
            if hasattr(self, 'bottomsheet_subcategoria') and self.bottomsheet_subcategoria.parent:
                self.bottomsheet_subcategoria.set_state("close")
                self.bottomsheet_subcategoria.parent.remove_widget(self.bottomsheet_subcategoria)
            
            # Cria tela de cadastro de nova subcategoria com pré-preenchimento
            self.criar_tela_nova_subcategoria(valor_preenchimento=valor_filtro)
            
        except Exception as e:
            logger.error(f"Erro ao abrir dialog de nova subcategoria: {e}")

    def criar_tela_nova_subcategoria(self, valor_preenchimento=""):
        """Cria tela para cadastrar nova subcategoria"""
        try:
            # Campo do formulário
            self.campo_nome_nova_subcategoria = MDTextField(
                hint_text="Nome da nova subcategoria",
                text=valor_preenchimento,  # Pré-preenche com valor do filtro
                on_text_validate=lambda instance: setattr(self.campo_nome_nova_subcategoria, 'focus', False)
            )
            self.campo_nome_nova_subcategoria.bind(text=self.forcar_maiusculas)
            
            # Exibe qual categoria foi selecionada
            categorias = listar_categorias_apk()
            categoria_info = next((c for c in categorias if c[0] == self.categoria_produto_form_selecionada_id), None)
            categoria_nome = categoria_info[1] if categoria_info else "Categoria não encontrada"
            
            # Layout do formulário
            content = BoxLayout(
                orientation="vertical",
                spacing=dp(15),
                padding=dp(20),
                size_hint_y=None,
            )
            content.bind(minimum_height=content.setter("height"))
            
            content.add_widget(MDLabel(text=f"Categoria: {str(categoria_nome).upper()}", theme_text_color="Primary"))
            content.add_widget(MDLabel(text="Nome da Subcategoria", theme_text_color="Primary"))
            content.add_widget(self.campo_nome_nova_subcategoria)

            scroll = MDScrollView()
            scroll.add_widget(content)

            # AppBar
            appbar = MDTopAppBar(
                MDTopAppBarLeadingButtonContainer(
                    MDActionTopAppBarButton(
                        icon="arrow-left",
                        on_release=lambda x: self.voltar_para_subcategoria_bottomsheet(),
                    ),
                ),
                MDTopAppBarTitle(
                    text="Nova Subcategoria",
                    halign="center",
                ),
                MDTopAppBarTrailingButtonContainer(
                    MDActionTopAppBarButton(
                        icon="content-save",
                        on_release=lambda x: self.salvar_nova_subcategoria(),
                    ),
                ),
                type="small",
                size_hint_y=None,
                height=dp(64),
            )

            layout = BoxLayout(orientation="vertical")
            layout.add_widget(appbar)
            layout.add_widget(scroll)

            # Remove tela antiga se existir
            self.remover_tela_segura("nova_subcategoria")
            
            # Cria a tela
            tela = MDScreen(layout, name="nova_subcategoria")
            
            # Adiciona ao screen manager e faz a transição
            self.screen_manager.add_widget(tela)
            self.screen_manager.current = "nova_subcategoria"
            
            # Define foco inicial
            Clock.schedule_once(lambda dt: setattr(self.campo_nome_nova_subcategoria, 'focus', True), 0.2)
            
            logger.info("Tela de nova subcategoria aberta")
            
        except Exception as e:
            logger.error(f"Erro ao criar tela de nova subcategoria: {e}")

    def salvar_nova_subcategoria(self):
        """Salva a nova subcategoria"""
        try:
            nome = self.campo_nome_nova_subcategoria.text.strip()
            
            if not nome:
                self.mostrar_snackbar("Nome da subcategoria é obrigatório!")
                return
            
            # Cadastra a nova subcategoria (assumindo que existe função no database_apk)
            from database_apk import cadastrar_subcategoria_apk
            cadastrar_subcategoria_apk(nome, self.categoria_produto_form_selecionada_id)
            
            self.mostrar_snackbar("Nova subcategoria cadastrada com sucesso!")
            
            # Volta para o BottomSheet de subcategorias atualizado
            self.voltar_para_subcategoria_bottomsheet()
            
            logger.info(f"Nova subcategoria cadastrada: {nome}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar nova subcategoria: {e}")
            self.mostrar_snackbar("Erro ao salvar nova subcategoria.")

    def voltar_para_subcategoria_bottomsheet(self):
        """Volta para o BottomSheet de subcategorias"""
        try:
            # Remove a tela atual
            self.remover_tela_segura("nova_subcategoria")
            
            # Volta para o formulário de produto
            screen_name = "cadastro_produto" if not hasattr(self, 'produto_edit_id') or not self.produto_edit_id else "edicao_produto"
            self.screen_manager.current = screen_name
            
            # Recarrega as subcategorias no BottomSheet
            self.abrir_bottomsheet_subcategoria_produto()
            
        except Exception as e:
            logger.error(f"Erro ao voltar para BottomSheet de subcategorias: {e}")

    def navegar_proximo_campo(self, campo_atual):
        """Navega para o próximo campo ao pressionar Enter"""
        try:
            sequencia_campos = {
                "nome": self.campo_marca_produto_form,
                "marca": self.campo_quantidade_produto_form,
                "quantidade": self.campo_codigo_barras_produto_form,
                "codigo_barras": None  # Último campo editável
            }
            
            proximo_campo = sequencia_campos.get(campo_atual)
            if proximo_campo:
                proximo_campo.focus = True
                logger.info(f"Navegando de {campo_atual} para próximo campo")
            else:
                # Se chegou ao final, pode focar no botão de salvar ou remover foco
                if hasattr(self, 'campo_codigo_barras_produto_form'):
                    self.campo_codigo_barras_produto_form.focus = False
                logger.info("Chegou ao último campo editável")
                
        except Exception as e:
            logger.error(f"Erro ao navegar entre campos: {e}")

    def atualizar_categoria_subcategoria_por_tipo_form(self, tipo_id):
        """Atualiza categoria e subcategoria baseado no tipo de produto (para cadastro)"""
        try:
            tipos_produto = listar_tipos_produto_apk()
            tipo_info = next((t for t in tipos_produto if t[0] == tipo_id), None)
            
            if tipo_info and len(tipo_info) > 2:
                categoria_id = tipo_info[2] if len(tipo_info) > 2 else None  # índice 2
                subcategoria_id = tipo_info[3] if len(tipo_info) > 3 else None  # índice 3
                
                # Atualiza categoria
                if categoria_id:
                    categorias = listar_categorias_apk()
                    categoria_info = next((c for c in categorias if c[0] == categoria_id), None)
                    if categoria_info:
                        self.categoria_produto_form_selecionada_id = categoria_id
                        self.campo_categoria_produto_form.text = str(categoria_info[1]).upper()
                        # Mantém campo bloqueado - categoria é automática baseada no tipo
                
                # Atualiza subcategoria
                if subcategoria_id and categoria_id:
                    subcategorias = listar_subcategorias_apk(categoria_id)
                    subcategoria_info = next((s for s in subcategorias if s[0] == subcategoria_id), None)
                    if subcategoria_info:
                        self.subcategoria_produto_form_selecionada_id = subcategoria_id
                        self.campo_subcategoria_produto_form.text = str(subcategoria_info[1]).upper()
                        # Mantém campo bloqueado - subcategoria é automática baseada no tipo
                        
                logger.info(f"Categoria e subcategoria atualizadas automaticamente para tipo {tipo_id}")
                
        except Exception as e:
            logger.error(f"Erro ao atualizar categoria/subcategoria por tipo: {e}")

    def atualizar_campos_categoria_subcategoria(self, categorias):
        """Atualiza campos de categoria e subcategoria com valores pré-existentes (para edição)"""
        try:
            # Atualiza campo de categoria
            if self.categoria_produto_form_selecionada_id:
                categoria_info = next((c for c in categorias if c[0] == self.categoria_produto_form_selecionada_id), None)
                if categoria_info:
                    self.campo_categoria_produto_form.text = str(categoria_info[1]).upper()
            
            # Atualiza campo de subcategoria
            if self.subcategoria_produto_form_selecionada_id and self.categoria_produto_form_selecionada_id:
                subcategorias = listar_subcategorias_apk(self.categoria_produto_form_selecionada_id)
                subcategoria_info = next((s for s in subcategorias if s[0] == self.subcategoria_produto_form_selecionada_id), None)
                if subcategoria_info:
                    self.campo_subcategoria_produto_form.text = str(subcategoria_info[1]).upper()
                    
        except Exception as e:
            logger.error(f"Erro ao atualizar campos de categoria/subcategoria: {e}")

    def salvar_produto_unificado(self, eh_edicao=False):
        """Salva produto no modo cadastro ou edição"""
        try:
            # Coleta dados do formulário
            nome = self.campo_nome_produto_form.text.strip()
            marca = self.campo_marca_produto_form.text.strip()
            quantidade = self.campo_quantidade_produto_form.text.strip()
            codigo_barras = self.campo_codigo_barras_produto_form.text.strip()
            
            # Validação
            valido, mensagem = self.validar_formulario_produto(
                self.tipo_produto_form_selecionado_id, nome, marca, quantidade,
                self.categoria_produto_form_selecionada_id, self.subcategoria_produto_form_selecionada_id
            )
            
            if not valido:
                self.mostrar_snackbar(mensagem)
                return
            
            # === OPERAÇÃO DIFERENCIADA POR MODO ===
            if eh_edicao:
                # EDIÇÃO: Altera produto existente
                alterar_produto_apk(
                    self.produto_edit_id,
                    self.tipo_produto_form_selecionado_id,
                    nome,
                    marca,
                    quantidade,
                    codigo_barras if codigo_barras else None,
                    self.categoria_produto_form_selecionada_id,
                    self.subcategoria_produto_form_selecionada_id,
                    None  # imagem
                )
                mensagem_sucesso = "Produto editado com sucesso!"
                logger.info(f"Produto {self.produto_edit_id} editado com sucesso")
            else:
                # CADASTRO: Cria novo produto
                cadastrar_produto_apk(
                    self.tipo_produto_form_selecionado_id,
                    nome,
                    marca,
                    quantidade,
                    codigo_barras if codigo_barras else None,
                    self.categoria_produto_form_selecionada_id,
                    self.subcategoria_produto_form_selecionada_id,
                    None  # imagem
                )
                mensagem_sucesso = "Produto cadastrado com sucesso!"
                logger.info(f"Produto '{nome}' cadastrado com sucesso")
            
            # === PÓS-PROCESSAMENTO COMUM ===
            self.invalidar_cache('produtos')
            self.voltar_para_produtos_seguro()  # Já atualiza a lista
            self.mostrar_snackbar(mensagem_sucesso)
            
        except Exception as e:
            logger.error(f"Erro ao salvar produto: {e}")
            self.mostrar_snackbar("Erro ao salvar produto.")

    # === SISTEMA UNIFICADO PARA SUPERMERCADOS ===
    def show_cadastro_supermercado_screen(self, *args):
        """Exibe formulário unificado de cadastro de supermercado"""
        try:
            selecionados = [super_id for checkbox, super_id in self.super_checkbox_refs if checkbox.active]
            supermercado_base = None
            
            if len(selecionados) == 1:
                supermercados = listar_supermercados_apk()
                supermercado_base = next((s for s in supermercados if s[0] == selecionados[0]), None)
                logger.info(f"Usando supermercado {selecionados[0]} como base para cadastro")
            
            self.show_form_supermercado_unificado(modo='cadastro', supermercado_base=supermercado_base)
                
        except Exception as e:
            logger.error(f"Erro ao abrir cadastro de supermercado: {e}")
            self.mostrar_snackbar("Erro ao abrir cadastro de supermercado.")

    def show_editar_supermercado_screen(self, *args):
        """Exibe formulário unificado de edição de supermercado"""
        try:
            selecionados = [super_id for checkbox, super_id in self.super_checkbox_refs if checkbox.active]
            if len(selecionados) != 1:
                self.mostrar_snackbar("Selecione apenas um supermercado para editar.")
                return
            
            super_id = selecionados[0]
            supermercados = listar_supermercados_apk()
            supermercado = next((s for s in supermercados if s[0] == super_id), None)
            
            if not supermercado:
                self.mostrar_snackbar("Supermercado não encontrado.")
                return
            
            self.show_form_supermercado_unificado(modo='edicao', supermercado_base=supermercado, supermercado_id=super_id)
            logger.info(f"Editando supermercado {super_id}")
                
        except Exception as e:
            logger.error(f"Erro ao abrir edição de supermercado: {e}")
            self.mostrar_snackbar("Erro ao abrir edição do supermercado.")

    def show_form_supermercado_unificado(self, modo='cadastro', supermercado_base=None, supermercado_id=None):
        """Exibe formulário unificado para cadastro/edição de supermercados"""
        try:
            # Define configurações baseadas no modo  
            if modo == 'edicao':
                titulo = "Editar Supermercado"
                eh_edicao = True
                self.supermercado_edit_id = supermercado_id
            else:
                titulo = "Cadastrar Supermercado"
                eh_edicao = False
                self.supermercado_edit_id = None
            
            # Campos de entrada unificados
            self.campo_nome_supermercado_form = MDTextField(
                hint_text="Nome do supermercado",
                on_text_validate=lambda instance: setattr(self.campo_bairro_supermercado_form, 'focus', True)
            )
            self.campo_nome_supermercado_form.bind(text=self.forcar_maiusculas)
            
            self.campo_bairro_supermercado_form = MDTextField(
                hint_text="Bairro",
                on_text_validate=lambda instance: setattr(self.campo_bairro_supermercado_form, 'focus', False)
            )
            self.campo_bairro_supermercado_form.bind(text=self.forcar_maiusculas)
            
            # Pré-preenchimento se houver supermercado base
            if supermercado_base:
                self.campo_nome_supermercado_form.text = str(supermercado_base[1])
                self.campo_bairro_supermercado_form.text = str(supermercado_base[2])
            
            # Layout do formulário
            content = BoxLayout(
                orientation="vertical",
                spacing=dp(15),
                padding=dp(20),
                size_hint_y=None,
            )
            content.bind(minimum_height=content.setter("height"))
            
            content.add_widget(MDLabel(text="Nome do Supermercado", theme_text_color="Primary"))
            content.add_widget(self.campo_nome_supermercado_form)
            content.add_widget(MDLabel(text="Bairro", theme_text_color="Primary"))
            content.add_widget(self.campo_bairro_supermercado_form)

            scroll = MDScrollView()
            scroll.add_widget(content)

            appbar = MDTopAppBar(
                MDTopAppBarLeadingButtonContainer(
                    MDActionTopAppBarButton(
                        icon="arrow-left",
                        on_release=lambda x: self.voltar_para_supermercados_seguro(),
                    ),
                ),
                MDTopAppBarTitle(
                    text=titulo,
                    halign="center",
                ),
                MDTopAppBarTrailingButtonContainer(
                    MDActionTopAppBarButton(
                        icon="content-save",
                        on_release=lambda x: self.salvar_supermercado_unificado(eh_edicao),
                    ),
                ),
                type="small",
                size_hint_y=None,
                height=dp(64),
            )

            layout = BoxLayout(orientation="vertical")
            layout.add_widget(appbar)
            layout.add_widget(scroll)

            # === ADICIONAR ESTAS LINHAS NO FINAL ===
            screen_name = f"{modo}_supermercado"
            
            # Remove tela antiga se existir
            self.remover_tela_segura(screen_name)
            
            # Cria a tela
            tela = MDScreen(layout, name=screen_name)
            
            # Adiciona ao screen manager e faz a transição
            self.screen_manager.add_widget(tela)
            self.screen_manager.current = screen_name
            
            # Define foco inicial no campo nome
            Clock.schedule_once(lambda dt: setattr(self.campo_nome_supermercado_form, 'focus', True), 0.2)
            
            logger.info(f"Tela de {modo} de supermercado aberta")
            
        except Exception as e:
            logger.error(f"Erro ao criar formulário de supermercado - Modo: {modo}: {e}")
            self.mostrar_snackbar("Erro ao abrir formulário de supermercado.")

    # === SISTEMA UNIFICADO PARA LISTAS ===
    def show_cadastro_lista_screen(self, *args):
        """Exibe formulário unificado de cadastro de lista"""
        try:
            selecionados = [lista_id for checkbox, lista_id in self.listas_checkbox_refs if checkbox.active]
            lista_base = None
            
            if len(selecionados) == 1:
                listas = listar_listas_apk()
                lista_base = next((l for l in listas if l[0] == selecionados[0]), None)
                logger.info(f"Usando lista {selecionados[0]} como base para cadastro")
            
            self.show_form_lista_unificado(modo='cadastro', lista_base=lista_base)
                
        except Exception as e:
            logger.error(f"Erro ao abrir cadastro de lista: {e}")
            self.mostrar_snackbar("Erro ao abrir cadastro de lista.")

    def show_editar_lista_screen(self, *args):
        """Exibe formulário unificado de edição de lista"""
        try:
            selecionados = [lista_id for checkbox, lista_id in self.listas_checkbox_refs if checkbox.active]
            if len(selecionados) != 1:
                self.mostrar_snackbar("Selecione apenas uma lista para editar.")
                return
            
            lista_id = selecionados[0]
            listas = listar_listas_apk()
            lista = next((l for l in listas if l[0] == lista_id), None)
            
            if not lista:
                self.mostrar_snackbar("Lista não encontrada.")
                return
            
            self.show_form_lista_unificado(modo='edicao', lista_base=lista, lista_id=lista_id)
            logger.info(f"Editando lista {lista_id}")
                
        except Exception as e:
            logger.error(f"Erro ao abrir edição de lista: {e}")
            self.mostrar_snackbar("Erro ao abrir edição da lista.")

    def show_form_lista_unificado(self, modo='cadastro', lista_base=None, lista_id=None):
        """Exibe formulário unificado para cadastro/edição de listas"""
        try:
            
            # Define configurações baseadas no modo
            if modo == 'edicao':
                titulo = "Editar Lista"
                eh_edicao = True

                self.lista_edit_id = lista_id
            else:
                titulo = "Cadastrar Lista"
                eh_edicao = False
                self.lista_edit_id = None
            
            # Campos de entrada unificados
            self.campo_nome_lista_form = MDTextField(
                hint_text="Nome da lista",
                on_text_validate=lambda instance: setattr(self.campo_data_lista_form, 'focus', True)
            )
            self.campo_nome_lista_form.bind(text=self.forcar_maiusculas)
            
            # Data: no cadastro usa data atual, na edição usa a existente
            data_padrao = datetime.now().strftime("%Y-%m-%d")
            if eh_edicao and lista_base:
                data_padrao = lista_base[2]  # data_criacao
            
            self.campo_data_lista_form = MDTextField(
                text=data_padrao,
                hint_text="Data de criação (AAAA-MM-DD)",
                on_text_validate=lambda instance: setattr(self.campo_data_lista_form, 'focus', False)
            )
            
            # Pré-preenchimento específico por modo
            if lista_base:
                if eh_edicao:
                    # Na edição, usa o nome original
                    self.campo_nome_lista_form.text = str(lista_base[1])
                else:
                    # No cadastro, prefixo "CÓPIA DE"
                    self.campo_nome_lista_form.text = f"CÓPIA DE {str(lista_base[1]).upper()}"
            
            # Layout do formulário
            content = BoxLayout(
                orientation="vertical",
                spacing=dp(15),
                padding=dp(20),
                size_hint_y=None,
            )
            content.bind(minimum_height=content.setter("height"))
            
            content.add_widget(MDLabel(text="Nome da Lista", theme_text_color="Primary"))
            content.add_widget(self.campo_nome_lista_form)
            content.add_widget(MDLabel(text="Data de Criação", theme_text_color="Primary"))
            content.add_widget(self.campo_data_lista_form)

            scroll = MDScrollView()
            scroll.add_widget(content)

            appbar = MDTopAppBar(
                MDTopAppBarLeadingButtonContainer(
                    MDActionTopAppBarButton(
                        icon="arrow-left",
                        on_release=lambda x: self.voltar_para_listas_seguro(),
                    ),
                ),
                MDTopAppBarTitle(
                    text=titulo,
                    halign="center",
                ),
                MDTopAppBarTrailingButtonContainer(
                    MDActionTopAppBarButton(
                        icon="content-save",
                        on_release=lambda x: self.salvar_lista_unificado(eh_edicao),
                    ),
                ),
                type="small",
                size_hint_y=None,
                height=dp(64),
            )

            layout = BoxLayout(orientation="vertical")
            layout.add_widget(appbar)
            layout.add_widget(scroll)

            # === ADICIONAR ESTAS LINHAS NO FINAL ===  
            screen_name = f"{modo}_lista"
            
            # Remove tela antiga se existir
            self.remover_tela_segura(screen_name)
            
            # Cria a tela
            tela = MDScreen(layout, name=screen_name)
            
            # Adiciona ao screen manager e faz a transição
            self.screen_manager.add_widget(tela)
            self.screen_manager.current = screen_name
            
            # Define foco inicial no campo nome
            Clock.schedule_once(lambda dt: setattr(self.campo_nome_lista_form, 'focus', True), 0.2)
            
            logger.info(f"Tela de {modo} de lista aberta")
            
        except Exception as e:
            logger.error(f"Erro ao criar formulário de lista - Modo: {modo}: {e}")
            self.mostrar_snackbar("Erro ao abrir formulário de lista.")

    def voltar_para_produtos_seguro(self):
        """Volta para tela de produtos de forma segura"""
        try:
            # Remove telas de cadastro/edição de produto
            self.remover_tela_segura("cadastro_produto")
            self.remover_tela_segura("edicao_produto")
            # Atualiza lista antes de exibir
            self.atualizar_lista_produtos()
            self.screen_manager.current = "produtos"
            logger.info("Voltou para tela de produtos")
        except Exception as e:
            logger.error(f"Erro ao voltar para produtos: {e}")

    def voltar_para_supermercados_seguro(self):
        """Volta para tela de supermercados de forma segura"""
        try:
            # Remove telas de cadastro/edição de supermercado
            self.remover_tela_segura("cadastro_supermercado")
            self.remover_tela_segura("edicao_supermercado")
            # Atualiza lista antes de exibir
            self.atualizar_lista_supermercados()
            self.screen_manager.current = "supermercados"
            logger.info("Voltou para tela de supermercados")
        except Exception as e:
            logger.error(f"Erro ao voltar para supermercados: {e}")

    def voltar_para_listas_seguro(self):
        """Volta para tela de listas de forma segura"""
        try:
            # Remove telas de cadastro/edição de lista
            self.remover_tela_segura("cadastro_lista")
            self.remover_tela_segura("edicao_lista")
            # Atualiza lista antes de exibir
            self.atualizar_lista_compras()
            self.screen_manager.current = "listas"
            logger.info("Voltou para tela de listas")
        except Exception as e:
            logger.error(f"Erro ao voltar para listas: {e}")

    def salvar_supermercado_unificado(self, eh_edicao=False):
        """Salva supermercado no modo cadastro ou edição"""
        try:
            nome = self.campo_nome_supermercado_form.text.strip()
            bairro = self.campo_bairro_supermercado_form.text.strip()
            
            # Validação
            valido, mensagem = self.validar_formulario_supermercado(nome, bairro)
            if not valido:
                self.mostrar_snackbar(mensagem)
                return
            
            if eh_edicao:
                # EDIÇÃO
                alterar_supermercado_apk(self.supermercado_edit_id, nome, bairro)
                mensagem_sucesso = "Supermercado editado com sucesso!"
                logger.info(f"Supermercado {self.supermercado_edit_id} editado")
            else:
                # CADASTRO
                cadastrar_supermercado_apk(nome, bairro)
                mensagem_sucesso = "Supermercado cadastrado com sucesso!"
                logger.info(f"Supermercado '{nome}' cadastrado")
            
            # Volta para lista e atualiza
            self.voltar_para_supermercados_seguro()  # Já atualiza a lista
            self.mostrar_snackbar(mensagem_sucesso)
            
        except Exception as e:
            logger.error(f"Erro ao salvar supermercado: {e}")
            self.mostrar_snackbar("Erro ao salvar supermercado.")

    def salvar_lista_unificado(self, eh_edicao=False):
        """Salva lista no modo cadastro ou edição"""
        try:
            nome = self.campo_nome_lista_form.text.strip()
            data_criacao = self.campo_data_lista_form.text.strip()
            
            # Validação
            valido, mensagem = self.validar_formulario_lista(nome, data_criacao)
            if not valido:
                self.mostrar_snackbar(mensagem)
                return
            
            if eh_edicao:
                # EDIÇÃO
                alterar_lista_apk(self.lista_edit_id, nome, data_criacao)
                mensagem_sucesso = "Lista editada com sucesso!"
                logger.info(f"Lista {self.lista_edit_id} editada")
            else:
                # CADASTRO
                cadastrar_lista_apk(nome, data_criacao)
                mensagem_sucesso = "Lista cadastrada com sucesso!"
                logger.info(f"Lista '{nome}' cadastrada")
            
            # Volta para lista e atualiza
            self.voltar_para_listas_seguro()  # Já atualiza a lista
            self.mostrar_snackbar(mensagem_sucesso)
            
        except Exception as e:
            logger.error(f"Erro ao salvar lista: {e}")
            self.mostrar_snackbar("Erro ao salvar lista.")

    # === VALIDAÇÕES ===
    def validar_formulario_produto(self, tipo_id, nome, marca, quantidade, categoria_id, subcategoria_id):
        """Valida dados do formulário de produto"""
        if not tipo_id:
            return False, "Selecione um tipo de produto."
        if not nome.strip():
            return False, "Nome do produto é obrigatório."
        if not marca.strip():
            return False, "Marca do produto é obrigatória."
        if not quantidade.strip():
            return False, "Quantidade/embalagem é obrigatória."
        if not categoria_id:
            return False, "Selecione uma categoria."
        if not subcategoria_id:
            return False, "Selecione uma subcategoria."
        return True, ""

    def validar_formulario_supermercado(self, nome, bairro):
        """Valida dados do formulário de supermercado"""
        if not nome.strip():
            return False, "Nome do supermercado é obrigatório."
        if not bairro.strip():
            return False, "Bairro é obrigatório."
        return True, ""

    def validar_formulario_lista(self, nome, data_criacao):
        """Valida dados do formulário de lista"""
        if not nome.strip():
            return False, "Nome da lista é obrigatório."
        if not data_criacao.strip():
            return False, "Data de criação é obrigatória."
        return True, ""

    # --- Funções de CRUD para Carrinhos ---
    def show_cadastro_carrinho_screen(self, *args):
        """Mostra tela de cadastro de carrinho"""
        self.criar_tela_carrinho_form(None)  # None indica novo carrinho

    def show_editar_carrinho_screen(self, *args):
        """Mostra tela de edição de carrinho"""
        selecionados = [carrinho_id for checkbox, carrinho_id in self.carrinhos_checkbox_refs if checkbox.active]
        if not selecionados:
            self.mostrar_snackbar("Selecione um carrinho para editar.")
            return
        if len(selecionados) > 1:
            self.mostrar_snackbar("Selecione apenas um carrinho para editar.")
            return
        
        self.criar_tela_carrinho_form(selecionados[0])  # ID do carrinho para edição

    def criar_tela_carrinho_form(self, carrinho_id=None):
        """Cria tela de cadastro/edição de carrinho"""
        try:
            # Determina se é edição ou cadastro
            is_edicao = carrinho_id is not None
            titulo = "Editar Carrinho" if is_edicao else "Cadastrar Carrinho"
            
            # Busca dados para pré-preenchimento
            dados_carrinho = None
            if is_edicao:
                carrinhos = listar_carrinhos_apk()
                dados_carrinho = next((c for c in carrinhos if c[0] == carrinho_id), None)
                if not dados_carrinho:
                    self.mostrar_snackbar("Carrinho não encontrado.")
                    return
            
            # Armazena ID do carrinho para edição
            self.carrinho_edit_id = carrinho_id
            
            # Inicializa seleções
            self.supermercado_carrinho_selecionado_id = dados_carrinho[2] if dados_carrinho else None
            self.lista_carrinho_selecionada_id = dados_carrinho[3] if dados_carrinho else None
            
            # Campo Nome
            self.campo_nome_carrinho = MDTextField(
                hint_text="Nome do Carrinho",
                text=dados_carrinho[1] if dados_carrinho else "",
                multiline=False,
                size_hint_y=None,
                height=dp(56),
                on_text=self.forcar_maiusculas
            )
            
            # Campo Supermercado (bottomsheet)
            texto_supermercado = "Selecionar Supermercado"
            if self.supermercado_carrinho_selecionado_id:
                supermercados = listar_supermercados_apk()
                super_info = next((s for s in supermercados if s[0] == self.supermercado_carrinho_selecionado_id), None)
                if super_info:
                    texto_supermercado = f"{super_info[1].upper()} - {super_info[2].upper()}"
            
            self.campo_supermercado_carrinho = MDTextField(
                hint_text="Supermercado",
                text=texto_supermercado,
                multiline=False,
                readonly=True,
                size_hint_y=None,
                height=dp(56)
            )
            self.campo_supermercado_carrinho.bind(on_touch_down=self._handle_supermercado_carrinho_touch)
            
            # Campo Lista (bottomsheet)
            texto_lista = "Selecionar Lista"
            if self.lista_carrinho_selecionada_id:
                listas = listar_listas_apk()
                lista_info = next((l for l in listas if l[0] == self.lista_carrinho_selecionada_id), None)
                if lista_info:
                    texto_lista = f"{lista_info[1].upper()} ({lista_info[2]})"
            
            self.campo_lista_carrinho = MDTextField(
                hint_text="Lista",
                text=texto_lista,
                multiline=False,
                readonly=True,
                size_hint_y=None,
                height=dp(56)
            )
            self.campo_lista_carrinho.bind(on_touch_down=self._handle_lista_carrinho_touch)
            
            # Campo Data
            data_padrao = datetime.now().strftime("%d/%m/%Y")
            if dados_carrinho and dados_carrinho[4]:
                # Converte de YYYY-MM-DD para DD/MM/YYYY
                try:
                    data_bd = datetime.strptime(dados_carrinho[4], "%Y-%m-%d")
                    data_padrao = data_bd.strftime("%d/%m/%Y")
                except:
                    pass
            
            self.campo_data_carrinho = MDTextField(
                hint_text="Data (DD/MM/AAAA)",
                text=data_padrao,
                multiline=False,
                size_hint_y=None,
                height=dp(56)
            )
            
            # Container principal
            content = BoxLayout(
                orientation="vertical",
                spacing=dp(15),
                padding=dp(20),
                size_hint_y=None,
            )
            content.bind(minimum_height=content.setter("height"))
            
            # Adiciona campos com rótulos
            content.add_widget(MDLabel(text="Nome do Carrinho", theme_text_color="Primary"))
            content.add_widget(self.campo_nome_carrinho)
            content.add_widget(MDLabel(text="Supermercado", theme_text_color="Primary"))
            content.add_widget(self.campo_supermercado_carrinho)
            content.add_widget(MDLabel(text="Lista", theme_text_color="Primary"))
            content.add_widget(self.campo_lista_carrinho)
            content.add_widget(MDLabel(text="Data", theme_text_color="Primary"))
            content.add_widget(self.campo_data_carrinho)
            
            # Scroll para o conteúdo
            scroll = MDScrollView()
            scroll.add_widget(content)
            
            # AppBar
            appbar = MDTopAppBar(
                MDTopAppBarLeadingButtonContainer(
                    MDActionTopAppBarButton(
                        icon="arrow-left",
                        on_release=lambda x: self.voltar_tela_carrinhos(),
                    ),
                ),
                MDTopAppBarTitle(
                    text=titulo,
                    halign="center",
                ),
                MDTopAppBarTrailingButtonContainer(
                    MDActionTopAppBarButton(
                        icon="content-save",
                        on_release=lambda x: self.salvar_carrinho(carrinho_id),
                    ),
                ),
                type="small",
                size_hint_y=None,
                height=dp(64),
            )
            
            # Layout principal
            layout = BoxLayout(orientation="vertical")
            layout.add_widget(appbar)
            layout.add_widget(scroll)
            
            # Adiciona tela ao screen manager
            screen_name = "form_carrinho"
            self.remover_tela_segura(screen_name)
            
            screen = MDScreen(layout, name=screen_name)
            self.screen_manager.add_widget(screen)
            self.screen_manager.current = screen_name
            
            # Define foco inicial
            Clock.schedule_once(lambda dt: setattr(self.campo_nome_carrinho, 'focus', True), 0.2)
            
        except Exception as e:
            logger.error(f"Erro ao criar tela de carrinho: {e}")
            self.mostrar_snackbar("Erro ao abrir formulário de carrinho.")

    # === HANDLERS PARA BOTTOMSHEETS DO CARRINHO ===
    def _handle_supermercado_carrinho_touch(self, instance, touch):
        """Handler para evento de toque no campo supermercado do carrinho"""
        if instance.collide_point(*touch.pos):
            self.abrir_bottomsheet_supermercados_carrinho()
        return False

    def _handle_lista_carrinho_touch(self, instance, touch):
        """Handler para evento de toque no campo lista do carrinho"""
        if instance.collide_point(*touch.pos):
            self.abrir_bottomsheet_listas_carrinho()
        return False

    def abrir_bottomsheet_supermercados_carrinho(self):
        """Abre BottomSheet para seleção de supermercado no carrinho"""
        try:
            supermercados = listar_supermercados_apk()
            
            # Container do BottomSheet
            bottomsheet_content = BoxLayout(
                orientation="vertical",
                spacing=dp(10),
                padding=dp(16),
                size_hint_y=None
            )
            bottomsheet_content.bind(minimum_height=bottomsheet_content.setter("height"))
            
            # Campo de filtro
            self.filtro_supermercado_carrinho = MDTextField(
                hint_text="Buscar supermercado...",
                size_hint_y=None,
                height=dp(56)
            )
            self.filtro_supermercado_carrinho.bind(text=self.filtrar_supermercados_carrinho_bottomsheet)
            bottomsheet_content.add_widget(self.filtro_supermercado_carrinho)
            
            # Lista scrollável
            self.lista_supermercados_carrinho = MDList()
            scroll = MDScrollView(size_hint=(1, 1), do_scroll_x=False)
            scroll.add_widget(self.lista_supermercados_carrinho)
            bottomsheet_content.add_widget(scroll)
            
            # Carrega supermercados
            self.carregar_supermercados_carrinho_bottomsheet(supermercados)
            
            # Cria BottomSheet
            self.bottomsheet_supermercados_carrinho = MDBottomSheet()
            self.bottomsheet_supermercados_carrinho.add_widget(bottomsheet_content)
            
            # Adiciona ao root para exibir
            self.root.add_widget(self.bottomsheet_supermercados_carrinho)
            self.bottomsheet_supermercados_carrinho.set_state("open")
            
            # Define foco no campo de filtro
            Clock.schedule_once(lambda dt: setattr(self.filtro_supermercado_carrinho, 'focus', True), 0.3)
            
        except Exception as e:
            logger.error(f"Erro ao abrir BottomSheet de supermercados: {e}")

    def carregar_supermercados_carrinho_bottomsheet(self, supermercados, filtro=""):
        """Carrega supermercados no BottomSheet com filtro opcional"""
        try:
            self.lista_supermercados_carrinho.clear_widgets()
            
            # Filtrar supermercados
            if filtro:
                supermercados_filtrados = [s for s in supermercados 
                                         if filtro.upper() in s[1].upper() or filtro.upper() in s[2].upper()]
            else:
                supermercados_filtrados = supermercados
            
            # Ordenar por nome
            supermercados_filtrados.sort(key=lambda x: x[1])
            
            for supermercado in supermercados_filtrados:
                super_id, nome, bairro = supermercado
                
                item = MDListItem(
                    MDListItemHeadlineText(text=nome.upper()),
                    MDListItemSupportingText(text=bairro.upper()),
                    on_release=lambda x, sid=super_id, snome=nome, sbairro=bairro: 
                        self.selecionar_supermercado_carrinho_bottomsheet(sid, snome, sbairro)
                )
                
                self.lista_supermercados_carrinho.add_widget(item)
                
        except Exception as e:
            logger.error(f"Erro ao carregar supermercados no BottomSheet: {e}")

    def filtrar_supermercados_carrinho_bottomsheet(self, instance, filtro):
        """Filtra supermercados no BottomSheet"""
        try:
            supermercados = listar_supermercados_apk()
            self.carregar_supermercados_carrinho_bottomsheet(supermercados, filtro)
        except Exception as e:
            logger.error(f"Erro ao filtrar supermercados: {e}")

    def selecionar_supermercado_carrinho_bottomsheet(self, supermercado_id, nome, bairro):
        """Seleciona supermercado via BottomSheet"""
        try:
            self.campo_supermercado_carrinho.text = f"{nome.upper()} - {bairro.upper()}"
            self.supermercado_carrinho_selecionado_id = supermercado_id
            self.bottomsheet_supermercados_carrinho.set_state("close")
            # Remove do root após fechar
            if self.bottomsheet_supermercados_carrinho.parent:
                self.bottomsheet_supermercados_carrinho.parent.remove_widget(self.bottomsheet_supermercados_carrinho)
        except Exception as e:
            logger.error(f"Erro ao selecionar supermercado: {e}")

    def abrir_bottomsheet_listas_carrinho(self):
        """Abre BottomSheet para seleção de lista no carrinho"""
        try:
            listas = listar_listas_apk()
            
            # Container do BottomSheet
            bottomsheet_content = BoxLayout(
                orientation="vertical",
                spacing=dp(10),
                padding=dp(16),
                size_hint_y=None
            )
            bottomsheet_content.bind(minimum_height=bottomsheet_content.setter("height"))
            
            # Campo de filtro
            self.filtro_lista_carrinho = MDTextField(
                hint_text="Buscar lista...",
                size_hint_y=None,
                height=dp(56)
            )
            self.filtro_lista_carrinho.bind(text=self.filtrar_listas_carrinho_bottomsheet)
            bottomsheet_content.add_widget(self.filtro_lista_carrinho)
            
            # Lista scrollável
            self.lista_listas_carrinho = MDList()
            scroll = MDScrollView(size_hint=(1, 1), do_scroll_x=False)
            scroll.add_widget(self.lista_listas_carrinho)
            bottomsheet_content.add_widget(scroll)
            
            # Carrega listas
            self.carregar_listas_carrinho_bottomsheet(listas)
            
            # Cria BottomSheet
            self.bottomsheet_listas_carrinho = MDBottomSheet()
            self.bottomsheet_listas_carrinho.add_widget(bottomsheet_content)
            
            # Adiciona ao root para exibir
            self.root.add_widget(self.bottomsheet_listas_carrinho)
            self.bottomsheet_listas_carrinho.set_state("open")
            
            # Define foco no campo de filtro
            Clock.schedule_once(lambda dt: setattr(self.filtro_lista_carrinho, 'focus', True), 0.3)
            
        except Exception as e:
            logger.error(f"Erro ao abrir BottomSheet de listas: {e}")

    def carregar_listas_carrinho_bottomsheet(self, listas, filtro=""):
        """Carrega listas no BottomSheet com filtro opcional"""
        try:
            self.lista_listas_carrinho.clear_widgets()
            
            # Filtrar listas
            if filtro:
                listas_filtradas = [l for l in listas if filtro.upper() in l[1].upper()]
            else:
                listas_filtradas = listas
            
            # Ordenar por nome
            listas_filtradas.sort(key=lambda x: x[1])
            
            for lista in listas_filtradas:
                lista_id, nome, data_criacao = lista
                
                # Formatar data
                data_formatada = data_criacao
                try:
                    data_obj = datetime.strptime(data_criacao, "%Y-%m-%d")
                    data_formatada = data_obj.strftime("%d/%m/%Y")
                except:
                    pass
                
                item = MDListItem(
                    MDListItemHeadlineText(text=nome.upper()),
                    MDListItemSupportingText(text=data_formatada),
                    on_release=lambda x, lid=lista_id, lnome=nome: 
                        self.selecionar_lista_carrinho_bottomsheet(lid, lnome)
                )
                
                self.lista_listas_carrinho.add_widget(item)
                
        except Exception as e:
            logger.error(f"Erro ao carregar listas no BottomSheet: {e}")

    def filtrar_listas_carrinho_bottomsheet(self, instance, filtro):
        """Filtra listas no BottomSheet"""
        try:
            listas = listar_listas_apk()
            self.carregar_listas_carrinho_bottomsheet(listas, filtro)
        except Exception as e:
            logger.error(f"Erro ao filtrar listas: {e}")

    def selecionar_lista_carrinho_bottomsheet(self, lista_id, nome):
        """Seleciona lista via BottomSheet"""
        try:
            self.campo_lista_carrinho.text = nome.upper()
            self.lista_carrinho_selecionada_id = lista_id
            self.bottomsheet_listas_carrinho.set_state("close")
            # Remove do root após fechar
            if self.bottomsheet_listas_carrinho.parent:
                self.bottomsheet_listas_carrinho.parent.remove_widget(self.bottomsheet_listas_carrinho)
        except Exception as e:
            logger.error(f"Erro ao selecionar lista: {e}")

    def salvar_carrinho(self, carrinho_id=None):
        """Salva carrinho (cadastro ou edição)"""
        try:
            # Validação
            nome = self.campo_nome_carrinho.text.strip()
            data_input = self.campo_data_carrinho.text.strip()
            
            if not nome:
                self.mostrar_snackbar("Nome do carrinho é obrigatório.")
                return
            
            if not hasattr(self, 'supermercado_carrinho_selecionado_id') or not self.supermercado_carrinho_selecionado_id:
                self.mostrar_snackbar("Selecione um supermercado.")
                return
            
            if not hasattr(self, 'lista_carrinho_selecionada_id') or not self.lista_carrinho_selecionada_id:
                self.mostrar_snackbar("Selecione uma lista.")
                return
            
            # Converte data de DD/MM/AAAA para AAAA-MM-DD
            data_bd = None
            if data_input:
                try:
                    # Tenta converter de DD/MM/AAAA
                    if "/" in data_input:
                        data_obj = datetime.strptime(data_input, "%d/%m/%Y")
                    else:
                        # Se já estiver em formato AAAA-MM-DD
                        data_obj = datetime.strptime(data_input, "%Y-%m-%d")
                    data_bd = data_obj.strftime("%Y-%m-%d")
                except:
                    self.mostrar_snackbar("Formato de data inválido. Use DD/MM/AAAA.")
                    return
            else:
                data_bd = datetime.now().strftime("%Y-%m-%d")
            
            # Salva no banco
            if carrinho_id:  # Edição
                sucesso = alterar_carrinho_apk(
                    carrinho_id, nome, self.supermercado_carrinho_selecionado_id,
                    self.lista_carrinho_selecionada_id, data_bd
                )
                mensagem = "Carrinho atualizado com sucesso!" if sucesso else "Erro ao atualizar carrinho."
            else:  # Cadastro
                sucesso = cadastrar_carrinho_apk(
                    nome, self.supermercado_carrinho_selecionado_id,
                    self.lista_carrinho_selecionada_id, data_bd
                )
                mensagem = "Carrinho cadastrado com sucesso!" if sucesso else "Erro ao cadastrar carrinho."
            
            self.mostrar_snackbar(mensagem)
            
            if sucesso:
                self.voltar_tela_carrinhos()
                
        except Exception as e:
            logger.error(f"Erro ao salvar carrinho: {e}")
            self.mostrar_snackbar("Erro ao salvar carrinho.")

    def voltar_tela_carrinhos(self):
        """Volta para tela de carrinhos e atualiza lista"""
        try:
            self.screen_manager.current = "carrinhos"
            self.atualizar_lista_carrinhos()
        except Exception as e:
            logger.error(f"Erro ao voltar para tela de carrinhos: {e}")

    def excluir_carrinho(self, *args):
        """Exclui carrinhos selecionados com confirmação ou abre lixeira se nada selecionado"""
        try:
            selecionados = [carrinho_id for checkbox, carrinho_id in self.carrinhos_checkbox_refs if checkbox.active]
            
            if not selecionados:
                # Se nada está selecionado, abre a lixeira específica de carrinhos
                self.visualizar_lixeira('carrinho')
                return
            
            # Cria popup de confirmação
            self.criar_popup_confirmacao_exclusao_carrinho(selecionados)
                
        except Exception as e:
            logger.error(f"Erro ao iniciar exclusão de carrinhos: {e}")
            self.mostrar_snackbar("Erro ao excluir carrinhos.")

    # === SISTEMA GENÉRICO DE CONFIRMAÇÃO DE EXCLUSÃO ===
    def criar_popup_confirmacao_exclusao_generico(self, itens_ids, tipo_item, callback_exclusao):
        """
        Cria popup de confirmação genérico para exclusão
        
        Args:
            itens_ids: Lista de IDs dos itens a serem excluídos
            tipo_item: String descrevendo o tipo de item (ex: "produto", "carrinho", "lista")
            callback_exclusao: Função que será chamada para executar a exclusão
        """
        try:
            qtd_itens = len(itens_ids)
            plural = "s" if qtd_itens > 1 else ""
            artigo = "os" if qtd_itens > 1 else ("o" if tipo_item.endswith('o') else "a")
            
            texto_confirmacao = f"Tem certeza que deseja excluir {artigo} {qtd_itens} {tipo_item}{plural} selecionado{plural}?"
            
            # Botões do dialog
            botoes = [
                MDButton(
                    MDButtonText(text="CANCELAR"),
                    style="text",
                    on_release=lambda x: self.fechar_popup_confirmacao()
                ),
                MDButton(
                    MDButtonText(text="EXCLUIR"),
                    style="filled",
                    on_release=lambda x: callback_exclusao(itens_ids)
                )
            ]
            
            # Cria o dialog
            self.popup_confirmacao = MDDialog(
                MDDialogHeadlineText(text="Confirmar Exclusão"),
                MDDialogSupportingText(text=texto_confirmacao),
                MDDialogButtonContainer(*botoes),
                size_hint=(0.8, None),
                height=dp(200)
            )
            
            self.popup_confirmacao.open()
            
        except Exception as e:
            logger.error(f"Erro ao criar popup de confirmação genérico: {e}")

    def fechar_popup_confirmacao(self):
        """Fecha popup de confirmação"""
        try:
            if hasattr(self, 'popup_confirmacao'):
                self.popup_confirmacao.dismiss()
        except Exception as e:
            logger.error(f"Erro ao fechar popup: {e}")

    # === SISTEMA DE LIXEIRA ===
    def inicializar_lixeira(self):
        """Inicializa o sistema de lixeira"""
        try:
            # Verifica se tabelas de lixeira existem, senão cria
            from database_apk import criar_tabelas_lixeira_apk
            criar_tabelas_lixeira_apk()
            logger.info("Sistema de lixeira inicializado")
        except Exception as e:
            logger.error(f"Erro ao inicializar lixeira: {e}")

    def executar_migracoes(self):
        """Executa migrações necessárias do banco de dados"""
        try:
            from database_apk import migrar_tabela_carrinhos_status
            migrar_tabela_carrinhos_status()
            logger.info("Migrações executadas com sucesso")
        except Exception as e:
            logger.error(f"Erro ao executar migrações: {e}")

    def mover_para_lixeira(self, item_id, tipo_item, dados_item):
        """
        Move item para lixeira antes da exclusão definitiva
        
        Args:
            item_id: ID do item
            tipo_item: Tipo do item (produto, carrinho, lista, etc.)
            dados_item: Dados completos do item em formato JSON
        """
        try:
            from database_apk import inserir_item_lixeira_apk
            
            data_exclusao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            dados_json = json.dumps(dados_item)
            
            sucesso = inserir_item_lixeira_apk(item_id, tipo_item, dados_json, data_exclusao)
            if sucesso:
                logger.info(f"Item {tipo_item} {item_id} movido para lixeira")
            
            return sucesso
            
        except Exception as e:
            logger.error(f"Erro ao mover item para lixeira: {e}")
            return False

    def visualizar_lixeira(self, tipo_filtro=None):
        """Abre tela para visualizar itens na lixeira com filtro opcional por tipo"""
        try:
            from database_apk import listar_itens_lixeira_apk
            
            # Armazena a tela atual antes de ir para lixeira
            if hasattr(self, 'screen_manager') and self.screen_manager.current != "lixeira":
                self.tela_anterior_lixeira = self.screen_manager.current
            
            # Busca itens na lixeira com filtro
            itens_lixeira = listar_itens_lixeira_apk(tipo_filtro)
            
            if not itens_lixeira:
                tipo_nome = tipo_filtro.replace('_', ' ').title() if tipo_filtro else "A"
                self.mostrar_snackbar(f"{tipo_nome} lixeira está vazia.")
                return
            
            self.criar_tela_lixeira(itens_lixeira, tipo_filtro)
            
        except Exception as e:
            logger.error(f"Erro ao visualizar lixeira: {e}")
            self.mostrar_snackbar("Erro ao abrir lixeira.")

    def criar_tela_lixeira(self, itens_lixeira, tipo_filtro=None):
        """Cria tela de visualização da lixeira com filtro opcional"""
        try:
            # Armazena o filtro atual para uso em atualizações
            self.lixeira_filtro_atual = tipo_filtro
            
            # Título baseado no filtro
            if tipo_filtro:
                tipo_nome = tipo_filtro.replace('_', ' ').title()
                titulo = f"Lixeira - {tipo_nome}s"
            else:
                titulo = "Lixeira"
            
            # Lista para itens da lixeira
            self.lixeira_list = MDList()
            self.lixeira_checkbox_refs = []
            # Limpa referências anteriores de checkboxes da lixeira
            self.limpar_referencias_checkbox('lixeira')
            
            # Limpeza adicional para evitar checkboxes órfãos
            self.lixeira_checkbox_refs = []
            
            # Carrega itens
            for item in itens_lixeira:
                item_id, tipo_item, dados_json, data_exclusao = item
                
                try:
                    dados = json.loads(dados_json)
                    
                    # Melhora a exibição baseada no tipo de item
                    if tipo_item == 'produto':
                        nome_produto = dados.get('nome', 'Nome não encontrado')
                        marca_produto = dados.get('marca', '')
                        if marca_produto:
                            nome_item = f"{nome_produto} - {marca_produto}"
                        else:
                            nome_item = nome_produto
                    else:
                        # Para outros tipos, usa o nome padrão
                        nome_item = str(dados.get('nome', f"{tipo_item.title()} {item_id}"))
                        
                except:
                    nome_item = f"{tipo_item.title()} {item_id}"
                
                # Formatar data
                data_formatada = str(data_exclusao)
                try:
                    data_obj = datetime.strptime(str(data_exclusao), "%Y-%m-%d %H:%M:%S")
                    data_formatada = data_obj.strftime("%d/%m/%y %H:%M")
                except:
                    pass
                
                checkbox = MDCheckbox()
                self.lixeira_checkbox_refs.append((checkbox, item_id, tipo_item))
                
                item_widget = MDListItem(
                    checkbox,
                    MDListItemHeadlineText(text=f"{nome_item.upper()} ({tipo_item.upper()})"),
                    MDListItemSupportingText(text=f"Excluído em: {data_formatada}"),
                    padding=(dp(8), dp(8), dp(8), dp(8)),
                )
                self.lixeira_list.add_widget(item_widget)
            
            # Scroll para a lista
            scroll = MDScrollView()
            scroll.add_widget(self.lixeira_list)
            
            # Botões de ação
            botoes_box = BoxLayout(
                orientation="horizontal",
                spacing=dp(8),
                size_hint_y=None,
                height=dp(56),
                padding=(dp(16), dp(8))
            )
            
            btn_restaurar = MDButton(
                MDButtonText(text="RESTAURAR"),
                style="outlined",
                on_release=lambda x: self.restaurar_itens_lixeira(),
                size_hint_x=0.5
            )
            
            btn_excluir_definitivo = MDButton(
                MDButtonText(text="EXCLUIR DEFINITIVAMENTE"),
                style="filled",
                theme_bg_color="Custom",
                md_bg_color=(1, 0, 0, 1),
                on_release=lambda x: self.excluir_definitivamente_lixeira(),
                size_hint_x=0.5
            )
            
            botoes_box.add_widget(btn_restaurar)
            botoes_box.add_widget(btn_excluir_definitivo)
            
            # AppBar
            appbar = MDTopAppBar(
                MDTopAppBarLeadingButtonContainer(
                    MDActionTopAppBarButton(
                        icon="arrow-left",
                        on_release=lambda x: self.voltar_tela_anterior(),
                    ),
                ),
                MDTopAppBarTitle(
                    text=titulo,
                    halign="center",
                ),
                MDTopAppBarTrailingButtonContainer(
                    MDActionTopAppBarButton(
                        icon="delete-sweep",
                        on_release=lambda x: self.limpar_lixeira_completa(),
                    ),
                ),
                type="small",
                size_hint_y=None,
                height=dp(64),
            )
            
            # Layout principal
            layout = BoxLayout(orientation="vertical")
            layout.add_widget(appbar)
            layout.add_widget(scroll)
            layout.add_widget(botoes_box)
            
            # Adiciona tela ao screen manager
            screen_name = "lixeira"
            self.remover_tela_segura(screen_name)
            
            screen = MDScreen(layout, name=screen_name)
            self.screen_manager.add_widget(screen)
            self.screen_manager.current = screen_name
            
            logger.info(f"Tela de lixeira aberta com {len(itens_lixeira)} itens")
            
        except Exception as e:
            logger.error(f"Erro ao criar tela de lixeira: {e}")
            self.mostrar_snackbar("Erro ao criar tela de lixeira.")

    def restaurar_itens_lixeira(self):
        """Restaura itens selecionados da lixeira"""
        try:
            selecionados = [(item_id, tipo_item) for checkbox, item_id, tipo_item in self.lixeira_checkbox_refs if checkbox.active]
            
            if not selecionados:
                self.mostrar_snackbar("Selecione itens para restaurar.")
                return
            
            self.criar_popup_confirmacao_restauracao(selecionados)
            
        except Exception as e:
            logger.error(f"Erro ao restaurar itens da lixeira: {e}")
            self.mostrar_snackbar("Erro ao restaurar itens.")

    def criar_popup_confirmacao_restauracao(self, itens_selecionados):
        """Cria popup de confirmação específico para restauração"""
        try:
            qtd_itens = len(itens_selecionados)
            plural = "s" if qtd_itens > 1 else ""
            artigo = "os" if qtd_itens > 1 else "o"
            
            texto_confirmacao = f"Tem certeza que deseja restaurar {artigo} {qtd_itens} item{plural} selecionado{plural}? Eles serão movidos de volta para suas listas originais."
            
            # Botões do dialog
            botoes = [
                MDButton(
                    MDButtonText(text="CANCELAR"),
                    style="text",
                    on_release=lambda x: self.fechar_popup_confirmacao()
                ),
                MDButton(
                    MDButtonText(text="RESTAURAR"),
                    style="filled",
                    theme_bg_color="Custom",
                    md_bg_color=(0, 0.6, 0, 1),
                    on_release=lambda x: self.confirmar_restauracao_lixeira(itens_selecionados)
                )
            ]
            
            # Cria o dialog
            self.popup_confirmacao = MDDialog(
                MDDialogHeadlineText(text="Confirmar Restauração"),
                MDDialogSupportingText(text=texto_confirmacao),
                MDDialogButtonContainer(*botoes),
                size_hint=(0.8, None),
                height=dp(250)
            )
            
            self.popup_confirmacao.open()
            
        except Exception as e:
            logger.error(f"Erro ao criar popup de confirmação de restauração: {e}")

    def confirmar_restauracao_lixeira(self, itens_selecionados):
        """Confirma e executa restauração dos itens da lixeira"""
        try:
            from database_apk import restaurar_item_lixeira_apk
            
            restaurados = 0
            tipos_restaurados = set()
            
            for item_id, tipo_item in itens_selecionados:
                sucesso = restaurar_item_lixeira_apk(item_id, tipo_item)
                if sucesso:
                    restaurados += 1
                    tipos_restaurados.add(tipo_item)
            
            self.fechar_popup_confirmacao()
            
            # Limpar seleções dos checkboxes SEMPRE
            if hasattr(self, 'lixeira_checkbox_refs'):
                for checkbox, item_id, tipo_item in self.lixeira_checkbox_refs:
                    checkbox.active = False
            
            if restaurados > 0:
                self.mostrar_snackbar(f"{restaurados} item(ns) restaurado(s)!")
                
                # Atualiza as listas correspondentes com base nos tipos restaurados
                if 'produto' in tipos_restaurados:
                    self.atualizar_lista_produtos()
                if 'supermercado' in tipos_restaurados:
                    self.atualizar_lista_supermercados()
                if 'lista' in tipos_restaurados:
                    self.atualizar_lista_compras()
                if 'carrinho' in tipos_restaurados:
                    self.atualizar_lista_carrinhos()
                if 'tipo_produto' in tipos_restaurados:
                    self.atualizar_lista_tipos_produto()
                
                # Volta para a tela anterior SEM chamar atualização novamente
                self.voltar_tela_anterior_sem_atualizacao()
            else:
                self.mostrar_snackbar("Nenhum item foi restaurado.")
                
        except Exception as e:
            logger.error(f"Erro na restauração de itens: {e}")
            self.mostrar_snackbar("Erro ao restaurar itens.")

    def excluir_definitivamente_lixeira(self):
        """Exclui definitivamente itens selecionados da lixeira"""
        try:
            selecionados = [(item_id, tipo_item) for checkbox, item_id, tipo_item in self.lixeira_checkbox_refs if checkbox.active]
            
            if not selecionados:
                self.mostrar_snackbar("Selecione itens para excluir definitivamente.")
                return
            
            self.criar_popup_confirmacao_exclusao_generico(
                selecionados, "item da lixeira (PERMANENTEMENTE)", self.confirmar_exclusao_definitiva_lixeira
            )
            
        except Exception as e:
            logger.error(f"Erro ao excluir definitivamente itens: {e}")
            self.mostrar_snackbar("Erro ao excluir itens.")

    def confirmar_exclusao_definitiva_lixeira(self, itens_selecionados):
        """Confirma e executa exclusão definitiva dos itens da lixeira"""
        try:
            from database_apk import excluir_definitivamente_lixeira_apk
            
            excluidos = 0
            for item_id, tipo_item in itens_selecionados:
                sucesso = excluir_definitivamente_lixeira_apk(item_id, tipo_item)
                if sucesso:
                    excluidos += 1
            
            self.fechar_popup_confirmacao()
            
            # Limpar seleções dos checkboxes SEMPRE
            if hasattr(self, 'lixeira_checkbox_refs'):
                for checkbox, item_id, tipo_item in self.lixeira_checkbox_refs:
                    checkbox.active = False
            
            if excluidos > 0:
                self.mostrar_snackbar(f"{excluidos} item(ns) excluído(s) definitivamente!")
                # Atualiza a tela de lixeira mantendo o filtro atual
                self.visualizar_lixeira(getattr(self, 'lixeira_filtro_atual', None))
            else:
                self.mostrar_snackbar("Nenhum item foi excluído.")
                
        except Exception as e:
            logger.error(f"Erro na exclusão definitiva de itens: {e}")
            self.mostrar_snackbar("Erro ao excluir itens definitivamente.")

    def limpar_lixeira_completa(self):
        """Limpa toda a lixeira após confirmação"""
        try:
            # Popup de confirmação para limpeza completa
            botoes = [
                MDButton(
                    MDButtonText(text="CANCELAR"),
                    style="text",
                    on_release=lambda x: self.fechar_popup_confirmacao()
                ),
                MDButton(
                    MDButtonText(text="LIMPAR TUDO"),
                    style="filled",
                    theme_bg_color="Custom",
                    md_bg_color=(1, 0, 0, 1),
                    on_release=lambda x: self.confirmar_limpeza_completa_lixeira()
                )
            ]
            
            self.popup_confirmacao = MDDialog(
                MDDialogHeadlineText(text="Limpar Lixeira"),
                MDDialogSupportingText(text="Tem certeza que deseja excluir TODOS os itens da lixeira permanentemente? Esta ação não pode ser desfeita."),
                MDDialogButtonContainer(*botoes),
                size_hint=(0.8, None),
                height=dp(220)
            )
            
            self.popup_confirmacao.open()
            
        except Exception as e:
            logger.error(f"Erro ao limpar lixeira: {e}")

    def confirmar_limpeza_completa_lixeira(self):
        """Confirma e executa limpeza completa da lixeira"""
        try:
            from database_apk import limpar_lixeira_completa_apk
            
            sucesso = limpar_lixeira_completa_apk()
            self.fechar_popup_confirmacao()
            
            if sucesso:
                self.mostrar_snackbar("Lixeira limpa completamente!")
                self.voltar_tela_anterior()  # Volta para tela anterior
            else:
                self.mostrar_snackbar("Erro ao limpar lixeira.")
                
        except Exception as e:
            logger.error(f"Erro na limpeza completa da lixeira: {e}")
            self.mostrar_snackbar("Erro ao limpar lixeira.")

    def voltar_tela_anterior(self):
        """Volta para a tela anterior (genérico)"""
        try:
            # Remove tela de lixeira
            self.remover_tela_segura("lixeira")
            
            # Vai para a tela anterior armazenada ou padrão
            if hasattr(self, 'screen_manager') and self.screen_manager:
                if hasattr(self, 'tela_anterior_lixeira') and self.tela_anterior_lixeira:
                    # Vai para a tela específica de onde veio
                    tela_anterior = self.tela_anterior_lixeira
                    self.screen_manager.current = tela_anterior
                    
                    # Atualiza a lista da tela anterior
                    if tela_anterior == "produtos":
                        self.atualizar_lista_produtos()
                    elif tela_anterior == "supermercados":
                        self.atualizar_lista_supermercados()
                    elif tela_anterior == "listas":
                        self.atualizar_lista_compras()
                    elif tela_anterior == "carrinhos":
                        self.atualizar_lista_carrinhos()
                    elif tela_anterior == "tipos_produto":
                        self.atualizar_lista_tipos_produto()
                else:
                    # Fallback para produtos
                    screens = [screen.name for screen in self.screen_manager.screens]
                    if "produtos" in screens:
                        self.screen_manager.current = "produtos"
                        self.atualizar_lista_produtos()
                    elif len(screens) > 1:
                        self.screen_manager.current = screens[-2]  # Penúltima tela
                    
        except Exception as e:
            logger.error(f"Erro ao voltar para tela anterior: {e}")

    def voltar_tela_anterior_sem_atualizacao(self):
        """Volta para a tela anterior SEM chamar atualizações (evita duplicação)"""
        try:
            # Remove tela de lixeira
            self.remover_tela_segura("lixeira")
            
            # Vai para a tela anterior armazenada ou padrão
            if hasattr(self, 'screen_manager') and self.screen_manager:
                if hasattr(self, 'tela_anterior_lixeira') and self.tela_anterior_lixeira:
                    # Vai para a tela específica de onde veio SEM atualizar
                    tela_anterior = self.tela_anterior_lixeira
                    self.screen_manager.current = tela_anterior
                    logger.info(f"Voltou para tela {tela_anterior} sem atualização adicional")
                else:
                    # Fallback para produtos sem atualização
                    screens = [screen.name for screen in self.screen_manager.screens]
                    if "produtos" in screens:
                        self.screen_manager.current = "produtos"
                    elif len(screens) > 1:
                        self.screen_manager.current = screens[-2]  # Penúltima tela
                    
        except Exception as e:
            logger.error(f"Erro ao voltar para tela anterior: {e}")

    def criar_popup_confirmacao_exclusao_carrinho(self, carrinhos_ids):
        """Cria popup de confirmação para exclusão de carrinhos"""
        self.criar_popup_confirmacao_exclusao_generico(
            carrinhos_ids, "carrinho", self.confirmar_exclusao_carrinhos
        )

    def confirmar_exclusao_carrinhos(self, carrinhos_ids):
        """Confirma e executa exclusão dos carrinhos com sistema de lixeira"""
        try:
            carrinhos = listar_carrinhos_apk()
            excluidos = []
            refs_para_remover = []
            
            for carrinho_id in carrinhos_ids:
                try:
                    # Busca dados do carrinho para mover para lixeira
                    carrinho_data = next((c for c in carrinhos if c[0] == carrinho_id), None)
                    if carrinho_data:
                        # Prepara dados para lixeira
                        dados_carrinho = {
                            'id': carrinho_data[0],
                            'nome': carrinho_data[1],
                            'supermercado_id': carrinho_data[2],
                            'lista_id': carrinho_data[3],
                            'data_criacao': carrinho_data[4]
                        }
                        
                        # Move para lixeira primeiro
                        if self.mover_para_lixeira(carrinho_id, 'carrinho', dados_carrinho):
                            # Depois exclui do banco principal
                            sucesso = excluir_carrinho_apk(carrinho_id)
                            if sucesso:
                                excluidos.append(carrinho_id)
                                # Encontra referência para remover
                                for checkbox, cid in self.carrinhos_checkbox_refs:
                                    if cid == carrinho_id:
                                        refs_para_remover.append((checkbox, cid))
                                        break
                                logger.info(f"Carrinho {carrinho_id} movido para lixeira e excluído")
                        
                except Exception as e:
                    logger.error(f"Erro ao excluir carrinho {carrinho_id}: {e}")
            
            # Remove referências
            for ref in refs_para_remover:
                checkbox, carrinho_id = ref
                # Limpa o estado visual do checkbox
                checkbox.active = False
                if ref in self.carrinhos_checkbox_refs:
                    self.carrinhos_checkbox_refs.remove(ref)
            
            # Fecha popup e mostra resultado
            self.fechar_popup_confirmacao()
            
            if excluidos:
                self.mostrar_snackbar(f"{len(excluidos)} carrinho(s) excluído(s) e movido(s) para lixeira!")
                # Atualiza a lista automaticamente
                self.atualizar_lista_carrinhos()
            else:
                self.mostrar_snackbar("Nenhum carrinho foi excluído.")
                
        except Exception as e:
            logger.error(f"Erro na confirmação de exclusão: {e}")
            self.mostrar_snackbar("Erro ao excluir carrinhos.")

    def show_itens_carrinho_screen(self, *args):
        """Mostra itens do carrinho selecionado"""
        try:
            selecionados = [carrinho_id for checkbox, carrinho_id in self.carrinhos_checkbox_refs if checkbox.active]
            if not selecionados:
                self.mostrar_snackbar("Selecione um carrinho para visualizar.")
                return
            if len(selecionados) > 1:
                self.mostrar_snackbar("Selecione apenas um carrinho para visualizar.")
                return
            
            self.carrinho_atual_visualizado_id = selecionados[0]
            self.criar_tela_itens_carrinho(selecionados[0])
                
        except Exception as e:
            logger.error(f"Erro ao mostrar itens do carrinho: {e}")
            self.mostrar_snackbar("Erro ao abrir itens do carrinho.")

    def criar_tela_itens_carrinho(self, carrinho_id):
        """Cria tela de itens do carrinho com totais"""
        try:
            # Busca informações do carrinho
            carrinhos = listar_carrinhos_apk()
            carrinho_info = next((c for c in carrinhos if c[0] == carrinho_id), None)
            if not carrinho_info:
                self.mostrar_snackbar("Carrinho não encontrado.")
                return
            
            nome_carrinho = carrinho_info[1]
            supermercado_id = carrinho_info[2]
            
            # Lista para itens
            self.itens_carrinho_list = MDList()
            
            # Container principal
            main_container = BoxLayout(orientation="vertical")
            
            # AppBar
            appbar = MDTopAppBar(
                MDTopAppBarLeadingButtonContainer(
                    MDActionTopAppBarButton(
                        icon="arrow-left",
                        on_release=lambda x: self.voltar_tela_carrinhos(),
                    ),
                ),
                MDTopAppBarTitle(
                    text=f"Itens - {nome_carrinho.upper()}",
                    halign="center",
                ),
                MDTopAppBarTrailingButtonContainer(
                    MDActionTopAppBarButton(
                        icon="plus",
                        on_release=lambda x: self.mostrar_snackbar("Adicionar item em desenvolvimento."),
                    ),
                ),
                type="small",
                size_hint_y=None,
                height=dp(64),
            )
            main_container.add_widget(appbar)
            
            # Scroll para lista de itens
            scroll = MDScrollView()
            scroll.add_widget(self.itens_carrinho_list)
            main_container.add_widget(scroll)
            
            # Área de totais (split button na parte inferior)
            self.criar_area_totais_carrinho()
            main_container.add_widget(self.area_totais_carrinho)
            
            # Atualiza lista de itens
            self.atualizar_lista_itens_carrinho(carrinho_id)
            
            # Adiciona tela ao screen manager
            screen_name = "itens_carrinho"
            if self.screen_manager.has_screen(screen_name):
                self.screen_manager.remove_widget(self.screen_manager.get_screen(screen_name))
            
            screen = MDScreen(main_container, name=screen_name)
            self.screen_manager.add_widget(screen)
            self.screen_manager.current = screen_name
            
        except Exception as e:
            logger.error(f"Erro ao criar tela de itens do carrinho: {e}")
            self.mostrar_snackbar("Erro ao abrir itens do carrinho.")

    def criar_area_totais_carrinho(self):
        """Cria área de totais na parte inferior"""
        try:
            self.area_totais_carrinho = BoxLayout(
                orientation="vertical",
                size_hint_y=None,
                height=dp(100),
                spacing=dp(8),
                padding=(dp(16), dp(8), dp(16), dp(16))
            )
            
            # Linha com total geral
            linha_total = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(40)
            )
            
            self.label_total_geral = MDLabel(
                text="TOTAL GERAL: R$ 0,00",
                theme_text_color="Primary",
                bold=True,
                halign="right",
                font_size="18sp"
            )
            
            linha_total.add_widget(MDLabel())  # Espaçador
            linha_total.add_widget(self.label_total_geral)
            
            # Linha com botões (split button)
            linha_botoes = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(48),
                spacing=dp(8)
            )
            
            # Verifica se carrinho está finalizado para mostrar botão apropriado
            carrinho_finalizado = self.verificar_carrinho_finalizado()
            
            if carrinho_finalizado:
                btn_reabrir = MDButton(
                    MDButtonText(text="REABRIR CARRINHO"),
                    style="outlined",
                    theme_bg_color="Custom",
                    md_bg_color=(0, 0.7, 0, 1),
                    on_release=lambda x: self.reabrir_carrinho(),
                    size_hint_x=0.6
                )
                linha_botoes.add_widget(btn_reabrir)
            else:
                btn_finalizar = MDButton(
                    MDButtonText(text="FINALIZAR COMPRA"),
                    style="filled",
                    theme_bg_color="Custom",
                    md_bg_color=(0, 0.6, 0, 1),
                    on_release=lambda x: self.finalizar_carrinho(),
                    size_hint_x=0.6
                )
                linha_botoes.add_widget(btn_finalizar)
            
            btn_editar = MDButton(
                MDButtonText(text="EDITAR"),
                style="outlined",
                on_release=lambda x: self.mostrar_snackbar("Editar itens em desenvolvimento."),
                size_hint_x=0.4
            )
            
            linha_botoes.add_widget(btn_editar)
            
            self.area_totais_carrinho.add_widget(linha_total)
            self.area_totais_carrinho.add_widget(linha_botoes)
            
        except Exception as e:
            logger.error(f"Erro ao criar área de totais: {e}")

    def verificar_carrinho_finalizado(self):
        """Verifica se o carrinho atual está finalizado"""
        try:
            if not hasattr(self, 'carrinho_atual_visualizado_id'):
                return False
            
            carrinhos = listar_carrinhos_apk()
            carrinho_info = next((c for c in carrinhos if c[0] == self.carrinho_atual_visualizado_id), None)
            if carrinho_info and len(carrinho_info) >= 6:
                return bool(carrinho_info[5])  # campo finalizado
            return False
        except Exception as e:
            logger.error(f"Erro ao verificar status do carrinho: {e}")
            return False

    def finalizar_carrinho(self):
        """Finaliza o carrinho atual"""
        try:
            if not hasattr(self, 'carrinho_atual_visualizado_id'):
                self.mostrar_snackbar("Nenhum carrinho selecionado.")
                return
            
            from database_apk import finalizar_carrinho_apk
            
            # Popup de confirmação
            botoes = [
                MDButton(
                    MDButtonText(text="CANCELAR"),
                    style="outlined",
                    on_release=lambda x: self.fechar_popup_confirmacao(),
                ),
                MDButton(
                    MDButtonText(text="FINALIZAR"),
                    style="filled",
                    theme_bg_color="Custom",
                    md_bg_color=(0, 0.6, 0, 1),
                    on_release=lambda x: self.confirmar_finalizacao_carrinho(),
                ),
            ]
            
            self.popup_confirmacao = MDDialog(
                MDDialogHeadlineText(text="Finalizar Carrinho"),
                MDDialogSupportingText(text="Deseja finalizar este carrinho? Ele será movido para a seção de carrinhos finalizados."),
                MDDialogButtonContainer(*botoes),
                size_hint=(0.8, None),
                height=dp(300),
            )
            self.popup_confirmacao.open()
            
        except Exception as e:
            logger.error(f"Erro ao finalizar carrinho: {e}")
            self.mostrar_snackbar("Erro ao finalizar carrinho.")

    def confirmar_finalizacao_carrinho(self):
        """Confirma a finalização do carrinho"""
        try:
            from database_apk import finalizar_carrinho_apk
            
            sucesso = finalizar_carrinho_apk(self.carrinho_atual_visualizado_id)
            
            self.fechar_popup_confirmacao()
            
            if sucesso:
                self.mostrar_snackbar("Carrinho finalizado com sucesso!")
                # Recria a área de totais para mostrar botão de reabrir
                self.area_totais_carrinho.clear_widgets()
                self.criar_area_totais_carrinho()
                # Atualiza a lista de carrinhos para refletir mudança de status
                self.atualizar_lista_carrinhos()
            else:
                self.mostrar_snackbar("Erro ao finalizar carrinho.")
                
        except Exception as e:
            logger.error(f"Erro na confirmação da finalização: {e}")
            self.mostrar_snackbar("Erro ao finalizar carrinho.")

    def reabrir_carrinho(self):
        """Reabre um carrinho finalizado"""
        try:
            if not hasattr(self, 'carrinho_atual_visualizado_id'):
                self.mostrar_snackbar("Nenhum carrinho selecionado.")
                return
            
            # Popup de confirmação
            botoes = [
                MDButton(
                    MDButtonText(text="CANCELAR"),
                    style="outlined",
                    on_release=lambda x: self.fechar_popup_confirmacao(),
                ),
                MDButton(
                    MDButtonText(text="REABRIR"),
                    style="filled",
                    theme_bg_color="Custom",
                    md_bg_color=(0, 0.7, 0, 1),
                    on_release=lambda x: self.confirmar_reabertura_carrinho(),
                ),
            ]
            
            self.popup_confirmacao = MDDialog(
                MDDialogHeadlineText(text="Reabrir Carrinho"),
                MDDialogSupportingText(text="Deseja reabrir este carrinho? Ele será movido de volta para a seção de carrinhos em aberto."),
                MDDialogButtonContainer(*botoes),
                size_hint=(0.8, None),
                height=dp(300),
            )
            self.popup_confirmacao.open()
            
        except Exception as e:
            logger.error(f"Erro ao reabrir carrinho: {e}")
            self.mostrar_snackbar("Erro ao reabrir carrinho.")

    def confirmar_reabertura_carrinho(self):
        """Confirma a reabertura do carrinho"""
        try:
            from database_apk import reabrir_carrinho_apk
            
            sucesso = reabrir_carrinho_apk(self.carrinho_atual_visualizado_id)
            
            self.fechar_popup_confirmacao()
            
            if sucesso:
                self.mostrar_snackbar("Carrinho reaberto com sucesso!")
                # Recria a área de totais para mostrar botão de finalizar
                self.area_totais_carrinho.clear_widgets()
                self.criar_area_totais_carrinho()
                # Atualiza a lista de carrinhos para refletir mudança de status
                self.atualizar_lista_carrinhos()
            else:
                self.mostrar_snackbar("Erro ao reabrir carrinho.")
                
        except Exception as e:
            logger.error(f"Erro na confirmação da reabertura: {e}")
            self.mostrar_snackbar("Erro ao reabrir carrinho.")

    def atualizar_lista_itens_carrinho(self, carrinho_id):
        """Atualiza lista de itens do carrinho organizados por categoria"""
        try:
            # Busca itens do carrinho
            itens = listar_itens_carrinho_apk(carrinho_id)
            self.itens_carrinho_list.clear_widgets()
            self.limpar_referencias_checkbox('itens')
            
            if not itens:
                label_vazio = MDLabel(
                    text="Este carrinho não possui itens.\nUse o botão '+' para adicionar produtos.",
                    halign="center",
                    theme_text_color="Primary",
                    size_hint_y=None,
                    height=dp(100),
                    padding=(dp(16), dp(16)),
                )
                self.itens_carrinho_list.add_widget(label_vazio)
                if hasattr(self, 'atualizar_total_carrinho'):
                    self.atualizar_total_carrinho(0.0)
                return
            
            # Busca informações adicionais (categorias, supermercado do carrinho)
            carrinhos = listar_carrinhos_apk()
            carrinho_info = next((c for c in carrinhos if c[0] == carrinho_id), None)
            supermercado_id = carrinho_info[2] if carrinho_info else None
            
            # Organiza por categoria
            categorias_dict = {}
            total_geral = 0.0
            
            for item in itens:
                item_id, carrinho_id_item, produto_id, quantidade, preco_unit, nome_produto, marca, quantidade_embalagem = item
                
                # Busca categoria do produto
                produtos = listar_produtos_apk()
                produto_info = next((p for p in produtos if p[0] == produto_id), None)
                if not produto_info:
                    continue
                
                categoria_id = produto_info[6]
                categorias = listar_categorias_apk()
                categoria_info = next((c for c in categorias if c[0] == categoria_id), None)
                categoria_nome = categoria_info[1] if categoria_info else "Categoria não encontrada"
                
                # Calcula subtotal
                subtotal = quantidade * preco_unit
                total_geral += subtotal
                
                # Busca último preço no supermercado (se disponível)
                preco_supermercado = self.buscar_preco_produto_supermercado(produto_id, supermercado_id)
                
                # Agrupa por categoria
                if categoria_nome not in categorias_dict:
                    categorias_dict[categoria_nome] = []
                
                categorias_dict[categoria_nome].append({
                    'item_id': item_id,
                    'produto_id': produto_id,
                    'nome_produto': nome_produto,
                    'marca': marca,
                    'quantidade_embalagem': quantidade_embalagem,
                    'quantidade': quantidade,
                    'preco_unit': preco_unit,
                    'subtotal': subtotal,
                    'preco_supermercado': preco_supermercado
                })
            
            # Cria seções por categoria
            for categoria_nome in sorted(categorias_dict.keys()):
                itens_categoria = categorias_dict[categoria_nome]
                self.criar_secao_categoria_carrinho(categoria_nome, itens_categoria)
            
            # Atualiza total geral
            self.atualizar_total_carrinho(total_geral)
            
            logger.info(f"Lista de itens do carrinho atualizada: {len(itens)} itens, total R$ {total_geral:.2f}")
            
        except Exception as e:
            logger.error(f"Erro ao atualizar itens do carrinho: {e}")
            self.mostrar_snackbar("Erro ao carregar itens do carrinho.")

    def buscar_preco_produto_supermercado(self, produto_id, supermercado_id):
        """Busca último preço do produto no supermercado específico"""
        try:
            if not supermercado_id:
                return None
                
            # Busca no histórico de preços
            historico = listar_historico_precos_apk(produto_id)
            if not historico:
                return None
            
            # Filtra por supermercado e pega o mais recente
            precos_supermercado = [h for h in historico if h[1] == supermercado_id]  # supermercado_id no índice 1
            if precos_supermercado:
                return precos_supermercado[-1][3]  # preco no índice 3
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar preço do produto {produto_id}: {e}")
            return None

    def criar_secao_categoria_carrinho(self, categoria_nome, itens_categoria):
        """Cria seção de categoria para itens do carrinho"""
        try:
            # Label da categoria
            total_categoria = sum(item['subtotal'] for item in itens_categoria)
            titulo_categoria = f"{categoria_nome.upper()} ({len(itens_categoria)} {'item' if len(itens_categoria) == 1 else 'itens'}) - R$ {total_categoria:.2f}"
            
            categoria_label = MDLabel(
                text=titulo_categoria,
                theme_text_color="Primary",
                size_hint_y=None,
                height=dp(32),
                padding=(dp(16), dp(4)),
                bold=True,
            )
            self.itens_carrinho_list.add_widget(categoria_label)
            
            # Itens da categoria
            for item in sorted(itens_categoria, key=lambda x: x['nome_produto'].upper()):
                self.criar_item_carrinho_visual(item)
            
            # Espaçamento após categoria
            espacador = BoxLayout(size_hint_y=None, height=dp(4))
            self.itens_carrinho_list.add_widget(espacador)
            
        except Exception as e:
            logger.error(f"Erro ao criar seção de categoria {categoria_nome}: {e}")

    def criar_item_carrinho_visual(self, item):
        """Cria widget visual para item do carrinho"""
        try:
            # Textos formatados
            nome_produto = item['nome_produto'].upper()
            marca_embalagem = f"Marca: {item['marca'].upper()} | Embalagem: {item['quantidade_embalagem'].upper()}"
            
            # Informações de preço e quantidade
            quantidade = item['quantidade']
            preco_unit = item['preco_unit']
            subtotal = item['subtotal']
            preco_supermercado = item['preco_supermercado']
            
            # Texto de preços
            texto_precos = f"Qtd: {quantidade} × R$ {preco_unit:.2f} = R$ {subtotal:.2f}"
            if preco_supermercado and preco_supermercado != preco_unit:
                diferenca = preco_supermercado - preco_unit
                sinal = "+" if diferenca > 0 else ""
                texto_precos += f" | Preço atual: R$ {preco_supermercado:.2f} ({sinal}R$ {diferenca:.2f})"
            
            item_widget = MDListItem(
                MDListItemHeadlineText(text=nome_produto),
                MDListItemSupportingText(text=marca_embalagem),
                MDListItemSupportingText(text=texto_precos),
                padding=(dp(8), dp(4), dp(8), dp(4)),
                size_hint_y=None,
                height=dp(72),
            )
            
            self.itens_carrinho_list.add_widget(item_widget)
            
        except Exception as e:
            logger.error(f"Erro ao criar item visual do carrinho: {e}")

    def atualizar_total_carrinho(self, total):
        """Atualiza display do total geral"""
        try:
            if hasattr(self, 'label_total_geral'):
                self.label_total_geral.text = f"TOTAL GERAL: R$ {total:.2f}"
        except Exception as e:
            logger.error(f"Erro ao atualizar total do carrinho: {e}")

    # --- Funções de CRUD para Tipos de Produto ---
    def show_cadastro_tipo_produto_screen(self, *args):
        """Mostra tela de cadastro de tipo de produto (placeholder)"""
        self.mostrar_snackbar("Funcionalidade de cadastro de tipo de produto em desenvolvimento.")

    def show_editar_tipo_produto_screen(self, *args):
        """Mostra tela de edição de tipo de produto (placeholder)"""
        selecionados = [tipo_id for checkbox, tipo_id in self.tipos_checkbox_refs if checkbox.active]
        if not selecionados:
            self.mostrar_snackbar("Selecione um tipo de produto para editar.")
            return
        if len(selecionados) > 1:
            self.mostrar_snackbar("Selecione apenas um tipo de produto para editar.")
            return
        self.mostrar_snackbar("Funcionalidade de edição de tipo de produto em desenvolvimento.")

    def excluir_tipo_produto(self, *args):
        """Exclui tipos de produto selecionados com confirmação e sistema de lixeira"""
        try:
            selecionados = [tipo_id for checkbox, tipo_id in self.tipos_checkbox_refs if checkbox.active]
            
            if not selecionados:
                # Se nenhum item está selecionado, abre a lixeira específica de tipos de produto
                self.visualizar_lixeira('tipo_produto')
                return
            
            # Usa sistema genérico de confirmação
            self.criar_popup_confirmacao_exclusao_generico(
                selecionados, "tipo de produto", self.confirmar_exclusao_tipos_produto
            )
                
        except Exception as e:
            logger.error(f"Erro ao iniciar exclusão de tipos de produto: {e}")
            self.mostrar_snackbar("Erro ao excluir tipos de produto.")

    def confirmar_exclusao_tipos_produto(self, tipos_ids):
        """Confirma e executa exclusão dos tipos de produto com sistema de lixeira"""
        try:
            tipos = listar_tipos_produto_apk()
            excluidos = []
            refs_para_remover = []
            
            for tipo_id in tipos_ids:
                try:
                    # Busca dados do tipo para mover para lixeira
                    tipo_data = next((t for t in tipos if t[0] == tipo_id), None)
                    if tipo_data:
                        # Prepara dados para lixeira
                        dados_tipo = {
                            'id': tipo_data[0],
                            'nome': tipo_data[1],
                            'categoria_id': tipo_data[2] if len(tipo_data) > 2 else None,
                            'subcategoria_id': tipo_data[3] if len(tipo_data) > 3 else None
                        }
                        
                        # Move para lixeira primeiro
                        if self.mover_para_lixeira(tipo_id, 'tipo_produto', dados_tipo):
                            # Depois exclui do banco principal
                            excluir_tipo_produto_apk(tipo_id)
                            excluidos.append(tipo_id)
                            # Encontra referência para remover
                            for checkbox, tid in self.tipos_checkbox_refs:
                                if tid == tipo_id:
                                    refs_para_remover.append((checkbox, tid))
                                    break
                            logger.info(f"Tipo de produto {tipo_id} movido para lixeira e excluído")
                        
                except Exception as e:
                    logger.error(f"Erro ao excluir tipo de produto {tipo_id}: {e}")
            
            # Remove referências
            for ref in refs_para_remover:
                if ref in self.tipos_checkbox_refs:
                    self.tipos_checkbox_refs.remove(ref)
            
            # Fecha popup e mostra resultado
            self.fechar_popup_confirmacao()
            
            if excluidos:
                self.mostrar_snackbar(f"{len(excluidos)} tipo(s) de produto excluído(s) e movido(s) para lixeira!")
                # Atualiza a lista
                self.atualizar_lista_tipos_produto()
            else:
                self.mostrar_snackbar("Nenhum tipo de produto foi excluído.")
                
        except Exception as e:
            logger.error(f"Erro na confirmação de exclusão: {e}")
            self.mostrar_snackbar("Erro ao excluir tipos de produto.")

# --- Execução da aplicação ---
if __name__ == "__main__":
    try:
        app = Example()
        app.run()
    except Exception as e:
        logger.critical(f"Erro crítico ao executar aplicação: {e}")
        import traceback
        traceback.print_exc()