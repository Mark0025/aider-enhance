import asyncio
from playwright.async_api import async_playwright
import json
import os
from datetime import datetime
import yaml
from typing import Dict, List, Optional

class ModelInfoScraper:
    def __init__(self):
        self.model_sources = {
            'anthropic': 'https://docs.anthropic.com/claude/reference/selecting-a-model',
            'openai': 'https://platform.openai.com/docs/models',
            'ollama': 'https://ollama.com/library',
            'aider': 'https://aider.chat/docs/models.html'
        }
        self.model_info = {}
        self.last_updated = None

    async def setup_browser(self):
        """Initialize browser with stealth mode"""
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        return playwright, browser, context

    async def scrape_anthropic_models(self, page) -> Dict:
        """Scrape Anthropic model information"""
        await page.goto(self.model_sources['anthropic'])
        models = await page.query_selector_all('.model-card')
        anthropic_models = {}
        
        for model in models:
            name = await model.query_selector('.model-name')
            specs = await model.query_selector('.model-specs')
            if name and specs:
                model_name = await name.inner_text()
                model_specs = await specs.inner_text()
                anthropic_models[model_name] = {
                    'specs': model_specs,
                    'provider': 'anthropic',
                    'last_updated': datetime.now().isoformat()
                }
        
        return anthropic_models

    async def scrape_openai_models(self, page) -> Dict:
        """Scrape OpenAI model information"""
        await page.goto(self.model_sources['openai'])
        models = await page.query_selector_all('.model-list-item')
        openai_models = {}
        
        for model in models:
            name = await model.query_selector('.model-name')
            if name:
                model_name = await name.inner_text()
                openai_models[model_name] = {
                    'provider': 'openai',
                    'last_updated': datetime.now().isoformat()
                }
        
        return openai_models

    async def update_aider_config(self, models: Dict):
        """Update Aider configuration with latest model information"""
        config_path = '.aider.conf.yml'
        
        config = {
            'model_configs': {
                'anthropic': {
                    'api_key': '${ANTHROPIC_API_KEY}',
                    'models': [m for m in models if models[m]['provider'] == 'anthropic']
                },
                'openai': {
                    'api_key': '${OPENAI_API_KEY}',
                    'models': [m for m in models if models[m]['provider'] == 'openai']
                }
            },
            'last_updated': datetime.now().isoformat()
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)

    async def run_scraper(self):
        """Main scraping function"""
        playwright, browser, context = await self.setup_browser()
        
        try:
            page = await context.new_page()
            
            # Scrape model information from different providers
            anthropic_models = await self.scrape_anthropic_models(page)
            openai_models = await self.scrape_openai_models(page)
            
            # Combine all model information
            self.model_info = {**anthropic_models, **openai_models}
            
            # Update Aider configuration
            await self.update_aider_config(self.model_info)
            
            # Save to JSON for reference
            with open('model_info.json', 'w') as f:
                json.dump(self.model_info, f, indent=2)
            
        finally:
            await browser.close()
            await playwright.stop()

    def get_latest_models(self) -> Dict:
        """Return the latest model information"""
        if os.path.exists('model_info.json'):
            with open('model_info.json', 'r') as f:
                return json.load(f)
        return {}

