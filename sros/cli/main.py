import typer
from .commands import init_sros, run_demo, demo_fintech, demo_healthcare, demo_contract

app = typer.Typer(help="SROS v1 CLI")

app.add_typer(init_sros.app, name="init")
app.add_typer(run_demo.app, name="run-demo")
app.add_typer(demo_fintech.app, name="demo-fintech")
app.add_typer(demo_healthcare.app, name="demo-healthcare")
app.add_typer(demo_contract.app, name="demo-contract")

if __name__ == "__main__":
    app()
