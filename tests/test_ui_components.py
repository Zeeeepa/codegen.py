"""
Tests for the UI components.

This module provides tests for the UI components,
ensuring that all functionality works as expected.
"""

import unittest
import os
import sys
import tkinter as tk
from unittest.mock import patch, MagicMock

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Skip tests if running in a headless environment
try:
    root = tk.Tk()
    root.destroy()
    SKIP_TESTS = False
except:
    SKIP_TESTS = True

@unittest.skipIf(SKIP_TESTS, "Skipping UI tests in headless environment")
class TestAgentRunCard(unittest.TestCase):
    """Tests for the AgentRunCard component."""
    
    def setUp(self):
        """Set up the test."""
        from ui.components.agent_run_card import AgentRunCard
        
        # Create a root window
        self.root = tk.Tk()
        
        # Create a mock agent run
        self.agent_run = {
            "id": "run_id",
            "status": "RUNNING",
            "prompt": "Test prompt",
            "created_at": "2023-01-01T00:00:00Z"
        }
        
        # Create mock callbacks
        self.on_view = MagicMock()
        self.on_star = MagicMock()
        self.on_resume = MagicMock()
        self.on_stop = MagicMock()
        
        # Create the component
        self.card = AgentRunCard(
            self.root,
            self.agent_run,
            on_view=self.on_view,
            on_star=self.on_star,
            on_resume=self.on_resume,
            on_stop=self.on_stop,
            is_starred=False
        )
    
    def tearDown(self):
        """Tear down the test."""
        # Destroy the root window
        self.root.destroy()
    
    def test_view_callback(self):
        """Test view callback."""
        # Call the view callback
        self.card._on_view_click()
        
        # Check the mock
        self.on_view.assert_called_once_with("run_id")
    
    def test_star_callback(self):
        """Test star callback."""
        # Call the star callback
        self.card._on_star_click()
        
        # Check the mock
        self.on_star.assert_called_once_with("run_id", True)
        
        # Check the state
        self.assertTrue(self.card.is_starred)
        
        # Call the star callback again
        self.card._on_star_click()
        
        # Check the mock
        self.on_star.assert_called_with("run_id", False)
        
        # Check the state
        self.assertFalse(self.card.is_starred)
    
    def test_resume_callback(self):
        """Test resume callback."""
        # Call the resume callback
        self.card._on_resume_click()
        
        # Check the mock
        self.on_resume.assert_called_once_with("run_id")
    
    def test_stop_callback(self):
        """Test stop callback."""
        # Call the stop callback
        self.card._on_stop_click()
        
        # Check the mock
        self.on_stop.assert_called_once_with("run_id")
    
    def test_update(self):
        """Test update method."""
        # Create a new agent run
        new_agent_run = {
            "id": "run_id_2",
            "status": "COMPLETED",
            "prompt": "Test prompt 2",
            "created_at": "2023-01-02T00:00:00Z"
        }
        
        # Update the card
        self.card.update(new_agent_run, is_starred=True)
        
        # Check the state
        self.assertEqual(self.card.agent_run, new_agent_run)
        self.assertTrue(self.card.is_starred)

