"""
Geoambiente & Google Cloud - Slide Master Generator
Entrypoint Principal do Workflow Multi-Agente ADK
"""

import sys
import logging
from src.workflow.orchestrator import SlideMasterWorkflow

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

def main():
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        print("\n=======================================================")
        print("  Geoambiente & Google Cloud - Slide Master Generator  ")
        print("  Workflow Multi-Agente ADK                           ")
        print("=======================================================\n")
        prompt = input("Digite o briefing da apresentação: ").strip()

    if not prompt:
        print("Prompt vazio. Encerrando.")
        return

    workflow = SlideMasterWorkflow()
    try:
        result = workflow.run(prompt)
        print("\n" + "="*60)
        print("  ✅ APRESENTAÇÃO GERADA COM SUCESSO!")
        print("="*60)
        print(f"📊 Título: {result.title}")
        if result.client_name:
            print(f"🏢 Cliente: {result.client_name}")
        print(f"📑 Total de Slides: {result.slide_count}")
        print(f"⏱️ Tempo de Execução: {result.execution_time_seconds:.2f}s")
        print(f"\n🔗 Link do Google Slides:")
        print(f"👉 {result.presentation_url}\n")
        print("="*60 + "\n")
    except Exception as e:
        logging.error(f"Falha na execução do workflow: {e}", exc_info=True)
        print(f"\n❌ Erro: {e}\n")

if __name__ == "__main__":
    main()