"""
Skrikx 0.1 CLI - SROS Wiring Agent Interface
==============================================

Command-line interface for wiring operations, backend testing, and prompt execution.
Exposes model backends through a simple, intuitive terminal interface.

Commands:
  test-backends    Test connectivity and health of all available backends
  chat             Send a prompt to a specific backend (default: Gemini)
  backends         List available backends and their status
  model-info       Show model configuration and details
"""

import typer
import logging
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from sros.models.model_router import get_router

app = typer.Typer(
    name="skrikx",
    help="Skrikx 0.1 - SROS Multi-Model Wiring Interface",
    no_args_is_help=True
)

console = Console()
logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)


@app.command()
def test_backends():
    """
    Test connectivity and health of all available backends.
    
    Sends a simple ping prompt to each backend and reports status.
    """
    console.print("\n[bold blue]Testing SROS Backends[/bold blue]")
    console.print("=" * 60)
    
    router = get_router()
    ping_prompt = "Respond with 'OK' and your model name."
    
    results = []
    available = router.get_available_backends()
    
    if not available:
        console.print("[red]ERROR: No backends available![/red]")
        console.print("Check your API keys in .env file")
        raise typer.Exit(1)
    
    for backend in available:
        console.print(f"\n[cyan]Testing {backend.upper()}...[/cyan]")
        
        result = router.chat(ping_prompt, backend=backend, max_tokens=100)
        
        if result["success"]:
            console.print(f"  [green]✓ SUCCESS[/green]")
            console.print(f"  Response: {result['text'][:80]}...")
            results.append((backend, "✓ OK", "[green]OK[/green]"))
        else:
            console.print(f"  [red]✗ FAILED[/red]")
            console.print(f"  Error: {result['error']}")
            results.append((backend, "✗ ERROR", f"[red]{result['error'][:40]}[/red]"))
    
    console.print("\n" + "=" * 60)
    console.print("[bold]Backend Test Summary[/bold]")
    
    table = Table(title="Backend Status")
    table.add_column("Backend", style="cyan")
    table.add_column("Status", style="magenta")
    
    for backend, status, _ in results:
        table.add_row(backend.upper(), status)
    
    console.print(table)
    console.print()


@app.command()
def chat(
    prompt: str = typer.Argument(..., help="Prompt to send to the model"),
    backend: Optional[str] = typer.Option("gemini", help="Backend to use (gemini, openai, claude)"),
    temperature: float = typer.Option(0.2, min=0.0, max=1.0, help="Sampling temperature"),
    max_tokens: int = typer.Option(1024, help="Maximum response tokens"),
):
    """
    Send a prompt to a specific backend and print the response.
    
    Example:
      skrikx chat "What is SROS?" --backend gemini
      skrikx chat "Hello" --backend openai --max-tokens 500
    """
    console.print(f"\n[bold blue]SROS Chat - {backend.upper()} Backend[/bold blue]")
    console.print("=" * 60)
    
    router = get_router()
    
    # Check backend availability
    if not router.is_backend_available(backend):
        console.print(f"[red]ERROR: Backend '{backend}' is not available[/red]")
        available = router.get_available_backends()
        console.print(f"Available backends: {', '.join(available)}")
        raise typer.Exit(1)
    
    console.print(f"\n[dim]Prompt:[/dim] {prompt}")
    console.print("[dim]Processing...[/dim]")
    
    result = router.chat(
        prompt,
        backend=backend,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    if result["success"]:
        console.print("\n[green]✓ Response received[/green]\n")
        console.print(result["text"])
    else:
        console.print(f"\n[red]✗ Error: {result['error']}[/red]")
        raise typer.Exit(1)
    
    console.print()


@app.command()
def backends():
    """
    List all available backends and their status.
    
    Shows which backends are configured and have valid API keys.
    """
    console.print("\n[bold blue]SROS Backend Status[/bold blue]")
    console.print("=" * 60 + "\n")
    
    router = get_router()
    available = router.get_available_backends()
    primary = router.get_primary_backend()
    
    table = Table(title="Available Backends")
    table.add_column("Backend", style="cyan")
    table.add_column("Status", style="magenta")
    table.add_column("Primary", style="yellow")
    
    all_backends = ["gemini", "openai", "claude"]
    for backend in all_backends:
        is_available = router.is_backend_available(backend)
        status = "[green]Available[/green]" if is_available else "[red]Unavailable[/red]"
        is_primary = "[bold]★[/bold]" if backend == primary else ""
        table.add_row(backend.upper(), status, is_primary)
    
    console.print(table)
    console.print(f"\nPrimary backend: [bold]{primary.upper()}[/bold]")
    console.print(f"Available backends: {', '.join(b.upper() for b in available)}")
    console.print()


@app.command()
def model_info():
    """
    Show model configuration and environment details.
    
    Displays model names, versions, and configuration from environment.
    """
    import os
    
    console.print("\n[bold blue]SROS Model Configuration[/bold blue]")
    console.print("=" * 60 + "\n")
    
    config_data = [
        ("Gemini Model", os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")),
        ("Gemini Base URL", os.environ.get("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")),
        ("OpenAI Model", os.environ.get("OPENAI_MODEL", "gpt-4")),
        ("Claude Model", os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")),
        ("Environment", os.environ.get("SROS_ENV", "dev")),
        ("Tenant", os.environ.get("SROS_TENANT", "default")),
    ]
    
    table = Table(title="Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="magenta")
    
    for key, value in config_data:
        table.add_row(key, value)
    
    console.print(table)
    
    # Show API key status (without revealing actual keys)
    console.print("\n[bold]API Key Status:[/bold]")
    
    gemini_key = os.environ.get("GEMINI_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    claude_key = os.environ.get("ANTHROPIC_API_KEY")
    
    console.print(f"  Gemini:  [{'green' if gemini_key else 'red'}]{'✓ Configured' if gemini_key else '✗ Missing'}[/]")
    console.print(f"  OpenAI:  [{'green' if openai_key and openai_key != 'your_openai_key_here' else 'red'}]{'✓ Configured' if openai_key and openai_key != 'your_openai_key_here' else '✗ Missing/Placeholder'}[/]")
    console.print(f"  Claude:  [{'green' if claude_key else 'red'}]{'✓ Configured' if claude_key else '✗ Missing'}[/]")
    
    console.print()


@app.command()
def version():
    """Show Skrikx version and build info."""
    console.print("\n[bold blue]Skrikx[/bold blue] v0.1.0")
    console.print("SROS Multi-Model Wiring Agent")
    console.print("Built on November 24, 2025")
    console.print()


def main():
    """Entry point for CLI."""
    app()


if __name__ == "__main__":
    main()
