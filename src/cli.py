"""
CLI interface for RAG MVP
Provides command-line interface for indexing and searching documents
"""
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import config
from .rag_system import RAGSystem
from .direct_processor import DirectProcessor

console = Console()


def print_welcome():
    """Print welcome message"""
    welcome_text = """
RAG MVP - Political Document Processing System
==============================================
OpenAI embeddings + Qdrant Cloud deployment

Commands:
  index         - Index documents from a directory
  search        - Search for relevant documents  
  stats         - Show system statistics
  benchmark     - Run performance benchmarks
  chat          - Interactive chat mode
  export-qdrant - Export data to Qdrant format
  upload-cloud  - Upload data to Qdrant Cloud
  process-direct - Process documents directly to Qdrant (file-by-file)
"""
    console.print(Panel(welcome_text, title="Welcome", border_style="blue"))


def print_error(message: str):
    """Print error message"""
    console.print(f"[red]ERROR: {message}[/red]")


def print_success(message: str):
    """Print success message"""
    console.print(f"[green]SUCCESS: {message}[/green]")


def print_info(message: str):
    """Print info message"""
    console.print(f"[blue]INFO: {message}[/blue]")


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """RAG MVP - Local Document Search System"""
    pass


@cli.command()
@click.option(
    "--path", "-p", 
    default=config.DOCUMENTS_PATH, 
    help="Path to documents directory"
)
@click.option(
    "--force", "-f", 
    is_flag=True, 
    help="Force reindexing even if index exists"
)
@click.option(
    "--model", "-m", 
    default=None, 
    help="Embedding model name"
)
@click.option(
    "--index-type", 
    default="IndexFlatIP", 
    type=click.Choice(["IndexFlatL2", "IndexFlatIP", "IndexIVFFlat"]),
    help="FAISS index type"
)
def index(path: str, force: bool, model: Optional[str], index_type: str):
    """Index documents for search"""
    
    if not Path(path).exists():
        print_error(f"Documents path does not exist: {path}")
        return
    
    # Ensure configuration directories exist
    config.ensure_directories()
    
    print_info(f"Indexing documents from: {path}")
    if force:
        print_info("Force reindexing enabled")
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Initializing RAG system...", total=None)
            
            # Initialize RAG system
            rag = RAGSystem(embedding_model=model)
            
            progress.update(task, description="Indexing documents...")
            
            # Index documents
            stats = rag.index_documents(
                documents_path=path,
                force_reindex=force,
                index_type=index_type
            )
        
        if stats["status"] == "success":
            print_success("Indexing completed successfully!")
            
            # Display stats table
            table = Table(title="Indexing Statistics")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="magenta")
            
            table.add_row("Documents Processed", str(stats["documents_processed"]))
            table.add_row("Chunks Created", str(stats["chunks_created"]))
            table.add_row("Embeddings Generated", str(stats["embeddings_generated"]))
            table.add_row("Embedding Dimension", str(stats["dimensions"]))
            table.add_row("Index Type", stats["index_type"])
            table.add_row("Total Time", f"{stats['total_time_seconds']}s")
            table.add_row("Avg Time per Chunk", f"{stats['avg_time_per_chunk_ms']}ms")
                        
            console.print(table)
            
        elif stats["status"] == "loaded_existing":
            print_info("Loaded existing index (use --force to reindex)")
            
        else:
            print_error(f"Indexing failed: {stats.get('message', 'Unknown error')}")
            
    except Exception as e:
        print_error(f"Indexing failed: {e}")
        if "--verbose" in sys.argv:
            console.print_exception()


