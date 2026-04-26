"""
Sentinel Core - Terminal de logistica autonoma (ES)
Arquitectura final:
- Drawer lateral con Panel, Configuracion local, Registro, Conexion y Viaje activo
- Portero Key-Only (solo valida HWID contra Render)
- Operacion local por socio (sin envio de tarifas al servidor)
"""

import base64
import hashlib
import json
import os
import threading
import time
import uuid
from datetime import datetime
from math import floor

import requests
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ColorProperty, NumericProperty, StringProperty
from kivy.utils import platform
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDIcon
from kivymd.uix.navigationdrawer import MDNavigationLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.slider import MDSlider
from kivymd.uix.textfield import MDTextField

try:
    from mapview import MapMarker, MapView
except Exception:
    MapMarker = None
    MapView = None

try:
    from config_advanced import advanced_config
except Exception:
    advanced_config = None

Window.size = (1320, 840)
Window.clearcolor = (0.03, 0.05, 0.10, 1)

APP_DIR = os.path.dirname(os.path.abspath(__file__))
IDENTITY_FILE = os.path.join(APP_DIR, "sentinel_identity.json")
OPERATIONS_FILE = os.path.join(APP_DIR, "sentinel_operations.json")
TICKETS_DIR = os.path.join(APP_DIR, "tickets")

# Base del panel ofuscada en partes para evitar lectura directa.
PANEL_B64_PARTS = (
    "aHR0cHM6Ly9hdG0t",
    "YWRtaW4tYXFrNi5v",
    "bnJlbmRlci5jb20=",
)
ALLOWED_DOMAIN_SHA256 = "76f5518f0807f7df50942ed1bb65ea07cb74aff17bddc50462da06f9ae4ad388"

DEFAULT_OPERATIONS = {
    "precio_minimo_viaje": 100.0,
    "precio_por_km": 2.5,
    "precio_espera_por_min": 1.8,
    "distancia_presencia_virtual": 0.0,
    "tipo_vehiculo": "carro",
    "radio_visibilidad_km": 8.0,
    "regla_1km_cada_10km": True,
    "ultima_actualizacion": None,
}

WAIT_RATE_PER_MIN = 1.8  # fallback

