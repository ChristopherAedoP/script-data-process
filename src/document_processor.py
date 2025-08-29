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
    """Metadata for document chunks"""
    source_file: str
    chunk_id: str
    chunk_index: int
    headers: Dict[str, str]
    char_count: int
    token_count: Optional[int] = None
    # Political document fields
    candidate: Optional[str] = None
    party: Optional[str] = None
    page_number: Optional[int] = None
    topic_category: Optional[str] = None
    proposal_type: Optional[str] = None
    section_hierarchy: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


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

    def extract_candidate_info_from_filename(self, filename: str) -> tuple[Optional[str], Optional[str]]:
        """Extract candidate info dynamically from filename"""
        # Extract from filename pattern like "Programa_Jeannette_Jara.md" or "Programa_Jose_Antonio_Kast_R.md"
        name_part = Path(filename).stem.replace('Programa_', '').replace('_', ' ')
        
        # Clean up common filename patterns
        candidate = name_part.strip()
        if not candidate:
            return None, None
        
        # Return candidate name directly - no hardcoded mapping required
        # Party information can be extracted from document content if needed
        return candidate, None

    def classify_topic_from_headers(self, headers: Dict[str, str]) -> str:
        """Classify topic category from headers"""
        header_text = ' '.join(headers.values()).lower()
        
        topic_keywords = {
            'pensiones': ['pensión', 'pension', 'previsional', 'afp', 'jubilación', 'adulto mayor'],
            'salud': ['salud', 'hospital', 'médico', 'medicina', 'enfermedad', 'tratamiento'],
            'educación': ['educación', 'educacion', 'escuela', 'universidad', 'estudiante', 'profesor'],
            'economía': ['economía', 'economia', 'económico', 'economico', 'empleo', 'trabajo', 'inflación'],
            'seguridad': ['seguridad', 'delincuencia', 'crimen', 'policía', 'policia', 'orden público'],
            'vivienda': ['vivienda', 'casa', 'hogar', 'habitacional', 'construcción'],
            'transporte': ['transporte', 'metro', 'micro', 'locomoción', 'tránsito', 'vialidad'],
            'medio_ambiente': ['medio ambiente', 'medioambiente', 'ecológico', 'sustentable', 'verde'],
        }
        
        for category, keywords in topic_keywords.items():
            for keyword in keywords:
                if keyword in header_text:
                    return category
        
        return 'general'

    def detect_proposal_type(self, content: str) -> str:
        """Detect the type of proposal from content"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['propongo', 'propuesta', 'implementar', 'crear', 'establecer']):
            return 'propuesta_especifica'
        elif any(word in content_lower for word in ['meta', 'objetivo', '%', 'millones', 'aumentar en']):
            return 'meta_cuantitativa'
        elif any(word in content_lower for word in ['problema', 'situación', 'diagnóstico', 'actualmente']):
            return 'diagnostico'
        else:
            return 'descripcion_general'

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
                
                # Split page content by headers first
                page_document = Document(
                    page_content=page.content,
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
                        # Classify topic and proposal type
                        topic = self.classify_topic_from_headers(headers)
                        proposal_type = self.detect_proposal_type(sub_chunk.page_content)
                        
                        # Build section hierarchy from headers
                        section_hierarchy = [v for v in headers.values() if v] if headers else []
                        
                        # Update metadata with political fields
                        sub_chunk.metadata.update({
                            'page_number': page.page_number,
                            'candidate': candidate,
                            'party': party,
                            'topic_category': topic,
                            'proposal_type': proposal_type,
                            'section_hierarchy': section_hierarchy
                        })
                        
                        final_chunks.append(sub_chunk)
            
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
            chunk_doc = Document(
                page_content=chunk.page_content,
                metadata={
                    **document.metadata,
                    **chunk.metadata,
                    'candidate': candidate,
                    'party': party
                }
            )
            
            sub_chunks = self.text_splitter.split_documents([chunk_doc])
            final_chunks.extend(sub_chunks)
        
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
        
        return ChunkMetadata(
            source_file=source_file,
            chunk_id=chunk_id,
            chunk_index=index,
            headers=headers,
            char_count=len(chunk.page_content),
            # Political fields from chunk metadata
            candidate=chunk.metadata.get("candidate"),
            party=chunk.metadata.get("party"),
            page_number=chunk.metadata.get("page_number"),
            topic_category=chunk.metadata.get("topic_category"),
            proposal_type=chunk.metadata.get("proposal_type"),
            section_hierarchy=chunk.metadata.get("section_hierarchy"),
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