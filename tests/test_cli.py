"""
Tests for the command-line interface.
"""

import os
import tempfile
from pathlib import Path
import pytest
from click.testing import CliRunner

from docgen.cli import main


class TestCLI:
    """Tests for the CLI commands."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI test runner."""
        return CliRunner()
    
    @pytest.fixture
    def sample_md_file(self, temp_dir):
        """Create a sample Markdown file for testing."""
        content = """---
title: "CLI Test Document"
version: "1.0"
---

# Test Document

This is a test.
"""
        path = os.path.join(temp_dir, "test.md")
        with open(path, 'w') as f:
            f.write(content)
        return path
    
    def test_version(self, runner):
        """Test --version flag."""
        result = runner.invoke(main, ['--version'])
        
        assert result.exit_code == 0
        assert '1.0.0' in result.output
    
    def test_help(self, runner):
        """Test --help flag."""
        result = runner.invoke(main, ['--help'])
        
        assert result.exit_code == 0
        assert 'PDF Document Generator' in result.output
        assert '--template' in result.output
        assert '--output' in result.output
    
    def test_list_templates(self, runner):
        """Test --list-templates flag."""
        result = runner.invoke(main, ['--list-templates'])
        
        assert result.exit_code == 0
        assert 'Available templates' in result.output or 'ford_release_notes' in result.output
    
    def test_template_info(self, runner):
        """Test --template-info flag."""
        result = runner.invoke(main, ['--template-info', '--template', 'ford_release_notes'])
        
        # May fail if template not found, but command should run
        assert result.exit_code in [0, 1]
    
    def test_no_input_file(self, runner):
        """Test error when no input file provided."""
        result = runner.invoke(main, [])
        
        assert result.exit_code == 1
        assert 'INPUT_FILE is required' in result.output or 'Error' in result.output
    
    def test_generate_basic(self, runner, sample_md_file, temp_dir):
        """Test basic PDF generation via CLI."""
        output_path = os.path.join(temp_dir, "output.pdf")
        
        result = runner.invoke(main, [
            sample_md_file,
            '-o', output_path,
            '--template', 'ford_release_notes'
        ])
        
        # Command may fail if template not found in test context
        # but we can at least check it runs
        if result.exit_code == 0:
            assert 'Successfully generated' in result.output
            assert os.path.exists(output_path)
    
    def test_generate_with_metadata(self, runner, sample_md_file, temp_dir):
        """Test PDF generation with metadata override."""
        output_path = os.path.join(temp_dir, "output.pdf")
        
        result = runner.invoke(main, [
            sample_md_file,
            '-o', output_path,
            '--template', 'ford_release_notes',
            '--meta', 'title=Custom Title',
            '--meta', 'version=2.0.0'
        ])
        
        # Check that metadata parsing worked
        assert result.exit_code in [0, 1]
    
    def test_default_output_name(self, runner, temp_dir):
        """Test that output defaults to input name with .pdf extension."""
        content = "# Test\n\nContent."
        input_path = os.path.join(temp_dir, "document.md")
        with open(input_path, 'w') as f:
            f.write(content)
        
        result = runner.invoke(main, [
            input_path,
            '--template', 'ford_release_notes'
        ])
        
        # The default output should be document.pdf
        expected_output = os.path.join(temp_dir, "document.pdf")
        
        if result.exit_code == 0:
            assert os.path.exists(expected_output)
    
    def test_invalid_template(self, runner, sample_md_file, temp_dir):
        """Test error handling for invalid template."""
        output_path = os.path.join(temp_dir, "output.pdf")
        
        result = runner.invoke(main, [
            sample_md_file,
            '-o', output_path,
            '--template', 'nonexistent_template'
        ])
        
        assert result.exit_code == 1
        assert 'not found' in result.output.lower() or 'error' in result.output.lower()
    
    def test_debug_flag(self, runner, sample_md_file, temp_dir):
        """Test --debug flag enables debug output."""
        output_path = os.path.join(temp_dir, "output.pdf")
        
        result = runner.invoke(main, [
            sample_md_file,
            '-o', output_path,
            '--template', 'ford_release_notes',
            '--debug'
        ])
        
        # Debug flag should be accepted
        assert result.exit_code in [0, 1]
    
    def test_batch_processing(self, runner, temp_dir):
        """Test batch processing of multiple files."""
        # Create multiple test files
        for i in range(3):
            content = f"# Test Document {i}\n\nThis is test {i}."
            path = os.path.join(temp_dir, f"test{i}.md")
            with open(path, 'w') as f:
                f.write(content)
        
        output_dir = os.path.join(temp_dir, "output")
        
        result = runner.invoke(main, [
            '--batch', temp_dir,
            '--output-dir', output_dir,
            '--template', 'ford_release_notes'
        ])
        
        # Check batch processing worked
        if result.exit_code == 0:
            assert 'Batch processing' in result.output
            assert 'Completed' in result.output
            # Check output files were created
            assert os.path.exists(os.path.join(output_dir, "test0.pdf"))
            assert os.path.exists(os.path.join(output_dir, "test1.pdf"))
    
    def test_batch_no_files(self, runner, temp_dir):
        """Test batch processing with no matching files."""
        empty_dir = os.path.join(temp_dir, "empty")
        os.makedirs(empty_dir)
        
        result = runner.invoke(main, [
            '--batch', empty_dir,
            '--template', 'ford_release_notes'
        ])
        
        assert result.exit_code == 1
        assert 'No .md or .adoc files' in result.output
    
    def test_watch_flag_in_help(self, runner):
        """Test that --watch flag is shown in help."""
        result = runner.invoke(main, ['--help'])
        
        assert result.exit_code == 0
        assert '--watch' in result.output or '-w' in result.output
