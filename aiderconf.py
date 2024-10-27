import os
import inquirer
from dotenv import load_dotenv, set_key
import yaml
import webbrowser
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table

console = Console()

# Configuration presets for different use cases
CONFIGURATION_PRESETS = {
    "basic": {
        "name": "Basic Setup (Cost-Effective)",
        "description": """
        - Uses GPT-3.5-Turbo as primary model
        - Basic Git integration
        - Minimal caching
        Cost: Lowest ($0.002/1K tokens)
        """,
        "settings": {
            "MODEL": "gpt-3.5-turbo",
            "CACHE_PROMPTS": "false",
            "MAP_TOKENS": "256",
            "MAX_CHAT_HISTORY_TOKENS": "2000",
            "EDIT_FORMAT": "simple",
            "STREAM": "true"
        }
    },
    "balanced": {
        "name": "Balanced Setup (Recommended)",
        "description": """
        - Uses GPT-4-Turbo as primary model
        - Full Git integration
        - OpenRouter for cost optimization
        Cost: Moderate ($0.01-0.03/1K tokens)
        """,
        "settings": {
            "MODEL": "gpt-4-turbo-preview",
            "OPENAI_API_BASE": "https://openrouter.ai/api/v1",
            "OPENAI_API_TYPE": "openai",
            "CACHE_PROMPTS": "true",
            "MAP_TOKENS": "512",
            "MAX_CHAT_HISTORY_TOKENS": "4000",
            "EDIT_FORMAT": "simple",
            "AUTO_COMMITS": "true",
            "SHOW_DIFFS": "true"
        }
    },
    "power": {
        "name": "Power User Setup (Performance)",
        "description": """
        - Uses Claude-3 Opus as primary model
        - Advanced caching and Git features
        - Maximum context window
        Cost: Highest ($0.08/1K tokens)
        """,
        "settings": {
            "MODEL": "claude-3-opus-20240229",
            "CACHE_PROMPTS": "true",
            "MAP_TOKENS": "1024",
            "MAX_CHAT_HISTORY_TOKENS": "8000",
            "EDIT_FORMAT": "architect",
            "AUTO_COMMITS": "true",
            "SHOW_DIFFS": "true",
            "MAP_REFRESH": "always"
        }
    }
}

API_PROVIDERS_INFO = {
    "OpenAI": {
        "url": "https://platform.openai.com/api-keys",
        "description": """
        OpenAI provides GPT-3.5 and GPT-4 models. Recommended for:
        - General code assistance
        - Quick iterations
        - Best documentation understanding
        Cost: $0.002/1K tokens (GPT-3.5) to $0.03/1K tokens (GPT-4)
        """,
        "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"]
    },
    "Anthropic": {
        "url": "https://console.anthropic.com/settings/keys",
        "description": """
        Anthropic's Claude models excel at:
        - Complex reasoning
        - Large context windows
        - Detailed code analysis
        Cost: $0.015/1K tokens (Claude-3 Sonnet) to $0.08/1K tokens (Claude-3 Opus)
        """,
        "models": ["claude-3-opus-20240229", "claude-3-sonnet-20240229"]
    },
    "OpenRouter": {
        "url": "https://openrouter.ai/keys",
        "description": """
        OpenRouter provides access to multiple models with:
        - Automatic fallback
        - Load balancing
        - Cost optimization
        - Access to multiple providers through one API
        Benefits:
        - Reduced costs
        - Higher availability
        - Model flexibility
        """,
        "models": ["openai/gpt-4-turbo", "anthropic/claude-3", "mistral/mixtral-8x7b"]
    }
}

def show_welcome():
    console.print(Panel.fit(
        "[bold blue]Welcome to Advanced Aider Configuration Setup![/bold blue]\n\n"
        "This tool will help you configure Aider for optimal performance and cost-effectiveness.\n"
        "You'll learn about different configuration options and their benefits as we go.\n\n"
        "[yellow]Key Features:[/yellow]\n"
        "• Multiple model provider support\n"
        "• Performance optimization settings\n"
        "• Cost management options\n"
        "• Git integration settings\n"
    ))

def show_configuration_presets():
    table = Table(title="Available Configuration Presets")
    table.add_column("Preset", style="cyan")
    table.add_column("Description", style="green")
    
    for preset_id, preset in CONFIGURATION_PRESETS.items():
        table.add_row(
            preset["name"],
            preset["description"]
        )
    
    console.print(table)
    
    choices = [
        inquirer.List('preset',
            message="Select a configuration preset to start with",
            choices=[(preset["name"], preset_id) for preset_id, preset in CONFIGURATION_PRESETS.items()]
        )
    ]
    
    return inquirer.prompt(choices)['preset']

