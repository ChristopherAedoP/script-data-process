#!/usr/bin/env python3
"""Simple cleanup test without emoji display issues"""

from src.document_processor import DocumentProcessor

processor = DocumentProcessor()

test_input = "7️⃣ Chao préstamo al Estado. Terminaremos con el préstamo"
cleaned = processor.clean_markdown_content(test_input)

print("Cleanup Test:")
print(f"Original length: {len(test_input)}")
print(f"Cleaned length: {len(cleaned)}")
print(f"Has emoji bullets removed: {'️⃣' not in cleaned}")
print(f"Content preserved: {'Chao préstamo' in cleaned}")

# Test with the actual problematic content from original_texts.json  
test_content = '''digital jugarán un rol central.",
  "7️⃣ Chao préstamo al Estado. Terminaremos con el préstamo de las personas al Estado contenido en la reforma previsional, para lo cual lo sustituiremos por la inversión en instrumentos financieros en condiciones de mercado. Así se consolidará que todo el aporte de cotización adicional vaya a las cuentas individuales de cada trabajador. Velaremos, asimismo, por el correcto funcionamiento y diseño del Seguro de Invalidez y Sobrevivencia (SIS). Revisaremos las reglas de inversión y la normativa de las",
  "Revisaremos las reglas de inversión y la normativa de las carteras de referencia de los nuevos fondos generacionales para maximizar la rentabilidad de los ahorros.",
  "8️⃣ Revitalizaremos la infraestructura como impulsor del desarrollo.'''

cleaned_content = processor.clean_markdown_content(test_content)

print("\nContent Analysis:")
print(f"Original has numbered emojis: {'️⃣' in test_content}")
print(f"Cleaned has numbered emojis: {'️⃣' in cleaned_content}")
print(f"Content starts correctly: {cleaned_content.startswith('digital')}")
print(f"Semantic content preserved: {'Chao préstamo al Estado' in cleaned_content}")

if '️⃣' not in cleaned_content and 'Chao préstamo al Estado' in cleaned_content:
    print("\nSUCCESS: Emoji cleanup working correctly!")
else:
    print("\nWARNING: Cleanup may need adjustment")