import typer
from .commands import init_sros, run_demo

app = typer.Typer(help="SROS v1 CLI")

app.add_typer(init_sros.app, name="init")
app.add_typer(run_demo.app, name="run-demo")

if __name__ == "__main__":
    app()
