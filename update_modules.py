import asyncio
from model_scraper import ModelInfoScraper
import schedule
import time

async def update_models():
    scraper = ModelInfoScraper()
    await scraper.run_scraper()
    print(f"Models updated at {time.strftime('%Y-%m-%d %H:%M:%S')}")

def run_update():
    asyncio.run(update_models())

def main():
    # Run immediately on start
    run_update()
    
    # Schedule updates every 24 hours
    schedule.every(24).hours.do(run_update)
    
    while True:
        schedule.run_pending()
        time.sleep(3600)  # Check every hour

if __name__ == "__main__":
    main()