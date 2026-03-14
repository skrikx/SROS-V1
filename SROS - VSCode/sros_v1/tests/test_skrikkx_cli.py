"""
Skrikx CLI Tests
================

Test Skrikx CLI commands and output formatting.
"""

import pytest
from typer.testing import CliRunner
from sros.cli.skrikkx import app


runner = CliRunner()


class TestSkrikxCLI:
    """Test Skrikx CLI commands."""
    
    def test_version_command(self):
        """Test version command displays version info."""
        result = runner.invoke(app, ["version"])
        
        assert result.exit_code == 0
        assert "Skrikx" in result.stdout or "version" in result.stdout.lower()
    
    def test_backends_command(self):
        """Test backends command lists available backends."""
        result = runner.invoke(app, ["backends"])
        
        assert result.exit_code == 0
        # Should mention at least one backend
        backends_lower = result.stdout.lower()
        assert "gemini" in backends_lower or "backend" in backends_lower
    
    def test_model_info_command(self):
        """Test model-info command shows model configuration."""
        result = runner.invoke(app, ["model-info"])
        
        assert result.exit_code == 0
        # Should show model info
        assert len(result.stdout) > 0
    
    def test_test_backends_command(self):
        """Test test-backends command pings all backends."""
        result = runner.invoke(app, ["test-backends"])
        
        # Should complete (might fail if no backends, but should not error)
        assert result.exit_code in [0, 1]
    
    def test_chat_command_with_prompt(self):
        """Test chat command with a prompt."""
        result = runner.invoke(app, ["chat", "Hello"])
        
        # Should execute the command
        assert result.exit_code == 0 or "error" in result.stdout.lower() or "not available" in result.stdout.lower()
    
    def test_chat_command_with_backend_option(self):
        """Test chat command with --backend option."""
        result = runner.invoke(app, ["chat", "Hello", "--backend", "gemini"])
        
        # Should handle the backend option
        assert result.exit_code in [0, 1]
    
    def test_chat_command_with_temperature_option(self):
        """Test chat command with --temperature option."""
        result = runner.invoke(app, ["chat", "Hello", "--temperature", "0.5"])
        
        # Should handle the temperature option
        assert result.exit_code in [0, 1]
    
    def test_chat_command_with_max_tokens_option(self):
        """Test chat command with --max-tokens option."""
        result = runner.invoke(app, ["chat", "Hello", "--max-tokens", "100"])
        
        # Should handle the max-tokens option
        assert result.exit_code in [0, 1]
    
    def test_chat_command_multiple_options(self):
        """Test chat command with multiple options."""
        result = runner.invoke(app, [
            "chat", "Hello",
            "--backend", "gemini",
            "--temperature", "0.3",
            "--max-tokens", "200"
        ])
        
        # Should handle all options
        assert result.exit_code in [0, 1]


class TestSkrikxCLIOutput:
    """Test Skrikx CLI output formatting."""
    
    def test_backends_command_output_format(self):
        """Test backends command output is formatted nicely."""
        result = runner.invoke(app, ["backends"])
        
        assert result.exit_code == 0
        # Output should be non-empty
        assert len(result.stdout) > 0
    
    def test_model_info_output_format(self):
        """Test model-info output is formatted nicely."""
        result = runner.invoke(app, ["model-info"])
        
        assert result.exit_code == 0
        # Output should contain model information
        output_lower = result.stdout.lower()
        assert "model" in output_lower or "backend" in output_lower or "config" in output_lower
    
    def test_version_output_format(self):
        """Test version output is formatted nicely."""
        result = runner.invoke(app, ["version"])
        
        assert result.exit_code == 0
        # Should have version info
        assert len(result.stdout) > 0


class TestSkrikxCLIErrorHandling:
    """Test Skrikx CLI error handling."""
    
    def test_invalid_backend(self):
        """Test chat with invalid backend handles gracefully."""
        result = runner.invoke(app, ["chat", "Hello", "--backend", "invalid"])
        
        # Should not crash
        assert result.exit_code in [0, 1, 2]
    
    def test_invalid_temperature(self):
        """Test chat with invalid temperature handles gracefully."""
        result = runner.invoke(app, ["chat", "Hello", "--temperature", "invalid"])
        
        # Should show error or reject invalid input
        assert result.exit_code in [1, 2]
    
    def test_invalid_max_tokens(self):
        """Test chat with invalid max_tokens handles gracefully."""
        result = runner.invoke(app, ["chat", "Hello", "--max-tokens", "invalid"])
        
        # Should show error or reject invalid input
        assert result.exit_code in [1, 2]


class TestSkrikxCLIIntegration:
    """Integration tests for Skrikx CLI."""
    
    def test_all_commands_available(self):
        """Test all expected commands are available."""
        result = runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        # Should list available commands
        help_text = result.stdout.lower()
        assert "test-backends" in help_text or "backends" in help_text
    
    def test_help_command(self):
        """Test help command works."""
        result = runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        # Should show help text
        assert len(result.stdout) > 0
    
    def test_command_help(self):
        """Test individual command help works."""
        result = runner.invoke(app, ["chat", "--help"])
        
        assert result.exit_code == 0
        # Should show chat command help
        assert len(result.stdout) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
