"""
LLM handler module for interacting with the language model.
"""

import json
import logging
from typing import Dict, Any, Optional

from langchain_community.llms import Ollama
from config import model_config

# Configure logger
logger = logging.getLogger(__name__)


class LLMHandler:
    """Handler for LLM interactions"""
    
    def __init__(self):
        """Initialize the LLM handler with configured model."""
        self.model = self._initialize_model()
        
    def _initialize_model(self) -> Ollama:
        """Initialize and return the LLM model."""
        logger.info(f"Initializing Ollama model: {model_config.name}")
        logger.info(f"Using Ollama base URL: {model_config.base_url}")
        return Ollama(
            model=model_config.name,
            base_url=model_config.base_url,
            temperature=model_config.temperature,
            num_ctx=model_config.num_ctx,
            num_predict=model_config.num_predict,
        )
    
    def test_connection(self) -> bool:
        """Test the connection to the LLM service."""
        try:
            logger.info("Testing connection to Ollama...")
            self.model.invoke("test")
            logger.info("Ollama connection successful")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            return False
    
    def analyze_message(self, prompt: str) -> Dict[str, Any]:
        """
        Send a prompt to the LLM and return the parsed decision.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            A dictionary containing the parsed decision
        
        Raises:
            ValueError: If the response could not be parsed as JSON
        """
        logger.info("Sending prompt to LLM for analysis")
        response_text = self.model.invoke(prompt)
        logger.debug(f"Raw LLM response: {response_text[:100]}...")
        
        # Parse the response
        decision = self._extract_json_from_response(response_text)
        logger.info(f"Extracted decision with action: {decision.get('action', 'unknown')}")
        
        return decision
    
    def _extract_json_from_response(self, response_text: str) -> Dict[str, Any]:
        """
        Extract JSON from the LLM response text.
        
        Args:
            response_text: The raw response from the LLM
            
        Returns:
            A dictionary parsed from the JSON in the response
            
        Raises:
            ValueError: If no valid JSON could be extracted
        """
        json_text = ""
        
        # Try different extraction methods in order of preference
        if "```json" in response_text and "```" in response_text:
            json_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text and "```" in response_text[response_text.find("```")+3:]:
            json_text = response_text.split("```")[1].strip()
        elif "{" in response_text and "}" in response_text:
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}") + 1
            if start_idx >= 0 and end_idx > 0:
                json_text = response_text[start_idx:end_idx].strip()
        else:
            json_text = response_text.strip()
        
        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from LLM response: {response_text}")
            raise ValueError("Could not parse JSON from LLM response")


# Create a singleton instance
llm_handler = LLMHandler()