@cli.command()
@click.argument("query")
@click.option(
    "--k", "-k", 
    default=config.MAX_CHUNKS_RETURN, 
    help="Number of results to return"
)
@click.option(
    "--min-score", 
    default=0.0, 
    type=float, 
    help="Minimum similarity score"
)
@click.option(
    "--model", "-m", 
    default=None, 
    help="Embedding model name"
)
def search(query: str, k: int, min_score: float, model: Optional[str]):
    """Search for relevant documents"""
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Loading RAG system...", total=None)
            
            # Initialize RAG system
            rag = RAGSystem(embedding_model=model)
            
            progress.update(task, description="Loading index...")
            
            # Try to load existing index
            index_path = config.INDEX_PATH + ".faiss"
            if not Path(index_path).exists():
                print_error("No index found. Run 'rag-cli index' first.")
                return
            
            # Load index
            rag._load_existing_index(index_path, config.METADATA_PATH)
            
            progress.update(task, description="Searching...")
            
            # Perform search
            results = rag.search_with_content(
                query=query,
                k=k, 
                min_similarity_score=min_score
            )
        
        if not results:
            print_info("No results found for your query.")
            return
        
        # Display results
        console.print(f"\nSearch Results for: [bold]'{query}'[/bold]\n")
        
        for result in results:
            # Create result panel
            headers_text = ", ".join([f"{k}: {v}" for k, v in result["headers"].items()]) if result["headers"] else "None"
            
            content = f"""
[bold]Source:[/bold] {result['source_file']}
[bold]Headers:[/bold] {headers_text}
[bold]Similarity Score:[/bold] {result['similarity_score']:.4f}
[bold]Character Count:[/bold] {result['char_count']}
[bold]Chunk ID:[/bold] {result['chunk_id']}

[bold]Content Preview:[/bold]
{result.get('content_preview', 'Content not available')}
            """.strip()
            
            panel = Panel(
                content,
                title=f"Result #{result['rank']}",
                border_style="green" if result['similarity_score'] > 0.7 else "yellow"
            )
            console.print(panel)
            console.print()
            
    except Exception as e:
        print_error(f"Search failed: {e}")
        if "--verbose" in sys.argv:
            console.print_exception()


@cli.command()
@click.option(
    "--model", "-m", 
    default=None, 
    help="Embedding model name"
)
def stats(model: Optional[str]):
    """Show system statistics"""
    
    try:
        rag = RAGSystem(embedding_model=model)
        
        # Try to load existing index
        index_path = config.INDEX_PATH + ".faiss"
        if Path(index_path).exists():
            rag._load_existing_index(index_path, config.METADATA_PATH)
        
        system_stats = rag.get_system_stats()
        
        # Display stats
        console.print("\n📊 System Statistics\n")
        
        # General info
        table = Table(title="General Information")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("System Indexed", "✅ Yes" if system_stats["is_indexed"] else "❌ No")
        table.add_row("Config Path", str(config.BASE_DIR))
        table.add_row("Documents Path", config.DOCUMENTS_PATH)
        table.add_row("Index Path", config.INDEX_PATH)
        
        console.print(table)
        
        # Model info
        if system_stats.get("model_info"):
            model_info = system_stats["model_info"]
            
            model_table = Table(title="Model Information")
            model_table.add_column("Property", style="cyan")
            model_table.add_column("Value", style="magenta")
            
            model_table.add_row("Model Name", model_info["model_name"])
            model_table.add_row("Embedding Dimension", str(model_info["dimensions"]))
            model_table.add_row("Device", model_info["device"])
            model_table.add_row("Max Sequence Length", str(model_info.get("max_seq_length", "Unknown")))
            
            console.print(model_table)
        
        # Vector store info
        if system_stats.get("vector_store"):
            vs_info = system_stats["vector_store"]
            
            vs_table = Table(title="Vector Store Information")
            vs_table.add_column("Property", style="cyan")
            vs_table.add_column("Value", style="magenta")
            
            vs_table.add_row("Index Type", vs_info.get("index_type", "Unknown"))
            vs_table.add_row("Total Vectors", str(vs_info.get("total_vectors", 0)))
            vs_table.add_row("Metadata Count", str(vs_info.get("metadata_count", 0)))
            vs_table.add_row("Memory Usage", f"{vs_info.get('memory_usage_mb', 0):.2f} MB")
            
            console.print(vs_table)
            
    except Exception as e:
        print_error(f"Failed to get stats: {e}")


@cli.command()
@click.option(
    "--model", "-m", 
    default=None, 
    help="Embedding model name"
)
def benchmark(model: Optional[str]):
    """Run performance benchmarks"""
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Loading system...", total=None)
            
            rag = RAGSystem(embedding_model=model)
            
            # Try to load existing index
            index_path = config.INDEX_PATH + ".faiss"
            if not Path(index_path).exists():
                print_error("No index found. Run 'rag-cli index' first.")
                return
            
            rag._load_existing_index(index_path, config.METADATA_PATH)
            
            progress.update(task, description="Running benchmarks...")
            
            benchmark_results = rag.benchmark_system()
        
        console.print("\n⚡ Performance Benchmarks\n")
        
        # Display benchmark results as JSON for now
        console.print(Panel(
            json.dumps(benchmark_results, indent=2),
            title="Benchmark Results",
            border_style="blue"
        ))
        
    except Exception as e:
        print_error(f"Benchmark failed: {e}")


