import re
from typing import List

class SafetyGuard:
    """
    Sovereign Safety Guard.
    Sanitizes commands and prevents destructive actions.
    """
    FORBIDDEN_COMMANDS = [
        "rm -rf /",
        "mkfs",
        "dd if=",
        ":(){:|:&};:", # Fork bomb
        "wget", # Prevent unauthorized downloads (unless whitelisted)
        "curl"
    ]
    
    FORBIDDEN_PATHS = [
        "/etc",
        "/var",
        "/usr",
        "C:\\Windows"
    ]

    @staticmethod
    def validate_command(command: str) -> bool:
        """Check if a command is safe to execute."""
        for forbidden in SafetyGuard.FORBIDDEN_COMMANDS:
            if forbidden in command:
                return False
        return True

    @staticmethod
    def validate_path(path: str) -> bool:
        """Check if a file path is safe to touch."""
        for forbidden in SafetyGuard.FORBIDDEN_PATHS:
            if path.startswith(forbidden):
                return False
        return True
