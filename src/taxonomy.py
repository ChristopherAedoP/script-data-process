"""
Taxonomy System for Political Document Classification
Handles hierarchical classification of political content into categories and subcategories
"""
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass


@dataclass
class TaxonomyClassification:
    """Result of taxonomy classification"""
    category: str
    subcategory: Optional[str] = None
    taxonomy_path: Optional[str] = None
    confidence: float = 0.0
    matched_keywords: List[str] = None
    
    def __post_init__(self):
        if self.matched_keywords is None:
            self.matched_keywords = []
        if self.category and self.subcategory:
            self.taxonomy_path = f"{self.category} > {self.subcategory}"


class TaxonomyClassifier:
    """Hierarchical taxonomy classifier for political documents"""
    
    def __init__(self, taxonomy_path: Optional[str] = None):
        """
        Initialize the taxonomy classifier
        
        Args:
            taxonomy_path: Path to taxonomy.json file, defaults to root taxonomy.json
        """
        if taxonomy_path is None:
            # Default to taxonomy.json in project root
            current_dir = Path(__file__).parent.parent
            taxonomy_path = current_dir / "taxonomy.json"
        
        self.taxonomy_path = Path(taxonomy_path)
        self.taxonomy_data = self._load_taxonomy()
        self.categories = self.taxonomy_data.get("categories", {})
        self.metadata = self.taxonomy_data.get("metadata", {})
        self.confidence_threshold = self.metadata.get("confidence_threshold", 0.6)
        
        # Precompute normalized keywords for faster matching
        self._build_keyword_index()
        
    def _load_taxonomy(self) -> Dict[str, Any]:
        """Load taxonomy configuration from JSON file"""
        try:
            with open(self.taxonomy_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"Loaded taxonomy with {data.get('metadata', {}).get('total_categories', 0)} categories")
                return data
        except FileNotFoundError:
            print(f"Warning: Taxonomy file not found at {self.taxonomy_path}")
            return {"categories": {}, "metadata": {"fallback_category": "General"}}
        except json.JSONDecodeError as e:
            print(f"Error parsing taxonomy JSON: {e}")
            return {"categories": {}, "metadata": {"fallback_category": "General"}}
    
    def _build_keyword_index(self):
        """Build normalized keyword index for efficient matching"""
        self.keyword_index = {}
        
        for category_name, category_data in self.categories.items():
            subcategories = category_data.get("subcategories", {})
            
            for subcategory_name, subcategory_data in subcategories.items():
                keywords = subcategory_data.get("keywords", [])
                
                for keyword in keywords:
                    # Normalize keyword for matching
                    normalized_keyword = self._normalize_text(keyword)
                    
                    if normalized_keyword not in self.keyword_index:
                        self.keyword_index[normalized_keyword] = []
                    
                    self.keyword_index[normalized_keyword].append({
                        "category": category_name,
                        "subcategory": subcategory_name,
                        "original_keyword": keyword
                    })
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for keyword matching"""
        # Convert to lowercase and remove extra whitespace
        text = text.lower().strip()
        # Remove accents and special characters for better matching
        text = re.sub(r'[áàäâ]', 'a', text)
        text = re.sub(r'[éèëê]', 'e', text)
        text = re.sub(r'[íìïî]', 'i', text)
        text = re.sub(r'[óòöô]', 'o', text)
        text = re.sub(r'[úùüû]', 'u', text)
        text = re.sub(r'[ñ]', 'n', text)
        text = re.sub(r'[ç]', 'c', text)
        
        # Handle common Spanish word variations for better matching
        # Economic variations
        text = re.sub(r'\beconomico\b', 'economia', text)
        text = re.sub(r'\beconomica\b', 'economia', text)
        text = re.sub(r'\beconomicos\b', 'economia', text)
        text = re.sub(r'\beconomicas\b', 'economia', text)
        
        # Security variations
        text = re.sub(r'\bsegura\b', 'seguridad', text)
        text = re.sub(r'\bseguro\b', 'seguridad', text)
        text = re.sub(r'\bseguros\b', 'seguridad', text)
        text = re.sub(r'\bseguras\b', 'seguridad', text)
        
        # Education variations  
        text = re.sub(r'\beducacional\b', 'educacion', text)
        text = re.sub(r'\beducacionales\b', 'educacion', text)
        text = re.sub(r'\beducativo\b', 'educacion', text)
        text = re.sub(r'\beducativa\b', 'educacion', text)
        text = re.sub(r'\beducativos\b', 'educacion', text)
        text = re.sub(r'\beducativas\b', 'educacion', text)
        
        return text
    
    def classify_from_headers(self, headers: Dict[str, str]) -> TaxonomyClassification:
        """
        Classify content based on document headers
        
        Args:
            headers: Dictionary of header levels and text
            
        Returns:
            TaxonomyClassification with category, subcategory, and confidence
        """
        # Combine all header text for analysis
        header_text = " ".join(headers.values()) if headers else ""
        return self.classify_from_text(header_text, boost_factor=1.5)
    
    def classify_from_content(self, content: str, max_words: int = 100) -> TaxonomyClassification:
        """
        Classify content based on text content
        
        Args:
            content: Text content to classify
            max_words: Maximum number of words to analyze for performance
            
        Returns:
            TaxonomyClassification with category, subcategory, and confidence
        """
        # Limit content length for performance
        words = content.split()[:max_words]
        limited_content = " ".join(words)
        
        return self.classify_from_text(limited_content)
    
    def classify_from_text(self, text: str, boost_factor: float = 1.0, fallback_to_category_only: bool = True) -> TaxonomyClassification:
        """
        Classify text using keyword matching
        
        Args:
            text: Text to classify
            boost_factor: Factor to boost confidence scores (useful for headers)
            
        Returns:
            TaxonomyClassification with results
        """
        if not text.strip():
            return TaxonomyClassification(
                category=self.metadata.get("fallback_category", "General"),
                confidence=0.0
            )
        
        # Normalize input text
        normalized_text = self._normalize_text(text)
        
        # Score tracking
        category_scores = {}
        subcategory_scores = {}
        matched_keywords = []
        
        # Check each keyword in our index
        for keyword, matches in self.keyword_index.items():
            if keyword in normalized_text:
                # Calculate keyword score based on specificity
                keyword_score = len(keyword.split()) * boost_factor
                
                for match in matches:
                    category = match["category"]
                    subcategory = match["subcategory"]
                    original_keyword = match["original_keyword"]
                    
                    # Update category scores
                    if category not in category_scores:
                        category_scores[category] = 0
                    category_scores[category] += keyword_score
                    
                    # Update subcategory scores
                    subcategory_key = f"{category}>{subcategory}"
                    if subcategory_key not in subcategory_scores:
                        subcategory_scores[subcategory_key] = 0
                    subcategory_scores[subcategory_key] += keyword_score
                    
                    matched_keywords.append(original_keyword)
        
        # Find best matches
        if not category_scores:
            return TaxonomyClassification(
                category=self.metadata.get("fallback_category", "General"),
                confidence=0.0
            )
        
        # Get top category
        top_category = max(category_scores.items(), key=lambda x: x[1])
        category_name, category_score = top_category
        
        # Get top subcategory for this category
        category_subcategories = {
            k: v for k, v in subcategory_scores.items()
            if k.startswith(f"{category_name}>")
        }
        
        subcategory_name = None
        subcategory_score = 0
        
        if category_subcategories:
            top_subcategory = max(category_subcategories.items(), key=lambda x: x[1])
            subcategory_key, subcategory_score = top_subcategory
            subcategory_name = subcategory_key.split(">", 1)[1]
        
        # Enhanced confidence calculation - less dependent on text length
        total_words = len(text.split())
        unique_keywords = len(set(matched_keywords))
        
        # Base confidence from keyword scoring with improved normalization
        # Reduced text length dependency from 0.05 to 0.02
        base_confidence = min(subcategory_score / max(total_words * 0.02, 1), 1.0)
        
        # Enhanced minimum confidence boost for any keyword match
        if subcategory_score > 0:
            base_confidence = max(base_confidence, 0.25)  # Increased from 0.2 to 0.25
        
        # Progressive confidence boost based on multiple keyword matches
        if unique_keywords > 1:
            # More keywords = higher confidence
            keyword_boost = min(1.0 + (unique_keywords - 1) * 0.15, 1.6)
            base_confidence *= keyword_boost
        
        # Additional boost for very specific (long) keywords
        long_keyword_count = sum(1 for kw in matched_keywords if len(kw.split()) >= 2)
        if long_keyword_count > 0:
            base_confidence *= 1.1
        
        confidence = min(base_confidence, 1.0)
        
        # Enhanced classification with cascaded fallback
        result = TaxonomyClassification(
            category=category_name,
            subcategory=subcategory_name if confidence >= self.confidence_threshold else None,
            confidence=confidence,
            matched_keywords=list(set(matched_keywords))
        )
        
        # If no subcategory assigned and fallback enabled, try category-only classification
        if not result.subcategory and fallback_to_category_only and confidence > 0.15:
            # Assign subcategory with lower confidence if we have strong category match
            if subcategory_name and confidence > 0.15:
                result.subcategory = subcategory_name
                result.taxonomy_path = f"{category_name} > {subcategory_name}"
        
        return result
    
    def get_category_info(self, category: str) -> Dict[str, Any]:
        """Get information about a specific category"""
        return self.categories.get(category, {})
    
    def get_subcategory_info(self, category: str, subcategory: str) -> Dict[str, Any]:
        """Get information about a specific subcategory"""
        category_data = self.categories.get(category, {})
        subcategories = category_data.get("subcategories", {})
        return subcategories.get(subcategory, {})
    
    def list_categories(self) -> List[str]:
        """List all available categories"""
        return list(self.categories.keys())
    
    def list_subcategories(self, category: str) -> List[str]:
        """List all subcategories for a given category"""
        category_data = self.categories.get(category, {})
        subcategories = category_data.get("subcategories", {})
        return list(subcategories.keys())
    
    def get_taxonomy_stats(self) -> Dict[str, Any]:
        """Get statistics about the taxonomy"""
        total_categories = len(self.categories)
        total_subcategories = sum(
            len(cat_data.get("subcategories", {}))
            for cat_data in self.categories.values()
        )
        total_keywords = sum(
            len(subcat_data.get("keywords", []))
            for cat_data in self.categories.values()
            for subcat_data in cat_data.get("subcategories", {}).values()
        )
        
        return {
            "total_categories": total_categories,
            "total_subcategories": total_subcategories,
            "total_keywords": total_keywords,
            "confidence_threshold": self.confidence_threshold,
            "taxonomy_version": self.taxonomy_data.get("version", "unknown")
        }
    
    def generate_tags_from_classification(self, classification: TaxonomyClassification) -> List[str]:
        """
        Generate strategic RAG-optimized tags from classification result
        
        Args:
            classification: Result from classify_from_* methods
            
        Returns:
            List of strategic tags for hybrid search and Qdrant filtering
        """
        tags = []
        
        if classification.category:
            # Add category as primary tag
            category_tag = self._normalize_text(classification.category)
            tags.append(category_tag)
            
            # Add subcategory if available
            if classification.subcategory:
                subcategory_tag = self._normalize_text(classification.subcategory)
                tags.append(subcategory_tag)
                
                # Add strategic keywords from matched keywords
                strategic_keywords = self._select_strategic_keywords(classification.matched_keywords)
                tags.extend(strategic_keywords)
                
                # Add domain-specific tags based on category
                domain_tags = self._generate_domain_specific_tags(classification.category, classification.subcategory)
                tags.extend(domain_tags)
        
        return list(set(tags))  # Remove duplicates and return unique tags
    
    def _select_strategic_keywords(self, matched_keywords: List[str]) -> List[str]:
        """
        Select strategic keywords for tags that are most useful for RAG queries
        
        Args:
            matched_keywords: List of matched keywords from classification
            
        Returns:
            List of strategic keywords suitable for hybrid search
        """
        strategic = []
        
        # Priority order: specific terms > general terms
        # Add specific multi-word keywords first (these are usually more valuable)
        specific_keywords = [kw for kw in matched_keywords if len(kw.split()) >= 2]
        strategic.extend(specific_keywords[:2])  # Max 2 specific keywords
        
        # Add single-word strategic keywords (avoid too generic ones)
        strategic_single = [kw for kw in matched_keywords if len(kw.split()) == 1 and len(kw) > 3]
        strategic.extend(strategic_single[:3])  # Max 3 single-word keywords
        
        return [self._normalize_text(kw) for kw in strategic]
    
    def _generate_domain_specific_tags(self, category: str, subcategory: str) -> List[str]:
        """
        Generate domain-specific tags based on category and subcategory
        These help with PDR question mapping and citizen query patterns
        
        Args:
            category: Main category
            subcategory: Subcategory
            
        Returns:
            List of domain-specific tags
        """
        domain_tags = []
        
        # Map categories to citizen-friendly terms for better query matching
        category_mapping = {
            "Pensiones": ["jubilacion", "retiro", "vejez"],
            "Salud": ["medico", "hospital", "atencion"],
            "Educacion": ["colegio", "universidad", "estudiar"],
            "Trabajo": ["empleo", "sueldo", "laboral"],
            "Economia": ["plata", "dinero", "costo"],
            "Seguridad": ["delincuencia", "crimen", "policia"],
            "Vivienda": ["casa", "hogar", "habitacion"],
            "Medioambiente": ["agua", "aire", "naturaleza"],
            "Regiones": ["provincia", "regional", "local"],
            "Institucionalidad": ["gobierno", "estado", "politica"]
        }
        
        if category in category_mapping:
            domain_tags.extend(category_mapping[category][:2])  # Max 2 per category
        
        return domain_tags
    
    def classify_with_cascaded_fallback(self, headers: Dict[str, str], content: str) -> TaxonomyClassification:
        """
        Enhanced cascaded classification that tries multiple strategies
        
        This method implements a hierarchical approach:
        1. Headers-based classification (high boost)
        2. Content-based classification
        3. Combined headers+content classification
        4. Relaxed threshold classification
        
        Args:
            headers: Document headers for classification
            content: Text content for classification
            
        Returns:
            Best TaxonomyClassification found across all strategies
        """
        strategies = []
        
        # Strategy 1: Headers-based (if available)
        if headers:
            header_result = self.classify_from_headers(headers)
            if header_result.confidence > 0.2:  # Headers are usually reliable
                strategies.append(('headers', header_result))
        
        # Strategy 2: Content-based
        content_result = self.classify_from_content(content)
        if content_result.confidence > 0.15:
            strategies.append(('content', content_result))
        
        # Strategy 3: Combined headers + content (if both available)
        if headers and content:
            combined_text = " ".join(headers.values()) + " " + content
            combined_result = self.classify_from_text(combined_text[:200], boost_factor=1.2)
            if combined_result.confidence > 0.15:
                strategies.append(('combined', combined_result))
        
        # Strategy 4: Relaxed threshold (last resort)
        if not strategies:
            # Try with lower confidence threshold for any content
            text_to_classify = content if content else " ".join(headers.values()) if headers else ""
            if text_to_classify:
                relaxed_result = self.classify_from_text(text_to_classify, fallback_to_category_only=True)
                if relaxed_result.confidence > 0.1:  # Very low threshold
                    strategies.append(('relaxed', relaxed_result))
        
        # Select best strategy result
        if not strategies:
            return TaxonomyClassification(
                category=self.metadata.get("fallback_category", "General"),
                confidence=0.0
            )
        
        # Prefer strategy with highest confidence, but prioritize headers if close
        best_strategy = max(strategies, key=lambda x: x[1].confidence + (0.1 if x[0] == 'headers' else 0))
        best_result = best_strategy[1]
        
        # Anti-General validation: avoid Generic classifications when specific ones are possible
        if best_result.category == "General" and len(strategies) > 1:
            # Try to find a non-General alternative with reasonable confidence
            non_general_strategies = [s for s in strategies if s[1].category != "General"]
            if non_general_strategies:
                # Pick the best non-General alternative if confidence is reasonable
                alt_strategy = max(non_general_strategies, key=lambda x: x[1].confidence)
                if alt_strategy[1].confidence > 0.12:  # Reasonable minimum for specific classification
                    best_result = alt_strategy[1]
        
        return best_result
    
    def validate_and_rebalance_classification(self, classification: TaxonomyClassification, content: str) -> TaxonomyClassification:
        """
        Validate classification and suggest rebalancing for PDR alignment
        
        This method helps rebalance categories by detecting content that might
        belong to under-represented categories like Pensiones, Trabajo, Regiones
        
        Args:
            classification: Initial classification result
            content: Text content for additional analysis
            
        Returns:
            Potentially rebalanced classification for better PDR coverage
        """
        # Skip if we already have high confidence specific classification
        if classification.confidence > 0.6 and classification.subcategory:
            return classification
        
        # Rebalancing rules for under-represented PDR categories
        content_lower = content.lower()
        
        # Check for Pensiones content misclassified as Economía or other
        pension_indicators = [
            "jubilación", "pensión", "afp", "previsional", "cotización", 
            "sistema pensiones", "reformar sistema", "vejez", "retiro"
        ]
        if any(indicator in content_lower for indicator in pension_indicators):
            pension_classification = self.classify_from_text(content, boost_factor=1.5)
            if pension_classification.category == "Pensiones" and pension_classification.confidence > 0.2:
                return pension_classification
        
        # Check for Trabajo content misclassified as other categories  
        trabajo_indicators = [
            "empleo", "trabajadores", "trabajo", "emprendedores", "desempleo",
            "salario", "sueldo", "generar empleos", "oportunidades"
        ]
        if any(indicator in content_lower for indicator in trabajo_indicators):
            trabajo_classification = self.classify_from_text(content, boost_factor=1.4)
            if trabajo_classification.category == "Trabajo" and trabajo_classification.confidence > 0.2:
                return trabajo_classification
                
        # Check for Regiones content (often misclassified)
        regiones_indicators = [
            "región", "regional", "territorio", "descentralización", 
            "municipio", "gobierno regional", "desarrollo regional"
        ]
        if any(indicator in content_lower for indicator in regiones_indicators):
            regiones_classification = self.classify_from_text(content, boost_factor=1.6)  # Higher boost for under-represented
            if regiones_classification.category == "Regiones" and regiones_classification.confidence > 0.15:
                return regiones_classification
        
        # Return original classification if no rebalancing needed
        return classification


def create_default_classifier() -> TaxonomyClassifier:
    """Create a default taxonomy classifier instance"""
    return TaxonomyClassifier()


# Convenience functions for easy import
def classify_headers(headers: Dict[str, str]) -> TaxonomyClassification:
    """Convenience function to classify headers"""
    classifier = create_default_classifier()
    return classifier.classify_from_headers(headers)


def classify_content(content: str) -> TaxonomyClassification:
    """Convenience function to classify content"""
    classifier = create_default_classifier()
    return classifier.classify_from_content(content)


def classify_text(text: str) -> TaxonomyClassification:
    """Convenience function to classify any text"""
    classifier = create_default_classifier()
    return classifier.classify_from_text(text)