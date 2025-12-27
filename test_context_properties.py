"""
Property-based tests for context management functionality.
Tests universal properties that should hold for all context operations.
"""

import pytest
from hypothesis import given, strategies as st, assume
import tempfile
import os
from pathlib import Path
from context_manager import ContextManager, LocalContext
from datetime import datetime


class TestContextLoadingProperties:
    """Property-based tests for context loading reliability."""
    
    def test_context_loading_reliability(self):
        """
        Feature: bangalore-local-guide, Property 7: Context loading reliability
        For any application startup, product.md content should be successfully 
        loaded and made available to the agent.
        **Validates: Requirements 6.1, 6.2**
        """
        # Test with the actual product.md file
        manager = ContextManager("product.md")
        context = manager.load_context()
        
        # Property: Context should always be valid when loaded successfully
        assert context.is_valid()
        assert len(context.content) > 0
        assert context.source_file
        assert context.last_updated
        
        # Property: Context should contain required sections
        sections = context.get_sections()
        required_sections = [
            "City Overview",
            "Languages Spoken", 
            "Local Slang and Meanings",
            "Traffic Patterns and Peak Hours",
            "Popular Breakfast Spots and Street Food Areas",
            "Cultural Norms and Etiquette",
            "Practical Local Tips"
        ]
        
        for section in required_sections:
            assert section in sections, f"Required section '{section}' missing"
        
        # Property: Formatted context should be ready for agent consumption
        formatted = manager.format_context_for_agent(context)
        assert "BANGALORE LOCAL GUIDE KNOWLEDGE BASE" in formatted
        assert context.content in formatted
        assert "IMPORTANT GUIDELINES" in formatted
    
    @given(st.text(min_size=1000, max_size=10000, alphabet=st.characters(min_codepoint=32, max_codepoint=126)))
    def test_context_validation_properties(self, content):
        """
        Property test for context validation with various content.
        Tests that context validation works correctly for different content types.
        """
        # Create temporary file with test content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
        
        try:
            manager = ContextManager(temp_path)
            
            # Property: If content has required sections, loading should succeed
            has_all_sections = all(
                f"## {section}" in content for section in [
                    "City Overview",
                    "Languages Spoken", 
                    "Local Slang and Meanings",
                    "Traffic Patterns and Peak Hours",
                    "Popular Breakfast Spots and Street Food Areas",
                    "Cultural Norms and Etiquette",
                    "Practical Local Tips"
                ]
            )
            
            if has_all_sections:
                context = manager.load_context()
                assert context.is_valid()
                assert context.content == content
            else:
                # Should raise ValueError for missing sections
                with pytest.raises(ValueError):
                    manager.load_context()
                    
        finally:
            os.unlink(temp_path)
    
    def test_context_caching_properties(self):
        """
        Property test for context caching behavior.
        Tests that caching works correctly and consistently.
        """
        manager = ContextManager("product.md")
        
        # Property: First load should cache the context
        context1 = manager.load_context()
        assert manager._cached_context is not None
        assert manager._last_check_time is not None
        
        # Property: Second load should return cached version (same object)
        context2 = manager.load_context()
        assert context1.content == context2.content
        assert context1.last_updated == context2.last_updated
        
        # Property: Force reload should return fresh context
        context3 = manager.load_context(force_reload=True)
        assert context3.content == context1.content  # Content should be same
        # But it should be a fresh load (new object)
        
        # Property: Context summary should reflect current state
        summary = manager.get_context_summary()
        assert summary["status"] == "loaded"
        assert summary["is_valid"] is True
        assert summary["content_length"] > 0
        assert len(summary["sections"]) >= 7
    
    def test_error_handling_properties(self):
        """
        Property test for error handling in context loading.
        Tests that errors are handled gracefully and consistently.
        """
        # Property: Non-existent file should raise FileNotFoundError
        manager = ContextManager("non_existent_file.md")
        with pytest.raises(FileNotFoundError):
            manager.load_context()
        
        # Property: Empty file should raise ValueError
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("")  # Empty content
            empty_path = f.name
        
        try:
            manager = ContextManager(empty_path)
            with pytest.raises(ValueError, match="empty"):
                manager.load_context()
        finally:
            os.unlink(empty_path)
        
        # Property: File with insufficient content should raise ValueError
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("Too short")  # Very short content
            short_path = f.name
        
        try:
            manager = ContextManager(short_path)
            with pytest.raises(ValueError, match="incomplete"):
                manager.load_context()
        finally:
            os.unlink(short_path)
    
    @given(st.text(min_size=1, max_size=100, alphabet=st.characters(min_codepoint=33, max_codepoint=126)).filter(lambda x: x.strip() and not x.startswith('#')))
    def test_section_parsing_properties(self, section_name):
        """
        Property test for section parsing functionality.
        Tests that section parsing works correctly for various section names.
        """
        # Create content with a test section
        content = f"""
# Test Document

## {section_name}
This is test content for the section.

## Another Section
More content here.
"""
        
        context = LocalContext(
            content=content,
            source_file="test.md",
            last_updated=datetime.now()
        )
        
        sections = context.get_sections()
        
        # Property: Section should be parsed correctly
        assert section_name in sections
        assert "This is test content" in sections[section_name]
        assert "Another Section" in sections
    
    def test_format_for_agent_properties(self):
        """
        Property test for agent formatting functionality.
        Tests that context is properly formatted for agent consumption.
        """
        manager = ContextManager("product.md")
        context = manager.load_context()
        
        # Property: Formatted content should always include guidelines
        formatted = manager.format_context_for_agent(context)
        
        required_elements = [
            "BANGALORE LOCAL GUIDE KNOWLEDGE BASE",
            "You are a friendly Bangalore local guide",
            "ONLY the information provided below",
            "IMPORTANT GUIDELINES",
            "Always explain any local slang",
            "Never hallucinate places"
        ]
        
        for element in required_elements:
            assert element in formatted, f"Missing required element: {element}"
        
        # Property: Original content should be preserved in formatted version
        assert context.content in formatted
        
        # Property: Formatted content should be longer than original (due to guidelines)
        assert len(formatted) > len(context.content)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

