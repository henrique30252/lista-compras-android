#!/usr/bin/env python3
"""
Teste simples de swipe no KivyMD

Este é um exemplo mínimo para testar a funcionalidade de swipe.
Execute este arquivo para testar o swipe em um ambiente controlado.
"""

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.boxlayout import BoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.metrics import dp
from kivy.animation import Animation
from kivy.clock import Clock

class SwipeTestCard(MDCard):
    """Card de teste com swipe simples"""
    
    def __init__(self, item_name="Teste", **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(70),
            padding=dp(10),
            spacing=dp(10),
            md_bg_color=[0.1, 0.1, 0.1, 0.1],
            elevation=2,
            **kwargs
        )
        
        self.item_name = item_name
        self.swipe_threshold = dp(80)
        self.touch_start_x = 0
        self.is_swiping = False
        self.original_x = 0
        
        # Cores de feedback
        self.delete_color = [1, 0.3, 0.3, 0.8]
        self.edit_color = [0.3, 1, 0.3, 0.8]
        
        # Adiciona conteúdo
        self.setup_content()
        
    def setup_content(self):
        # Checkbox
        checkbox = MDCheckbox(active=False)
        self.add_widget(checkbox)
        
        # Label
        label = MDLabel(
            text=f"[b]{self.item_name}[/b] - Arraste para testar swipe",
            markup=True,
            theme_text_color="Primary",
        )
        self.add_widget(label)
        
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            print(f"Touch down em: {self.item_name}")
            self.touch_start_x = touch.x
            self.original_x = self.x
            self.is_swiping = True
            touch.grab(self)
            return True
        return super().on_touch_down(touch)
    
    def on_touch_move(self, touch):
        if touch.grab_current is self and self.is_swiping:
            dx = touch.x - self.touch_start_x
            print(f"Movendo: {dx}")
            
            # Limita movimento
            max_move = self.width * 0.3
            dx = max(-max_move, min(max_move, dx))
            
            # Move o card
            self.x = self.original_x + dx
            
            # Feedback visual
            if dx < -self.swipe_threshold / 2:
                self.md_bg_color = self.delete_color
                print("Feedback: DELETE (vermelho)")
            elif dx > self.swipe_threshold / 2:
                self.md_bg_color = self.edit_color
                print("Feedback: EDIT (verde)")
            else:
                self.md_bg_color = [0.1, 0.1, 0.1, 0.1]
            
            return True
        return super().on_touch_move(touch)
    
    def on_touch_up(self, touch):
        if touch.grab_current is self and self.is_swiping:
            dx = touch.x - self.touch_start_x
            print(f"Touch up: {dx}, threshold: {self.swipe_threshold}")
            
            # Ações
            if dx < -self.swipe_threshold:
                print(f"🗑️  DELETAR: {self.item_name}")
            elif dx > self.swipe_threshold:
                print(f"✏️  EDITAR: {self.item_name}")
            else:
                print("Swipe muito pequeno")
            
            # Volta à posição
            anim = Animation(
                x=self.original_x, 
                md_bg_color=[0.1, 0.1, 0.1, 0.1], 
                duration=0.2
            )
            anim.start(self)
            
            self.is_swiping = False
            touch.ungrab(self)
            return True
        return super().on_touch_up(touch)


class SwipeTestApp(MDApp):
    def build(self):
        # Layout principal
        main_layout = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(10))
        
        # Título
        title = MDLabel(
            text="[b]Teste de Swipe[/b]\nArraste os cards para os lados:",
            markup=True,
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(80),
            halign="center",
        )
        
        # Container para cards
        cards_container = BoxLayout(orientation="vertical", spacing=dp(10))
        
        # Cria vários cards de teste
        items = ["ARROZ", "FEIJÃO", "AÇÚCAR", "CAFÉ", "LEITE"]
        for item in items:
            card = SwipeTestCard(item_name=item)
            cards_container.add_widget(card)
        
        # ScrollView
        scroll = MDScrollView()
        scroll.add_widget(cards_container)
        
        # Monta layout
        main_layout.add_widget(title)
        main_layout.add_widget(scroll)
        
        return MDScreen(main_layout)


if __name__ == "__main__":
    SwipeTestApp().run()
