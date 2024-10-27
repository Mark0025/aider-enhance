#!/usr/bin/env python
from aider_config.core.config_manager import AiderConfigManager
from rich.console import Console
from aider_config.utils.logger import TestLogger
import os

console = Console()
logger = TestLogger()

def main():
    logger.start_test_session()
    
    # Create test config path
    test_config_path = os.path.expanduser("~/test_aider.conf.yml")
    logger.logger.info(f"Using config path: {test_config_path}")
    
    # Initialize config manager
    manager = AiderConfigManager(config_path=test_config_path)
    
    try:
        # Log test steps
        logger.logger.info("Starting manual configuration test")
        
        # Run setup
        logger.logger.info("Running configuration setup")
        manager.setup()
        
        # Verify configuration
        logger.logger.info("Verifying configuration file")
        if os.path.exists(test_config_path):
            logger.logger.info("Configuration file created successfully")
        else:
            raise FileNotFoundError("Configuration file was not created")
        
        console.print("\n[bold green]Manual test completed successfully![/bold green]")
        console.print(f"Configuration saved to: {test_config_path}")
        logger.logger.info("Manual test completed successfully")
        
    except Exception as e:
        logger.log_error(e)
        console.print(f"\n[bold red]Error during manual test: {str(e)}[/bold red]")
        return 1
    
    finally:
        logger.end_test_session(1, 0, 0)  # Assuming one test run
        console.print(f"\nDetailed test log available at: {logger.log_file}")
    
    return 0

if __name__ == "__main__":
    main()
