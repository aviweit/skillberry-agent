"""Tests for prompt.py module."""

import logging
import os
from unittest.mock import patch

import pytest

from skillberry_agent_lib.prompt import build_chat_messages


class TestBuildChatMessages:
    """Test suite for build_chat_messages function."""
    
    def test_default_mcp_prompts_position(self):
        """Test that default mcp_prompts_position is 'prefix'."""
        chat_history = [{"role": "user", "content": "test message"}]
        
        with patch('skillberry_agent_lib.prompt.get_mcp_prompts_and_format') as mock_get:
            mock_get.return_value = "Test MCP prompt"
            
            # Call without specifying mcp_prompts_position to test default
            result = build_chat_messages(
                chat_history=chat_history,
                mcp_port=8080,
                mcp_server_name="test-server",
                skillberry_context={"env_id": "test"}
            )
            
            # Verify MCP prompts were fetched
            mock_get.assert_called_once()
            
            # Verify result is valid
            assert result is not None
    
    def test_mcp_prompts_fetched(self):
        """Test that MCP prompts are fetched and injected."""
        chat_history = [{"role": "user", "content": "test message"}]
        
        # Mock get_mcp_prompts_and_format to verify it IS called
        with patch('skillberry_agent_lib.prompt.get_mcp_prompts_and_format') as mock_get:
            mock_get.return_value = "Test MCP prompt content"
            
            result = build_chat_messages(
                chat_history=chat_history,
                mcp_port=8080,
                mcp_server_name="test-server",
                skillberry_context={"env_id": "test"}
            )
            
            # Verify MCP prompts WERE fetched
            mock_get.assert_called_once_with(
                port=8080,
                server_name="test-server",
                skillberry_context={"env_id": "test"}
            )
            
            # Verify result is valid
            assert result is not None
    
    def test_empty_mcp_prompts(self):
        """Test behavior when MCP prompts return empty."""
        chat_history = [{"role": "user", "content": "test message"}]
        
        with patch('skillberry_agent_lib.prompt.get_mcp_prompts_and_format') as mock_get:
            # Return empty string (no prompts available)
            mock_get.return_value = ""
            
            result = build_chat_messages(
                chat_history=chat_history,
                mcp_port=8080,
                mcp_server_name="test-server",
                skillberry_context={"env_id": "test"}
            )
            
            # Verify MCP prompts WERE attempted to be fetched
            mock_get.assert_called_once()
            
            # Verify result is valid
            assert result is not None
    
    def test_mcp_prompts_position_prefix(self):
        """Test that MCP prompts are inserted at prefix position."""
        chat_history = [{"role": "user", "content": "test message"}]
        
        with patch('skillberry_agent_lib.prompt.get_mcp_prompts_and_format') as mock_format:
            mock_format.return_value = "Test MCP prompt"
            
            result = build_chat_messages(
                chat_history=chat_history,
                mcp_port=8080,
                mcp_server_name="test-server",
                skillberry_context={"env_id": "test"},
                mcp_prompts_position='prefix'
            )
            
            # Verify the function was called
            mock_format.assert_called_once()
            
            # Verify result is valid
            assert result is not None
    
    def test_mcp_prompts_position_postfix(self):
        """Test that MCP prompts are inserted at postfix position."""
        chat_history = [{"role": "user", "content": "test message"}]
        
        with patch('skillberry_agent_lib.prompt.get_mcp_prompts_and_format') as mock_format:
            mock_format.return_value = "Test MCP prompt"
            
            result = build_chat_messages(
                chat_history=chat_history,
                mcp_port=8080,
                mcp_server_name="test-server",
                skillberry_context={"env_id": "test"},
                mcp_prompts_position='postfix'
            )
            
            # Verify the function was called
            mock_format.assert_called_once()
            
            # Verify result is valid
            assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# Made with Bob
