#!/usr/bin/env python
import pytest
import sys
from rich.console import Console
from rich.panel import Panel
from aider_config.utils.logger import TestLogger
from pathlib import Path

console = Console()
logger = TestLogger()

class TestResultCollector:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.current_test = None

def pytest_runtest_protocol(item, nextitem):
    logger.log_test_start(item.name)
    TestResultCollector.current_test = item.name
    return None

def pytest_runtest_logreport(report):
    if report.when == 'call':
        result = report.outcome == 'passed'
        logger.log_test_result(
            TestResultCollector.current_test,
            result,
            str(report.longrepr) if not result else None
        )
        if result:
            TestResultCollector.passed += 1
        else:
            TestResultCollector.failed += 1
    elif report.outcome == 'skipped':
        TestResultCollector.skipped += 1

def main():
    console.print(Panel.fit(
        "[bold blue]Running Aider Config Tests[/bold blue]\n\n"
        "Testing configuration manager and AI assistant..."
    ))
    
    logger.start_test_session()
    
    try:
        # Create test collector
        collector = TestResultCollector()
        
        # Run pytest with custom plugins
        result = pytest.main([
            '-v',
            '--capture=no',
            'tests/',
            '-p', 'no:warnings',
            '--tb=short'
        ])
        
        # Log final results
        logger.end_test_session(
            collector.passed,
            collector.failed,
            collector.skipped
        )
        
        if result == 0:
            console.print("\n[bold green]All tests passed! ✨[/bold green]")
        else:
            console.print("\n[bold red]Some tests failed! ❌[/bold red]")
        
        # Show log file location
        console.print(f"\nDetailed test log available at: {logger.log_file}")
        
    except Exception as e:
        logger.log_error(e)
        return 1
    
    return result

if __name__ == "__main__":
    sys.exit(main())
