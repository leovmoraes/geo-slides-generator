"""
Serviço de Operações no Google Slides (Batch Updates Determinísticos)
"""

import logging
from typing import List, Dict, Any, Optional
from src.models.presentation_spec import PresentationSpec, SlideSpec, CardSpec
from src.services.auth_service import get_slides_service
from src.config import (
    COLOR_PRIMARY_ORANGE,
    COLOR_PRIMARY_BLUE,
    COLOR_BG_CARD,
    COLOR_BORDER_CARD,
    COLOR_TEXT_DARK,
    COLOR_TEXT_MUTED,
    FONT_TITLE,
    FONT_BODY,
    EMU_PER_PT
)

logger = logging.getLogger(__name__)

class SlidesService:
    def __init__(self, slides_client=None, user_token: Optional[str] = None):
        self.client = slides_client or get_slides_service(user_token=user_token)

    def apply_presentation_spec(self, presentation_id: str, spec: PresentationSpec) -> str:
        """
        Executa as alterações estruturadas na apresentação clonada via batchUpdate.
        """
        logger.info(f"Aplicando especificação de slides na apresentação {presentation_id}...")

        presentation = self.client.presentations().get(
            presentationId=presentation_id
        ).execute()

        slides = presentation.get("slides", [])
        num_slides = len(slides)
        logger.info(f"Apresentação matriz possui {num_slides} slides iniciais.")

        requests = []

        # 1. Atualizar Capa (Slide 1)
        if num_slides > 0:
            cover_slide_id = slides[0]["objectId"]
            requests.extend(self._build_cover_requests(cover_slide_id, spec))

        # 2. Atualizar Slide 2 (Boas-vindas / Contexto) se existir
        if num_slides > 1 and spec.welcome_slide:
            welcome_slide_id = slides[1]["objectId"]
            requests.extend(self._build_welcome_requests(welcome_slide_id, spec))

        # 3. Criar Slides de Conteúdo baseados em Cards
        for idx, slide_spec in enumerate(spec.slides):
            insert_index = 2 + idx
            slide_id = f"content_slide_{idx+1}"
            requests.extend(self._build_content_slide_requests(slide_id, insert_index, slide_spec))

        # 4. Executar tudo em um único lote atômico (batchUpdate)
        logger.info(f"Executando batchUpdate com {len(requests)} operações...")
        body = {"requests": requests}
        self.client.presentations().batchUpdate(
            presentationId=presentation_id,
            body=body
        ).execute()

        url = f"https://docs.google.com/presentation/d/{presentation_id}/edit"
        logger.info(f"Apresentação concluída com sucesso! URL: {url}")
        return url

    def _build_cover_requests(self, slide_id: str, spec: PresentationSpec) -> List[Dict[str, Any]]:
        client_name = getattr(spec, "client_name", None) or getattr(spec, "client", "") or ""
        requests = [
            {
                "replaceAllText": {
                    "containsText": {"text": "{{TITULO}}", "matchCase": False},
                    "replaceText": spec.title,
                    "pageObjectIds": [slide_id]
                }
            },
            {
                "replaceAllText": {
                    "containsText": {"text": "{{SUBTITULO}}", "matchCase": False},
                    "replaceText": spec.subtitle,
                    "pageObjectIds": [slide_id]
                }
            },
            {
                "replaceAllText": {
                    "containsText": {"text": "{{CLIENTE}}", "matchCase": False},
                    "replaceText": client_name,
                    "pageObjectIds": [slide_id]
                }
            }
        ]
        return requests

    def _build_welcome_requests(self, slide_id: str, spec: PresentationSpec) -> List[Dict[str, Any]]:
        welcome = spec.welcome_slide
        obj_text = getattr(welcome, "objective", None) or getattr(welcome, "title", "Objetivo Estratégico")
        return [
            {
                "replaceAllText": {
                    "containsText": {"text": "{{OBJETIVO}}", "matchCase": False},
                    "replaceText": obj_text,
                    "pageObjectIds": [slide_id]
                }
            }
        ]

    def _build_content_slide_requests(self, slide_id: str, insertion_index: int, slide_spec: SlideSpec) -> List[Dict[str, Any]]:
        requests = []
        section_cat = getattr(slide_spec, "section_title", None) or getattr(slide_spec, "section_category", "VISÃO GERAL")

        # 1. Slide em branco
        requests.append({
            "createSlide": {
                "objectId": slide_id,
                "insertionIndex": insertion_index,
                "slideLayoutReference": {"predefinedLayout": "BLANK"}
            }
        })

        # 2. Seção Cabeçalho
        category_box_id = f"{slide_id}_cat"
        requests.extend([
            {
                "createShape": {
                    "objectId": category_box_id,
                    "shapeType": "TEXT_BOX",
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "size": {"width": {"magnitude": 650 * EMU_PER_PT, "unit": "EMU"}, "height": {"magnitude": 25 * EMU_PER_PT, "unit": "EMU"}},
                        "transform": {"scaleX": 1, "scaleY": 1, "translateX": 30 * EMU_PER_PT, "translateY": 30 * EMU_PER_PT, "unit": "EMU"}
                    }
                }
            },
            {
                "insertText": {
                    "objectId": category_box_id,
                    "text": section_cat.upper(),
                    "insertionIndex": 0
                }
            },
            {
                "updateTextStyle": {
                    "objectId": category_box_id,
                    "style": {
                        "fontFamily": FONT_TITLE,
                        "fontSize": {"magnitude": 12, "unit": "PT"},
                        "bold": True,
                        "foregroundColor": {"opaqueColor": {"rgbColor": COLOR_PRIMARY_ORANGE}}
                    },
                    "fields": "fontFamily,fontSize,bold,foregroundColor"
                }
            }
        ])

        # 3. Título do Slide
        title_box_id = f"{slide_id}_title"
        requests.extend([
            {
                "createShape": {
                    "objectId": title_box_id,
                    "shapeType": "TEXT_BOX",
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "size": {"width": {"magnitude": 650 * EMU_PER_PT, "unit": "EMU"}, "height": {"magnitude": 40 * EMU_PER_PT, "unit": "EMU"}},
                        "transform": {"scaleX": 1, "scaleY": 1, "translateX": 30 * EMU_PER_PT, "translateY": 55 * EMU_PER_PT, "unit": "EMU"}
                    }
                }
            },
            {
                "insertText": {
                    "objectId": title_box_id,
                    "text": slide_spec.title,
                    "insertionIndex": 0
                }
            },
            {
                "updateTextStyle": {
                    "objectId": title_box_id,
                    "style": {
                        "fontFamily": FONT_TITLE,
                        "fontSize": {"magnitude": 20, "unit": "PT"},
                        "bold": True,
                        "foregroundColor": {"opaqueColor": {"rgbColor": COLOR_PRIMARY_BLUE}}
                    },
                    "fields": "fontFamily,fontSize,bold,foregroundColor"
                }
            }
        ])

        # 4. Inserção dos Cartões (Cards)
        cards = slide_spec.cards
        num_cards = min(len(cards), 4)
        if num_cards == 0:
            return requests

        slide_width_pt = 720
        margin_left_pt = 30
        gap_pt = 15
        available_width = slide_width_pt - (2 * margin_left_pt) - ((num_cards - 1) * gap_pt)
        card_width_pt = available_width / num_cards
        card_height_pt = 260
        card_top_pt = 105

        for card_idx, card in enumerate(cards[:num_cards]):
            card_x_pt = margin_left_pt + (card_idx * (card_width_pt + gap_pt))
            card_shape_id = f"{slide_id}_card_{card_idx}"

            requests.extend([
                {
                    "createShape": {
                        "objectId": card_shape_id,
                        "shapeType": "ROUND_RECTANGLE",
                        "elementProperties": {
                            "pageObjectId": slide_id,
                            "size": {"width": {"magnitude": card_width_pt * EMU_PER_PT, "unit": "EMU"}, "height": {"magnitude": card_height_pt * EMU_PER_PT, "unit": "EMU"}},
                            "transform": {"scaleX": 1, "scaleY": 1, "translateX": card_x_pt * EMU_PER_PT, "translateY": card_top_pt * EMU_PER_PT, "unit": "EMU"}
                        }
                    }
                },
                {
                    "updateShapeProperties": {
                        "objectId": card_shape_id,
                        "shapeProperties": {
                            "shapeBackgroundFill": {"solidFill": {"color": {"rgbColor": COLOR_BG_CARD}}},
                            "outline": {
                                "outlineFill": {"solidFill": {"color": {"rgbColor": COLOR_BORDER_CARD}}},
                                "weight": {"magnitude": 1, "unit": "PT"}
                            }
                        },
                        "fields": "shapeBackgroundFill.solidFill.color,outline.outlineFill.solidFill.color,outline.weight"
                    }
                }
            ])

            card_text_id = f"{slide_id}_cardtext_{card_idx}"
            bullet_list = getattr(card, "points", None) or getattr(card, "bullets", [])
            full_card_text = f"[{card.tag}]\n{card.title}\n\n" + "\n".join([f"• {b}" for b in bullet_list])

            requests.extend([
                {
                    "createShape": {
                        "objectId": card_text_id,
                        "shapeType": "TEXT_BOX",
                        "elementProperties": {
                            "pageObjectId": slide_id,
                            "size": {"width": {"magnitude": (card_width_pt - 20) * EMU_PER_PT, "unit": "EMU"}, "height": {"magnitude": (card_height_pt - 20) * EMU_PER_PT, "unit": "EMU"}},
                            "transform": {"scaleX": 1, "scaleY": 1, "translateX": (card_x_pt + 10) * EMU_PER_PT, "translateY": (card_top_pt + 10) * EMU_PER_PT, "unit": "EMU"}
                        }
                    }
                },
                {
                    "insertText": {
                        "objectId": card_text_id,
                        "text": full_card_text,
                        "insertionIndex": 0
                    }
                },
                {
                    "updateTextStyle": {
                        "objectId": card_text_id,
                        "style": {
                            "fontFamily": FONT_BODY,
                            "fontSize": {"magnitude": 10.5, "unit": "PT"},
                            "foregroundColor": {"opaqueColor": {"rgbColor": COLOR_TEXT_DARK}}
                        },
                        "fields": "fontFamily,fontSize,foregroundColor"
                    }
                }
            ])

        return requests