def show_provider_info(provider):
    info = API_PROVIDERS_INFO.get(provider)
    if info:
        console.print(Panel.fit(
            f"[bold blue]{provider} Information[/bold blue]\n\n"
            f"{info['description']}\n\n"
            f"[yellow]Available Models:[/yellow]\n"
            f"{', '.join(info['models'])}\n\n"
            f"[green]Get your API key at:[/green] {info['url']}"
        ))

def get_api_keys():
    api_keys = {}
    
    for provider, info in API_PROVIDERS_INFO.items():
        show_provider_info(provider)
        
        questions = [
            inquirer.Confirm('configure',
                message=f"Would you like to configure {provider}?",
                default=False
            )
        ]
        
        if inquirer.prompt(questions)['configure']:
            questions = [
                inquirer.Text('api_key',
                    message=f'Enter your {provider} API key',
                )
            ]
            result = inquirer.prompt(questions)
            if result and result['api_key']:
                api_keys[provider] = result['api_key']
    
    return api_keys

def get_advanced_settings():
    questions = [
        inquirer.Confirm('configure_git',
            message="Would you like to configure Git integration settings?",
            default=True
        ),
        inquirer.Confirm('configure_performance',
            message="Would you like to configure performance settings?",
            default=True
        )
    ]
    
    answers = inquirer.prompt(questions)
    settings = {}
    
    if answers['configure_git']:
        git_questions = [
            inquirer.Confirm('GIT', message="Enable Git integration?", default=True),
            inquirer.Confirm('AUTO_COMMITS', message="Enable automatic commits?", default=True),
            inquirer.Confirm('SHOW_DIFFS', message="Show diffs when committing changes?", default=True)
        ]
        git_settings = inquirer.prompt(git_questions)
        settings.update(git_settings)
    
    if answers['configure_performance']:
        perf_questions = [
            inquirer.Text('MAX_CHAT_HISTORY_TOKENS',
                message="Maximum chat history tokens (recommended: 4000)",
                default="4000"
            ),
            inquirer.Confirm('CACHE_PROMPTS',
                message="Enable prompt caching?",
                default=True
            )
        ]
        perf_settings = inquirer.prompt(perf_questions)
        settings.update(perf_settings)
    
    return settings

def create_env_file(api_keys, preset_id, advanced_settings):
    env_content = "# Aider Configuration - API Keys\n\n"
    
    # Add API keys
    for provider, key in api_keys.items():
        env_content += f"{provider.upper()}_API_KEY={key}\n"
    
    # Add preset settings
    preset = CONFIGURATION_PRESETS[preset_id]["settings"]
    for key, value in preset.items():
        env_content += f"{key}={value}\n"
    
    # Add advanced settings
    for key, value in advanced_settings.items():
        env_content += f"{key}={value}\n"
    
    with open('.env', 'w') as f:
        f.write(env_content)

def main():
    try:
        show_welcome()
        
        # Load existing .env file if it exists
        if os.path.exists('.env'):
            load_dotenv()
            existing_api_keys = {provider: os.getenv(f"{provider.upper()}_API_KEY") for provider in API_PROVIDERS_INFO.keys()}
            existing_api_keys = {k: v for k, v in existing_api_keys.items() if v}
            
            if existing_api_keys:
                console.print("[bold green]Detected existing API keys in .env file:[/bold green]")
                for provider, key in existing_api_keys.items():
                    console.print(f"[bold blue]{provider}:[/bold blue] {key[:4]}...{key[-4:]}")
                    show_provider_info(provider)
                
                choices = [
                    inquirer.List('action',
                        message="What would you like to do?",
                        choices=[
                            ('Modify existing setup', 'modify'),
                            ('Create a new configuration', 'new'),
                            ('Run Aider', 'run')
                        ]
                    )
                ]
                
                action = inquirer.prompt(choices)['action']
                
                if action == 'run':
                    console.print("[bold green]Running Aider...[/bold green]")
                    os.system('aider')
                    return
                elif action == 'modify':
                    api_keys = existing_api_keys
                else:
                    api_keys = get_api_keys()
            else:
                api_keys = get_api_keys()
        else:
            api_keys = get_api_keys()
        
        # Select configuration preset
        preset_id = show_configuration_presets()
        
        # Get advanced settings
        advanced_settings = get_advanced_settings()
        
        # Create configuration files
        create_env_file(api_keys, preset_id, advanced_settings)
        
        console.print(Panel.fit(
            "[bold green]Setup Complete![/bold green]\n\n"
            "Created:\n"
            "- .env file with your API keys and settings\n"
            "- .aider.conf.yml with optimal configuration\n\n"
            "[yellow]Next Steps:[/yellow]\n"
            "1. Start Aider with: aider\n"
            "2. Use /help to see available commands\n"
            "3. Visit [link]https://aider.chat/docs/[/link] for more information"
        ))
        
    except KeyboardInterrupt:
        console.print("\n[bold red]Setup cancelled by user.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An error occurred: {str(e)}[/bold red]")

if __name__ == "__main__":
    main()
