"""
Document Processor for RAG Pipeline
Handles chunking and preparation of scraped data for vector storage
"""
import json
from typing import List, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Processes scraped mutual fund data into chunks for RAG"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize document processor
        
        Args:
            chunk_size: Maximum characters per chunk
            chunk_overlap: Overlap between chunks for context preservation
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def load_fund_data(self, data_path: Path) -> Dict[str, Any]:
        """
        Load fund data from JSON file
        
        Args:
            data_path: Path to JSON file
            
        Returns:
            Fund data dictionary
        """
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading fund data from {data_path}: {e}")
            return {}
    
    def process_fund_to_chunks(self, fund_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Convert fund data into text chunks for embedding
        
        Args:
            fund_data: Fund data dictionary
            
        Returns:
            List of chunk dictionaries with metadata
        """
        chunks = []
        fund_name = fund_data.get('fund_name', 'Unknown Fund')
        
        # Extract structured data
        data = fund_data.get('data', {})
        sources = fund_data.get('sources', [])
        
        # Extract source URLs from sources list
        source_urls = []
        for source in sources:
            if isinstance(source, dict) and 'url' in source:
                source_urls.append(source['url'])
            elif isinstance(source, str):
                source_urls.append(source)
        
        # Get primary source URL (prefer HDFC, then SEBI, then AMFI, then Groww)
        primary_source_url = self._get_primary_source_url(source_urls, fund_name)
        
        # Create chunks from structured data
        # Chunk 1: Basic fund information
        basic_info = self._format_basic_info(fund_name, data)
        if basic_info:
            chunks.append({
                'text': basic_info,
                'metadata': {
                    'fund_name': fund_name,
                    'chunk_type': 'basic_info',
                    'source': 'structured_data',
                    'source_urls': source_urls,
                    'primary_source_url': primary_source_url
                }
            })
        
        # Chunk 2: Investment details
        investment_info = self._format_investment_details(fund_name, data)
        if investment_info:
            chunks.append({
                'text': investment_info,
                'metadata': {
                    'fund_name': fund_name,
                    'chunk_type': 'investment_details',
                    'source': 'structured_data',
                    'source_urls': source_urls,
                    'primary_source_url': primary_source_url
                }
            })
        
        # Chunk 3: Fees and charges
        fees_info = self._format_fees_charges(fund_name, data)
        if fees_info:
            chunks.append({
                'text': fees_info,
                'metadata': {
                    'fund_name': fund_name,
                    'chunk_type': 'fees_charges',
                    'source': 'structured_data',
                    'source_urls': source_urls,
                    'primary_source_url': primary_source_url
                }
            })
        
        # Chunk 4: Risk and performance
        risk_info = self._format_risk_performance(fund_name, data)
        if risk_info:
            chunks.append({
                'text': risk_info,
                'metadata': {
                    'fund_name': fund_name,
                    'chunk_type': 'risk_performance',
                    'source': 'structured_data',
                    'source_urls': source_urls,
                    'primary_source_url': primary_source_url
                }
            })
        
        # Chunk 5: Additional information
        additional_info = self._format_additional_info(fund_name, data)
        if additional_info:
            chunks.append({
                'text': additional_info,
                'metadata': {
                    'fund_name': fund_name,
                    'chunk_type': 'additional_info',
                    'source': 'structured_data',
                    'source_urls': source_urls,
                    'primary_source_url': primary_source_url
                }
            })
        
        logger.info(f"Created {len(chunks)} chunks for {fund_name}")
        return chunks
    
    def _format_basic_info(self, fund_name: str, data: Dict[str, Any]) -> str:
        """Format basic fund information"""
        parts = [f"Fund Name: {fund_name}"]
        
        if 'fund_category' in data:
            parts.append(f"Category: {data['fund_category']}")
        if 'scheme_type' in data:
            parts.append(f"Scheme Type: {data['scheme_type']}")
        if 'asset_class' in data:
            parts.append(f"Asset Class: {data['asset_class']}")
        if 'launch_date' in data:
            parts.append(f"Launch Date: {data['launch_date']}")
        if 'investment_objective' in data:
            parts.append(f"Investment Objective: {data['investment_objective']}")
        
        return "\n".join(parts)
    
    def _format_investment_details(self, fund_name: str, data: Dict[str, Any]) -> str:
        """Format investment-related details"""
        parts = [f"Investment Details for {fund_name}:"]
        
        if 'minimum_sip' in data:
            parts.append(f"Minimum SIP Amount: {data['minimum_sip']}")
        if 'minimum_sip_amount' in data:
            parts.append(f"Minimum SIP Amount: {data['minimum_sip_amount']}")
        if 'minimum_lumpsum' in data:
            parts.append(f"Minimum Lumpsum Investment: {data['minimum_lumpsum']}")
        if 'minimum_lumpsum_investment' in data:
            parts.append(f"Minimum Lumpsum Investment: {data['minimum_lumpsum_investment']}")
        if 'lock_in_period' in data:
            parts.append(f"Lock-in Period: {data['lock_in_period']}")
        if 'available_plans' in data:
            parts.append(f"Available Plans: {data['available_plans']}")
        if 'available_options' in data:
            parts.append(f"Available Options: {data['available_options']}")
        
        return "\n".join(parts) if len(parts) > 1 else ""
    
    def _format_fees_charges(self, fund_name: str, data: Dict[str, Any]) -> str:
        """Format fees and charges information"""
        parts = [f"Fees and Charges for {fund_name}:"]
        
        if 'expense_ratio' in data:
            expense_ratio = data['expense_ratio']
            # Format expense ratio nicely
            if isinstance(expense_ratio, dict):
                if 'direct_plan' in expense_ratio and 'regular_plan' in expense_ratio:
                    parts.append(f"Expense Ratio - Direct Plan: {expense_ratio['direct_plan']}")
                    parts.append(f"Expense Ratio - Regular Plan: {expense_ratio['regular_plan']}")
                    if 'as_on_date' in expense_ratio:
                        parts.append(f"As on Date: {expense_ratio['as_on_date']}")
                else:
                    parts.append(f"Expense Ratio: {expense_ratio}")
            elif isinstance(expense_ratio, list):
                for er in expense_ratio:
                    if isinstance(er, dict):
                        plan_type = er.get('plan_type', 'Unknown')
                        value = er.get('value', 'N/A')
                        unit = er.get('unit', '')
                        date = er.get('as_on_date', '')
                        parts.append(f"Expense Ratio - {plan_type}: {value}{unit} (as on {date})")
                    else:
                        parts.append(f"Expense Ratio: {er}")
            else:
                parts.append(f"Expense Ratio: {expense_ratio}")
        if 'exit_load' in data:
            parts.append(f"Exit Load: {data['exit_load']}")
        if 'entry_load' in data:
            parts.append(f"Entry Load: {data['entry_load']}")
        
        return "\n".join(parts) if len(parts) > 1 else ""
    
    def _format_risk_performance(self, fund_name: str, data: Dict[str, Any]) -> str:
        """Format risk and performance information"""
        parts = [f"Risk and Performance for {fund_name}:"]
        
        if 'riskometer' in data:
            parts.append(f"Riskometer Rating: {data['riskometer']}")
        if 'benchmark_index' in data:
            parts.append(f"Benchmark Index: {data['benchmark_index']}")
        if 'benchmark' in data:
            parts.append(f"Benchmark Index: {data['benchmark']}")
        if 'nav' in data:
            parts.append(f"NAV: {data['nav']}")
        if 'aum' in data:
            parts.append(f"AUM (Assets Under Management): {data['aum']}")
        if 'fund_managers' in data:
            parts.append(f"Fund Manager(s): {data['fund_managers']}")
        
        return "\n".join(parts) if len(parts) > 1 else ""
    
    def _format_additional_info(self, fund_name: str, data: Dict[str, Any]) -> str:
        """Format additional information"""
        parts = [f"Additional Information for {fund_name}:"]
        
        # Include any other relevant fields
        excluded_fields = {
            'fund_name', 'fund_category', 'scheme_type', 'asset_class', 'launch_date',
            'investment_objective', 'minimum_sip', 'minimum_lumpsum', 'lock_in_period',
            'available_plans', 'available_options', 'expense_ratio', 'exit_load',
            'entry_load', 'riskometer', 'benchmark_index', 'nav', 'aum', 'fund_managers'
        }
        
        for key, value in data.items():
            if key not in excluded_fields and not key.endswith('_alternatives'):
                if value and str(value).strip():
                    parts.append(f"{key.replace('_', ' ').title()}: {value}")
        
        return "\n".join(parts) if len(parts) > 1 else ""
    
    def process_all_funds(self, data_dir: Path) -> List[Dict[str, Any]]:
        """
        Process all fund data files into chunks
        
        Args:
            data_dir: Directory containing fund data JSON files
            
        Returns:
            List of all chunks from all funds
        """
        all_chunks = []
        
        # Process consolidated file if exists
        consolidated_file = data_dir / "all_funds_*.json"
        consolidated_files = list(data_dir.glob("all_funds_*.json"))
        
        if consolidated_files:
            latest_consolidated = max(consolidated_files, key=lambda p: p.stat().st_mtime)
            logger.info(f"Processing consolidated file: {latest_consolidated}")
            data = self.load_fund_data(latest_consolidated)
            
            funds = data.get('funds', [])
            for fund_data in funds:
                chunks = self.process_fund_to_chunks(fund_data)
                all_chunks.extend(chunks)
        
        # Also process individual fund files
        individual_files = list(data_dir.glob("HDFC_*.json"))
        processed_funds = set()
        
        for file_path in individual_files:
            fund_data = self.load_fund_data(file_path)
            fund_name = fund_data.get('fund_name', '')
            
            # Skip if already processed from consolidated file
            if fund_name not in processed_funds:
                chunks = self.process_fund_to_chunks(fund_data)
                all_chunks.extend(chunks)
                processed_funds.add(fund_name)
        
        logger.info(f"Total chunks created: {len(all_chunks)}")
        return all_chunks
    
    def _get_primary_source_url(self, source_urls: List[str], fund_name: str) -> str:
        """
        Get the primary source URL, prioritizing HDFC > SEBI > AMFI > Groww > any other source
        
        Args:
            source_urls: List of source URLs
            fund_name: Fund name for fallback URL generation
            
        Returns:
            Primary source URL
        """
        if not source_urls:
            # Fallback: try to load from config
            return self._get_fallback_url(fund_name)
        
        # Priority order: HDFC > SEBI > AMFI > Groww > any other source
        for url in source_urls:
            if 'hdfcfund.com' in url:
                return url
        for url in source_urls:
            if 'sebi.gov.in' in url:
                return url
        for url in source_urls:
            if 'amfiindia.com' in url:
                return url
        for url in source_urls:
            if 'groww.in' in url:
                return url
        
        # Return first valid URL (any other source)
        for url in source_urls:
            if url and url.startswith('http'):
                return url
        
        # Final fallback
        return self._get_fallback_url(fund_name)
    
    def _get_fallback_url(self, fund_name: str) -> str:
        """
        Get fallback URL from config file
        
        Args:
            fund_name: Fund name
            
        Returns:
            Fallback URL
        """
        try:
            config_path = Path("config/fund_sources.json")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    for fund in config.get('funds', []):
                        if fund.get('name') == fund_name:
                            sources = fund.get('sources', {})
                            # Priority: HDFC > SEBI > AMFI > Groww
                            if 'hdfc' in sources:
                                return sources['hdfc']
                            if 'sebi' in sources:
                                return sources['sebi']
                            if 'amfi_pdf' in sources:
                                return sources['amfi_pdf']
                            if 'groww' in sources:
                                return sources['groww']
        except Exception as e:
            logger.warning(f"Error loading fallback URL: {e}")
        
        # Default fallback
        return "https://groww.in/p/mutual-funds"