KV = """
#:import dp kivy.metrics.dp

<StatusLed>:
    canvas:
        Color:
            rgba: self.color
        Ellipse:
            pos: self.pos
            size: self.size

<RotatingPlanetIcon>:
    canvas.before:
        PushMatrix
        Rotate:
            angle: self.angle
            origin: self.center
        Color:
            rgba: 0.13, 0.83, 0.93, self.glow_alpha
        Ellipse:
            pos: self.center_x - self.font_size*1.1, self.center_y - self.font_size*1.1
            size: self.font_size*2.2, self.font_size*2.2
        Color:
            rgba: 0.64, 0.90, 0.21, self.glow_alpha * 0.45
        Ellipse:
            pos: self.center_x - self.font_size*1.5, self.center_y - self.font_size*1.5
            size: self.font_size*3.0, self.font_size*3.0
    canvas.after:
        PopMatrix

<RadarMapWidget>:
    canvas:
        # Fondo oscuro satellite
        Color:
            rgba: 0.03, 0.08, 0.14, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [16, 16, 16, 16]
        # Grid de lineas
        Color:
            rgba: 0.13, 0.83, 0.93, 0.07
        Line:
            points: self.x, self.center_y, self.right, self.center_y
            width: 1
        Line:
            points: self.center_x, self.y, self.center_x, self.top
            width: 1
        # Anillo exterior
        Color:
            rgba: 0.13, 0.83, 0.93, 0.18
        Line:
            ellipse: self.center_x - self.width*0.44, self.center_y - self.height*0.44, self.width*0.88, self.height*0.88
            width: 1
        # Anillo medio
        Color:
            rgba: 0.13, 0.83, 0.93, 0.28
        Line:
            ellipse: self.center_x - self.width*0.28, self.center_y - self.height*0.28, self.width*0.56, self.height*0.56
            width: 1
        # Anillo interior
        Color:
            rgba: 0.64, 0.90, 0.21, 0.35
        Line:
            ellipse: self.center_x - self.width*0.12, self.center_y - self.height*0.12, self.width*0.24, self.height*0.24
            width: 1.5
        # Punto central (posicion del chofer)
        Color:
            rgba: 0.64, 0.90, 0.21, 0.9
        Ellipse:
            pos: self.center_x - dp(5), self.center_y - dp(5)
            size: dp(10), dp(10)
        # Etiqueta radio
        Color:
            rgba: 1, 1, 1, 0
    MDLabel:
        id: radar_km_label
        text: root.radar_text
        halign: "center"
        valign: "bottom"
        pos: root.pos
        size: root.size
        bold: True
        font_size: "15sp"
        theme_text_color: "Custom"
        text_color: 0.90, 0.96, 1, 1

<FloatingBubble>:
    size_hint: None, None
    size: dp(220), dp(84)
    md_bg_color: 0.08, 0.12, 0.22, 0.96
    radius: [20, 20, 20, 20]
    elevation: 6
    pos: dp(1010), dp(630)
    padding: dp(10)

    MDBoxLayout:
        orientation: "vertical"
        spacing: dp(2)

        MDLabel:
            text: "Overlay de Viaje"
            font_style: "Caption"
            theme_text_color: "Custom"
            text_color: 0.64, 0.90, 0.21, 1

        MDLabel:
            text: root.bubble_text
            bold: True
            theme_text_color: "Custom"
            text_color: 0.13, 0.83, 0.93, 1


<LockedScreen>:
    name: "locked"
    MDBoxLayout:
        orientation: "vertical"
        padding: dp(18)
        spacing: dp(14)
        md_bg_color: 0.03, 0.05, 0.10, 1

        MDBoxLayout:
            size_hint_y: None
            height: dp(76)
            spacing: dp(10)

            RotatingPlanetIcon:
                id: locked_planet
                icon: "earth"
                angle: 0
                theme_text_color: "Custom"
                text_color: 0.13, 0.83, 0.93, 1
                font_size: "42sp"

            MDLabel:
                text: "SENTINEL CORE\\nTerminal de Logistica"
                bold: True
                theme_text_color: "Custom"
                text_color: 0.96, 0.98, 1, 1
                font_style: "H5"

        Widget:

        MDCard:
            size_hint_y: None
            height: dp(280)
            radius: [18, 18, 18, 18]
            md_bg_color: 0.07, 0.10, 0.18, 1
            padding: dp(18)

            MDBoxLayout:
                orientation: "vertical"
                spacing: dp(10)

                MDIcon:
                    icon: "shield-lock"
                    font_size: "56sp"
                    theme_text_color: "Custom"
                    text_color: 1, 0.22, 0.22, 1

                MDLabel:
                    id: locked_title
                    text: "Validando acceso"
                    halign: "center"
                    bold: True
                    font_style: "H4"
                    theme_text_color: "Custom"
                    text_color: 1, 0.22, 0.22, 1

                MDLabel:
                    id: locked_message
                    text: "Conectando con el portero de acceso..."
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 0.76, 0.82, 0.92, 1

                MDLabel:
                    id: locked_hwid
                    text: "HWID: --"
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 0.62, 0.68, 0.78, 1
                    font_size: "11sp"

        MDRaisedButton:
            text: "Reintentar validacion"
            md_bg_color: 0.64, 0.90, 0.21, 1
            text_color: 0.04, 0.06, 0.10, 1
            size_hint_y: None
            height: dp(44)
            on_release: app.retry_validation()

        Widget:

<OnboardingScreen>:
    name: "onboarding"
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 0.03, 0.05, 0.10, 1
        padding: dp(14)
        spacing: dp(10)

        MDTopAppBar:
            title: "Tutorial Sentinel"
            md_bg_color: 0.05, 0.09, 0.16, 1
            specific_text_color: 0.95, 0.98, 1, 1

        MDCard:
            radius: [20, 20, 20, 20]
            elevation: 8
            md_bg_color: 0.07, 0.11, 0.20, 1
            padding: dp(16)

            MDBoxLayout:
                orientation: "vertical"
                spacing: dp(10)

                MDLabel:
                    id: onboarding_step_title
                    text: "Paso 1: El Escudo (Acceso)"
                    bold: True
                    font_style: "H5"
                    theme_text_color: "Custom"
                    text_color: 0.13, 0.83, 0.93, 1

                MDLabel:
                    id: onboarding_step_body
                    text: "Tu HWID es tu llave unica. El administrador valida acceso con Render."
                    theme_text_color: "Custom"
                    text_color: 0.92, 0.96, 1, 1

                MDLabel:
                    id: onboarding_indicator
                    text: "1 / 3"
                    halign: "right"
                    theme_text_color: "Custom"
                    text_color: 0.64, 0.90, 0.21, 1

        MDBoxLayout:
            size_hint_y: None
            height: dp(50)
            spacing: dp(8)

            MDRaisedButton:
                text: "Anterior"
                md_bg_color: 0.07, 0.18, 0.29, 1
                text_color: 0.9, 0.97, 1, 1
                on_release: app.onboarding_prev()

            MDRaisedButton:
                text: "Siguiente"
                md_bg_color: 0.13, 0.83, 0.93, 1
                text_color: 0.04, 0.06, 0.10, 1
                on_release: app.onboarding_next()

            MDRaisedButton:
                text: "Finalizar"
                md_bg_color: 0.64, 0.90, 0.21, 1
                text_color: 0.04, 0.06, 0.10, 1
                on_release: app.onboarding_finish()

<DashboardScreen>:
    name: "dashboard"
    MDFloatLayout:
        md_bg_color: 0.03, 0.05, 0.10, 1

        MDBoxLayout:
            orientation: "vertical"
            size_hint: 1, 1

            MDTopAppBar:
                title: "Panel Principal"
                left_action_items: [["menu", lambda x: app.toggle_drawer()]]
                right_action_items: [["shield-check", lambda x: app.manual_validation()]]
                md_bg_color: 0.05, 0.09, 0.16, 1
                specific_text_color: 0.95, 0.98, 1, 1

            MDBoxLayout:
                size_hint_y: None
                height: dp(106)
                padding: dp(12), dp(8)
                spacing: dp(12)
                md_bg_color: 0.04, 0.08, 0.15, 1

                RotatingPlanetIcon:
                    id: panel_planet
                    icon: "earth"
                    angle: 0
                    theme_text_color: "Custom"
                    text_color: 0.13, 0.83, 0.93, 1
                    font_size: "48sp"

                MDBoxLayout:
                    orientation: "vertical"

                    MDLabel:
                        text: "SENTINEL CORE v1.0"
                        bold: True
                        font_style: "H5"
                        theme_text_color: "Custom"
                        text_color: 0.96, 0.98, 1, 1

                    MDBoxLayout:
                        size_hint_y: None
                        height: dp(22)
                        spacing: dp(6)

                        StatusLed:
                            id: panel_led
                            size_hint: None, None
                            size: dp(14), dp(14)
                            color: 0.64, 0.90, 0.21, 1

                        MDLabel:
                            id: panel_connection_small
                            text: "Conectado | Render"
                            theme_text_color: "Custom"
                            text_color: 0.64, 0.90, 0.21, 1
                            font_size: "11sp"

                Widget:

                MDLabel:
                    id: panel_latency
                    text: "Latencia: --"
                    size_hint_x: None
                    width: dp(190)
                    halign: "right"
                    theme_text_color: "Custom"
                    text_color: 0.13, 0.83, 0.93, 1

            MDScrollView:
                MDBoxLayout:
                    orientation: "vertical"
                    adaptive_height: True
                    padding: dp(14)
                    spacing: dp(12)

                    MDGridLayout:
                        cols: 3
                        adaptive_height: True
                        spacing: dp(10)

                        MDCard:
                            radius: [18, 18, 18, 18]
                            md_bg_color: 0.08, 0.12, 0.21, 1
                            padding: dp(14)
                            orientation: "vertical"
                            size_hint_y: None
                            height: dp(130)

                            MDLabel:
                                text: "Estado de Licencia"
                                theme_text_color: "Custom"
                                text_color: 0.13, 0.83, 0.93, 1

                            MDLabel:
                                id: panel_connection
                                text: "Bloqueado"
                                bold: True
                                font_style: "H5"
                                theme_text_color: "Custom"
                                text_color: 1, 0.22, 0.22, 1

                        MDCard:
                            radius: [18, 18, 18, 18]
                            md_bg_color: 0.08, 0.12, 0.21, 1
                            padding: dp(14)
                            orientation: "vertical"
                            size_hint_y: None
                            height: dp(130)

                            MDLabel:
                                text: "ID de Nodo (HWID)"
                                theme_text_color: "Custom"
                                text_color: 0.13, 0.83, 0.93, 1

                            MDLabel:
                                id: panel_hwid
                                text: "--"
                                theme_text_color: "Custom"
                                text_color: 0.95, 0.98, 1, 1

                            MDTextButton:
                                text: "Copiar"
                                theme_text_color: "Custom"
                                text_color: 0.13, 0.83, 0.93, 1
                                on_release: app.copy_hwid()

                        MDCard:
                            radius: [18, 18, 18, 18]
                            md_bg_color: 0.08, 0.12, 0.21, 1
                            padding: dp(14)
                            orientation: "vertical"
                            size_hint_y: None
                            height: dp(130)

                            MDLabel:
                                text: "Latencia de Servidor"
                                theme_text_color: "Custom"
                                text_color: 0.13, 0.83, 0.93, 1

                            MDLabel:
                                id: panel_latency_big
                                text: "-- ms"
                                bold: True
                                font_style: "H5"
                                theme_text_color: "Custom"
                                text_color: 0.95, 0.98, 1, 1

                    MDCard:
                        radius: [20, 20, 20, 20]
                        md_bg_color: 0.07, 0.11, 0.19, 1
                        padding: dp(14)
                        orientation: "vertical"
                        adaptive_height: True

                        MDBoxLayout:
                            size_hint_y: None
                            height: dp(160)
                            md_bg_color: 0.06, 0.16, 0.23, 1
                            radius: [16, 16, 16, 16]
                            padding: dp(12)

                            MDLabel:
                                id: panel_visibility_value
                                text: "RADIO DE VISIBILIDAD\\n12.0 KM"
                                halign: "center"
                                theme_text_color: "Custom"
                                text_color: 0.90, 0.96, 1, 1
                                bold: True

                        MDRelativeLayout:
                            id: map_host
                            size_hint_y: None
                            height: dp(180)

                            RadarMapWidget:
                                id: radar_map
                                size_hint: 1, 1

                        MDSlider:
                            id: visibility_slider
                            min: 0
                            max: 20
                            step: 0.5
                            value: app.get_visibility_value()
                            color: 0.64, 0.90, 0.21, 1
                            on_value: app.on_visibility_slider(self.value)

                        MDBoxLayout:
                            size_hint_y: None
                            height: dp(22)

                            MDLabel:
                                text: "0 KM"
                                theme_text_color: "Custom"
                                text_color: 0.72, 0.80, 0.92, 1
                                font_size: "10sp"

                            MDLabel:
                                text: "20 KM"
                                halign: "right"
                                theme_text_color: "Custom"
                                text_color: 0.72, 0.80, 0.92, 1
                                font_size: "10sp"

                        MDRaisedButton:
                            text: "CAMBIAR RADIO"
                            md_bg_color: 0.13, 0.83, 0.93, 1
                            text_color: 0.04, 0.06, 0.10, 1
                            size_hint_y: None
                            height: dp(42)
                            on_release: app.apply_visibility_radius()

                    MDRaisedButton:
                        text: "BUSCAR ACTUALIZACIONES"
                        md_bg_color: 0.32, 0.55, 0.18, 1
                        text_color: 0.86, 1, 0.58, 1
                        size_hint_y: None
                        height: dp(46)
                        on_release: app.buscar_actualizaciones()

        MDFloatingActionButtonSpeedDial:
            id: panel_speed_dial
            data: app.get_speed_dial_data()
            callback: app.on_speed_dial_callback
            root_button_anim: True
            rotation_root_button: True
            hint_animation: True
            right_pad: True
            bg_hint_color: 0.05, 0.09, 0.16, 1
            bg_color_stack_button: 0.13, 0.83, 0.93, 1
            color_icon_stack_button: 0.04, 0.06, 0.10, 1
            bg_color_root_button: 0.64, 0.90, 0.21, 1
            color_icon_root_button: 0.04, 0.06, 0.10, 1
            icon: "plus"

<OperationsScreen>:
    name: "operations"
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 0.03, 0.05, 0.10, 1

        MDTopAppBar:
            title: "Configuracion de Operacion (Local)"
            left_action_items: [["menu", lambda x: app.toggle_drawer()]]
            md_bg_color: 0.05, 0.09, 0.16, 1
            specific_text_color: 0.95, 0.98, 1, 1

        MDScrollView:
            MDBoxLayout:
                orientation: "vertical"
                adaptive_height: True
                padding: dp(14)
                spacing: dp(12)

                MDCard:
                    radius: [18, 18, 18, 18]
                    md_bg_color: 0.08, 0.12, 0.21, 1
                    padding: dp(14)
                    spacing: dp(8)
                    orientation: "vertical"
                    adaptive_height: True

                    MDLabel:
                        text: "Precio Minimo del Viaje"
                        theme_text_color: "Custom"
                        text_color: 0.64, 0.90, 0.21, 1

                    MDTextField:
                        id: minimo_field
                        hint_text: "Ej: 100"
                        mode: "rectangle"
                        input_filter: "float"
                        line_color_focus: 0.13, 0.83, 0.93, 1

                MDCard:
                    radius: [18, 18, 18, 18]
                    md_bg_color: 0.08, 0.12, 0.21, 1
                    padding: dp(14)
                    spacing: dp(8)
                    orientation: "vertical"
                    adaptive_height: True

                    MDLabel:
                        text: "Precio por Kilometro"
                        theme_text_color: "Custom"
                        text_color: 0.64, 0.90, 0.21, 1

                    MDTextField:
                        id: km_field
                        hint_text: "Ej: 2.5"
                        mode: "rectangle"
                        input_filter: "float"
                        line_color_focus: 0.13, 0.83, 0.93, 1

                MDCard:
                    radius: [18, 18, 18, 18]
                    md_bg_color: 0.08, 0.12, 0.21, 1
                    padding: dp(14)
                    spacing: dp(8)
                    orientation: "vertical"
                    adaptive_height: True

                    MDLabel:
                        text: "Radio de Visibilidad (KM)"
                        theme_text_color: "Custom"
                        text_color: 0.64, 0.90, 0.21, 1

                    MDTextField:
                        id: radio_field
                        hint_text: "Ej: 8"
                        mode: "rectangle"
                        input_filter: "float"
                        line_color_focus: 0.13, 0.83, 0.93, 1

                MDCard:
                    radius: [18, 18, 18, 18]
                    md_bg_color: 0.08, 0.12, 0.21, 1
                    padding: dp(14)
                    spacing: dp(8)
                    orientation: "vertical"
                    adaptive_height: True

                    MDLabel:
                        text: "Regla de Beneficio"
                        theme_text_color: "Custom"
                        text_color: 0.64, 0.90, 0.21, 1

                    MDSwitch:
                        id: beneficio_switch
                        active: True
                        pos_hint: {"center_x": .1}

                    MDLabel:
                        text: "1km de regalo por cada 10km"
                        theme_text_color: "Custom"
                        text_color: 0.86, 0.90, 0.96, 1

                MDLabel:
                    text: "Estos ajustes se guardan en local y nunca se envian al servidor."
                    theme_text_color: "Custom"
                    text_color: 0.72, 0.80, 0.92, 1

                MDRaisedButton:
                    text: "Guardar configuracion local"
                    md_bg_color: 0.64, 0.90, 0.21, 1
                    text_color: 0.04, 0.06, 0.10, 1
                    size_hint_y: None
                    height: dp(44)
                    on_release: app.save_operations_config()

                MDCard:
                    radius: [18, 18, 18, 18]
                    md_bg_color: 0.08, 0.12, 0.21, 1
                    padding: dp(14)
                    spacing: dp(8)
                    orientation: "vertical"
                    adaptive_height: True

                    MDLabel:
                        text: "Precio por Minuto de Parada ($)"
                        theme_text_color: "Custom"
                        text_color: 0.64, 0.90, 0.21, 1

                    MDTextField:
                        id: espera_field
                        hint_text: "Ej: 1.8"
                        mode: "rectangle"
                        input_filter: "float"
                        line_color_focus: 0.13, 0.83, 0.93, 1

                MDCard:
                    radius: [18, 18, 18, 18]
                    md_bg_color: 0.08, 0.12, 0.21, 1
                    padding: dp(14)
                    spacing: dp(8)
                    orientation: "vertical"
                    adaptive_height: True

                    MDLabel:
                        text: "Distancia de Presencia Virtual (KM)"
                        theme_text_color: "Custom"
                        text_color: 0.64, 0.90, 0.21, 1

                    MDLabel:
                        text: "0 = posicion real. Ej: 2.5 = aparecer a 2.5 KM del punto real"
                        font_size: "10sp"
                        theme_text_color: "Custom"
                        text_color: 0.50, 0.60, 0.75, 1

                    MDTextField:
                        id: presencia_field
                        hint_text: "Ej: 0.0"
                        mode: "rectangle"
                        input_filter: "float"
                        line_color_focus: 0.13, 0.83, 0.93, 1

                MDCard:
                    radius: [18, 18, 18, 18]
                    md_bg_color: 0.08, 0.12, 0.21, 1
                    padding: dp(14)
                    spacing: dp(8)
                    orientation: "vertical"
                    adaptive_height: True

                    MDLabel:
                        text: "Tipo de Vehiculo"
                        theme_text_color: "Custom"
                        text_color: 0.64, 0.90, 0.21, 1

                    MDBoxLayout:
                        size_hint_y: None
                        height: dp(38)
                        spacing: dp(12)

                        MDSwitch:
                            id: vehiculo_switch
                            active: False
                            size_hint_x: None
                            width: dp(56)
                            on_active: app.on_vehiculo_switch(self.active)

                        MDLabel:
                            id: vehiculo_label
                            text: "CARRO  (velocidad normal)"
                            bold: True
                            theme_text_color: "Custom"
                            text_color: 0.13, 0.83, 0.93, 1

<NodeScreen>:
    name: "node"
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 0.03, 0.05, 0.10, 1

        MDTopAppBar:
            title: "Registro de Nodo"
            left_action_items: [["menu", lambda x: app.toggle_drawer()]]
            md_bg_color: 0.05, 0.09, 0.16, 1
            specific_text_color: 0.95, 0.98, 1, 1

        MDBoxLayout:
            orientation: "vertical"
            padding: dp(14)
            spacing: dp(12)

            MDCard:
                radius: [18, 18, 18, 18]
                md_bg_color: 0.08, 0.12, 0.21, 1
                padding: dp(14)
                orientation: "vertical"
                adaptive_height: True

                MDLabel:
                    text: "Identificador unico del dispositivo"
                    theme_text_color: "Custom"
                    text_color: 0.13, 0.83, 0.93, 1

                MDLabel:
                    id: node_hwid
                    text: "--"
                    theme_text_color: "Custom"
                    text_color: 0.95, 0.98, 1, 1

            MDCard:
                radius: [18, 18, 18, 18]
                md_bg_color: 0.08, 0.12, 0.21, 1
                padding: dp(14)
                orientation: "vertical"
                adaptive_height: True

                MDLabel:
                    text: "Ultima sincronizacion de acceso"
                    theme_text_color: "Custom"
                    text_color: 0.13, 0.83, 0.93, 1

                MDLabel:
                    id: node_sync_status
                    text: "Pendiente"
                    theme_text_color: "Custom"
                    text_color: 0.95, 0.98, 1, 1

            MDRaisedButton:
                text: "Sincronizar Nodo"
                md_bg_color: 0.64, 0.90, 0.21, 1
                text_color: 0.04, 0.06, 0.10, 1
                size_hint_y: None
                height: dp(44)
                on_release: app.sync_node()

<ConnectionScreen>:
    name: "connection"
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 0.03, 0.05, 0.10, 1

        MDTopAppBar:
            title: "Estado de Conexion"
            left_action_items: [["menu", lambda x: app.toggle_drawer()]]
            md_bg_color: 0.05, 0.09, 0.16, 1
            specific_text_color: 0.95, 0.98, 1, 1

        MDBoxLayout:
            orientation: "vertical"
            padding: dp(14)
            spacing: dp(12)

            MDCard:
                radius: [18, 18, 18, 18]
                md_bg_color: 0.08, 0.12, 0.21, 1
                padding: dp(14)
                orientation: "vertical"
                adaptive_height: True

                MDLabel:
                    text: "Modo"
                    theme_text_color: "Custom"
                    text_color: 0.13, 0.83, 0.93, 1

                MDLabel:
                    text: "Key-Only"
                    bold: True
                    theme_text_color: "Custom"
                    text_color: 0.64, 0.90, 0.21, 1

            MDCard:
                radius: [18, 18, 18, 18]
                md_bg_color: 0.08, 0.12, 0.21, 1
                padding: dp(14)
                orientation: "vertical"
                adaptive_height: True

                MDLabel:
                    text: "Canal"
                    theme_text_color: "Custom"
                    text_color: 0.13, 0.83, 0.93, 1

                MDLabel:
                    id: conn_status
                    text: "Bloqueado"
                    theme_text_color: "Custom"
                    text_color: 1, 0.22, 0.22, 1

            MDCard:
                radius: [18, 18, 18, 18]
                md_bg_color: 0.08, 0.12, 0.21, 1
                padding: dp(14)
                orientation: "vertical"
                adaptive_height: True

                MDLabel:
                    text: "Endpoint"
                    theme_text_color: "Custom"
                    text_color: 0.13, 0.83, 0.93, 1

                MDLabel:
                    id: conn_endpoint
                    text: "Oculto por seguridad"
                    theme_text_color: "Custom"
                    text_color: 0.86, 0.90, 0.96, 1

                MDLabel:
                    text: "Solo se valida acceso por HWID. No hay reportes semanales."
                    theme_text_color: "Custom"
                    text_color: 0.72, 0.80, 0.92, 1

<TripScreen>:
    name: "trip"
    MDFloatLayout:
        md_bg_color: 0.03, 0.05, 0.10, 1

        MDBoxLayout:
            orientation: "vertical"
            size_hint: 1, 1

            MDTopAppBar:
                title: "Terminal de Viaje Activa"
                left_action_items: [["menu", lambda x: app.toggle_drawer()]]
                md_bg_color: 0.05, 0.09, 0.16, 1
                specific_text_color: 0.95, 0.98, 1, 1

            MDBoxLayout:
                orientation: "vertical"
                padding: dp(14)
                spacing: dp(12)

                MDCard:
                    radius: [18, 18, 18, 18]
                    md_bg_color: 0.08, 0.12, 0.21, 1
                    padding: dp(14)
                    orientation: "vertical"
                    adaptive_height: True

                    MDLabel:
                        id: trip_live_stats
                        text: "KM: 0.00 | Espera: 0 min | Extras: 0.00"
                        theme_text_color: "Custom"
                        text_color: 0.13, 0.83, 0.93, 1

                    MDLabel:
                        id: trip_live_total
                        text: "Total: 0.00"
                        bold: True
                        font_style: "H5"
                        theme_text_color: "Custom"
                        text_color: 0.64, 0.90, 0.21, 1

                MDGridLayout:
                    cols: 3
                    spacing: dp(8)
                    size_hint_y: None
                    height: dp(100)

                    MDRaisedButton:
                        text: "Iniciar viaje"
                        md_bg_color: 0.13, 0.83, 0.93, 1
                        text_color: 0.04, 0.06, 0.10, 1
                        on_release: app.start_trip()

                    MDRaisedButton:
                        text: "Pausa/Espera"
                        md_bg_color: 1.0, 0.74, 0.0, 1
                        text_color: 0.04, 0.06, 0.10, 1
                        on_release: app.toggle_pause_wait()

                    MDRaisedButton:
                        text: "Finalizar"
                        md_bg_color: 0.64, 0.90, 0.21, 1
                        text_color: 0.04, 0.06, 0.10, 1
                        on_release: app.finish_trip()

                    MDRaisedButton:
                        text: "+1 KM"
                        md_bg_color: 0.18, 0.70, 0.95, 1
                        text_color: 0.04, 0.06, 0.10, 1
                        on_release: app.add_distance(1.0)

                    MDRaisedButton:
                        text: "+0.1 KM"
                        md_bg_color: 0.18, 0.70, 0.95, 1
                        text_color: 0.04, 0.06, 0.10, 1
                        on_release: app.add_distance(0.1)

                    MDRaisedButton:
                        text: "Anadir gastos extra"
                        md_bg_color: 0.45, 0.56, 1.0, 1
                        text_color: 0.04, 0.06, 0.10, 1
                        on_release: app.open_extra_cost_dialog()

                MDLabel:
                    text: "Burbuja flotante: overlay interno activo (en Android usar servicio overlay)."
                    theme_text_color: "Custom"
                    text_color: 0.72, 0.80, 0.92, 1

        FloatingBubble:
            id: bubble

<TicketScreen>:
    name: "ticket"
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 0.03, 0.05, 0.10, 1

        MDTopAppBar:
            title: "Ticket Digital"
            left_action_items: [["menu", lambda x: app.toggle_drawer()]]
            md_bg_color: 0.05, 0.09, 0.16, 1
            specific_text_color: 0.95, 0.98, 1, 1

        MDScrollView:
            MDBoxLayout:
                orientation: "vertical"
                adaptive_height: True
                padding: dp(14)
                spacing: dp(12)

                MDCard:
                    radius: [18, 18, 18, 18]
                    md_bg_color: 0.08, 0.12, 0.21, 1
                    padding: dp(14)
                    orientation: "vertical"
                    adaptive_height: True

                    MDLabel:
                        id: ticket_summary
                        text: "Sin ticket"
                        theme_text_color: "Custom"
                        text_color: 0.95, 0.98, 1, 1

                MDCard:
                    radius: [18, 18, 18, 18]
                    md_bg_color: 0.08, 0.12, 0.21, 1
                    padding: dp(14)
                    orientation: "vertical"
                    adaptive_height: True

                    MDLabel:
                        id: ticket_store_status
                        text: "Ticket pendiente"
                        theme_text_color: "Custom"
                        text_color: 0.64, 0.90, 0.21, 1


<BandejaCapturaScreen>:
    name: "bandeja"
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 0.03, 0.05, 0.10, 1

        MDTopAppBar:
            title: "Bandeja de Captacion"
            left_action_items: [["menu", lambda x: app.toggle_drawer()]]
            md_bg_color: 0.05, 0.09, 0.16, 1
            specific_text_color: 0.95, 0.98, 1, 1

        MDBoxLayout:
            size_hint_y: None
            height: dp(70)
            padding: dp(12), dp(6)
            spacing: dp(8)
            md_bg_color: 0.04, 0.08, 0.15, 1

            MDBoxLayout:
                orientation: "vertical"
                size_hint_x: None
                width: dp(180)

                MDLabel:
                    id: capture_status_label
                    text: "Motor: INACTIVO"
                    bold: True
                    font_size: "11sp"
                    theme_text_color: "Custom"
                    text_color: 1, 0.22, 0.22, 1

                MDLabel:
                    id: capture_counter_label
                    text: "Viajes capturados: 0"
                    font_size: "10sp"
                    theme_text_color: "Custom"
                    text_color: 0.72, 0.80, 0.92, 1

                MDLabel:
                    id: queue_status_label
                    text: "Cola: --"
                    font_size: "10sp"
                    theme_text_color: "Custom"
                    text_color: 0.13, 0.83, 0.93, 1

            Widget:

            MDBoxLayout:
                size_hint_x: None
                width: dp(150)
                spacing: dp(4)

                MDSwitch:
                    id: excl_filter_switch
                    active: False
                    size_hint_x: None
                    width: dp(56)
                    on_active: app.toggle_exclusividad_filter(self.active)

                MDLabel:
                    text: "Solo Exclusivos"
                    font_size: "10sp"
                    theme_text_color: "Custom"
                    text_color: 0.13, 0.83, 0.93, 1

            MDRaisedButton:
                id: capture_toggle_btn
                text: "ACTIVAR"
                md_bg_color: 0.13, 0.83, 0.93, 1
                text_color: 0.04, 0.06, 0.10, 1
                size_hint_y: None
                height: dp(40)
                on_release: app.toggle_capture_engine()

            MDRaisedButton:
                text: "OVERLAY"
                md_bg_color: 0.64, 0.90, 0.21, 1
                text_color: 0.04, 0.06, 0.10, 1
                size_hint_y: None
                height: dp(40)
                on_release: app.request_overlay_bridge()

        MDBoxLayout:
            size_hint_y: None
            height: dp(36)
            padding: dp(12), dp(4)
            spacing: dp(8)
            md_bg_color: 0.05, 0.10, 0.18, 1

            MDLabel:
                text: "Velocidad de escaneo:"
                font_size: "11sp"
                theme_text_color: "Custom"
                text_color: 0.72, 0.80, 0.92, 1
                size_hint_x: None
                width: dp(160)

            MDSlider:
                id: scan_speed_slider
                min: 200
                max: 2000
                step: 100
                value: 800
                color: 0.64, 0.90, 0.21, 1
                on_value: app.on_scan_speed_change(self.value)

            MDLabel:
                id: scan_speed_label
                text: "800 ms"
                font_size: "11sp"
                size_hint_x: None
                width: dp(60)
                theme_text_color: "Custom"
                text_color: 0.64, 0.90, 0.21, 1

        MDScrollView:
            MDBoxLayout:
                id: bandeja_list
                orientation: "vertical"
                adaptive_height: True
                padding: dp(10)
                spacing: dp(8)

<RootLayout>:
    MDScreenManager:
        id: screen_manager
        LockedScreen:
        OnboardingScreen:
        DashboardScreen:
        OperationsScreen:
        NodeScreen:
        ConnectionScreen:
        TripScreen:
        TicketScreen:
        BandejaCapturaScreen:

    MDNavigationDrawer:
        id: nav_drawer
        radius: (0, 18, 18, 0)
        width: dp(330)
        md_bg_color: 0.05, 0.09, 0.16, 1

        MDBoxLayout:
            orientation: "vertical"
            padding: dp(14)
            spacing: dp(8)

            MDBoxLayout:
                size_hint_y: None
                height: dp(90)
                spacing: dp(10)

                RotatingPlanetIcon:
                    id: drawer_planet
                    icon: "earth"
                    angle: 0
                    theme_text_color: "Custom"
                    text_color: 0.13, 0.83, 0.93, 1
                    font_size: "40sp"

                MDBoxLayout:
                    orientation: "vertical"

                    MDLabel:
                        text: "Sentinel Core"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: 0.96, 0.98, 1, 1

                    MDLabel:
                        text: "Terminal Neon"
                        theme_text_color: "Custom"
                        text_color: 0.64, 0.90, 0.21, 1

            MDSeparator:

            ScrollView:
                MDList:
                    OneLineIconListItem:
                        text: "Tutorial"
                        on_release: app.nav_to("onboarding")
                        IconLeftWidget:
                            icon: "book-open-page-variant"

                    OneLineIconListItem:
                        text: "Panel Principal"
                        on_release: app.nav_to("dashboard")
                        IconLeftWidget:
                            icon: "view-dashboard"

                    OneLineIconListItem:
                        text: "Configuracion de Operacion"
                        on_release: app.nav_to("operations")
                        IconLeftWidget:
                            icon: "tune"

                    OneLineIconListItem:
                        text: "Registro de Nodo"
                        on_release: app.nav_to("node")
                        IconLeftWidget:
                            icon: "chip"

                    OneLineIconListItem:
                        text: "Estado de Conexion"
                        on_release: app.nav_to("connection")
                        IconLeftWidget:
                            icon: "lan"

                    OneLineIconListItem:
                        text: "Terminal de Viaje"
                        on_release: app.nav_to("trip")
                        IconLeftWidget:
                            icon: "car-side"

                    OneLineIconListItem:
                        text: "Bandeja de Captacion"
                        on_release: app.nav_to("bandeja")
                        IconLeftWidget:
                            icon: "lightning-bolt-circle"

                    OneLineIconListItem:
                        text: "Ticket Digital"
                        on_release: app.nav_to("ticket")
                        IconLeftWidget:
                            icon: "receipt-text-outline"
"""