@cli.command()
@click.option(
    "--model", "-m", 
    default=None, 
    help="Embedding model name"
)
def chat(model: Optional[str]):
    """Interactive chat mode"""
    
    try:
        # Initialize system
        rag = RAGSystem(embedding_model=model)
        
        # Try to load existing index
        index_path = config.INDEX_PATH + ".faiss"
        if not Path(index_path).exists():
            print_error("No index found. Run 'rag-cli index' first.")
            return
        
        print_info("Loading index...")
        rag._load_existing_index(index_path, config.METADATA_PATH)
        
        print_success("RAG system loaded successfully!")
        console.print("\nInteractive Chat Mode")
        console.print("Type your questions below. Commands:")
        console.print("  /quit or /exit - Exit chat mode")
        console.print("  /stats - Show search statistics")
        console.print("  /help - Show this help\n")
        
        while True:
            try:
                query = console.input("[bold green]Query: [/bold green]")
                
                if query.lower() in ['/quit', '/exit']:
                    print_info("Goodbye!")
                    break
                elif query.lower() == '/stats':
                    stats = rag.get_system_stats()
                    console.print(json.dumps(stats, indent=2))
                    continue
                elif query.lower() == '/help':
                    console.print("Available commands:")
                    console.print("  /quit, /exit - Exit")
                    console.print("  /stats - System stats")
                    console.print("  /help - This help")
                    continue
                elif not query.strip():
                    continue
                
                # Perform search
                results = rag.search_with_content(query, k=3)
                
                if not results:
                    print_info("No relevant results found.")
                    continue
                
                console.print(f"\n[bold]Results for:[/bold] {query}\n")
                
                for i, result in enumerate(results, 1):
                    console.print(f"[bold cyan]{i}. {result['source_file']}[/bold cyan] (Score: {result['similarity_score']:.3f})")
                    if result['headers']:
                        headers_str = " > ".join([v for v in result['headers'].values() if v])
                        console.print(f"   -> {headers_str}")
                    console.print()
                
            except KeyboardInterrupt:
                print_info("\nGoodbye!")
                break
            except Exception as e:
                print_error(f"Search error: {e}")
                
    except Exception as e:
        print_error(f"Chat mode failed: {e}")


@cli.command()
@click.option(
    "--output-dir", 
    default="./data/qdrant_export", 
    help="Output directory for export files"
)
@click.option(
    "--collection-name", 
    default="political_documents", 
    help="Qdrant collection name"
)
@click.option(
    "--model", "-m", 
    default=None, 
    help="Embedding model name"
)
def export_qdrant(output_dir: str, collection_name: str, model: Optional[str]):
    """Export processed data to Qdrant format"""
    
    try:
        print_info(f"Exporting to Qdrant format...")
        print_info(f"Output directory: {output_dir}")
        print_info(f"Collection name: {collection_name}")
        
        # Initialize RAG system
        rag = RAGSystem(embedding_model=model)
        
        # Check if index exists
        index_path = config.INDEX_PATH + ".faiss"
        if not Path(index_path).exists():
            print_error("No index found. Run 'rag-cli index' first.")
            return
        
        # Load existing index
        rag._load_existing_index(index_path, config.METADATA_PATH)
        
        # Export to Qdrant
        result = rag.export_to_qdrant(output_dir, collection_name)
        
        if result["status"] == "success":
            print_success("Export completed successfully!")
            
            # Display export info
            table = Table(title="Export Summary")
            table.add_column("Item", style="cyan")
            table.add_column("Value", style="magenta")
            
            table.add_row("Collection Name", result["collection_name"])
            table.add_row("Total Points", str(result["total_points"]))
            table.add_row("Data File", result["output_files"]["data"])
            
            console.print(table)
            
            # Display political stats
            if "stats" in result:
                stats = result["stats"]
                
                stats_table = Table(title="Political Data Statistics")
                stats_table.add_column("Category", style="cyan")
                stats_table.add_column("Count", style="magenta")
                
                stats_table.add_row("Candidates", str(len(stats["candidates"])))
                stats_table.add_row("Parties", str(len(stats["parties"])))
                stats_table.add_row("Topics", str(len(stats["topics"])))
                stats_table.add_row("Subcategories", str(len(stats.get("subcategories", []))))
                stats_table.add_row("Taxonomy Paths", str(len(stats.get("taxonomy_paths", []))))
                stats_table.add_row("Proposal Types", str(len(stats["proposal_types"])))
                stats_table.add_row("Vector Dimension", str(stats["dimensions"]))
                stats_table.add_row("Export Date", stats.get("export_date", "legacy"))
                
                console.print(stats_table)
                
                print_info("\nQueries Examples (Use in Qdrant Cloud):")
                if stats.get("candidates"):
                    print(f"Candidates: {', '.join(stats['candidates'][:3])}{'...' if len(stats['candidates']) > 3 else ''}")
                if stats.get("topics"):
                    print(f"Topics: {', '.join(stats['topics'][:5])}{'...' if len(stats['topics']) > 5 else ''}")
                if stats.get("proposal_types"):
                    print(f"Proposal types: {', '.join(stats['proposal_types'])}")
                
                print_info("\nNext steps:")
                print("1. Set environment variables: QDRANT_API_KEY and QDRANT_URL")
                print("2. Run upload command: python -m src.cli upload-cloud")
                print("3. Test queries in Qdrant Cloud dashboard")
                print("4. See readme.md for Qdrant query examples")
        else:
            print_error("Export failed")
            
    except Exception as e:
        print_error(f"Export failed: {e}")