@unittest.skipIf(SKIP_TESTS, "Skipping UI tests in headless environment")
class TestProjectCard(unittest.TestCase):
    """Tests for the ProjectCard component."""
    
    def setUp(self):
        """Set up the test."""
        from ui.components.project_card import ProjectCard
        
        # Create a root window
        self.root = tk.Tk()
        
        # Create a mock project
        self.project = {
            "id": "project_id",
            "name": "Test Project",
            "description": "Test description",
            "full_name": "org/repo"
        }
        
        # Create mock callbacks
        self.on_view = MagicMock()
        self.on_star = MagicMock()
        self.on_create_run = MagicMock()
        
        # Create the component
        self.card = ProjectCard(
            self.root,
            self.project,
            on_view=self.on_view,
            on_star=self.on_star,
            on_create_run=self.on_create_run,
            is_starred=False,
            has_setup_commands=True
        )
    
    def tearDown(self):
        """Tear down the test."""
        # Destroy the root window
        self.root.destroy()
    
    def test_view_callback(self):
        """Test view callback."""
        # Call the view callback
        self.card._on_view_click()
        
        # Check the mock
        self.on_view.assert_called_once_with("project_id")
    
    def test_star_callback(self):
        """Test star callback."""
        # Call the star callback
        self.card._on_star_click()
        
        # Check the mock
        self.on_star.assert_called_once_with("project_id", True)
        
        # Check the state
        self.assertTrue(self.card.is_starred)
        
        # Call the star callback again
        self.card._on_star_click()
        
        # Check the mock
        self.on_star.assert_called_with("project_id", False)
        
        # Check the state
        self.assertFalse(self.card.is_starred)
    
    def test_create_run_callback(self):
        """Test create run callback."""
        # Call the create run callback
        self.card._on_create_run_click()
        
        # Check the mock
        self.on_create_run.assert_called_once_with("project_id")
    
    def test_update(self):
        """Test update method."""
        # Create a new project
        new_project = {
            "id": "project_id_2",
            "name": "Test Project 2",
            "description": "Test description 2",
            "full_name": "org/repo2"
        }
        
        # Update the card
        self.card.update(new_project, is_starred=True, has_setup_commands=False)
        
        # Check the state
        self.assertEqual(self.card.project, new_project)
        self.assertTrue(self.card.is_starred)
        self.assertFalse(self.card.has_setup_commands)

@unittest.skipIf(SKIP_TESTS, "Skipping UI tests in headless environment")
class TestTemplateCard(unittest.TestCase):
    """Tests for the TemplateCard component."""
    
    def setUp(self):
        """Set up the test."""
        from ui.components.template_card import TemplateCard
        
        # Create a root window
        self.root = tk.Tk()
        
        # Create a mock template
        self.template = {
            "id": "template_id",
            "name": "Test Template",
            "description": "Test description",
            "category": "GENERAL",
            "content": "Test content"
        }
        
        # Create mock callbacks
        self.on_view = MagicMock()
        self.on_edit = MagicMock()
        self.on_delete = MagicMock()
        self.on_use = MagicMock()
        
        # Create the component
        self.card = TemplateCard(
            self.root,
            self.template,
            on_view=self.on_view,
            on_edit=self.on_edit,
            on_delete=self.on_delete,
            on_use=self.on_use
        )
    
    def tearDown(self):
        """Tear down the test."""
        # Destroy the root window
        self.root.destroy()
    
    def test_view_callback(self):
        """Test view callback."""
        # Call the view callback
        self.card._on_view_click()
        
        # Check the mock
        self.on_view.assert_called_once_with("template_id")
    
    def test_edit_callback(self):
        """Test edit callback."""
        # Call the edit callback
        self.card._on_edit_click()
        
        # Check the mock
        self.on_edit.assert_called_once_with("template_id")
    
    def test_delete_callback(self):
        """Test delete callback."""
        # Call the delete callback
        self.card._on_delete_click()
        
        # Check the mock
        self.on_delete.assert_called_once_with("template_id")
    
    def test_use_callback(self):
        """Test use callback."""
        # Call the use callback
        self.card._on_use_click()
        
        # Check the mock
        self.on_use.assert_called_once_with("template_id")
    
    def test_update(self):
        """Test update method."""
        # Create a new template
        new_template = {
            "id": "template_id_2",
            "name": "Test Template 2",
            "description": "Test description 2",
            "category": "DEVELOPMENT",
            "content": "Test content 2"
        }
        
        # Update the card
        self.card.update(new_template)
        
        # Check the state
        self.assertEqual(self.card.template, new_template)

if __name__ == "__main__":
    unittest.main()