class StatusLed(Widget):
    color = ColorProperty((1, 0.22, 0.22, 1))


class RotatingPlanetIcon(MDIcon):
    angle = NumericProperty(0)
    glow_alpha = NumericProperty(0.18)


class RadarMapWidget(MDBoxLayout):
    radar_text = StringProperty("RADIO\\n8.0 KM")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.route_points = []
        self.blocked_points = []
        self.favorite_points = []
        self._long_event = None
        self._last_touch_pos = None
        self._last_action = ""
        self.bind(pos=lambda *_: self._redraw_overlay(), size=lambda *_: self._redraw_overlay())

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        self._last_touch_pos = touch.pos
        self._long_event = Clock.schedule_once(
            lambda *_: self._on_long_press(touch.pos),
            0.55,
        )
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self._long_event is not None and self._long_event.is_triggered == 0:
            self._long_event.cancel()
            self._long_event = None
            if self.collide_point(*touch.pos):
                self._add_route_point(touch.pos)
        return super().on_touch_up(touch)

    def _on_long_press(self, pos):
        self._long_event = None
        if not self.collide_point(*pos):
            return
        # Alterna entre bloqueo y favorito para mantener UX simple en Android.
        if len(self.blocked_points) <= len(self.favorite_points):
            self.blocked_points.append(pos)
            self._last_action = "Zona bloqueada"
        else:
            self.favorite_points.append(pos)
            self._last_action = "Zona favorita"
        self._redraw_overlay()

    def _add_route_point(self, pos):
        self.route_points.append(pos)
        if len(self.route_points) > 18:
            self.route_points = self.route_points[-18:]
        self._last_action = "Punto de ruta"
        self._redraw_overlay()

    def _redraw_overlay(self):
        self.canvas.after.clear()
        with self.canvas.after:
            if len(self.route_points) > 1:
                Color(0.13, 0.83, 0.93, 0.85)
                flat = []
                for x, y in self.route_points:
                    flat.extend([x, y])
                Line(points=flat, width=1.3)

            Color(0.64, 0.90, 0.21, 0.92)
            for x, y in self.favorite_points:
                Ellipse(pos=(x - dp(4), y - dp(4)), size=(dp(8), dp(8)))

            Color(1.0, 0.22, 0.22, 0.90)
            for x, y in self.blocked_points:
                Line(points=[x - dp(5), y - dp(5), x + dp(5), y + dp(5)], width=1.4)
                Line(points=[x - dp(5), y + dp(5), x + dp(5), y - dp(5)], width=1.4)


