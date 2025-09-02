"""
Document processing module for RAG MVP
Handles Markdown files, chunking, and text preprocessing
"""
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter, 
    RecursiveCharacterTextSplitter
)
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.schema import Document

from .config import config
from .taxonomy import TaxonomyClassifier, TaxonomyClassification


@dataclass
class PageContent:
    """Represents content within a specific page"""
    page_number: int
    content: str = ""
    headers: Dict[str, str] = None
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {}


@dataclass
class ChunkMetadata:
    """Optimized metadata for document chunks - web RAG focused"""
    source_file: str
    chunk_id: str
    chunk_index: int
    # Political document fields
    candidate: Optional[str] = None
    party: Optional[str] = None
    page_number: Optional[int] = None
    topic_category: Optional[str] = None
    proposal_type: Optional[str] = None
    # Enhanced taxonomy fields
    sub_category: Optional[str] = None
    taxonomy_path: Optional[str] = None
    tags: Optional[List[str]] = None
    # Conditional fields (only if not empty)
    headers: Optional[Dict[str, str]] = None
    section_hierarchy: Optional[List[str]] = None
    # Embedding metadata
    embedding_metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Initialize default values for mutable fields"""
        if self.tags is None:
            self.tags = []
        if self.embedding_metadata is None:
            from datetime import date
            self.embedding_metadata = {
                "language": "es",
                "model": "text-embedding-3-small",
                "dimensions": 1536,
                "generated_date": date.today().strftime("%Y-%m-%d")
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with conditional fields"""
        result = asdict(self)
        # Remove empty headers and section_hierarchy
        if not result.get('headers'):
            result.pop('headers', None)
        if not result.get('section_hierarchy'):
            result.pop('section_hierarchy', None)
        return result


