"""Shared utilities for SROS apex-grade demos."""

import typer
import json
from pathlib import Path
from typing import Dict, Any

def print_banner(title: str, domain: str, governance: str):
    """Print a standardized apex demo banner."""
    typer.secho("\n" + "=" * 62, fg=typer.colors.CYAN, bold=True)
    typer.secho(f"  SROS v1 - {title}", fg=typer.colors.WHITE, bold=True)
    typer.secho(f"  Domain: {domain} | Governance: {governance}", fg=typer.colors.BRIGHT_BLACK)
    typer.secho("=" * 62 + "\n", fg=typer.colors.CYAN, bold=True)

def print_step(index: int, total: int, agent: str, instruction: str):
    """Print a standardized step header."""
    typer.echo(f"  [{index}/{total}] {agent}: ", nl=False)
    typer.secho(f"{instruction[:60]}...", fg=typer.colors.WHITE)

def print_verdict(verdict: str, risk: str, reason: str, conditions: list = None):
    """Print a standardized governance verdict."""
    color = typer.colors.GREEN if "allow" in verdict else typer.colors.RED
    if verdict == "allow_with_conditions":
        color = typer.colors.YELLOW
        
    typer.secho(f"    Policy: {verdict.upper()} ", fg=color, bold=True, nl=False)
    typer.secho(f"({risk})", fg=typer.colors.BRIGHT_BLACK)
    
    if reason:
        typer.secho(f"    Reason: {reason}", fg=typer.colors.BRIGHT_BLACK)
    
    if conditions:
        for c in conditions:
            typer.secho(f"      - {c}", fg=typer.colors.YELLOW)

def print_drift(value: float, threshold: float):
    """Print a standardized drift metric."""
    alert = value > threshold
    color = typer.colors.RED if alert else typer.colors.GREEN
    status = "ALERT" if alert else "OK"
    typer.echo(f"    Drift: ", nl=False)
    typer.secho(f"{value:.2f} / {threshold:.2f}", fg=color, nl=False)
    typer.echo(f" - {status}")

def print_footer(receipt: Dict[str, Any], receipt_path: Path):
    """Print a standardized apex demo footer."""
    typer.secho("\n" + "=" * 62, fg=typer.colors.CYAN, bold=True)
    typer.secho("  Demo Complete", fg=typer.colors.WHITE, bold=True)
    typer.secho("=" * 62 + "\n", fg=typer.colors.CYAN, bold=True)
    
    typer.echo(f"  Status:       ", nl=False)
    typer.secho(receipt['status'].upper(), fg=typer.colors.GREEN if receipt['status'] == 'success' else typer.colors.RED)
    
    typer.echo(f"  Steps:        {receipt['total_steps']}")
    
    gov = receipt['governance_summary']
    typer.echo(f"  Verdicts:     {gov['verdicts']}")
    
    if gov.get('domain_blocked'):
        typer.echo(f"  Restrictions: ", nl=False)
        typer.secho(f"{gov['domain_blocked']}", fg=typer.colors.YELLOW)
        
    mirror = receipt['mirror_summary']
    typer.echo(f"  Drift:        ", nl=False)
    if mirror['drift_detected']:
        typer.secho(f"DETECTED (max: {mirror['max_drift_score']:.2f})", fg=typer.colors.RED)
    else:
        typer.secho(f"None (max: {mirror['max_drift_score']:.2f})", fg=typer.colors.GREEN)
        
    typer.echo(f"\n  Receipt:      ", nl=False)
    typer.secho(str(receipt_path.resolve()), fg=typer.colors.BRIGHT_BLUE)
    
    typer.echo(f"  Chain Hash:   ", nl=False)
    typer.secho(receipt['receipt_chain']['chain_hash'], fg=typer.colors.MAGENTA)
    typer.echo("")

def resolve_demo_paths(name: str):
    """Helper to resolve SRXML and receipt paths."""
    base_dir = Path.cwd()
    srxml = base_dir / "examples" / f"{name}.srxml"
    if not srxml.exists():
        typer.secho(f"Missing required workflow asset: {srxml}", fg=typer.colors.RED)
        raise typer.Exit(code=2)
    receipt_dir = base_dir / "receipts"
    receipt_dir.mkdir(exist_ok=True)
    receipt = receipt_dir / f"{name}_receipt.json"
    return srxml, receipt
