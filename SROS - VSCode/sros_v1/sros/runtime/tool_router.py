"""
Tool Router
===========

Abstracts tool execution from agents.
Agents request a tool by name/capability, and the router finds and executes it.
"""
import logging
import os
import subprocess
import glob
from typing import Dict, Any, List, Optional, Callable
from sros.kernel.event_bus import EventBus

logger = logging.getLogger(__name__)

class ToolRouter:
    def __init__(self, event_bus: EventBus, adapter_registry=None):
        self.event_bus = event_bus
        self.adapter_registry = adapter_registry or {}
        self._tools: Dict[str, Dict[str, Any]] = {}
        
        # Auto-register sovereign tools
        self.register_sovereign_tools()
        
    def register_tool(self, name: str, func: Callable, description: str):
        """Register a new tool."""
        self._tools[name] = {
            "func": func,
            "description": description
        }
        logger.info(f"Tool registered: {name}")

    def register_sovereign_tools(self):
        """Register core sovereign tools (File I/O, Shell, Search)."""

        def edit_file(path: str, content: str):
            """Write content to a file. Overwrites if exists."""
            try:
                # Ensure dir exists
                os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                return f"File written: {path}"
            except Exception as e:
                return f"Error writing file: {str(e)}"

        def read_file(path: str):
            """Read content from a file."""
            try:
                if not os.path.exists(path):
                    return f"Error: File not found: {path}"
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                return f"Error reading file: {str(e)}"

        def list_dir(path: str = "."):
            """List files in a directory."""
            try:
                files = os.listdir(path)
                return "\n".join(files)
            except Exception as e:
                return f"Error listing directory: {str(e)}"

        def run_command(command: str):
            """Run a shell command."""
            try:
                # Safety: In production, this needs strict sandboxing.
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output = result.stdout
                if result.stderr:
                    output += f"\nSTDERR: {result.stderr}"
                return output if output else "Command executed with no output."
            except Exception as e:
                return f"Execution error: {str(e)}"
        
        def search_files(pattern: str, path: str = "."):
            """Search for files matching a glob pattern."""
            try:
                matches = glob.glob(os.path.join(path, "**", pattern), recursive=True)
                return "\n".join(matches)
            except Exception as e:
                return f"Search error: {str(e)}"

        def grep_search(pattern: str, path: str = "."):
            """Search for text pattern in files (recursive) using Python."""
            results = []
            try:
                for root, _, files in os.walk(path):
                    for file in files:
                        # Skip common binary/hidden files
                        if file.endswith(('.pyc', '.git', '.png', '.jpg', '.db')):
                            continue
                            
                        full_path = os.path.join(root, file)
                        try:
                            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                                for i, line in enumerate(f, 1):
                                    if pattern in line:
                                        results.append(f"{full_path}:{i}: {line.strip()}")
                        except Exception:
                            continue
                            
                return "\n".join(results) if results else "No matches found."
            except Exception as e:
                return f"Grep error: {str(e)}"

        def read_file_outline(path: str):
            """Read file structure (classes/functions) using AST."""
            try:
                import ast
                if not os.path.exists(path):
                    return f"File not found: {path}"
                
                with open(path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                
                outline = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        outline.append(f"Class: {node.name} (Line {node.lineno})")
                        for sub in node.body:
                            if isinstance(sub, ast.FunctionDef):
                                outline.append(f"  Method: {sub.name} (Line {sub.lineno})")
                    elif isinstance(node, ast.FunctionDef):
                        # Only top-level functions (not methods, handled above)
                        # This naive check might duplicate methods if we walk everything.
                        # Better to just iterate top-level body.
                        pass
                
                # Better AST walker
                outline = []
                for node in tree.body:
                    if isinstance(node, ast.ClassDef):
                        outline.append(f"Class: {node.name}")
                        for sub in node.body:
                            if isinstance(sub, ast.FunctionDef):
                                doc = ast.get_docstring(sub) or ""
                                doc_summary = doc.split('\n')[0] if doc else ""
                                outline.append(f"  Method: {sub.name} - {doc_summary}")
                    elif isinstance(node, ast.FunctionDef):
                        doc = ast.get_docstring(node) or ""
                        doc_summary = doc.split('\n')[0] if doc else ""
                        outline.append(f"Function: {node.name} - {doc_summary}")
                        
                return "\n".join(outline) if outline else "No classes/functions found."
            except Exception as e:
                return f"Outline error: {str(e)}"

        def read_url(url: str):
            """Read content from a URL (GET request)."""
            try:
                import urllib.request
                from html.parser import HTMLParser
                
                # Simple HTML stripper
                class MLStripper(HTMLParser):
                    def __init__(self):
                        super().__init__()
                        self.reset()
                        self.strict = False
                        self.convert_charrefs= True
                        self.text = []
                    def handle_data(self, d):
                        self.text.append(d)
                    def get_data(self):
                        return "".join(self.text)

                def strip_tags(html):
                    s = MLStripper()
                    s.feed(html)
                    return s.get_data()

                with urllib.request.urlopen(url) as response:
                    html = response.read().decode('utf-8')
                    text = strip_tags(html)
                    # Basic cleanup
                    lines = [line.strip() for line in text.splitlines() if line.strip()]
                    return "\n".join(lines)[:10000] # Limit size
            except Exception as e:
                return f"Error reading URL: {str(e)}"

        def search_web(query: str):
            """
            Search the web.
            NOTE: Requires external API key (e.g. Google/Bing).
            Currently a placeholder.
            """
            return f"Web Search Placeholder: Please use read_url directly. Query '{query}' logged."

        def spawn_sub_agent(role: str, task: str):
            """Spawn a sub-agent to execute a task."""
            # This requires access to the factory, which isn't directly here.
            # We'll need to inject it or instantiate it.
            # For now, we'll instantiate a fresh one (inefficient but functional).
            # In a real system, this would be a service.
            from sros.runtime.agents.sub_agent_factory import SubAgentFactory
            # We need a kernel context mock or real one.
            # This is a limitation of the current tool router design (stateless tools).
            # We'll use a minimal context.
            factory = SubAgentFactory(kernel_context=None) 
            return factory.spawn_agent(role, task)

        self.register_tool("edit_file", edit_file, "Write content to a file. Args: path, content")
        self.register_tool("read_file", read_file, "Read content from a file. Args: path")
        self.register_tool("list_dir", list_dir, "List files in a directory. Args: path")
        self.register_tool("run_command", run_command, "Run a shell command. Args: command")
        self.register_tool("search_files", search_files, "Find files by name. Args: pattern, path")
        self.register_tool("grep_search", grep_search, "Search text in files. Args: pattern, path")
        self.register_tool("read_file_outline", read_file_outline, "Get file structure. Args: path")
        self.register_tool("read_url", read_url, "Read text from URL. Args: url")
        self.register_tool("search_web", search_web, "Search web (Placeholder). Args: query")
        self.register_tool("spawn_sub_agent", spawn_sub_agent, "Spawn sub-agent. Args: role, task")

    def get_tool(self, name: str) -> Optional[Callable]:
        """Get a tool by name."""
        return self._tools.get(name, {}).get("func")

    def list_tools(self) -> Dict[str, str]:
        """List all available tools."""
        return {name: data["description"] for name, data in self._tools.items()}

    def execute_tool(self, name: str, *args, **kwargs) -> Any:
        """Execute a tool."""
        func = self.get_tool(name)
        if not func:
            raise ValueError(f"Tool not found: {name}")
        return func(*args, **kwargs)