@cli.command()
@click.option(
    "--data-file", 
    default="./data/qdrant_export/political_documents.json",
    help="Path to the JSON data file to upload"
)
@click.option(
    "--collection-name", 
    default="political_documents", 
    help="Qdrant collection name"
)
@click.option(
    "--api-key", 
    default=None, 
    help="Qdrant API key (or set QDRANT_API_KEY env var)"
)
@click.option(
    "--url", 
    default=None, 
    help="Qdrant cluster URL (or set QDRANT_URL env var)"
)
def upload_cloud(data_file: str, collection_name: str, api_key: Optional[str], url: Optional[str]):
    """Upload data to Qdrant Cloud"""
    
    try:
        # Get credentials from env vars or options
        api_key = api_key or os.getenv("QDRANT_API_KEY")
        url = url or os.getenv("QDRANT_URL")
        
        # Validate credentials
        if not api_key:
            print_error("QDRANT_API_KEY not found")
            print("Set it with: export QDRANT_API_KEY=your_api_key_here")
            print("Or use --api-key option")
            return
        
        if not url:
            print_error("QDRANT_URL not found")
            print("Set it with: export QDRANT_URL=https://your-cluster-url.qdrant.tech")
            print("Or use --url option")
            return
        
        # Check if data file exists
        if not Path(data_file).exists():
            print_error(f"Data file not found: {data_file}")
            print("Run 'python -m src.cli export-qdrant' first")
            return
        
        print_info("Starting upload to Qdrant Cloud...")
        print_info(f"Cluster: {url}")
        print_info(f"API Key: {api_key[:8]}...")
        print_info(f"Data file: {data_file}")
        
        # Import required modules
        from qdrant_client import QdrantClient
        from qdrant_client.http import models
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Connecting to Qdrant Cloud...", total=None)
            
            # Initialize client
            client = QdrantClient(url=url, api_key=api_key)
            
            progress.update(task, description="Checking collection...")
            
            # Create collection if it doesn't exist
            try:
                client.get_collection(collection_name)
                print_info(f"Collection {collection_name} already exists")
            except:
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(
                        size=1536,  # text-embedding-3-small dimension
                        distance=models.Distance.COSINE
                    )
                )
                print_success(f"Created collection {collection_name}")
            
            progress.update(task, description="Loading data...")
            
            # Load points from JSON file
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            points = data["points"]
            total_points = len(points)
            
            print_info(f"Uploading {total_points} points...")
            
            # Upload points in batches
            batch_size = 32
            total_batches = (total_points + batch_size - 1) // batch_size
            
            for i in range(0, total_points, batch_size):
                batch = points[i:i + batch_size]
                batch_num = i // batch_size + 1
                
                progress.update(task, description=f"Uploading batch {batch_num}/{total_batches}...")
                
                qdrant_points = [
                    models.PointStruct(
                        id=point["id"],
                        vector=point["vector"],
                        payload=point["payload"]
                    )
                    for point in batch
                ]
                
                # Upload with retry logic
                max_retries = 3
                success = False
                for attempt in range(max_retries):
                    try:
                        client.upsert(
                            collection_name=collection_name,
                            points=qdrant_points
                        )
                        success = True
                        break
                    except Exception as e:
                        if attempt < max_retries - 1:
                            wait_time = 2 ** attempt
                            print_error(f"Error uploading batch {batch_num} (attempt {attempt + 1}/{max_retries}): {e}")
                            print_info(f"Retrying in {wait_time} seconds...")
                            time.sleep(wait_time)
                        else:
                            print_error(f"Failed to upload batch {batch_num} after {max_retries} attempts: {e}")
                            return
                
                if success:
                    print_success(f"Uploaded batch {batch_num}/{total_batches} ({len(batch)} points)")
        
        print_success(f"Successfully uploaded {total_points} points to Qdrant Cloud!")
        
        # Display collection info
        try:
            collection_info = client.get_collection(collection_name)
            
            info_table = Table(title="Collection Information")
            info_table.add_column("Property", style="cyan")
            info_table.add_column("Value", style="magenta")
            
            info_table.add_row("Collection Name", collection_name)
            
            # Safe access to collection info with fallbacks
            try:
                points_count = getattr(collection_info, 'points_count', 'Unknown')
                info_table.add_row("Vector Count", str(points_count))
            except:
                info_table.add_row("Vector Count", str(total_points))  # Fallback to uploaded count
            
            try:
                vector_size = collection_info.config.params.vectors.size
                info_table.add_row("Vector Size", str(vector_size))
            except:
                info_table.add_row("Vector Size", "1536")  # Known dimension
            
            try:
                distance = collection_info.config.params.vectors.distance
                info_table.add_row("Distance", str(distance))
            except:
                info_table.add_row("Distance", "Cosine")  # Known configuration
            
            console.print(info_table)
            
        except Exception as e:
            print_error(f"Could not fetch collection info: {e}")
        
        print_info("\nNext steps:")
        print("1. Test queries using Qdrant Cloud dashboard")
        print("2. Check the filters guide for query examples")
        print("3. Integrate with your web chatbot")
            
    except ImportError:
        print_error("qdrant-client not installed")
        print("Install with: pip install qdrant-client")
    except Exception as e:
        print_error(f"Upload failed: {e}")
        if "--verbose" in sys.argv:
            console.print_exception()