class DocumentProcessor:
    """Processes documents for RAG pipeline"""
    
    def __init__(self):
        self.markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=config.MARKDOWN_HEADERS,
            strip_headers=False
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            length_function=len,
            add_start_index=True,
        )
        
        # Initialize taxonomy classifier
        self.taxonomy_classifier = TaxonomyClassifier()
        # print(f"Loaded taxonomy with {len(self.taxonomy_classifier.list_categories())} categories")
        
    def extract_pages_from_content(self, content: str) -> List[PageContent]:
        """Extract pages from markdown content using page markers"""
        import re
        
        pages = []
        lines = content.split('\n')
        current_page = None
        
        for line in lines:
            # Look for start page marker
            start_match = re.search(r'\[START OF PAGE:\s*(\d+)\]', line)
            if start_match:
                page_num = int(start_match.group(1))
                current_page = PageContent(page_number=page_num)
                continue
            
            # Look for end page marker
            end_match = re.search(r'\[END OF PAGE:\s*(\d+)\]', line)
            if end_match and current_page:
                pages.append(current_page)
                current_page = None
                continue
            
            # Add content to current page
            if current_page is not None:
                if current_page.content:
                    current_page.content += '\n'
                current_page.content += line
        
        # Handle case where document doesn't end with page marker
        if current_page:
            pages.append(current_page)
        
        return pages

    def extract_candidate_info_from_filename(self, filename: str) -> tuple[Optional[str], str]:
        """Extract candidate info dynamically from filename"""
        # Extract from filename pattern like "Programa_Jeannette_Jara.md" or "Programa_Jose_Antonio_Kast_R.md"
        name_part = Path(filename).stem.replace('Programa_', '').replace('_', ' ')
        
        # Clean up common filename patterns
        candidate = name_part.strip()
        if not candidate:
            return None, "Independiente"
        
        # Basic party mapping for known candidates (can be expanded)
        party_mapping = {
            "Jose Antonio Kast": "Partido Republicano",
            "Evelyn Matthei": "Unión Demócrata Independiente (UDI)",
            "Jeannette Jara": "Partido Comunista de Chile",
            "Johannes Kaiser": "Partido Nacional Libertario (PNL)",
            "Harold Mayne-Nicholls": "Independiente",
            "Eduardo Artés": "Partido Comunista Chileno (Acción Proletaria) - no partido legalizado en Servel",
            "Franco Parisi": "Partido de la Gente"
        }
        
        # Try to find party, default to "Independiente"
        party = party_mapping.get(candidate, "Independiente")
        
        return candidate, party

    def classify_with_taxonomy(self, headers: Dict[str, str], content: str) -> TaxonomyClassification:
        """
        Enhanced taxonomy classification using cascaded fallback strategies
        
        Args:
            headers: Document headers for classification
            content: Text content for classification
            
        Returns:
            TaxonomyClassification with improved accuracy and coverage
        """
        # Use the new cascaded classification method for better results
        return self.taxonomy_classifier.classify_with_cascaded_fallback(headers, content)
    

    def merge_small_chunks(self, chunks: List[Document]) -> List[Document]:
        """
        Merge small chunks with adjacent ones to prevent fragmentation.
        Specifically handles cases like single-word titles or isolated numbers.
        """
        if not chunks:
            return chunks
            
        merged_chunks = []
        i = 0
        
        while i < len(chunks):
            current_chunk = chunks[i]
            current_content = current_chunk.page_content.strip()
            
            # Check if current chunk is too small (less than 50 characters)
            if len(current_content) < 50:
                # Try to merge with next chunk if available and from same page
                if (i + 1 < len(chunks) and 
                    current_chunk.metadata.get('page_number') == chunks[i + 1].metadata.get('page_number')):
                    
                    next_chunk = chunks[i + 1]
                    
                    # Merge current small chunk with next chunk
                    merged_content = current_content + "\n\n" + next_chunk.page_content
                    
                    # Create merged chunk with combined metadata
                    merged_chunk = Document(
                        page_content=merged_content,
                        metadata={
                            **current_chunk.metadata,
                            # Preserve headers from both chunks
                            **{k: v for k, v in next_chunk.metadata.items() if k.startswith('Header')}
                        }
                    )
                    
                    merged_chunks.append(merged_chunk)
                    i += 2  # Skip both chunks since they're merged
                    continue
                else:
                    # If it's the last chunk or different page, try merging with previous
                    if merged_chunks and current_chunk.metadata.get('page_number') == merged_chunks[-1].metadata.get('page_number'):
                        # Merge with previous chunk
                        prev_chunk = merged_chunks[-1]
                        merged_content = prev_chunk.page_content + "\n\n" + current_content
                        
                        merged_chunks[-1] = Document(
                            page_content=merged_content,
                            metadata={
                                **prev_chunk.metadata,
                                **{k: v for k, v in current_chunk.metadata.items() if k.startswith('Header')}
                            }
                        )
                        i += 1
                        continue
                    else:
                        # Can't merge, but keep small chunk as-is - important titles shouldn't be lost
                        merged_chunks.append(current_chunk)
                        i += 1
                        continue
            
            # Chunk is large enough, add it as-is
            merged_chunks.append(current_chunk)
            i += 1
        
        return merged_chunks

    def clean_markdown_content(self, content: str) -> str:
        """
        Clean Markdown formatting from content for better embeddings
        Removes visual formatting while preserving semantic content
        """
        import re
        
        if not content or not content.strip():
            return content
        
        cleaned = content
        
        # Remove Markdown headers (# ## ### #### ##### ######)
        cleaned = re.sub(r'^#{1,6}\s+', '', cleaned, flags=re.MULTILINE)
        
        # Remove bold and italic formatting
        cleaned = re.sub(r'\*\*([^*]+)\*\*', r'\1', cleaned)  # **bold** -> bold
        cleaned = re.sub(r'\*([^*]+)\*', r'\1', cleaned)      # *italic* -> italic
        cleaned = re.sub(r'__([^_]+)__', r'\1', cleaned)      # __bold__ -> bold
        cleaned = re.sub(r'_([^_]+)_', r'\1', cleaned)        # _italic_ -> italic
        
        # Remove links but preserve text [text](url) -> text
        cleaned = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', cleaned)
        
        # Remove inline code backticks
        cleaned = re.sub(r'`([^`]+)`', r'\1', cleaned)
        
        # Remove horizontal rules
        cleaned = re.sub(r'^[-*_]{3,}\s*$', '', cleaned, flags=re.MULTILINE)
        
        # Remove numbered emoji bullets (1️⃣ 2️⃣ 3️⃣ ... 9️⃣ 🔟)
        cleaned = re.sub(r'[0-9]️⃣\s*', '', cleaned)
        cleaned = re.sub(r'🔟\s*', '', cleaned)
        
        # Remove other common emojis and visual symbols
        cleaned = re.sub(r'[🎯🚀💡⚡🔥🌟✨💪👍🎉🏆📊📈📋🔔🎁💰]', '', cleaned)
        
        # Remove Unicode emoji ranges (comprehensive emoji removal)
        # Emoticons and symbols
        cleaned = re.sub(r'[\U0001F600-\U0001F64F]', '', cleaned)  # emoticons
        cleaned = re.sub(r'[\U0001F300-\U0001F5FF]', '', cleaned)  # symbols & pictographs
        cleaned = re.sub(r'[\U0001F680-\U0001F6FF]', '', cleaned)  # transport & map symbols
        cleaned = re.sub(r'[\U0001F700-\U0001F77F]', '', cleaned)  # alchemical symbols
        cleaned = re.sub(r'[\U0001F780-\U0001F7FF]', '', cleaned)  # geometric shapes extended
        cleaned = re.sub(r'[\U0001F800-\U0001F8FF]', '', cleaned)  # supplemental arrows
        cleaned = re.sub(r'[\U0001F900-\U0001F9FF]', '', cleaned)  # supplemental symbols
        cleaned = re.sub(r'[\U0001FA00-\U0001FA6F]', '', cleaned)  # chess symbols
        cleaned = re.sub(r'[\U0001FA70-\U0001FAFF]', '', cleaned)  # symbols and pictographs extended
        cleaned = re.sub(r'[\U00002702-\U000027B0]', '', cleaned)  # dingbats
        cleaned = re.sub(r'[\U000024C2-\U0001F251]', '', cleaned)  # enclosed characters
        
        # Remove list markers (- * +) but preserve content
        cleaned = re.sub(r'^[\s]*[-*+]\s+', '', cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r'^[\s]*\d+\.\s+', '', cleaned, flags=re.MULTILINE)
        
        # Remove bullet symbols and special markers
        cleaned = re.sub(r'[•◦▪▫■□▲►♦◆●○]', '', cleaned)
        
        # Normalize whitespace
        # Convert multiple line breaks to single spaces
        cleaned = re.sub(r'\n+', ' ', cleaned)
        # Remove extra spaces
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Remove leading/trailing whitespace
        cleaned = cleaned.strip()
        
        return cleaned

    def detect_proposal_type(self, content: str) -> str:
        """Detect the type of proposal from content - Enhanced for PDR questions"""
        content_lower = content.lower()
        
        # Keywords específicas para propuestas concretas (PDR P1-P30)
        propuesta_keywords = [
            # Verbos de acción
            'propongo', 'propuesta', 'implementar', 'implementaremos', 'crear', 'establecer',
            'realizaremos', 'haremos', 'llevaremos a cabo', 'pondremos en marcha',
            'impulsaremos', 'promoveremos', 'desarrollaremos',
            # Términos específicos de política
            'plan', 'programa', 'medida', 'reforma', 'cambio', 'nuevo sistema',
            'gobierno de emergencia', 'operativo', 'estrategia', 'iniciativa',
            # Específicos por área PDR
            'vamos a', 'nos comprometemos', 'trabajaremos', 'fomentaremos'
        ]
        
        # Keywords para metas cuantitativas (PDR necesita números específicos)
        cuantitativa_keywords = [
            # Números y porcentajes
            '%', 'porciento', 'por ciento', 'millones', 'miles', 'billones',
            # Verbos cuantitativos
            'aumentar', 'reducir', 'disminuir', 'incrementar', 'alcanzar',
            'aumentar en', 'reducir en', 'duplicar', 'triplicar',
            # Términos de medición
            'meta', 'objetivo', 'cifra', 'número', 'cantidad',
            'uno de cada', 'más de', 'menos de', 'hasta', 'desde',
            # Específicos PDR
            '2.7 millones', 'lista de espera', 'pacientes', 'especialistas',
            'días', 'horas', 'años', 'meses'
        ]
        
        # Keywords para diagnósticos (PDR necesita identificar problemas)
        diagnostico_keywords = [
            # Términos de problema
            'problema', 'problemas', 'situación', 'diagnóstico', 'crisis',
            'dificultad', 'desafío', 'obstáculo', 'barrera',
            # Estado actual
            'actualmente', 'hoy', 'en la actualidad', 'la realidad',
            'estado actual', 'situación actual',
            # Términos críticos PDR
            'emergencia', 'urgencia', 'crítico', 'grave', 'alarmante',
            'insatisfacción', 'déficit', 'escasez', 'falta', 'carencia',
            # Específicos por área
            'estancamiento', 'decadencia', 'deterioro', 'crisis de'
        ]
        
        # Clasificación por prioridad
        if any(word in content_lower for word in propuesta_keywords):
            return 'propuesta_especifica'
        elif any(word in content_lower for word in cuantitativa_keywords):
            return 'meta_cuantitativa'  
        elif any(word in content_lower for word in diagnostico_keywords):
            return 'diagnostico'
        else:
            return 'descripcion_general'

    def validate_taxonomy_proposal_coherence(self, content: str, taxonomy_path: str, initial_proposal_type: str) -> str:
        """Validate and adjust proposal_type based on taxonomy for PDR coherence"""
        if not taxonomy_path:
            return initial_proposal_type
            
        content_lower = content.lower()
        category = taxonomy_path.split(' > ')[0] if ' > ' in taxonomy_path else taxonomy_path
        
        # Reglas específicas de coherencia basadas en las 30 preguntas PDR
        coherence_rules = {
            'Pensiones': {
                'propuesta_triggers': ['reforma', 'cambio', 'nuevo sistema', 'propongo', 'implementar'],
                'cuantitativa_triggers': ['aumentar', 'reducir', '%', 'millones', 'pensión básica'],
                'diagnostico_triggers': ['problema', 'crisis', 'situación actual', 'déficit']
            },
            'Salud': {
                'propuesta_triggers': ['crear', 'establecer', 'plan', 'programa', 'implementar', 'nuevo hospital'],
                'cuantitativa_triggers': ['2.7 millones', 'lista de espera', 'reducir', 'aumentar', '%', 'pacientes', 'especialistas'],
                'diagnostico_triggers': ['crisis', 'problema', 'insatisfacción', 'alarmante', 'déficit']
            },
            'Seguridad': {
                'propuesta_triggers': ['operativo', 'plan', 'medida', 'implementar', 'combatir', 'enfrentar'],
                'cuantitativa_triggers': ['reducir', '%', 'aumentar', 'millones', 'homicidios'],
                'diagnostico_triggers': ['emergencia', 'crisis', 'problema', 'situación', 'inseguridad']
            },
            'Trabajo': {
                'propuesta_triggers': ['implementar', 'crear', 'establecer', 'plan', 'programa', 'incentivar'],
                'cuantitativa_triggers': ['salario mínimo', 'aumentar', 'reducir', '%', 'horas', 'jornada'],
                'diagnostico_triggers': ['problema', 'informalidad', 'desempleo', 'crisis']
            },
            'Economía': {
                'propuesta_triggers': ['plan', 'política', 'implementar', 'medida', 'estrategia'],
                'cuantitativa_triggers': ['crecer', '%', 'inflación', 'reducir', 'aumentar', 'millones'],
                'diagnostico_triggers': ['crisis', 'estancamiento', 'problema', 'emergencia económica']
            },
            'Vivienda': {
                'propuesta_triggers': ['plan', 'programa', 'crear', 'construir', 'implementar'],
                'cuantitativa_triggers': ['déficit', 'millones', 'reducir', 'aumentar', '%', 'viviendas'],
                'diagnostico_triggers': ['crisis', 'problema', 'déficit habitacional', 'campamentos']
            }
        }
        
        # Si tenemos reglas para esta categoría
        if category in coherence_rules:
            rules = coherence_rules[category]
            
            # Si está clasificado como descripcion_general pero debería ser más específico
            if initial_proposal_type == 'descripcion_general':
                # Verificar si debería ser propuesta específica
                if any(trigger in content_lower for trigger in rules['propuesta_triggers']):
                    return 'propuesta_especifica'
                # Verificar si debería ser meta cuantitativa
                elif any(trigger in content_lower for trigger in rules['cuantitativa_triggers']):
                    return 'meta_cuantitativa'
                # Verificar si debería ser diagnóstico
                elif any(trigger in content_lower for trigger in rules['diagnostico_triggers']):
                    return 'diagnostico'
        
        return initial_proposal_type

    def load_documents(self, documents_path: str) -> List[Document]:
        """Load all markdown files from directory"""
        try:
            loader = DirectoryLoader(
                documents_path,
                glob="**/*.md",
                loader_cls=TextLoader,
                loader_kwargs={"encoding": "utf-8"}
            )
            documents = loader.load()
            print(f"Loaded {len(documents)} documents from {documents_path}")
            return documents
        except Exception as e:
            print(f"Error loading documents: {e}")
            return []
    
    def process_markdown_document(self, document: Document) -> List[Document]:
        """Process a single markdown document with page-aware chunking"""
        try:
            # Extract candidate info from filename
            source_file = document.metadata.get('source', '')
            candidate, party = self.extract_candidate_info_from_filename(source_file)
            
            # Extract pages from document content
            pages = self.extract_pages_from_content(document.page_content)
            
            if not pages:
                # Fallback to original method if no pages found
                return self._process_without_pages(document)
            
            final_chunks = []
            
            # Process each page separately
            for page in pages:
                if not page.content.strip():
                    continue
                
                # Clean content first to remove Markdown formatting for better embeddings
                cleaned_content = self.clean_markdown_content(page.content)
                
                # Split page content by headers first
                page_document = Document(
                    page_content=page.content,  # Keep original for metadata extraction
                    metadata=document.metadata
                )
                
                md_chunks = self.markdown_splitter.split_text(page.content)
                
                # Process each chunk within the page
                for chunk in md_chunks:
                    # Extract headers for this chunk
                    headers = chunk.metadata if hasattr(chunk, 'metadata') else {}
                    
                    # Create document for this chunk
                    chunk_doc = Document(
                        page_content=chunk.page_content,
                        metadata={
                            **document.metadata,
                            **headers,
                            'page_number': page.page_number,
                            'candidate': candidate,
                            'party': party
                        }
                    )
                    
                    # Apply size-based splitting within page boundaries
                    # But ensure chunks don't cross page boundaries
                    sub_chunks = self.text_splitter.split_documents([chunk_doc])
                    
                    # Add political metadata to each sub-chunk
                    for sub_chunk in sub_chunks:
                        # Clean the content for embeddings (remove Markdown formatting)
                        cleaned_content = self.clean_markdown_content(sub_chunk.page_content)
                        # Update the sub-chunk with cleaned content
                        sub_chunk.page_content = cleaned_content
                        
                        # Use new taxonomy classification (on original content for better header/structure recognition)
                        taxonomy_result = self.classify_with_taxonomy(headers, chunk.page_content if hasattr(chunk, 'page_content') else cleaned_content)
                        
                        # Classify proposal type with coherence validation
                        initial_proposal_type = self.detect_proposal_type(sub_chunk.page_content)
                        proposal_type = self.validate_taxonomy_proposal_coherence(
                            sub_chunk.page_content, 
                            taxonomy_result.taxonomy_path, 
                            initial_proposal_type
                        )
                        
                        # Build section hierarchy from headers
                        section_hierarchy = [v for v in headers.values() if v] if headers else []
                        
                        # Generate tags from taxonomy classification
                        tags = self.taxonomy_classifier.generate_tags_from_classification(taxonomy_result)
                        
                        # Update metadata with enhanced political fields
                        sub_chunk.metadata.update({
                            'page_number': page.page_number,
                            'candidate': candidate,
                            'party': party,
                            'topic_category': taxonomy_result.category,
                            'sub_category': taxonomy_result.subcategory,
                            'taxonomy_path': taxonomy_result.taxonomy_path,
                            'proposal_type': proposal_type,
                            'section_hierarchy': section_hierarchy,
                            'tags': tags,
                            'taxonomy_confidence': taxonomy_result.confidence,
                            'matched_keywords': taxonomy_result.matched_keywords
                        })
                        
                        final_chunks.append(sub_chunk)
            
            # Apply chunk merging to reduce fragmentation 
            final_chunks = self.merge_small_chunks(final_chunks)
            
            return final_chunks
            
        except Exception as e:
            print(f"Error processing document {document.metadata.get('source', 'unknown')}: {e}")
            # Fallback to basic text splitting
            return self.text_splitter.split_documents([document])

    def _process_without_pages(self, document: Document) -> List[Document]:
        """Fallback processing without page markers"""
        # Extract candidate info from filename
        source_file = document.metadata.get('source', '')
        candidate, party = self.extract_candidate_info_from_filename(source_file)
        
        # Use original chunking method
        md_chunks = self.markdown_splitter.split_text(document.page_content)
        
        final_chunks = []
        for chunk in md_chunks:
            # Clean content for embeddings
            cleaned_content = self.clean_markdown_content(chunk.page_content)
            
            chunk_doc = Document(
                page_content=cleaned_content,
                metadata={
                    **document.metadata,
                    **chunk.metadata,
                    'candidate': candidate,
                    'party': party
                }
            )
            
            sub_chunks = self.text_splitter.split_documents([chunk_doc])
            final_chunks.extend(sub_chunks)
        
        # Apply chunk merging to reduce fragmentation 
        final_chunks = self.merge_small_chunks(final_chunks)
        
        return final_chunks
    
    def generate_chunk_id(self, content: str, source: str, index: int) -> str:
        """Generate unique chunk ID"""
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        source_name = Path(source).stem
        return f"{source_name}_{index}_{content_hash}"
    
    def create_chunk_metadata(
        self, 
        chunk: Document, 
        index: int, 
        total_chunks: int
    ) -> ChunkMetadata:
        """Create metadata for a chunk with political information"""
        source_file = chunk.metadata.get("source", "unknown")
        chunk_id = self.generate_chunk_id(chunk.page_content, source_file, index)
        
        # Extract headers from metadata
        headers = {
            k: v for k, v in chunk.metadata.items() 
            if k.startswith("Header")
        }
        
        # Create embedding metadata
        from datetime import date
        embedding_metadata = {
            "language": "es",
            "model": "text-embedding-3-small",
            "dimensions": 1536,
            "generated_date": date.today().strftime("%Y-%m-%d")
        }
        
        # Simplify source_file to filename only
        source_filename = Path(source_file).name
        
        # Prepare conditional fields
        headers_data = headers if headers else None
        section_hierarchy_data = chunk.metadata.get("section_hierarchy")
        if section_hierarchy_data and not section_hierarchy_data:
            section_hierarchy_data = None
        
        return ChunkMetadata(
            source_file=source_filename,
            chunk_id=chunk_id,
            chunk_index=index,
            # Political fields from chunk metadata
            candidate=chunk.metadata.get("candidate"),
            party=chunk.metadata.get("party") or "Independiente",  # Ensure no null parties
            page_number=chunk.metadata.get("page_number"),
            topic_category=chunk.metadata.get("topic_category"),
            proposal_type=chunk.metadata.get("proposal_type"),
            # Enhanced taxonomy fields
            sub_category=chunk.metadata.get("sub_category"),
            taxonomy_path=chunk.metadata.get("taxonomy_path"),
            tags=chunk.metadata.get("tags", []),
            # Conditional fields
            headers=headers_data,
            section_hierarchy=section_hierarchy_data,
            # Embedding metadata
            embedding_metadata=embedding_metadata
        )
    
    def process_documents(self, documents_path: str) -> tuple[List[str], List[ChunkMetadata]]:
        """Process all documents and return texts and metadata"""
        documents = self.load_documents(documents_path)
        
        if not documents:
            return [], []
        
        all_chunks = []
        all_metadata = []
        
        print("Processing documents...")
        for doc in documents:
            chunks = self.process_markdown_document(doc)
            all_chunks.extend(chunks)
        
        print(f"Generated {len(all_chunks)} chunks from {len(documents)} documents")
        
        # Create texts and metadata
        texts = []
        for i, chunk in enumerate(all_chunks):
            texts.append(chunk.page_content)
            metadata = self.create_chunk_metadata(chunk, i, len(all_chunks))
            all_metadata.append(metadata)
        
        return texts, all_metadata
    
    def save_metadata(self, metadata: List[ChunkMetadata], path: str) -> None:
        """Save chunk metadata to JSON file"""
        try:
            metadata_dict = [meta.to_dict() for meta in metadata]
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(metadata_dict, f, indent=2, ensure_ascii=False)
            print(f"Saved metadata to {path}")
        except Exception as e:
            print(f"Error saving metadata: {e}")
    
    def load_metadata(self, path: str) -> List[ChunkMetadata]:
        """Load chunk metadata from JSON file"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return [ChunkMetadata(**item) for item in data]
        except Exception as e:
            print(f"Error loading metadata: {e}")
            return []