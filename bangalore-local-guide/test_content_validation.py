"""
Unit tests for content validation of product.md
Tests that product.md contains all required sections and content.
"""

import pytest
import os
from pathlib import Path


def load_product_content():
    """Load product.md content for testing."""
    product_path = Path(__file__).parent / "product.md"
    if not product_path.exists():
        pytest.fail("product.md file not found")
    
    with open(product_path, 'r', encoding='utf-8') as f:
        return f.read()


class TestProductMdContent:
    """Test suite for product.md content validation."""
    
    @pytest.fixture
    def content(self):
        """Fixture to load product.md content."""
        return load_product_content()
    
    def test_file_exists(self):
        """Test that product.md file exists."""
        product_path = Path(__file__).parent / "product.md"
        assert product_path.exists(), "product.md file must exist"
    
    def test_city_overview_section(self, content):
        """Test that city overview section exists and has content."""
        assert "## City Overview" in content
        assert "Bangalore" in content or "Bengaluru" in content
        assert "Silicon Valley of India" in content
        assert "Garden City" in content
    
    def test_languages_section(self, content):
        """Test that languages section exists with required languages."""
        assert "## Languages Spoken" in content
        assert "Kannada" in content
        assert "English" in content
        assert "Hindi" in content
        assert "Tamil" in content
        assert "Telugu" in content
    
    def test_slang_section(self, content):
        """Test that slang section exists with definitions."""
        assert "## Local Slang and Meanings" in content
        assert "Scene illa maga" in content
        assert "Guru" in content
        assert "Machcha" in content
        assert "Sakkath" in content
        # Verify explanations are provided
        assert "not happening" in content or "not possible" in content
    
    def test_traffic_patterns_section(self, content):
        """Test that traffic patterns section exists with peak hours."""
        assert "## Traffic Patterns and Peak Hours" in content
        assert "Peak Traffic Hours" in content
        assert "8:00 AM" in content
        assert "6:00 PM" in content
        assert "Silk Board" in content
        assert "Metro" in content or "Namma Metro" in content
    
    def test_food_section(self, content):
        """Test that food section exists with breakfast spots and street food."""
        assert "## Popular Breakfast Spots and Street Food Areas" in content
        assert "Malleshwaram" in content
        assert "Basavanagudi" in content
        assert "VV Puram" in content
        assert "Dosa" in content
        assert "Idli" in content
    
    def test_cultural_norms_section(self, content):
        """Test that cultural norms section exists."""
        assert "## Cultural Norms and Etiquette" in content
        assert "Namaste" in content or "Namaskara" in content
        assert "respect" in content.lower()
        assert "temple" in content.lower()
    
    def test_practical_tips_section(self, content):
        """Test that practical tips section exists."""
        assert "## Practical Local Tips" in content
        assert "Transportation" in content
        assert "Weather" in content
        assert "Shopping" in content
        assert "Safety" in content
    
    def test_content_completeness(self, content):
        """Test that content has sufficient detail."""
        # Content should be substantial
        assert len(content) > 5000, "Content should be comprehensive"
        
        # Should have multiple sections
        section_count = content.count("##")
        assert section_count >= 7, "Should have at least 7 main sections"
        
        # Should have subsections
        subsection_count = content.count("###")
        assert subsection_count >= 10, "Should have detailed subsections"
    
    def test_no_placeholder_content(self, content):
        """Test that there are no placeholder texts."""
        placeholders = ["TODO", "TBD", "PLACEHOLDER", "[INSERT", "FIXME"]
        for placeholder in placeholders:
            assert placeholder not in content.upper(), f"Found placeholder: {placeholder}"
    
    def test_emergency_contacts(self, content):
        """Test that emergency contacts are included."""
        assert "Emergency" in content
        assert "Police: 100" in content
        assert "Fire: 101" in content
        assert "Ambulance: 108" in content


if __name__ == "__main__":
    pytest.main([__file__])