@cli.command()
@click.option(
    "--docs-path", 
    default="./docs", 
    help="Path to documents directory containing .md files"
)
@click.option(
    "--collection-name", 
    default="political_documents", 
    help="Qdrant collection name"
)
def process_direct(docs_path: str, collection_name: str):
    """Process documents directly to Qdrant Cloud (file-by-file for optimal data quality)"""
    
    try:
        print_info("Starting Direct Processing to Qdrant Cloud")
        print_info(f"Documents path: {docs_path}")
        print_info(f"Target collection: {collection_name}")
        
        print_info("Initializing Direct Processor...")
        
        # Initialize DirectProcessor
        processor = DirectProcessor()
        
        print_info("Processing documents...")
        
        # Process all documents directly to Qdrant
        result = processor.process_all_documents(docs_path, collection_name)
        
        if result["status"] in ["success", "partial"]:
            print_success("Direct processing completed!")
            
            # Display results table
            table = Table(title="Direct Processing Summary")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="magenta")
            
            table.add_row("Collection Name", result["collection_name"])
            table.add_row("Files Processed", str(result["files_processed"]))
            table.add_row("Files Failed", str(result["files_failed"]))
            table.add_row("Total Chunks", str(result["total_chunks"]))
            table.add_row("Total Embeddings", str(result["total_embeddings"]))
            table.add_row("Total Points Uploaded", str(result["total_points"]))
            table.add_row("Total Time", f"{result['total_time']}s")
            table.add_row("Avg Time per File", f"{result['avg_time_per_file']}s")
            
            console.print(table)
            
            # Display candidates processed
            if result["candidates"]:
                candidates_table = Table(title="Candidates Processed")
                candidates_table.add_column("Candidate", style="green")
                
                for candidate in result["candidates"]:
                    candidates_table.add_row(candidate)
                
                console.print(candidates_table)
            
            if result["status"] == "partial":
                print_error(f"{result['files_failed']} files failed to process")
                
            print_info("\nNext steps:")
            print("1. Review local export files in ./data/direct_export/")
            print("   - processed_data.json: All points with complete metadata")
            print("   - processing_log.json: Detailed per-file processing log")
            print("   - summary_stats.json: Session statistics and technical details")
            print("2. Verify data in Qdrant Cloud dashboard")
            print("3. Test political queries with filters")
            print("4. Integrate with web chatbot using @qdrant/js-client-rest")
            
        else:
            print_error(f"Processing failed: {result.get('message', 'Unknown error')}")
            
    except ValueError as e:
        # Environment variable errors
        print_error(str(e))
    except Exception as e:
        print_error(f"Direct processing failed: {e}")
        if "--verbose" in sys.argv:
            console.print_exception()


def main():
    """Main entry point"""
    if len(sys.argv) == 1:
        print_welcome()
        ctx = click.Context(cli)
        click.echo(ctx.get_help())
    else:
        cli()


if __name__ == "__main__":
    main()