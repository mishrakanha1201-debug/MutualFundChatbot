"""
Data Storage Layer - Stores scraped data in JSON format
"""
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DataStorage:
    """Handles storage of scraped mutual fund data"""
    
    def __init__(self, data_dir: str = "data/scraped"):
        """
        Initialize data storage
        
        Args:
            data_dir: Directory to store scraped data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Data storage initialized at: {self.data_dir}")
    
    def save_fund_data(self, fund_data: Dict[str, Any], fund_name: str) -> Path:
        """
        Save fund data to JSON file
        
        Args:
            fund_data: Extracted fund data dictionary
            fund_name: Name of the fund
            
        Returns:
            Path to saved file
        """
        # Create safe filename from fund name
        safe_name = self._sanitize_filename(fund_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_name}_{timestamp}.json"
        filepath = self.data_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(fund_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Fund data saved to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving fund data to {filepath}: {e}")
            raise
    
    def save_consolidated_data(self, all_funds_data: List[Dict[str, Any]]) -> Path:
        """
        Save all funds data in a single consolidated file
        
        Args:
            all_funds_data: List of fund data dictionaries
            
        Returns:
            Path to saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"all_funds_{timestamp}.json"
        filepath = self.data_dir / filename
        
        consolidated = {
            "extraction_date": datetime.now().isoformat(),
            "total_funds": len(all_funds_data),
            "funds": all_funds_data
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(consolidated, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Consolidated data saved to: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving consolidated data to {filepath}: {e}")
            raise
    
    def load_fund_data(self, fund_name: str) -> Optional[Dict[str, Any]]:
        """
        Load most recent fund data
        
        Args:
            fund_name: Name of the fund
            
        Returns:
            Fund data dictionary or None if not found
        """
        safe_name = self._sanitize_filename(fund_name)
        pattern = f"{safe_name}_*.json"
        
        matching_files = list(self.data_dir.glob(pattern))
        if not matching_files:
            logger.warning(f"No data found for fund: {fund_name}")
            return None
        
        # Get most recent file
        latest_file = max(matching_files, key=lambda p: p.stat().st_mtime)
        
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Loaded fund data from: {latest_file}")
            return data
        except Exception as e:
            logger.error(f"Error loading fund data from {latest_file}: {e}")
            return None
    
    def list_all_funds(self) -> List[str]:
        """
        List all funds that have been scraped
        
        Returns:
            List of fund names
        """
        json_files = list(self.data_dir.glob("*.json"))
        funds = set()
        
        for file in json_files:
            # Extract fund name from filename (before timestamp)
            parts = file.stem.split('_')
            if len(parts) >= 2:
                # Reconstruct fund name (everything except last 2 parts which are date/time)
                fund_name = '_'.join(parts[:-2])
                funds.add(fund_name.replace('_', ' '))
        
        return sorted(list(funds))
    
    @staticmethod
    def _sanitize_filename(name: str) -> str:
        """
        Sanitize filename by removing/replacing invalid characters
        
        Args:
            name: Original name
            
        Returns:
            Sanitized filename
        """
        # Replace spaces and special characters
        sanitized = name.replace(' ', '_')
        sanitized = ''.join(c for c in sanitized if c.isalnum() or c in ('_', '-'))
        return sanitized

