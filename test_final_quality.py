#!/usr/bin/env python3
"""Final quality test - Check emoji cleanup in indexed content"""

from src.rag_system import RAGSystem
import json

def test_final_content_quality():
    """Test that indexed content is clean of emojis and formatting artifacts"""
    
    print("=== FINAL CONTENT QUALITY TEST ===")
    
    # Load system
    rag = RAGSystem()
    rag.index_documents("./docs", force_reindex=False)  # Load existing
    
    # Read the cleaned original texts
    with open('./data/original_texts.json', 'r', encoding='utf-8') as f:
        original_texts = json.load(f)
    
    print(f"Loaded {len(original_texts)} chunks for quality analysis")
    
    # Quality checks
    emoji_issues = []
    formatting_issues = []
    quality_metrics = {
        'total_chunks': len(original_texts),
        'emoji_contaminated': 0,
        'markdown_contaminated': 0,
        'clean_chunks': 0,
        'avg_length': 0
    }
    
    total_length = 0
    
    for i, text in enumerate(original_texts):
        total_length += len(text)
        
        # Check for emoji contamination
        has_emoji = any(char in text for char in ['️⃣', '🎯', '🚀', '💡', '⚡', '🔥', '🌟', '✨'])
        if has_emoji:
            quality_metrics['emoji_contaminated'] += 1
            emoji_issues.append(f"Chunk {i}: {text[:100]}...")
        
        # Check for markdown formatting artifacts
        has_markdown = any(artifact in text for artifact in ['**', '##', '###', '_', '`', '[', ']', '(', ')http'])
        if has_markdown:
            quality_metrics['markdown_contaminated'] += 1
            if len(formatting_issues) < 5:  # Only show first 5
                formatting_issues.append(f"Chunk {i}: {text[:100]}...")
        
        if not has_emoji and not has_markdown:
            quality_metrics['clean_chunks'] += 1
    
    quality_metrics['avg_length'] = total_length // len(original_texts)
    
    # Report results
    print(f"\nQuality Analysis Results:")
    print(f"  Total chunks: {quality_metrics['total_chunks']}")
    print(f"  Clean chunks: {quality_metrics['clean_chunks']}")
    print(f"  Emoji contaminated: {quality_metrics['emoji_contaminated']}")
    print(f"  Markdown contaminated: {quality_metrics['markdown_contaminated']}")
    print(f"  Average chunk length: {quality_metrics['avg_length']} chars")
    
    clean_percentage = (quality_metrics['clean_chunks'] / quality_metrics['total_chunks']) * 100
    print(f"  Content cleanliness: {clean_percentage:.1f}%")
    
    if emoji_issues:
        print(f"\n!! EMOJI CONTAMINATION DETECTED ({len(emoji_issues)} chunks):")
        for issue in emoji_issues[:3]:
            print(f"    {issue}")
    
    if formatting_issues:
        print(f"\n!! MARKDOWN CONTAMINATION DETECTED ({len(formatting_issues)} chunks):")
        for issue in formatting_issues[:3]:
            print(f"    {issue}")
    
    # Test search quality with cleaned content
    print(f"\n=== SEARCH QUALITY TEST ===")
    
    test_query = "pensiones AFP sistema previsional"
    results = rag.search(test_query, k=3)
    
    if results:
        print(f"Search results for '{test_query}':")
        for i, result in enumerate(results, 1):
            score = result.get('similarity_score', 0)
            metadata = result.get('metadata', {})
            content_preview = result.get('content', 'N/A')[:100]
            
            print(f"  {i}. Score: {score:.3f}")
            print(f"     Category: {metadata.get('topic_category', 'N/A')}")
            print(f"     Taxonomy: {metadata.get('taxonomy_path', 'N/A')}")
            print(f"     Content: {content_preview}...")
            
            # Check if this result has emoji contamination
            has_content_emoji = any(char in content_preview for char in ['️⃣', '🎯', '🚀', '💡'])
            if has_content_emoji:
                print(f"     !! EMOJI FOUND IN SEARCH RESULT")
            print()
    
    # Overall assessment
    print("=" * 50)
    if quality_metrics['emoji_contaminated'] == 0:
        print("SUCCESS: No emoji contamination detected!")
    else:
        print(f"WARNING: {quality_metrics['emoji_contaminated']} chunks still contain emojis")
    
    if clean_percentage >= 90:
        print(f"SUCCESS: High content cleanliness ({clean_percentage:.1f}%)")
    else:
        print(f"WARNING: Content cleanliness below 90% ({clean_percentage:.1f}%)")
    
    return quality_metrics

if __name__ == "__main__":
    try:
        metrics = test_final_content_quality()
        print(f"\nFinal Quality Score: {(metrics['clean_chunks']/metrics['total_chunks'])*100:.1f}%")
    except Exception as e:
        print(f"Test failed: {e}")