class TestContextUpdateConsistency:
    """Property-based tests for context update consistency."""
    
    @given(st.text(min_size=1000, max_size=2000, alphabet=st.characters(min_codepoint=32, max_codepoint=126)))
    def test_context_update_consistency(self, additional_content):
        """
        Feature: bangalore-local-guide, Property 2: Context update consistency
        For any modification to product.md, subsequent responses should reflect 
        the updated information.
        **Validates: Requirements 2.4**
        """
        # Create a temporary file with initial content that meets minimum requirements
        initial_content = """
# Test Bangalore Guide

## City Overview
Initial city information with enough content to meet the minimum length requirement.
This section provides comprehensive details about Bangalore's history, geography, and demographics.
The city is known for its pleasant climate, IT industry, and vibrant culture.

## Languages Spoken
- Kannada (official language)
- English (widely used in business)
- Hindi (commonly understood)
- Tamil (spoken by many residents)

## Local Slang and Meanings
- Guru: Friend or buddy
- Machcha: Dude or mate
- Sakkath: Awesome or excellent
- Bekku: Cat (used affectionately)

## Traffic Patterns and Peak Hours
Morning rush: 8:00 AM to 10:00 AM with heavy congestion on major roads.
Evening rush: 6:00 PM to 9:00 PM with significant delays expected.
Weekend traffic is generally lighter but shopping areas remain busy.

## Popular Breakfast Spots and Street Food Areas
- CTR for crispy dosas
- Vidyarthi Bhavan for traditional breakfast
- VV Puram Food Street for evening snacks
- Shivaji Nagar market for local delicacies

## Cultural Norms and Etiquette
Respect for elders is paramount in Bangalore culture.
Remove shoes when entering homes and temples.
Greeting with 'Namaste' is appreciated and shows cultural awareness.

## Practical Local Tips
Always carry an umbrella during monsoon season.
Learn basic Kannada phrases for better local interaction.
Use metro during peak hours to avoid traffic congestion.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(initial_content)
            temp_path = f.name
        
        try:
            manager = ContextManager(temp_path)
            
            # Load initial context
            context1 = manager.load_context()
            initial_length = len(context1.content)
            
            # Property: Initial context should be valid
            assert context1.is_valid()
            assert "Initial city information" in context1.content
            
            # Modify the file by appending content
            modified_content = initial_content + f"\n\n## Additional Section\n{additional_content}"
            
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            # Force reload to get updated content
            context2 = manager.load_context(force_reload=True)
            
            # Property: Updated context should reflect changes
            assert context2.is_valid()
            assert len(context2.content) > initial_length
            assert additional_content in context2.content
            assert "Additional Section" in context2.content
            
            # Property: Context should have updated timestamp
            assert context2.last_updated > context1.last_updated
            
            # Property: Context summary should reflect updates
            summary = manager.get_context_summary()
            assert summary["content_length"] > initial_length
            
        finally:
            os.unlink(temp_path)
    
    def test_context_consistency_across_sessions(self):
        """
        Property test for context consistency across multiple manager instances.
        Tests that different manager instances see the same content.
        """
        # Property: Multiple managers should load identical content
        manager1 = ContextManager("product.md")
        manager2 = ContextManager("product.md")
        
        context1 = manager1.load_context()
        context2 = manager2.load_context()
        
        # Property: Content should be identical across managers
        assert context1.content == context2.content
        assert context1.source_file == context2.source_file
        
        # Property: Both contexts should be valid
        assert context1.is_valid()
        assert context2.is_valid()
        
        # Property: Sections should be parsed identically
        sections1 = context1.get_sections()
        sections2 = context2.get_sections()
        assert sections1.keys() == sections2.keys()
        
        for section_name in sections1.keys():
            assert sections1[section_name] == sections2[section_name]
    
    @given(st.integers(min_value=1, max_value=10))
    def test_multiple_reload_consistency(self, reload_count):
        """
        Property test for consistency across multiple reloads.
        Tests that multiple reloads of the same file produce consistent results.
        """
        manager = ContextManager("product.md")
        
        # Load context multiple times
        contexts = []
        for _ in range(reload_count):
            context = manager.load_context(force_reload=True)
            contexts.append(context)
        
        # Property: All contexts should have identical content
        first_context = contexts[0]
        for context in contexts[1:]:
            assert context.content == first_context.content
            assert context.source_file == first_context.source_file
            assert context.is_valid()
        
        # Property: All contexts should parse sections identically
        first_sections = first_context.get_sections()
        for context in contexts[1:]:
            sections = context.get_sections()
            assert sections.keys() == first_sections.keys()
            for section_name in sections.keys():
                assert sections[section_name] == first_sections[section_name]