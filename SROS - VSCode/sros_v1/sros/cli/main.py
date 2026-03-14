import typer
from .commands import init_sros, run_demo
from .skrikkx import app as skrikkx_app

app = typer.Typer(help="SROS v1 CLI")

app.add_typer(init_sros.app, name="init")
app.add_typer(run_demo.app, name="run-demo")
app.add_typer(skrikkx_app, name="skrikx", help="Skrikx 0.1 - Multi-Model Wiring Interface")

if __name__ == "__main__":
    app()
