"""
Context Manager for Bangalore Local Guide
Handles loading and managing the product.md knowledge base.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LocalContext:
    """Data model for local context information."""
    content: str
    source_file: str
    last_updated: datetime
    
    def is_valid(self) -> bool:
        """Check if the context is valid and has content."""
        return bool(self.content and self.source_file)
    
    def get_sections(self) -> Dict[str, str]:
        """Parse content into sections for easier access."""
        sections = {}
        current_section = None
        current_content = []
        
        for line in self.content.split('\n'):
            if line.startswith('## '):
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = line[3:].strip()
                current_content = []
            else:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(current_content)
        
        return sections


class ContextManager:
    """Manages loading and validation of Bangalore knowledge context."""
    
    def __init__(self, product_file_path: str = "product.md"):
        """
        Initialize context manager.
        
        Args:
            product_file_path: Path to the product.md file
        """
        self.product_file_path = Path(product_file_path)
        self._cached_context: Optional[LocalContext] = None
        self._last_check_time: Optional[datetime] = None
    
    def load_context(self, force_reload: bool = False) -> LocalContext:
        """
        Load context from product.md file.
        
        Args:
            force_reload: Force reload even if cached version exists
            
        Returns:
            LocalContext object with loaded content
            
        Raises:
            FileNotFoundError: If product.md file doesn't exist
            ValueError: If file content is invalid
        """
        try:
            # Check if we need to reload
            if not force_reload and self._cached_context and self._is_cache_valid():
                logger.info("Using cached context")
                return self._cached_context
            
            # Validate file exists
            if not self.product_file_path.exists():
                raise FileNotFoundError(
                    f"Product knowledge file not found: {self.product_file_path}"
                )
            
            # Load file content
            logger.info(f"Loading context from {self.product_file_path}")
            with open(self.product_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Validate content
            if not content.strip():
                raise ValueError("Product file is empty")
            
            if len(content) < 1000:  # Minimum content length check
                raise ValueError("Product file content appears incomplete")
            
            # Create context object
            file_stat = self.product_file_path.stat()
            context = LocalContext(
                content=content,
                source_file=str(self.product_file_path),
                last_updated=datetime.fromtimestamp(file_stat.st_mtime)
            )
            
            # Validate context structure
            self._validate_context_structure(context)
            
            # Cache the context
            self._cached_context = context
            self._last_check_time = datetime.now()
            
            logger.info("Context loaded successfully")
            return context
            
        except FileNotFoundError as e:
            logger.error(f"Context file not found: {e}")
            raise
        except ValueError as e:
            logger.error(f"Invalid context content: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading context: {e}")
            raise ValueError(f"Failed to load context: {str(e)}")
    
    def _is_cache_valid(self) -> bool:
        """Check if cached context is still valid."""
        if not self._cached_context or not self._last_check_time:
            return False
        
        # Check if file has been modified since last load
        try:
            file_stat = self.product_file_path.stat()
            file_modified = datetime.fromtimestamp(file_stat.st_mtime)
            return file_modified <= self._cached_context.last_updated
        except OSError:
            return False
    
    def _validate_context_structure(self, context: LocalContext) -> None:
        """
        Validate that context has required sections.
        
        Args:
            context: LocalContext to validate
            
        Raises:
            ValueError: If required sections are missing
        """
        required_sections = [
            "City Overview",
            "Languages Spoken", 
            "Local Slang and Meanings",
            "Traffic Patterns and Peak Hours",
            "Popular Breakfast Spots and Street Food Areas",
            "Cultural Norms and Etiquette",
            "Practical Local Tips"
        ]
        
        content = context.content
        missing_sections = []
        
        for section in required_sections:
            if f"## {section}" not in content:
                missing_sections.append(section)
        
        if missing_sections:
            raise ValueError(
                f"Context missing required sections: {', '.join(missing_sections)}"
            )
    
    def get_context_summary(self) -> Dict[str, Any]:
        """
        Get summary information about loaded context.
        
        Returns:
            Dictionary with context metadata
        """
        if not self._cached_context:
            return {"status": "not_loaded"}
        
        sections = self._cached_context.get_sections()
        
        return {
            "status": "loaded",
            "source_file": self._cached_context.source_file,
            "last_updated": self._cached_context.last_updated.isoformat(),
            "content_length": len(self._cached_context.content),
            "sections_count": len(sections),
            "sections": list(sections.keys()),
            "is_valid": self._cached_context.is_valid()
        }
    
    def reload_context(self) -> LocalContext:
        """Force reload context from file."""
        return self.load_context(force_reload=True)
    
    def format_context_for_agent(self, context: Optional[LocalContext] = None) -> str:
        """
        Format context content for agent consumption.
        
        Args:
            context: Optional context to format, uses cached if None
            
        Returns:
            Formatted context string for agent
        """
        if context is None:
            context = self.load_context()
        
        formatted_content = f"""
BANGALORE LOCAL GUIDE KNOWLEDGE BASE
====================================

You are a friendly Bangalore local guide. Use ONLY the information provided below 
to answer questions. Do not make up any places, facts, or information not explicitly 
mentioned in this knowledge base.

{context.content}

IMPORTANT GUIDELINES:
- Always explain any local slang you use
- Recommend food based on time of day when relevant
- Give realistic traffic warnings
- Suggest metro during peak hours when appropriate
- Never hallucinate places or information not in this knowledge base
- Be helpful, practical, and culturally aware
- Keep responses concise but informative
"""
        
        return formatted_content


# Convenience function for easy import
def load_bangalore_context(product_file_path: str = "product.md") -> LocalContext:
    """
    Convenience function to load Bangalore context.
    
    Args:
        product_file_path: Path to product.md file
        
    Returns:
        LocalContext with loaded Bangalore knowledge
    """
    manager = ContextManager(product_file_path)
    return manager.load_context()


if __name__ == "__main__":
    # Test the context manager
    try:
        manager = ContextManager()
        context = manager.load_context()
        print("Context loaded successfully!")
        print(f"Content length: {len(context.content)} characters")
        print(f"Sections: {len(context.get_sections())} found")
        print("\nContext summary:")
        summary = manager.get_context_summary()
        for key, value in summary.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"Error: {e}")