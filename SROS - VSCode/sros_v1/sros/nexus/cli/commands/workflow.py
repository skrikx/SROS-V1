"""
Workflow CLI Commands

Commands for workflow execution.
"""
import argparse
from pathlib import Path
from sros.srxml.parser import SRXMLParser
from sros.runtime.workflow_engine import WorkflowEngine


def register_commands(parser: argparse.ArgumentParser):
    """Register workflow subcommands."""
    subparsers = parser.add_subparsers(dest="action", help="Workflow actions")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run a workflow")
    run_parser.add_argument("workflow_file", help="Path to workflow SRXML file")
    
    # List command
    subparsers.add_parser("list", help="List available workflows")


def execute(args: argparse.Namespace) -> dict:
    """Execute workflow command."""
    if args.action == "run":
        return run_workflow(args.workflow_file)
    elif args.action == "list":
        return list_workflows()
    else:
        return {"error": "Unknown workflow action"}


def run_workflow(workflow_file: str) -> dict:
    """Run a workflow from SRXML file."""
    try:
        # Parse workflow
        parser = SRXMLParser()
        workflow = parser.parse_to_object(workflow_file)
        
        # Execute workflow
        engine = WorkflowEngine()
        result = engine.execute(workflow)
        
        return {
            "status": "success",
            "workflow": workflow.id,
            "steps_completed": len(workflow.steps),
            "result": result
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def list_workflows() -> dict:
    """List available workflows."""
    workflows_dir = Path("./workflows")
    
    if not workflows_dir.exists():
        return {"workflows": []}
    
    workflows = []
    for srxml_file in workflows_dir.glob("*.srxml"):
        workflows.append({
            "name": srxml_file.stem,
            "path": str(srxml_file)
        })
    
    return {"workflows": workflows}
