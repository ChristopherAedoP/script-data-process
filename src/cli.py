"""
CLI interface for RAG MVP
Provides command-line interface for indexing and searching documents
"""
import json
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import config
from .rag_system import RAGSystem

console = Console()


def print_welcome():
    """Print welcome message"""
    welcome_text = """
RAG MVP - Local Document Search System
======================================
Local embeddings with Sentence Transformers + FAISS

Commands:
  index         - Index documents from a directory
  search        - Search for relevant documents  
  stats         - Show system statistics
  benchmark     - Run performance benchmarks
  chat          - Interactive chat mode
  export-qdrant - Export data to Qdrant format
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
            table.add_row("Embedding Dimension", str(stats["embedding_dimension"]))
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
            model_table.add_row("Embedding Dimension", str(model_info["embedding_dimension"]))
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
            table.add_row("Upload Script", result["output_files"]["upload_script"])
            table.add_row("Filters Guide", result["output_files"]["filters_guide"])
            
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
                stats_table.add_row("Proposal Types", str(len(stats["proposal_types"])))
                stats_table.add_row("Vector Dimension", str(stats["embedding_dimension"]))
                
                console.print(stats_table)
                
                print_info("\nNext steps:")
                print("1. Install Qdrant: docker run -p 6333:6333 qdrant/qdrant")
                print(f"2. Run upload script: python {result['output_files']['upload_script']}")
                print(f"3. Check filters guide: {result['output_files']['filters_guide']}")
        else:
            print_error("Export failed")
            
    except Exception as e:
        print_error(f"Export failed: {e}")


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