"""
Configurações e Design System Corporativo Geoambiente & Google Cloud
"""

import os
from dotenv import load_dotenv

load_dotenv()

# GCP & Workspace Settings (Gemini 3.7 Flash utiliza location "global")
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "geo-gemini-enterprise")
GCP_REGION = os.getenv("GCP_REGION", "global")

# Modelo Gemini de Alta Performance
DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")

# Template Matrix Oficial Homologado no Google Slides
TEMPLATE_PRESENTATION_ID = os.getenv(
    "TEMPLATE_PRESENTATION_ID", 
    "19F33ff11h0p2NF6GEcYAPj3se0eGzWKwzir3szAZpiI"
)

# Paleta de Cores Institucional
COLORS = {
    "ORANGE_GEO": {"red": 0.961, "green": 0.506, "blue": 0.125},    # #F58120
    "BLUE_GCP": {"red": 0.102, "green": 0.451, "blue": 0.910},      # #1A73E8
    "TEXT_PRIMARY": {"red": 0.125, "green": 0.129, "blue": 0.141},  # #202124
    "TEXT_SECONDARY": {"red": 0.373, "green": 0.388, "blue": 0.408},# #5F6368
    "CARD_BG": {"red": 1.0, "green": 1.0, "blue": 1.0},             # #FFFFFF
    "SLIDE_BG": {"red": 0.961, "green": 0.969, "blue": 0.980},      # #F5F7FA
    "CARD_BORDER": {"red": 0.910, "green": 0.918, "blue": 0.929}   # #E8EAED
}

# Hex Cores para referência e prompts
COLORS_HEX = {
    "ORANGE_GEO": "#F58120",
    "BLUE_GCP": "#1A73E8",
    "TEXT_PRIMARY": "#202124",
    "TEXT_SECONDARY": "#5F6368",
    "CARD_BG": "#FFFFFF",
    "SLIDE_BG": "#F5F7FA",
    "CARD_BORDER": "#E8EAED"
}

# Tipografia Homologada
FONTS = {
    "TITLE": "Poppins",
    "BODY": "Inter"
}

# Constantes de conveniência para montagem visual
COLOR_PRIMARY_ORANGE = COLORS["ORANGE_GEO"]
COLOR_PRIMARY_BLUE = COLORS["BLUE_GCP"]
COLOR_BG_CARD = COLORS["CARD_BG"]
COLOR_BORDER_CARD = COLORS["CARD_BORDER"]
COLOR_TEXT_DARK = COLORS["TEXT_PRIMARY"]
COLOR_TEXT_MUTED = COLORS["TEXT_SECONDARY"]
FONT_TITLE = FONTS["TITLE"]
FONT_BODY = FONTS["BODY"]
EMU_PER_PT = 12700

# Dimensões Padrão de Slides 16:9 (em Pontos - PT)
SLIDE_LAYOUT = {
    "WIDTH": 720,
    "HEIGHT": 405,
    "MARGIN_X": 40,
    "TOP_Y": 95,
    "CARD_HEIGHT": 260,
    "GAP": 16
}
