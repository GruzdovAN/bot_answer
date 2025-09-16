import re
from typing import Dict, List, Any

class SimpleParser:
    """Простой парсер для извлечения сущностей"""
    
    def __init__(self, parser_type: str):
        from config.parsers import PARSERS
        self.config = PARSERS.get(parser_type, {})
    
    def parse_message(self, message) -> Dict[str, Any]:
        """Парсинг сообщения"""
        text = message.text or ""
        
        return {
            'text': text,
            'hashtags': self.extract_hashtags(text),
            'mentions': self.extract_mentions(text),
            'links': self.extract_links(text),
            'technologies': self.extract_technologies(text),
            'companies': self.extract_companies(text),
        }
    
    def extract_hashtags(self, text: str) -> List[str]:
        """Извлечение хештегов"""
        if not self.config.get('extract_hashtags', False):
            return []
        return re.findall(r'#\w+', text)
    
    def extract_mentions(self, text: str) -> List[str]:
        """Извлечение упоминаний"""
        if not self.config.get('extract_mentions', False):
            return []
        return re.findall(r'@\w+', text)
    
    def extract_links(self, text: str) -> List[str]:
        """Извлечение ссылок"""
        if not self.config.get('extract_links', False):
            return []
        return re.findall(r'https?://[^\s]+', text)
    
    def extract_technologies(self, text: str) -> List[str]:
        """Извлечение технологий"""
        if not self.config.get('extract_technologies', False):
            return []
        
        technologies = []
        tech_list = self.config.get('technologies', [])
        for tech in tech_list:
            if tech.lower() in text.lower():
                technologies.append(tech)
        return technologies
    
    def extract_companies(self, text: str) -> List[str]:
        """Извлечение компаний"""
        if not self.config.get('extract_companies', False):
            return []
        
        companies = []
        company_list = self.config.get('companies', [])
        for company in company_list:
            if company.lower() in text.lower():
                companies.append(company)
        return companies
