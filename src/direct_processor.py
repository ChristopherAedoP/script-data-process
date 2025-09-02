"""
Direct Processor - Streamlined file-by-file processing to Qdrant
Processes .md files individually for better data quality and coherence
"""
import os
import time
import uuid
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime

from qdrant_client import QdrantClient
from qdrant_client.http import models

from .config import config
from .document_processor import DocumentProcessor
from .embeddings import EmbeddingGenerator


class DirectProcessor:
    """Process documents directly to Qdrant by file for optimal data quality"""
    
    def __init__(self):
        # Initialize processors
        self.document_processor = DocumentProcessor()
        self.embedding_generator = EmbeddingGenerator()
        
        # Get validated API credentials
        credentials = config.get_api_credentials()
        
        # Initialize Qdrant client with robust connection settings
        self.qdrant_client = QdrantClient(
            url=credentials["qdrant_url"],
            api_key=credentials["qdrant_api_key"],
            timeout=60.0,  # 60 second timeout for operations
        )
        
        # Setup export directory for local files
        self.export_dir = Path("./data/direct_export")
        self.export_dir.mkdir(parents=True, exist_ok=True)
        
        # Session tracking and validation errors
        self.validation_errors = {}  # {candidate_name: []}
        self.start_time = None
        self.processed_candidates = []  # Track successfully processed candidates
    
    def ensure_collection(self, collection_name: str) -> bool:
        """Create Qdrant collection if it doesn't exist"""
        try:
            self.qdrant_client.get_collection(collection_name)
            print(f"OK: Collection '{collection_name}' already exists")
            return True
        except:
            try:
                self.qdrant_client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(
                        size=1536,  # text-embedding-3-small dimension
                        distance=models.Distance.COSINE
                    )
                )
                print(f"OK: Created collection '{collection_name}'")
                return True
            except Exception as e:
                print(f"ERROR: Failed to create collection: {e}")
                return False
    
    def _validate_chunk(self, text: str, chunk_index: int, source_file: str) -> Tuple[bool, Optional[str]]:
        """Validate chunk for OpenAI API compatibility"""
        
        # Check for empty or whitespace-only chunks
        if not text or not text.strip():
            return False, f"Empty or whitespace-only chunk at index {chunk_index}"
        
        # Check length limits (OpenAI has ~8192 token limit, roughly 30K characters)
        if len(text) > 30000:
            return False, f"Chunk too long ({len(text)} chars) at index {chunk_index}"
        
        # Check for null bytes or problematic control characters
        if '\x00' in text:
            return False, f"Null byte found in chunk at index {chunk_index}"
        
        # Only reject completely empty chunks 
        if len(text.strip()) < 1:
            return False, f"Empty chunk at index {chunk_index}"
        
        # Check for valid UTF-8 encoding
        try:
            text.encode('utf-8')
        except UnicodeEncodeError as e:
            return False, f"Unicode encoding error in chunk at index {chunk_index}: {e}"
        
        # Check for extremely repetitive content that might confuse embeddings
        words = text.split()
        if len(words) > 10:
            unique_words = len(set(words))
            if unique_words / len(words) < 0.1:  # Less than 10% unique words
                return False, f"Extremely repetitive content in chunk at index {chunk_index}"
        
        return True, None
    
    def _validate_chunks(self, texts: List[str], source_file: str, candidate_name: str) -> Tuple[List[str], List[int]]:
        """Validate all chunks and return valid chunks with their indices"""
        valid_texts = []
        valid_indices = []
        errors = []
        
        print(f"  Validating {len(texts)} chunks...")
        
        for i, text in enumerate(texts):
            is_valid, error_msg = self._validate_chunk(text, i, source_file)
            
            if is_valid:
                valid_texts.append(text)
                valid_indices.append(i)
            else:
                errors.append({
                    "chunk_index": i,
                    "error": error_msg,
                    "chunk_preview": text[:200] + "..." if len(text) > 200 else text,
                    "chunk_length": len(text)
                })
        
        # Store validation errors for this candidate
        if errors:
            if candidate_name not in self.validation_errors:
                self.validation_errors[candidate_name] = []
            self.validation_errors[candidate_name].extend(errors)
            
            print(f"  WARNING: {len(errors)} chunks failed validation")
            print(f"  Valid chunks: {len(valid_texts)}/{len(texts)}")
        else:
            print(f"  OK: All {len(texts)} chunks passed validation")
        
        return valid_texts, valid_indices
    
    def _write_candidate_files(self, candidate_name: str, points: List[Dict], log_entry: Dict, validation_errors: List[Dict] = None) -> None:
        """Write candidate files immediately after processing"""
        
        # Create candidate directory
        candidate_dir = self.export_dir / self._sanitize_filename(candidate_name)
        candidate_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Save candidate's processed data
        processed_data = {
            "candidate": candidate_name,
            "collection_name": "political_documents",
            "metadata": {
                "processing_date": datetime.now().isoformat(),
                "embedding_model": "text-embedding-3-small",
                "embedding_dimensions": 1536,
                "total_points": len(points),
                "export_date": datetime.now().strftime("%Y-%m-%d")
            },
            "points": points
        }
        
        processed_file = candidate_dir / "processed_data.json"
        with open(processed_file, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=2)
        
        # 2. Save candidate's processing log
        log_file = candidate_dir / "processing_log.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_entry, f, ensure_ascii=False, indent=2)
        
        # 3. Save validation errors if any
        if validation_errors:
            validation_errors_file = candidate_dir / "failed_chunks.json"
            validation_data = {
                "candidate": candidate_name,
                "validation_summary": {
                    "total_failed_chunks": len(validation_errors),
                    "validation_date": datetime.now().isoformat()
                },
                "failed_chunks": validation_errors
            }
            
            with open(validation_errors_file, 'w', encoding='utf-8') as f:
                json.dump(validation_data, f, ensure_ascii=False, indent=2)
        
        # 4. Create chunks preview for debugging
        if points:
            preview_file = candidate_dir / "chunks_preview.txt"
            with open(preview_file, 'w', encoding='utf-8') as f:
                f.write(f"Chunks preview for {candidate_name}\n")
                f.write(f"{'='*50}\n\n")
                
                for i, point in enumerate(points[:20]):  # First 20 chunks
                    content = point["payload"]["content"]
                    preview = content[:200] + "..." if len(content) > 200 else content
                    f.write(f"Chunk {i+1} (ID: {point['id']}):\n")
                    f.write(f"{preview}\n\n")
        
        print(f"  Files written: {candidate_dir.name}/")
    
    def _store_error_log(self, candidate_name: str, document_path: Path, error_msg: str, chunks_processed: int, embeddings_generated: int, start_time: float) -> None:
        """Store error log for a candidate and write files immediately"""
        processing_time = time.time() - start_time
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "file": document_path.name,
            "candidate": candidate_name,
            "status": "error",
            "error_message": error_msg,
            "chunks_processed": chunks_processed,
            "embeddings_generated": embeddings_generated,
            "points_uploaded": 0,
            "processing_time_seconds": round(processing_time, 2)
        }
        
        # Get validation errors for this candidate
        validation_errors = self.validation_errors.get(candidate_name, [])
        
        # Write candidate files immediately (even for errors)
        self._write_candidate_files(candidate_name, [], log_entry, validation_errors)

    def process_single_file(self, document_path: Path, collection_name: str) -> Dict[str, Any]:
        """Process a single document file to Qdrant"""
        start_time = time.time()
        
        print(f"\nProcessing: {document_path.name}")
        
        # Ensure collection exists
        if not self.ensure_collection(collection_name):
            error_msg = f"Failed to create/access collection {collection_name}"
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "file": document_path.name,
                "candidate": "Unknown",
                "status": "error",
                "error_message": error_msg,
                "chunks_processed": 0,
                "embeddings_generated": 0,
                "points_uploaded": 0,
                "processing_time_seconds": 0
            }
            self.processing_log.append(log_entry)
            return {"status": "error", "message": error_msg}
        
        # Load single document
        try:
            from langchain_community.document_loaders import TextLoader
            loader = TextLoader(str(document_path), encoding='utf-8')
            documents = loader.load()
            
            if not documents:
                return {"status": "error", "message": "No content found"}
            
            document = documents[0]
        except Exception as e:
            return {"status": "error", "message": f"Failed to load document: {e}"}
        
        # Process document into chunks
        try:
            chunks = self.document_processor.process_markdown_document(document)
            if not chunks:
                return {"status": "error", "message": "No chunks generated"}
            
            print(f"  Generated {len(chunks)} chunks")
        except Exception as e:
            return {"status": "error", "message": f"Chunking failed: {e}"}
        
        # Extract texts and create metadata
        texts = [chunk.page_content for chunk in chunks]
        metadata_list = []
        
        for i, chunk in enumerate(chunks):
            metadata = self.document_processor.create_chunk_metadata(chunk, i, len(chunks))
            metadata_list.append(metadata)
        
        candidate_name = metadata_list[0].candidate if metadata_list else "Unknown"
        print(f"  Candidate: {candidate_name}")
        
        # Validate chunks before embedding generation
        valid_texts, valid_indices = self._validate_chunks(texts, document_path.name, candidate_name)
        
        if not valid_texts:
            error_msg = f"No valid chunks after validation for {candidate_name}"
            self._store_error_log(candidate_name, document_path, error_msg, 0, 0, start_time)
            return {"status": "error", "message": error_msg}
        
        # Filter metadata to match valid chunks
        valid_metadata = [metadata_list[i] for i in valid_indices]
        
        # Generate embeddings only for valid chunks
        try:
            print(f"  Generating embeddings for {len(valid_texts)} valid chunks...")
            embeddings = self.embedding_generator.encode_texts(valid_texts, show_progress=False)
            print(f"  OK: Generated {len(embeddings)} embeddings")
        except Exception as e:
            return {"status": "error", "message": f"Embedding generation failed: {e}"}
        
        # Upload to Qdrant immediately
        try:
            print(f"  Uploading to Qdrant...")
            points = []
            
            for i, (text, embedding, meta) in enumerate(zip(valid_texts, embeddings, valid_metadata)):
                point = models.PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding.tolist() if hasattr(embedding, 'tolist') else embedding,
                    payload={
                        # Core metadata
                        "source_file": meta.source_file,
                        "chunk_id": meta.chunk_id,
                        "chunk_index": meta.chunk_index,
                        
                        # Political metadata - critical for PDR filtering
                        "candidate": meta.candidate,
                        "party": meta.party or "Independiente",
                        "page_number": meta.page_number,
                        "topic_category": meta.topic_category,
                        "proposal_type": meta.proposal_type,
                        
                        # Enhanced taxonomy fields
                        "sub_category": meta.sub_category,
                        "taxonomy_path": meta.taxonomy_path,
                        "tags": meta.tags or [],
                        
                        # Content for retrieval
                        "content": text,
                        
                        # Content preview for display
                        "content_preview": text[:100] + "..." if len(text) > 100 else text,
                        
                        # Additional searchable fields
                        "has_page_number": meta.page_number is not None,
                        
                        # Embedding metadata
                        "embedding_metadata": meta.embedding_metadata or {
                            "language": "es",
                            "model": "text-embedding-3-small",
                            "dimensions": 1536,
                            "generated_date": __import__('datetime').date.today().strftime("%Y-%m-%d")
                        }
                    }
                )
                
                # Add conditional fields only if they exist and are not empty
                if meta.headers:
                    point.payload["headers"] = meta.headers
                if meta.section_hierarchy:
                    point.payload["section_hierarchy"] = meta.section_hierarchy
                    point.payload["section_depth"] = len(meta.section_hierarchy)
                
                points.append(point)
            
            # Prepare points for immediate writing
            candidate_points = []
            for point in points:
                candidate_points.append({
                    "id": point.id,
                    "vector": point.vector,
                    "payload": point.payload
                })
            
            # Upload in smaller batches with retry logic
            batch_size = 16  # Reduced batch size for reliability
            total_batches = (len(points) + batch_size - 1) // batch_size
            
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                batch_num = i // batch_size + 1
                
                # Retry logic with exponential backoff
                max_retries = 3
                success = False
                
                for attempt in range(max_retries):
                    try:
                        self.qdrant_client.upsert(
                            collection_name=collection_name,
                            points=batch,
                            wait=True  # Wait for operation to complete
                        )
                        print(f"    OK: Uploaded batch {batch_num}/{total_batches} ({len(batch)} points)")
                        success = True
                        break
                        
                    except Exception as e:
                        wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                        if attempt < max_retries - 1:
                            print(f"    WARNING: Batch {batch_num} failed (attempt {attempt + 1}/{max_retries}): {e}")
                            print(f"    Retrying in {wait_time}s...")
                            time.sleep(wait_time)
                        else:
                            print(f"    ERROR: Failed batch {batch_num} after {max_retries} attempts: {e}")
                            return {"status": "error", "message": f"Upload failed at batch {batch_num} after {max_retries} retries: {e}"}
                
                if not success:
                    return {"status": "error", "message": f"Upload failed at batch {batch_num}: max retries exceeded"}
            
            processing_time = time.time() - start_time
            print(f"  OK: Completed in {processing_time:.2f}s")
            
            # Create detailed log entry for this candidate
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "file": document_path.name,
                "candidate": candidate_name,
                "status": "success",
                "total_chunks_found": len(chunks),
                "chunks_processed": len(valid_texts),
                "chunks_failed_validation": len(chunks) - len(valid_texts),
                "embeddings_generated": len(embeddings),
                "points_uploaded": len(points),
                "processing_time_seconds": round(processing_time, 2),
                "batches_uploaded": total_batches,
                "embedding_model": "text-embedding-3-small",
                "embedding_dimensions": 1536
            }
            
            # Get validation errors for this candidate
            validation_errors = self.validation_errors.get(candidate_name, [])
            
            # Write candidate files immediately after successful processing
            self._write_candidate_files(candidate_name, candidate_points, log_entry, validation_errors if validation_errors else None)
            
            return {
                "status": "success",
                "candidate": candidate_name,
                "total_chunks_found": len(chunks),
                "chunks_processed": len(valid_texts),
                "chunks_failed_validation": len(chunks) - len(valid_texts),
                "embeddings_generated": len(embeddings),
                "points_uploaded": len(points),
                "processing_time": round(processing_time, 2)
            }
            
        except Exception as e:
            # Use _store_error_log for consistent error handling
            chunks_processed = len(valid_texts) if 'valid_texts' in locals() else (len(chunks) if 'chunks' in locals() else 0)
            embeddings_generated = len(embeddings) if 'embeddings' in locals() else 0
            candidate = candidate_name if 'candidate_name' in locals() else "Unknown"
            
            self._store_error_log(candidate, document_path, f"Qdrant upload failed: {e}", chunks_processed, embeddings_generated, start_time)
            
            return {"status": "error", "message": f"Qdrant upload failed: {e}"}
    
    def process_all_documents(self, documents_path: str, collection_name: str = "political_documents") -> Dict[str, Any]:
        """Process all documents in directory directly to Qdrant"""
        
        documents_path = Path(documents_path)
        if not documents_path.exists():
            return {"status": "error", "message": f"Documents path does not exist: {documents_path}"}
        
        # Find all .md files
        md_files = list(documents_path.glob("**/*.md"))
        if not md_files:
            return {"status": "error", "message": f"No .md files found in {documents_path}"}
        
        print(f"Starting direct processing to Qdrant Cloud")
        print(f"Documents path: {documents_path}")
        print(f"Found {len(md_files)} .md files")
        print(f"Target collection: {collection_name}")
        
        # Set processing start time and clear previous data
        self.start_time = datetime.now()
        self.validation_errors.clear()
        self.processed_candidates.clear()
        
        # Ensure Qdrant collection exists
        if not self.ensure_collection(collection_name):
            return {"status": "error", "message": "Failed to create/access Qdrant collection"}
        
        # Process each file individually
        total_start_time = time.time()
        results = []
        total_stats = {
            "files_processed": 0,
            "files_failed": 0,
            "total_chunks": 0,
            "total_embeddings": 0,
            "total_points": 0,
            "candidates": set(),
            "processing_times": []
        }
        
        for i, md_file in enumerate(md_files, 1):
            print(f"\n{'='*60}")
            print(f"Processing file {i}/{len(md_files)}")
            
            result = self.process_single_file(md_file, collection_name)
            results.append(result)
            
            if result["status"] == "success":
                total_stats["files_processed"] += 1
                total_stats["total_chunks"] += result["chunks_processed"]
                total_stats["total_embeddings"] += result["embeddings_generated"] 
                total_stats["total_points"] += result["points_uploaded"]
                total_stats["candidates"].add(result["candidate"])
                total_stats["processing_times"].append(result["processing_time"])
                self.processed_candidates.append(result["candidate"])
            else:
                total_stats["files_failed"] += 1
                print(f"  ERROR: Failed: {result['message']}")
        
        total_time = time.time() - total_start_time
        avg_time = sum(total_stats["processing_times"]) / len(total_stats["processing_times"]) if total_stats["processing_times"] else 0
        
        print(f"\n{'='*60}")
        print(f"DIRECT PROCESSING COMPLETED")
        print(f"OK: Files processed: {total_stats['files_processed']}")
        print(f"ERROR: Files failed: {total_stats['files_failed']}")
        print(f"Total chunks: {total_stats['total_chunks']}")
        print(f"Total embeddings: {total_stats['total_embeddings']}")
        print(f"Total points uploaded: {total_stats['total_points']}")
        print(f"Candidates processed: {len(total_stats['candidates'])}")
        print(f"Total time: {total_time:.2f}s")
        print(f"Average per file: {avg_time:.2f}s")
        
        # Generate session summary (candidate files already written individually)
        self._write_session_summary(collection_name, total_stats, total_time, avg_time)
        
        return {
            "status": "success" if total_stats["files_failed"] == 0 else "partial",
            "collection_name": collection_name,
            "total_time": round(total_time, 2),
            "files_processed": total_stats["files_processed"],
            "files_failed": total_stats["files_failed"],
            "total_chunks": total_stats["total_chunks"],
            "total_embeddings": total_stats["total_embeddings"],
            "total_points": total_stats["total_points"],
            "candidates": list(total_stats["candidates"]),
            "avg_time_per_file": round(avg_time, 2),
            "results": results
        }
    
    def _write_session_summary(self, collection_name: str, total_stats: dict, total_time: float, avg_time: float) -> None:
        """Write session summary after all candidates have been processed individually"""
        
        end_time = datetime.now()
        
        # Create session summary
        session_summary = {
            "session_summary": {
                "processing_start": self.start_time.isoformat() if self.start_time else None,
                "processing_end": end_time.isoformat(),
                "total_processing_time_seconds": total_time,
                "average_time_per_file_seconds": avg_time,
                "collection_name": collection_name
            },
            "processing_stats": {
                "files_found": len(total_stats["candidates"]) + total_stats["files_failed"],
                "files_processed": total_stats["files_processed"],
                "files_failed": total_stats["files_failed"],
                "total_chunks": total_stats["total_chunks"],
                "total_embeddings": total_stats["total_embeddings"],
                "total_points_uploaded": total_stats["total_points"],
                "candidates_processed": len(total_stats["candidates"]),
                "candidates": list(total_stats["candidates"])
            },
            "technical_details": {
                "embedding_model": "text-embedding-3-small",
                "embedding_dimensions": 1536,
                "batch_size": 16,
                "retry_attempts": 3,
                "timeout_seconds": 60
            },
            "validation_summary": {
                "candidates_with_validation_errors": len(self.validation_errors),
                "total_failed_chunks": sum(len(errors) for errors in self.validation_errors.values())
            }
        }
        
        session_file = self.export_dir / "session_summary.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_summary, f, ensure_ascii=False, indent=2)
        
        # Print summary
        print(f"\nSession summary generated:")
        print(f"  File: {session_file}")
        print(f"  Candidates processed: {len(self.processed_candidates)}")
        print(f"  Export directory: {self.export_dir}")
        
        if self.validation_errors:
            print(f"\nValidation errors found:")
            for candidate, errors in self.validation_errors.items():
                print(f"  {candidate}: {len(errors)} chunks failed validation")
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize candidate name for directory creation"""
        # Remove problematic characters and replace spaces with underscores
        sanitized = re.sub(r'[<>:"/\\|?*]', '', name)
        sanitized = sanitized.replace(' ', '_').replace('-', '_')
        return sanitized