class FloatingBubble(MDCard):
    bubble_text = StringProperty("KM: 0.00 | Total: 0.00")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._dragging = False
        self._dx = 0
        self._dy = 0

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._dragging = True
            self._dx = touch.x - self.x
            self._dy = touch.y - self.y
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self._dragging:
            self.x = max(0, min(Window.width - self.width, touch.x - self._dx))
            self.y = max(0, min(Window.height - self.height, touch.y - self._dy))
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self._dragging:
            self._dragging = False
            return True
        return super().on_touch_up(touch)


class LockedScreen(MDScreen):
    """Pantalla bloqueada por licencia."""


class OnboardingScreen(MDScreen):
    """Tutorial inicial de 3 pasos."""


class DashboardScreen(MDScreen):
    """Panel principal."""


class OperationsScreen(MDScreen):
    """Ajustes de operación local."""


class NodeScreen(MDScreen):
    """Estado e identidad del nodo."""


class ConnectionScreen(MDScreen):
    """Estado de conexión y endpoint."""


class TripScreen(MDScreen):
    """Terminal de viaje activo."""


class TicketScreen(MDScreen):
    """Vista de ticket final."""


class BandejaCapturaScreen(MDScreen):
    """Bandeja de captación con retención."""


class RootLayout(MDNavigationLayout):
    """Layout principal con drawer y screen manager."""


