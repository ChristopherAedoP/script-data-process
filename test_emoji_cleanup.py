#!/usr/bin/env python3
"""
Test emoji and special character cleanup
"""

from src.document_processor import DocumentProcessor

def test_emoji_cleanup():
    """Test the enhanced emoji and special character cleanup"""
    
    processor = DocumentProcessor()
    
    # Test cases with problematic content from original_texts.json
    test_cases = [
        {
            'input': '7️⃣ Chao préstamo al Estado. Terminaremos con el préstamo',
            'expected_clean': 'Chao préstamo al Estado. Terminaremos con el préstamo'
        },
        {
            'input': '8️⃣ Revitalizaremos la infraestructura como impulsor del desarrollo.',
            'expected_clean': 'Revitalizaremos la infraestructura como impulsor del desarrollo.'
        },
        {
            'input': '9️⃣ Promoveremos una transición energética 🚀 segura ⚡ eficiente',
            'expected_clean': 'Promoveremos una transición energética segura eficiente'
        },
        {
            'input': '• Plan estratégico ► Implementación ◆ Resultados',
            'expected_clean': 'Plan estratégico Implementación Resultados'
        },
        {
            'input': '**Propuesta importante** para *mejorar* la __situación__ _actual_',
            'expected_clean': 'Propuesta importante para mejorar la situación actual'
        },
        {
            'input': '## Título Principal\n\n### Subtítulo\n\nContenido normal',
            'expected_clean': 'Título Principal Subtítulo Contenido normal'
        }
    ]
    
    print("=== EMOJI & SPECIAL CHARACTER CLEANUP TEST ===\n")
    
    all_passed = True
    
    for i, case in enumerate(test_cases, 1):
        cleaned = processor.clean_markdown_content(case['input'])
        passed = cleaned == case['expected_clean']
        
        print(f"Test {i}: {'PASS' if passed else 'FAIL'}")
        print(f"  Input:    '{case['input']}'")
        print(f"  Expected: '{case['expected_clean']}'")
        print(f"  Got:      '{cleaned}'")
        
        if not passed:
            all_passed = False
            # Show character differences
            print(f"  Diff:     Expected len={len(case['expected_clean'])}, Got len={len(cleaned)}")
        
        print()
    
    print("=" * 60)
    if all_passed:
        print("SUCCESS: ALL TESTS PASSED - EMOJI CLEANUP WORKING CORRECTLY!")
    else:
        print("WARNING: SOME TESTS FAILED - REVIEW CLEANUP LOGIC")
    print("=" * 60)
    
    return all_passed

if __name__ == "__main__":
    test_emoji_cleanup()