"""
Serviço de Construção e Formatação de Slides no Google Slides API
"""

import time
import logging
from typing import List, Dict, Any
from src.config import COLORS, FONTS, SLIDE_LAYOUT
from src.models.presentation_spec import PresentationSpec, SlideSpec, CardSpec
from src.services.auth_service import get_slides_service

logger = logging.getLogger(__name__)

class SlidesService:
    def __init__(self, slides_client=None):
        self.client = slides_client or get_slides_service()

    def get_presentation(self, presentation_id: str) -> Dict[str, Any]:
        """Obtém detalhes da apresentação."""
        return self.client.presentations().get(
            presentationId=presentation_id
        ).execute()

    def apply_presentation_spec(self, presentation_id: str, spec: PresentationSpec) -> str:
        """
        Aplica a especificação completa da apresentação (Capa, Boas-vindas, Cartões e Encerramento)
        utilizando requisições em lote (batchUpdate) determinísticas.
        """
        logger.info(f"Aplicando especificação de slides na apresentação {presentation_id}...")
        
        presentation = self.get_presentation(presentation_id)
        existing_slides = presentation.get("slides", [])
        total_initial = len(existing_slides)
        logger.info(f"Apresentação matriz possui {total_initial} slides iniciais.")

        requests: List[Dict[str, Any]] = []

        # 1. Substituição global de tags da Capa e Metadados
        placeholders = {
            "{{TITULO}}": spec.title,
            "{{SUBTITULO}}": spec.subtitle + (f"\nPreparado para: {spec.client}" if spec.client else ""),
            "{{CLIENTE}}": spec.client or "",
            "{{AUTOR}}": spec.author,
            "{{DATA}}": spec.date or time.strftime("%d/%m/%Y")
        }

        for p_key, p_val in placeholders.items():
            if p_val:
                requests.append({
                    "replaceAllText": {
                        "containsText": {"text": p_key, "matchCase": True},
                        "replaceText": p_val
                    }
                })

        # 2. Inserir Slide de Boas-vindas se fornecido
        current_index = 1
        ts = int(time.time())

        if spec.welcome_slide:
            welcome_slide_id = f"slide_welcome_{ts}"
            welcome_reqs = self._create_card_slide_requests(
                slide_id=welcome_slide_id,
                insertion_index=current_index,
                slide_spec=spec.welcome_slide
            )
            requests.extend(welcome_reqs)
            current_index += 1

        # 3. Inserir Slides Intermediários de Conteúdo em Cartões
        for idx, slide_spec in enumerate(spec.slides):
            slide_id = f"slide_content_{idx+1}_{ts}"
            slide_reqs = self._create_card_slide_requests(
                slide_id=slide_id,
                insertion_index=current_index,
                slide_spec=slide_spec
            )
            requests.extend(slide_reqs)
            current_index += 1

        # Executar todas as mutações no Google Slides em uma única transação batchUpdate
        if requests:
            logger.info(f"Executando batchUpdate com {len(requests)} operações...")
            self.client.presentations().batchUpdate(
                presentationId=presentation_id,
                body={"requests": requests}
            ).execute()

        url = f"https://docs.google.com/presentation/d/{presentation_id}/edit"
        logger.info(f"Apresentação concluída com sucesso! URL: {url}")
        return url

    def _create_card_slide_requests(
        self, slide_id: str, insertion_index: int, slide_spec: SlideSpec
    ) -> List[Dict[str, Any]]:
        """Gera a lista de operações para desenhar um slide determinístico com padrão de cartões."""
        reqs: List[Dict[str, Any]] = []

        # 1. Criação do Slide em Branco
        reqs.append({
            "createSlide": {
                "objectId": slide_id,
                "insertionIndex": insertion_index,
                "slideLayoutReference": {"predefinedLayout": "BLANK"}
            }
        })

        # 2. Fundo Claro Institucional (#F5F7FA)
        reqs.append({
            "updateSlideProperties": {
                "objectId": slide_id,
                "slideProperties": {
                    "isSkipped": False
                },
                "fields": "isSkipped"
            }
        })

        # 3. Cabeçalho: Tag/Categoria em Laranja (#F58120)
        sec_shape_id = f"sec_{slide_id}"
        reqs.extend([
            {
                "createShape": {
                    "objectId": sec_shape_id,
                    "shapeType": "TEXT_BOX",
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "size": {"width": {"magnitude": 640, "unit": "PT"}, "height": {"magnitude": 20, "unit": "PT"}},
                        "transform": {"scaleX": 1, "scaleY": 1, "translateX": 40, "translateY": 25, "unit": "PT"}
                    }
                }
            },
            {
                "insertText": {
                    "objectId": sec_shape_id,
                    "text": slide_spec.section_title.upper()
                }
            },
            {
                "updateTextStyle": {
                    "objectId": sec_shape_id,
                    "style": {
                        "fontFamily": FONTS["TITLE"],
                        "fontSize": {"magnitude": 10, "unit": "PT"},
                        "bold": True,
                        "foregroundColor": {"opaqueColor": {"rgbColor": COLORS["ORANGE_GEO"]}}
                    },
                    "fields": "fontFamily,fontSize,bold,foregroundColor"
                }
            }
        ])

        # 4. Título do Slide em Poppins Bold (#202124)
        title_shape_id = f"title_{slide_id}"
        reqs.extend([
            {
                "createShape": {
                    "objectId": title_shape_id,
                    "shapeType": "TEXT_BOX",
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "size": {"width": {"magnitude": 640, "unit": "PT"}, "height": {"magnitude": 35, "unit": "PT"}},
                        "transform": {"scaleX": 1, "scaleY": 1, "translateX": 40, "translateY": 45, "unit": "PT"}
                    }
                }
            },
            {
                "insertText": {
                    "objectId": title_shape_id,
                    "text": slide_spec.title
                }
            },
            {
                "updateTextStyle": {
                    "objectId": title_shape_id,
                    "style": {
                        "fontFamily": FONTS["TITLE"],
                        "fontSize": {"magnitude": 18, "unit": "PT"},
                        "bold": True,
                        "foregroundColor": {"opaqueColor": {"rgbColor": COLORS["TEXT_PRIMARY"]}}
                    },
                    "fields": "fontFamily,fontSize,bold,foregroundColor"
                }
            }
        ])

        # 5. Renderização dos Cartões Brancos (Cards Pattern)
        cards = slide_spec.cards
        card_count = min(max(len(cards), 1), 4)

        margin_x = SLIDE_LAYOUT["MARGIN_X"]
        top_y = SLIDE_LAYOUT["TOP_Y"]
        available_width = SLIDE_LAYOUT["WIDTH"] - (margin_x * 2)
        gap = SLIDE_LAYOUT["GAP"]
        card_width = (available_width - ((card_count - 1) * gap)) / card_count
        card_height = SLIDE_LAYOUT["CARD_HEIGHT"]

        for c_idx, card in enumerate(cards):
            card_x = margin_x + (c_idx * (card_width + gap))
            card_shape_id = f"card_bg_{slide_id}_{c_idx}"
            card_text_id = f"card_txt_{slide_id}_{c_idx}"

            # Retângulo Branco com borda suave (#FFFFFF com borda #E8EAED)
            reqs.extend([
                {
                    "createShape": {
                        "objectId": card_shape_id,
                        "shapeType": "ROUND_RECTANGLE",
                        "elementProperties": {
                            "pageObjectId": slide_id,
                            "size": {"width": {"magnitude": card_width, "unit": "PT"}, "height": {"magnitude": card_height, "unit": "PT"}},
                            "transform": {"scaleX": 1, "scaleY": 1, "translateX": card_x, "translateY": top_y, "unit": "PT"}
                        }
                    }
                },
                {
                    "updateShapeProperties": {
                        "objectId": card_shape_id,
                        "shapeProperties": {
                            "shapeBackgroundFill": {"solidFill": {"color": {"rgbColor": COLORS["CARD_BG"]}}},
                            "outline": {
                                "outlineFill": {"solidFill": {"color": {"rgbColor": COLORS["CARD_BORDER"]}}},
                                "weight": {"magnitude": 1, "unit": "PT"}
                            }
                        },
                        "fields": "shapeBackgroundFill,outline"
                    }
                }
            ])

            # Conteúdo do Cartão: Tag Laranja + Título Azul + Tópicos em Inter
            tag_text = card.tag or f"0{c_idx+1}"
            card_title = card.title
            points_text = "\n\n".join([f"• {p}" for p in card.points])
            full_card_content = f"{tag_text}\n{card_title}\n\n{points_text}"

            reqs.extend([
                {
                    "createShape": {
                        "objectId": card_text_id,
                        "shapeType": "TEXT_BOX",
                        "elementProperties": {
                            "pageObjectId": slide_id,
                            "size": {"width": {"magnitude": card_width - 24, "unit": "PT"}, "height": {"magnitude": card_height - 24, "unit": "PT"}},
                            "transform": {"scaleX": 1, "scaleY": 1, "translateX": card_x + 12, "translateY": top_y + 12, "unit": "PT"}
                        }
                    }
                },
                {
                    "insertText": {
                        "objectId": card_text_id,
                        "text": full_card_content
                    }
                },
                {
                    "updateTextStyle": {
                        "objectId": card_text_id,
                        "style": {
                            "fontFamily": FONTS["BODY"],
                            "fontSize": {"magnitude": 10, "unit": "PT"},
                            "foregroundColor": {"opaqueColor": {"rgbColor": COLORS["TEXT_SECONDARY"]}}
                        },
                        "fields": "fontFamily,fontSize,foregroundColor"
                    }
                }
            ])

        # 6. Rodapé Institucional Oficial
        footer_shape_id = f"footer_{slide_id}"
        reqs.extend([
            {
                "createShape": {
                    "objectId": footer_shape_id,
                    "shapeType": "TEXT_BOX",
                    "elementProperties": {
                        "pageObjectId": slide_id,
                        "size": {"width": {"magnitude": 640, "unit": "PT"}, "height": {"magnitude": 20, "unit": "PT"}},
                        "transform": {"scaleX": 1, "scaleY": 1, "translateX": 40, "translateY": 380, "unit": "PT"}
                    }
                }
            },
            {
                "insertText": {
                    "objectId": footer_shape_id,
                    "text": "Geoambiente & Google Cloud • Padrão Corporativo Oficial"
                }
            },
            {
                "updateTextStyle": {
                    "objectId": footer_shape_id,
                    "style": {
                        "fontFamily": FONTS["BODY"],
                        "fontSize": {"magnitude": 8, "unit": "PT"},
                        "foregroundColor": {"opaqueColor": {"rgbColor": COLORS["TEXT_SECONDARY"]}}
                    },
                    "fields": "fontFamily,fontSize,foregroundColor"
                }
            }
        ])

        return reqs