class SentinelCoreTerminal(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.identity = self._load_identity()
        self.operations = self._load_operations()

        self.is_authorized = False
        self.last_latency_ms = None
        self.last_validation = None
        self.validation_error = "Pendiente"
        self._validation_lock = threading.Lock()
        self.active_panel_base = None

        self.trip_active = False
        self.trip_paused = False
        self.trip_distance_km = 0.0
        self.trip_wait_seconds = 0
        self.trip_extra_cost = 0.0
        self.trip_started_at = None

        # Motor de captacion de viajes
        self.capture_active = False
        self.captured_trips: list = []
        self.exclusividad_filter = False
        self.scan_speed_ms = 800
        self._capture_thread = None
        self._capture_stop_flag = threading.Event()

        # Cola de viajes (double-queueing)
        self.trip_queue = []  # viajes aceptados mientras uno ya esta activo

        # Estado de mapa integrado
        self._dashboard_map_ready = False
        self._dashboard_map_widget = None
        self._map_touch_ts = 0.0
        self._map_block_toggle = False
        self._map_route_points = []
        self._map_blocked_points = []
        self._map_favorite_points = []

        # Glow planet
        self._glow_dir = 1
        self._glow_alpha = 0.18

        # Onboarding de sesión
        self.onboarding_step = 0
        self._session_onboarding_shown = False

        self.extra_dialog = None
        self._tick_event = None

    def _save_identity(self):
        with open(IDENTITY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.identity, f, indent=2, ensure_ascii=False)

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Cyan"
        self.theme_cls.accent_palette = "Lime"

        Builder.load_string(KV)
        root = RootLayout()
        Clock.schedule_once(lambda *_: self._bootstrap(), 0.25)
        Clock.schedule_interval(self._spin_planets, 1 / 30)
        self._tick_event = Clock.schedule_interval(self._trip_tick, 1)
        Clock.schedule_interval(lambda *_: self._validate_in_background(silent=True), 20)
        return root

    def _android_service_bridge(self, start=True):
        """Bridge seguro: en desktop no hace nada; en Android intenta enlazar el service."""
        if platform != "android":
            return
        try:
            from android import AndroidService

            if start:
                if not hasattr(self, "_android_service") or self._android_service is None:
                    self._android_service = AndroidService(
                        "Sentinel scan service",
                        "running",
                    )
                self._android_service.start("Sentinel scan service")
                self._notify("Servicio Android iniciado")
            else:
                if hasattr(self, "_android_service") and self._android_service is not None:
                    self._android_service.stop()
                self._notify("Servicio Android detenido")
        except Exception as ex:
            self._notify(f"Service Android no disponible: {ex}")

    def request_overlay_bridge(self):
        if platform != "android":
            self._notify("Overlay solo disponible en Android")
            return
        try:
            from jnius import autoclass

            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Settings = autoclass("android.provider.Settings")
            Intent = autoclass("android.content.Intent")
            Uri = autoclass("android.net.Uri")

            activity = PythonActivity.mActivity
            if not Settings.canDrawOverlays(activity):
                intent = Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION)
                intent.setData(Uri.parse("package:" + activity.getPackageName()))
                activity.startActivity(intent)
                self._notify("Solicitando permiso de superposicion")
            else:
                self._notify("Permiso de superposicion ya concedido")
        except Exception as ex:
            self._notify(f"No se pudo abrir permiso overlay: {ex}")

    def _bootstrap(self):
        self.root.ids.screen_manager.current = "locked"
        self._fill_node_screen()
        self._fill_operations_screen()
        self._update_connection_screen()
        self._set_locked_state("Validando acceso", "Conectando con el portero de acceso...")
        self._validate_in_background(silent=False)

    def _spin_planets(self, dt):
        speed = 38 * dt
        planet_ids = ["drawer_planet", "panel_planet", "locked_planet"]
        for pid in planet_ids:
            w = self._safe_get_id(pid)
            if w is not None:
                w.angle = (w.angle + speed) % 360

        # Pulso de glow
        self._glow_alpha += 0.015 * self._glow_dir
        if self._glow_alpha >= 0.45:
            self._glow_dir = -1
        elif self._glow_alpha <= 0.08:
            self._glow_dir = 1
        for pid in planet_ids:
            w = self._safe_get_id(pid)
            if w is not None:
                w.glow_alpha = self._glow_alpha

    def _safe_get_id(self, widget_id):
        try:
            return self.root.ids.get(widget_id)
        except Exception:
            return None

    def _load_identity(self):
        if os.path.exists(IDENTITY_FILE):
            try:
                with open(IDENTITY_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if "hwid" in loaded:
                        return loaded
            except Exception:
                pass

        identity = {
            "hwid": str(uuid.getnode()),
            "created_at": datetime.now().isoformat(),
        }
        with open(IDENTITY_FILE, "w", encoding="utf-8") as f:
            json.dump(identity, f, indent=2, ensure_ascii=False)
        return identity

    def _load_operations(self):
        if os.path.exists(OPERATIONS_FILE):
            try:
                with open(OPERATIONS_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                merged = dict(DEFAULT_OPERATIONS)
                merged.update(loaded)
                return merged
            except Exception:
                pass
        return dict(DEFAULT_OPERATIONS)

    def _save_operations(self):
        self.operations["ultima_actualizacion"] = datetime.now().isoformat()
        with open(OPERATIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.operations, f, indent=2, ensure_ascii=False)

    def _decode_panel_base(self):
        raw = "".join(PANEL_B64_PARTS)
        return base64.b64decode(raw.encode("utf-8")).decode("utf-8")

    def _build_validate_url(self, hwid):
        return f"{self._decode_panel_base().rstrip('/')}/validar/{hwid}"

    def _build_register_url(self):
        return f"{self._decode_panel_base().rstrip('/')}/registro_cliente"

    def _panel_base_candidates(self):
        candidates = [self._decode_panel_base()]
        if self.active_panel_base:
            candidates.insert(0, self.active_panel_base)

        if advanced_config is not None:
            try:
                candidates.append(advanced_config.get("server_endpoint", ""))
                for b in advanced_config.get("backup_endpoints", []):
                    candidates.append(b)
            except Exception:
                pass

        dedup = []
        for base in candidates:
            b = (base or "").strip().rstrip("/")
            if b and b not in dedup:
                dedup.append(b)
        return dedup

    def _integrity_check(self):
        try:
            endpoint = self._decode_panel_base()
            if not endpoint.startswith("https://"):
                return False, "Integridad comprometida"
            domain = endpoint.split("//", 1)[1].split("/", 1)[0]
            digest = hashlib.sha256(domain.encode()).hexdigest()
            if digest != ALLOWED_DOMAIN_SHA256:
                return False, "Endpoint alterado"
            return True, "OK"
        except Exception:
            return False, "Error de seguridad"

    def sync_node(self):
        self._notify("Sincronizando nodo...")
        threading.Thread(target=self._sync_node_thread, daemon=True).start()

    def _sync_node_thread(self):
        hwid = self.identity.get("hwid", "")
        if not hwid:
            self._notify("HWID no disponible")
            return

        nombre = (self.identity.get("nombre") or "").strip()
        email = (self.identity.get("email") or "").strip()
        if not nombre:
            nombre = f"Nodo-{hwid[-6:]}"
            self.identity["nombre"] = nombre
            with open(IDENTITY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.identity, f, indent=2, ensure_ascii=False)

        payload = {"hwid": hwid, "nombre": nombre, "email": email}
        synced = False
        last_error = ""
        for base in self._panel_base_candidates():
            try:
                url = f"{base}/registro_cliente"
                response = requests.post(url, json=payload, timeout=8)
                if response.status_code == 200:
                    self.active_panel_base = base
                    synced = True
                    break
                last_error = f"HTTP {response.status_code}"
            except Exception as ex:
                last_error = str(ex)

        if synced:
            self._notify("Nodo sincronizado con panel")
        else:
            self._notify(f"Sincronizacion fallida: {last_error}")

        self._validate_in_background(silent=False)

    def toggle_drawer(self):
        nav = self.root.ids.nav_drawer
        nav.set_state("open" if nav.state == "close" else "close")

    def nav_to(self, screen_name):
        self.root.ids.nav_drawer.set_state("close")
        if not self.is_authorized:
            self.root.ids.screen_manager.current = "locked"
            self._set_locked_state(
                "Licencia Inactiva",
                "Licencia Inactiva. Contacte al Administrador",
            )
            return

        self.root.ids.screen_manager.current = screen_name
        if screen_name == "onboarding":
            self.onboarding_step = 0
            self._render_onboarding_step()
            return
        if screen_name == "operations":
            self._fill_operations_screen()
        elif screen_name == "connection":
            self._update_connection_screen()
        elif screen_name == "node":
            self._fill_node_screen()
        elif screen_name == "bandeja":
            self._refresh_bandeja_header()
            self._refresh_bandeja_ui()

    def retry_validation(self):
        self._notify("Revalidando acceso...")
        self._validate_in_background(silent=False)

    def manual_validation(self):
        self._notify("Validando licencia...")
        self._validate_in_background(silent=False)

    def _notify(self, message):
        print(f"[SENTINEL] {message}")

    def _onboarding_steps(self):
        return [
            (
                "Paso 1: El Escudo (Acceso)",
                "Tu HWID es tu llave unica. El administrador controla acceso desde Render.",
            ),
            (
                "Paso 2: El Secuestro (Agilidad)",
                "La bandeja retiene viajes por 5 segundos. El motor prioriza viajes rentables.",
            ),
            (
                "Paso 3: El Control (Mapa y Precios)",
                "Bloquea/favorita zonas en mapa tactil y define tus tarifas locales.",
            ),
        ]

    def _render_onboarding_step(self):
        try:
            screen = self.root.ids.screen_manager.get_screen("onboarding")
            steps = self._onboarding_steps()
            idx = max(0, min(self.onboarding_step, len(steps) - 1))
            title, body = steps[idx]
            screen.ids.onboarding_step_title.text = title
            screen.ids.onboarding_step_body.text = body
            screen.ids.onboarding_indicator.text = f"{idx + 1} / {len(steps)}"
        except Exception:
            pass

    def onboarding_next(self):
        self.onboarding_step = min(self.onboarding_step + 1, len(self._onboarding_steps()) - 1)
        self._render_onboarding_step()

    def onboarding_prev(self):
        self.onboarding_step = max(self.onboarding_step - 1, 0)
        self._render_onboarding_step()

    def onboarding_finish(self):
        self.identity["onboarding_done"] = True
        self.identity["onboarding_done_at"] = datetime.now().isoformat()
        self._save_identity()
        self._session_onboarding_shown = True
        self.root.ids.screen_manager.current = "dashboard"

    def _setup_dashboard_map_once(self):
        if self._dashboard_map_ready:
            return
        try:
            screen = self.root.ids.screen_manager.get_screen("dashboard")
            host = screen.ids.map_host
        except Exception:
            return

        if MapView is None or MapMarker is None:
            self._dashboard_map_ready = True
            return

        try:
            map_widget = MapView(zoom=12, lat=18.4861, lon=-69.9312)
            map_widget.bind(on_touch_down=self._on_dashboard_map_touch_down)
            map_widget.bind(on_touch_up=self._on_dashboard_map_touch_up)
            host.clear_widgets()
            host.add_widget(map_widget)
            self._dashboard_map_widget = map_widget
            self._dashboard_map_ready = True
            self._notify("Mapa integrado activo")
        except Exception as ex:
            self._notify(f"Mapa integrado no disponible: {ex}")
            self._dashboard_map_ready = True

    def _on_dashboard_map_touch_down(self, instance, touch):
        if not instance.collide_point(*touch.pos):
            return False
        self._map_touch_ts = time.time()
        return False

    def _on_dashboard_map_touch_up(self, instance, touch):
        if not instance.collide_point(*touch.pos):
            return False
        if MapMarker is None:
            return False
        try:
            hold_s = time.time() - self._map_touch_ts
            lat, lon = instance.get_latlon_at(touch.x, touch.y)
            marker = MapMarker(lat=lat, lon=lon)
            instance.add_widget(marker)

            if hold_s >= 0.55:
                self._map_block_toggle = not self._map_block_toggle
                if self._map_block_toggle:
                    self._map_blocked_points.append((lat, lon))
                    self._notify("Zona bloqueada en mapa")
                else:
                    self._map_favorite_points.append((lat, lon))
                    self._notify("Zona favorita en mapa")
            else:
                self._map_route_points.append((lat, lon))
                self._notify("Punto de ruta trazado")
        except Exception:
            return False
        return False

    def get_visibility_value(self):
        try:
            return float(self.operations.get("radio_visibilidad_km", 8.0))
        except Exception:
            return 8.0

    def on_visibility_slider(self, value):
        km = round(max(0.0, min(20.0, float(value))), 1)
        self.operations["radio_visibilidad_km"] = km
        try:
            screen = self.root.ids.screen_manager.get_screen("dashboard")
            screen.ids.panel_visibility_value.text = f"RADIO DE VISIBILIDAD\\n{km:.1f} KM"
            if "radar_map" in screen.ids:
                screen.ids.radar_map.radar_text = f"RADIO DE VISIBILIDAD\\n{km:.1f} KM"
        except Exception:
            pass

    def apply_visibility_radius(self):
        self._save_operations()
        km = float(self.operations.get("radio_visibilidad_km", 8.0))
        self._notify(f"Radio actualizado a {km:.1f} KM")

    def copy_hwid(self):
        hwid = self.identity.get("hwid", "--")
        Clipboard.copy(hwid)
        self._notify("HWID copiado")

    def buscar_actualizaciones(self):
        self._notify("Buscando actualizaciones...")
        self.sync_node()

    def get_speed_dial_data(self):
        return {
            "Precios": "cash-multiple",
            "Endpoint": "server-network",
            "Espera": "timer-outline",
        }

    def on_speed_dial_callback(self, *args):
        action_icon = ""
        for item in args:
            if hasattr(item, "icon") and getattr(item, "icon"):
                action_icon = getattr(item, "icon")
            elif isinstance(item, str):
                action_icon = item

        action_icon = (action_icon or "").lower()
        if action_icon in ("cash-multiple", "precios"):
            self.nav_to("operations")
            return
        if action_icon in ("server-network", "endpoint"):
            self.nav_to("connection")
            return
        if action_icon in ("timer-outline", "espera"):
            self.nav_to("trip")
            self.toggle_pause_wait()
            return

    def _validate_in_background(self, silent):
        threading.Thread(
            target=self._validate_access,
            kwargs={"silent": silent},
            daemon=True,
        ).start()

    def _validate_access(self, silent=False):
        if not self._validation_lock.acquire(blocking=False):
            return

        try:
            secure_ok, reason = self._integrity_check()
            if not secure_ok:
                self.is_authorized = False
                self.validation_error = reason
                Clock.schedule_once(
                    lambda *_: self._set_locked_state(
                        "Sistema Protegido",
                        "Integridad fallida. Reinstale el cliente oficial.",
                    )
                )
                return

            authorized = False
            self.last_latency_ms = None
            hwid = self.identity.get("hwid", "")
            nombre = (self.identity.get("nombre") or "").strip()
            validated = False
            last_error = ""

            for base in self._panel_base_candidates():
                validate_url = f"{base}/validar/{hwid}"
                legacy_url = f"{base}/protocol/v1/verify/{hwid}"
                query = {"nombre": nombre} if nombre else None

                try:
                    t0 = time.time()
                    response = requests.get(validate_url, params=query, timeout=8)
                    self.last_latency_ms = int((time.time() - t0) * 1000)
                    if response.status_code == 200:
                        payload = response.json()
                        access = str(payload.get("access", "")).lower()
                        authorized = access == "granted"
                        self.active_panel_base = base
                        validated = True
                        break

                    if response.status_code not in (404,):
                        last_error = f"HTTP {response.status_code}"
                        continue
                except Exception as ex:
                    last_error = str(ex)
                    continue

                # Fallback legado
                try:
                    t0 = time.time()
                    response = requests.get(legacy_url, timeout=8)
                    self.last_latency_ms = int((time.time() - t0) * 1000)
                    if response.status_code == 200:
                        payload = response.json()
                        authorized = bool(payload.get("authorized", False))
                        self.active_panel_base = base
                        validated = True
                        break
                    last_error = f"HTTP {response.status_code}"
                except Exception as ex:
                    last_error = str(ex)

            if not validated:
                self.validation_error = last_error or "No se pudo validar"

            self.last_validation = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.is_authorized = authorized

            if authorized:
                Clock.schedule_once(lambda *_: self._unlock_app())
            else:
                Clock.schedule_once(
                    lambda *_: self._set_locked_state(
                        "Licencia Inactiva",
                        "Licencia Inactiva. Contacte al Administrador",
                    )
                )

            if not silent:
                Clock.schedule_once(
                    lambda *_: self._notify(
                        "Acceso autorizado" if authorized else "Acceso denegado"
                    )
                )

            Clock.schedule_once(lambda *_: self._refresh_status_widgets())
        finally:
            self._validation_lock.release()

    def _unlock_app(self):
        self._refresh_status_widgets()
        self._setup_dashboard_map_once()
        if not self._session_onboarding_shown:
            self.onboarding_step = 0
            self._render_onboarding_step()
            self.root.ids.screen_manager.current = "onboarding"
            self._session_onboarding_shown = True
        else:
            self.root.ids.screen_manager.current = "dashboard"

    def _set_locked_state(self, title, message):
        self.root.ids.screen_manager.current = "locked"
        locked = self.root.ids.screen_manager.get_screen("locked")
        locked.ids.locked_title.text = title
        locked.ids.locked_message.text = message
        locked.ids.locked_hwid.text = f"HWID: {self.identity.get('hwid', '--')}"

    def _refresh_status_widgets(self):
        self._fill_dashboard()
        self._fill_node_screen()
        self._update_connection_screen()

    def _fill_dashboard(self):
        self._setup_dashboard_map_once()
        screen = self.root.ids.screen_manager.get_screen("dashboard")
        screen.ids.panel_hwid.text = self.identity.get("hwid", "--")

        if self.is_authorized:
            screen.ids.panel_connection.text = "Conectado y habilitado"
            screen.ids.panel_connection.text_color = (0.64, 0.90, 0.21, 1)
            screen.ids.panel_connection_small.text = "Conectado | Render"
            screen.ids.panel_connection_small.text_color = (0.64, 0.90, 0.21, 1)
        else:
            screen.ids.panel_connection.text = "Bloqueado"
            screen.ids.panel_connection.text_color = (1, 0.22, 0.22, 1)
            screen.ids.panel_connection_small.text = "Sin acceso de licencia"
            screen.ids.panel_connection_small.text_color = (1, 0.22, 0.22, 1)

        if self.last_validation:
            if "panel_last_check" in screen.ids:
                screen.ids.panel_last_check.text = self.last_validation
        else:
            if "panel_last_check" in screen.ids:
                screen.ids.panel_last_check.text = "Pendiente"

        if self.last_latency_ms is not None:
            screen.ids.panel_latency.text = f"Latencia: {self.last_latency_ms} ms"
            screen.ids.panel_latency_big.text = f"{self.last_latency_ms} ms"
            if self.last_latency_ms <= 350:
                screen.ids.panel_led.color = (0.13, 0.83, 0.93, 1)
            elif self.last_latency_ms <= 900:
                screen.ids.panel_led.color = (1.0, 0.74, 0.0, 1)
            else:
                screen.ids.panel_led.color = (1, 0.22, 0.22, 1)
        else:
            screen.ids.panel_latency.text = "Latencia: --"
            screen.ids.panel_latency_big.text = "-- ms"
            screen.ids.panel_led.color = (1, 0.22, 0.22, 1)

        km = float(self.operations.get("radio_visibilidad_km", 8.0))
        screen.ids.panel_visibility_value.text = f"RADIO DE VISIBILIDAD\\n{km:.1f} KM"
        if "radar_map" in screen.ids:
            screen.ids.radar_map.radar_text = f"RADIO DE VISIBILIDAD\\n{km:.1f} KM"
        screen.ids.visibility_slider.value = km

    def _fill_operations_screen(self):
        screen = self.root.ids.screen_manager.get_screen("operations")
        screen.ids.minimo_field.text = str(self.operations.get("precio_minimo_viaje", 100.0))
        screen.ids.km_field.text = str(self.operations.get("precio_por_km", 2.5))
        screen.ids.radio_field.text = str(self.operations.get("radio_visibilidad_km", 8.0))
        screen.ids.beneficio_switch.active = bool(
            self.operations.get("regla_1km_cada_10km", True)
        )
        screen.ids.espera_field.text = str(self.operations.get("precio_espera_por_min", 1.8))
        screen.ids.presencia_field.text = str(self.operations.get("distancia_presencia_virtual", 0.0))
        es_moto = self.operations.get("tipo_vehiculo", "carro") == "moto"
        screen.ids.vehiculo_switch.active = es_moto
        screen.ids.vehiculo_label.text = (
            "MOTO  (alta agilidad)" if es_moto else "CARRO  (velocidad normal)"
        )

    def save_operations_config(self):
        screen = self.root.ids.screen_manager.get_screen("operations")
        try:
            minimo = float(screen.ids.minimo_field.text)
            por_km = float(screen.ids.km_field.text)
            radio = float(screen.ids.radio_field.text)
        except ValueError:
            self._notify("Valores invalidos. Usa numeros.")
            return

        if minimo < 0 or por_km < 0 or radio <= 0:
            self._notify("Revisa rangos: minimo>=0, km>=0, radio>0")
            return

        self.operations["precio_minimo_viaje"] = minimo
        self.operations["precio_por_km"] = por_km
        self.operations["radio_visibilidad_km"] = radio
        self.operations["regla_1km_cada_10km"] = bool(screen.ids.beneficio_switch.active)
        try:
            espera = float(screen.ids.espera_field.text)
            if espera < 0:
                espera = 0.0
            self.operations["precio_espera_por_min"] = espera
        except ValueError:
            pass
        try:
            presencia = float(screen.ids.presencia_field.text)
            if presencia < 0:
                presencia = 0.0
            self.operations["distancia_presencia_virtual"] = presencia
        except ValueError:
            pass
        self._save_operations()
        self._notify("Configuracion local guardada")

    def on_vehiculo_switch(self, active):
        tipo = "moto" if active else "carro"
        self.operations["tipo_vehiculo"] = tipo
        self._save_operations()
        try:
            screen = self.root.ids.screen_manager.get_screen("operations")
            screen.ids.vehiculo_label.text = (
                "MOTO  (alta agilidad)" if active else "CARRO  (velocidad normal)"
            )
        except Exception:
            pass
        self._notify(f"Vehiculo activo: {tipo}")

    def _is_trip_rentable(self, offered_price, distance_km):
        base_min = float(self.operations.get("precio_minimo_viaje", 100.0))
        cost_km = float(self.operations.get("precio_por_km", 2.5))
        required = max(base_min, float(distance_km) * cost_km)
        return float(offered_price) >= required

    def _fill_node_screen(self):
        screen = self.root.ids.screen_manager.get_screen("node")
        screen.ids.node_hwid.text = self.identity.get("hwid", "--")
        if self.last_validation:
            screen.ids.node_sync_status.text = self.last_validation
        else:
            screen.ids.node_sync_status.text = "Pendiente"

    def _update_connection_screen(self):
        screen = self.root.ids.screen_manager.get_screen("connection")
        if self.is_authorized:
            lat = f" ({self.last_latency_ms} ms)" if self.last_latency_ms is not None else ""
            screen.ids.conn_status.text = "Activo" + lat
            screen.ids.conn_status.text_color = (0.64, 0.90, 0.21, 1)
        else:
            screen.ids.conn_status.text = "Bloqueado"
            screen.ids.conn_status.text_color = (1, 0.22, 0.22, 1)
        screen.ids.conn_endpoint.text = "Endpoint protegido y ofuscado"

    def start_trip(self):
        if not self.is_authorized:
            self._set_locked_state(
                "Licencia Inactiva",
                "Licencia Inactiva. Contacte al Administrador",
            )
            return

        self.trip_active = True
        self.trip_paused = False
        self.trip_distance_km = 0.0
        self.trip_wait_seconds = 0
        self.trip_extra_cost = 0.0
        self.trip_started_at = datetime.now().isoformat()
        self._update_trip_widgets()
        self._notify("Viaje iniciado")

    def add_distance(self, km):
        if not self.trip_active:
            self._notify("Inicia un viaje primero")
            return
        self.trip_distance_km = max(0.0, self.trip_distance_km + km)
        self._update_trip_widgets()

    def toggle_pause_wait(self):
        if not self.trip_active:
            self._notify("No hay viaje activo")
            return
        self.trip_paused = not self.trip_paused
        self._notify("Modo espera activado" if self.trip_paused else "Modo espera desactivado")

    def open_extra_cost_dialog(self):
        if not self.trip_active:
            self._notify("No hay viaje activo")
            return

        field = MDTextField(
            hint_text="Monto extra (peaje/parqueo)",
            input_filter="float",
            mode="rectangle",
        )

        self.extra_dialog = MDDialog(
            title="Anadir gasto extra",
            type="custom",
            content_cls=field,
            buttons=[],
        )
        self.extra_dialog.buttons = [
            self._dialog_button("Cancelar", self.extra_dialog.dismiss),
            self._dialog_button("Agregar", lambda *_: self._confirm_extra_cost(field.text)),
        ]
        self.extra_dialog.open()

    def _dialog_button(self, text, cb):
        from kivymd.uix.button import MDFlatButton

        return MDFlatButton(text=text, on_release=cb)

    def _confirm_extra_cost(self, value):
        try:
            extra = float(value)
        except ValueError:
            self._notify("Monto invalido")
            return

        if extra < 0:
            self._notify("El monto no puede ser negativo")
            return

        self.trip_extra_cost += extra
        if self.extra_dialog:
            self.extra_dialog.dismiss()
        self._update_trip_widgets()
        self._notify("Gasto agregado")

    def _trip_tick(self, _dt):
        if self.trip_active and self.trip_paused:
            self.trip_wait_seconds += 1
            self._update_trip_widgets()

    def _calculate_trip_total(self):
        base_min = float(self.operations.get("precio_minimo_viaje", 100.0))
        price_km = float(self.operations.get("precio_por_km", 2.5))
        benefit = bool(self.operations.get("regla_1km_cada_10km", True))

        charged_km = self.trip_distance_km
        if benefit:
            charged_km = max(0.0, self.trip_distance_km - floor(self.trip_distance_km / 10.0))

        km_cost = charged_km * price_km
        wait_cost = (self.trip_wait_seconds / 60.0) * WAIT_RATE_PER_MIN
        wait_rate = float(self.operations.get("precio_espera_por_min", WAIT_RATE_PER_MIN))
        # Moto: +20% costo de espera por alta demanda urbana
        if self.operations.get("tipo_vehiculo", "carro") == "moto":
            wait_rate *= 1.2
        wait_cost = (self.trip_wait_seconds / 60.0) * wait_rate

        subtotal = max(base_min, km_cost)
        total = subtotal + wait_cost + self.trip_extra_cost

        return {
            "charged_km": round(charged_km, 2),
            "km_cost": round(km_cost, 2),
            "wait_cost": round(wait_cost, 2),
            "extra_cost": round(self.trip_extra_cost, 2),
            "total": round(total, 2),
        }

    def _update_trip_widgets(self):
        screen = self.root.ids.screen_manager.get_screen("trip")
        calc = self._calculate_trip_total()

        wait_min = int(self.trip_wait_seconds // 60)
        screen.ids.trip_live_stats.text = (
            f"KM: {self.trip_distance_km:.2f} | Espera: {wait_min} min | Extras: {calc['extra_cost']:.2f}"
        )
        screen.ids.trip_live_total.text = f"Total: {calc['total']:.2f}"

        bubble = screen.ids.bubble
        bubble.bubble_text = f"KM {self.trip_distance_km:.2f} | Total {calc['total']:.2f}"

    # ─── Motor de Captacion ────────────────────────────────────────────────

    def toggle_capture_engine(self):
        if not self.is_authorized:
            self._notify("Licencia inactiva: motor bloqueado")
            return
        if self.capture_active:
            self._stop_capture_engine()
        else:
            self._start_capture_engine()

    def _start_capture_engine(self):
        self.capture_active = True
        self._capture_stop_flag.clear()
        self._capture_thread = threading.Thread(
            target=self._capture_scan_loop, daemon=True
        )
        self._capture_thread.start()
        self._countdown_clock = Clock.schedule_interval(self._countdown_tick, 1)
        self._android_service_bridge(start=True)
        Clock.schedule_once(lambda *_: self._refresh_bandeja_header())
        self._notify("Motor de captacion activado")

    def _stop_capture_engine(self):
        self.capture_active = False
        self._capture_stop_flag.set()
        if hasattr(self, "_countdown_clock") and self._countdown_clock:
            self._countdown_clock.cancel()
            self._countdown_clock = None
        self._android_service_bridge(start=False)
        Clock.schedule_once(lambda *_: self._refresh_bandeja_header())
        self._notify("Motor detenido")

    def _countdown_tick(self, _dt):
        """Cada segundo: libera viajes cuyo deadline ya paso."""
        now = time.time()
        antes = len(self.captured_trips)
        self.captured_trips = [
            t for t in self.captured_trips if t.get("deadline", now + 1) > now
        ]
        if self.capture_active:
            Clock.schedule_once(lambda *_: self._refresh_bandeja_ui())
        if len(self.captured_trips) < antes:
            self._notify("Viaje liberado por timeout (5s)")

    def _capture_scan_loop(self):
        """Bucle de escaneo de alta velocidad — simula deteccion de viajes."""
        import random

        zonas = ["Zona Norte", "Centro", "Aeropuerto", "Zona Sur", "Mercado", "Universidad"]
        trip_counter = 0

        while not self._capture_stop_flag.is_set():
            tipo = self.operations.get("tipo_vehiculo", "carro")
            agility_factor = 0.82 if tipo == "moto" else 1.0
            interval = max(0.2, (self.scan_speed_ms / 1000.0) * agility_factor)
            self._capture_stop_flag.wait(interval)
            if self._capture_stop_flag.is_set():
                break

            # Probabilidad de capturar un viaje en este ciclo (35 %)
            if random.random() > 0.35:
                continue

            trip_counter += 1
            dist = round(random.uniform(0.8, 22.0), 1)
            precio_por_km = float(self.operations.get("precio_por_km", 2.5))
            precio_base = float(self.operations.get("precio_minimo_viaje", 100.0))

            # Precio ofrecido: aleatorio ±40 % del precio justo
            precio_justo = max(precio_base, dist * precio_por_km)
            precio_ofrecido = round(
                precio_justo * random.uniform(0.60, 1.40), 2
            )
            rentable = self._is_trip_rentable(precio_ofrecido, dist)

            # Exclusivo: moto o scan rapido (<500 ms) bate a la app estandar (~900 ms)
            tipo = self.operations.get("tipo_vehiculo", "carro")
            exclusivo = (self.scan_speed_ms < 500) or (tipo == "moto")

            # Temporizador: 5 s para aceptar antes de que el viaje se libere
            deadline = time.time() + 5.0

            trip = {
                "id": f"TR-{trip_counter:04d}",
                "distancia_km": dist,
                "precio_ofrecido": precio_ofrecido,
                "precio_por_km": dist and round(precio_ofrecido / dist, 2),
                "capturado_en": time.time(),
                "deadline": deadline,
                "zona": random.choice(zonas),
                "exclusivo": exclusivo,
                "rentable": rentable,
            }

            self.captured_trips.append(trip)
            # Limitar bandeja a 12 viajes (los mas recientes)
            if len(self.captured_trips) > 12:
                self.captured_trips = self.captured_trips[-12:]

            Clock.schedule_once(lambda *_: self._refresh_bandeja_ui())

    def toggle_exclusividad_filter(self, active):
        self.exclusividad_filter = bool(active)
        self._refresh_bandeja_ui()

    def on_scan_speed_change(self, value):
        self.scan_speed_ms = int(value)
        try:
            screen = self.root.ids.screen_manager.get_screen("bandeja")
            screen.ids.scan_speed_label.text = f"{self.scan_speed_ms} ms"
        except Exception:
            pass

    def accept_captured_trip(self, trip_id):
        """Acepta un viaje capturado. Si hay viaje activo, encola (double-queue)."""
        trip = next((t for t in self.captured_trips if t["id"] == trip_id), None)
        if not trip:
            self._notify("Viaje ya no disponible")
            return

        # Remover de la bandeja
        self.captured_trips = [t for t in self.captured_trips if t["id"] != trip_id]

        if self.trip_active:
            # Double-queue: agregar a la cola secundaria
            self.trip_queue.append(trip)
            self._notify(
                f"Viaje {trip_id} encolado (en ruta) — Cola: {len(self.trip_queue)} pendiente(s)"
            )
            self._refresh_bandeja_ui()
            return

        # Iniciar inmediatamente
        self._launch_trip(trip)

    def _launch_trip(self, trip):
        self.trip_active = True
        self.trip_paused = False
        self.trip_distance_km = trip["distancia_km"]
        self.trip_wait_seconds = 0
        self.trip_extra_cost = 0.0
        self.trip_started_at = datetime.now().isoformat()
        self._update_trip_widgets()
        self._refresh_bandeja_ui()
        self.nav_to("trip")
        self._notify(
            f"Viaje {trip['id']} activo — {trip['distancia_km']} KM | ${trip['precio_ofrecido']}"
        )

    def discard_captured_trip(self, trip_id):
        self.captured_trips = [t for t in self.captured_trips if t["id"] != trip_id]
        self._refresh_bandeja_ui()

    def _refresh_bandeja_header(self):
        try:
            screen = self.root.ids.screen_manager.get_screen("bandeja")
            if self.capture_active:
                screen.ids.capture_status_label.text = "Motor: ACTIVO ●"
                screen.ids.capture_status_label.text_color = (0.64, 0.90, 0.21, 1)
                screen.ids.capture_toggle_btn.text = "DETENER"
                screen.ids.capture_toggle_btn.md_bg_color = (1, 0.22, 0.22, 1)
            else:
                screen.ids.capture_status_label.text = "Motor: INACTIVO"
                screen.ids.capture_status_label.text_color = (1, 0.22, 0.22, 1)
                screen.ids.capture_toggle_btn.text = "ACTIVAR"
                screen.ids.capture_toggle_btn.md_bg_color = (0.13, 0.83, 0.93, 1)
        except Exception:
            pass

    def _refresh_bandeja_ui(self):
        from kivymd.uix.button import MDFlatButton, MDRaisedButton as _RB
        from kivymd.uix.label import MDLabel as _LBL

        try:
            screen = self.root.ids.screen_manager.get_screen("bandeja")
            container = screen.ids.bandeja_list
            container.clear_widgets()

            visible = self.captured_trips
            if self.exclusividad_filter:
                visible = [t for t in visible if t["exclusivo"]]

            # Actualizar contador y estado de cola
            screen.ids.capture_counter_label.text = (
                f"Viajes capturados: {len(self.captured_trips)}"
                + (" (filtro activo)" if self.exclusividad_filter else "")
            )
            cola_n = len(self.trip_queue)
            if "queue_status_label" in screen.ids:
                if self.trip_active:
                    screen.ids.queue_status_label.text = (
                        f"En ruta | Cola: {cola_n} pendiente(s)"
                    )
                    screen.ids.queue_status_label.text_color = (
                        (0.64, 0.90, 0.21, 1) if cola_n else (0.13, 0.83, 0.93, 1)
                    )
                else:
                    screen.ids.queue_status_label.text = "Cola: vacia"
                    screen.ids.queue_status_label.text_color = (0.50, 0.60, 0.75, 1)

            if not visible:
                empty = _LBL(
                    text="Sin viajes capturados aun. Activa el motor.",
                    halign="center",
                    theme_text_color="Custom",
                    text_color=(0.72, 0.80, 0.92, 1),
                    size_hint_y=None,
                    height=dp(60),
                )
                container.add_widget(empty)
                return

            now = time.time()
            for trip in reversed(visible):
                elapsed = int(now - trip["capturado_en"])
                remaining = max(0, int(trip.get("deadline", now) - now))
                urgente = remaining <= 2
                excl_badge = "[EXCL]" if trip["exclusivo"] else "[STD]"
                rent_badge = "RENTABLE" if trip["rentable"] else "BAJO PRECIO"
                excl_color = (0.64, 0.90, 0.21, 1) if trip["exclusivo"] else (0.72, 0.80, 0.92, 1)
                rent_color = (0.13, 0.83, 0.93, 1) if trip["rentable"] else (1, 0.74, 0.0, 1)
                # Card bg urgente = rojo tenue
                card_bg = (0.14, 0.04, 0.04, 1) if urgente else (0.06, 0.10, 0.19, 1)

                card = MDCard(
                    radius=[14, 14, 14, 14],
                    md_bg_color=card_bg,
                    padding=dp(12),
                    orientation="vertical",
                    size_hint_y=None,
                    height=dp(130),
                )

                # Fila 1: ID, zona, exclusividad, countdown
                row1 = MDBoxLayout(size_hint_y=None, height=dp(24), spacing=dp(6))
                row1.add_widget(_LBL(
                    text=f"{trip['id']} — {trip['zona']} {excl_badge}",
                    bold=True, font_size="12sp",
                    theme_text_color="Custom",
                    text_color=excl_color,
                ))
                countdown_color = (1, 0.22, 0.22, 1) if urgente else (0.64, 0.90, 0.21, 1)
                row1.add_widget(_LBL(
                    text=f"⏱ {remaining}s",
                    font_size="11sp", halign="right", bold=True,
                    theme_text_color="Custom",
                    text_color=countdown_color,
                ))
                card.add_widget(row1)

                # Fila 2: distancia, precio, rentabilidad
                row2 = MDBoxLayout(size_hint_y=None, height=dp(28), spacing=dp(10))
                row2.add_widget(_LBL(
                    text=f"Dist: {trip['distancia_km']} KM",
                    font_size="13sp", bold=True,
                    theme_text_color="Custom",
                    text_color=(0.90, 0.96, 1, 1),
                ))
                row2.add_widget(_LBL(
                    text=f"Precio: ${trip['precio_ofrecido']}",
                    font_size="13sp", bold=True,
                    theme_text_color="Custom",
                    text_color=rent_color,
                ))
                row2.add_widget(_LBL(
                    text=f"${trip['precio_por_km']}/KM  {rent_badge}",
                    font_size="10sp", halign="right",
                    theme_text_color="Custom",
                    text_color=rent_color,
                ))
                card.add_widget(row2)

                # Fila 3: botones aceptar / descartar
                row3 = MDBoxLayout(size_hint_y=None, height=dp(36), spacing=dp(8))
                tid = trip["id"]

                btn_aceptar = _RB(
                    text="ACEPTAR",
                    md_bg_color=(0.64, 0.90, 0.21, 1),
                    text_color=(0.04, 0.06, 0.10, 1),
                    size_hint_y=None, height=dp(34),
                )
                btn_aceptar.bind(on_release=lambda _btn, t=tid: self.accept_captured_trip(t))

                btn_desc = MDFlatButton(
                    text="Descartar",
                    theme_text_color="Custom",
                    text_color=(1, 0.40, 0.40, 1),
                )
                btn_desc.bind(on_release=lambda _btn, t=tid: self.discard_captured_trip(t))

                row3.add_widget(btn_aceptar)
                row3.add_widget(btn_desc)
                card.add_widget(row3)

                container.add_widget(card)

        except Exception as e:
            self._notify(f"Error al refrescar bandeja: {e}")

    # ─── Fin Motor de Captacion ────────────────────────────────────────────

    def finish_trip(self):
        if not self.trip_active:
            self._notify("No hay viaje activo")
            return

        calc = self._calculate_trip_total()
        payload = {
            "fecha": datetime.now().isoformat(),
            "hwid": self.identity.get("hwid", "--"),
            "km_reales": round(self.trip_distance_km, 2),
            "km_cobrados": calc["charged_km"],
            "costo_km": calc["km_cost"],
            "costo_espera": calc["wait_cost"],
            "extras": calc["extra_cost"],
            "total": calc["total"],
            "radio_visibilidad_km": self.operations.get("radio_visibilidad_km", 8.0),
        }

        ticket_path = self._store_ticket(payload)
        self._show_ticket(payload, ticket_path)

        self.trip_active = False
        self.trip_paused = False
        self.trip_distance_km = 0.0
        self.trip_wait_seconds = 0
        self.trip_extra_cost = 0.0
        self._update_trip_widgets()
        self._notify("Viaje finalizado y ticket generado")

        # Si hay viajes en cola, lanzar el siguiente automaticamente
        if self.trip_queue:
            siguiente = self.trip_queue.pop(0)
            self._notify(f"Iniciando siguiente viaje de la cola: {siguiente['id']}")
            Clock.schedule_once(lambda *_: self._launch_trip(siguiente), 0.5)

    def _store_ticket(self, payload):
        os.makedirs(TICKETS_DIR, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        txt_file = os.path.join(TICKETS_DIR, f"ticket_{stamp}.txt")
        with open(txt_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False, indent=2))
        return txt_file

    def _show_ticket(self, payload, ticket_path):
        screen = self.root.ids.screen_manager.get_screen("ticket")
        summary = (
            f"HWID: {payload['hwid']}\n"
            f"KM reales: {payload['km_reales']}\n"
            f"KM cobrados: {payload['km_cobrados']}\n"
            f"Costo KM: {payload['costo_km']}\n"
            f"Espera: {payload['costo_espera']}\n"
            f"Extras: {payload['extras']}\n"
            f"TOTAL: {payload['total']}"
        )
        screen.ids.ticket_summary.text = summary
        screen.ids.ticket_store_status.text = f"Ticket guardado en: {ticket_path}"
        self.nav_to("ticket")


if __name__ == "__main__":
    SentinelCoreTerminal().run()
