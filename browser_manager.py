import time
import random
from playwright.sync_api import sync_playwright
from actions import HumanAction
from utils import rotate_user_agent, parse_proxy, spoof_fingerprint
from profiles import ProfileManager

class BrowserManager:
    def __init__(self, profile_manager=None):
        """Initialize browser manager with optional profile manager"""
        self.profile_manager = profile_manager or ProfileManager()
        self.active_browsers = {}

    def _setup_playwright_browser(self, profile_id, proxy=None):
        """Setup Playwright browser with anti-detection measures"""
        try:
            playwright = sync_playwright().start()
            
            # Get or create profile
            profile = self.profile_manager.get_profile(profile_id)
            
            # Browser launch options
            browser_options = {
                'headless': True,  # Run in headless mode since we're in a web environment
                'args': [
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--no-sandbox',  # Required for running in container
                    '--disable-setuid-sandbox',
                ]
            }

            # Add proxy if provided
            if proxy:
                proxy_config = parse_proxy(proxy)
                if proxy_config:
                    browser_options['proxy'] = {
                        'server': proxy_config['server'],
                        'username': proxy_config['username'],
                        'password': proxy_config['password']
                    }

            # Launch browser
            browser = playwright.chromium.launch(**browser_options)
            
            # Create context with specific device profile
            context = browser.new_context(
                user_agent=rotate_user_agent(),
                viewport=profile['settings']['viewport'],
                locale=profile['settings']['language'],
                timezone_id=profile['settings']['timezone'],
                geolocation=profile['settings']['geolocation'],
            )

            # Load cookies if available
            if profile['cookies']:
                context.add_cookies(profile['cookies'])

            return playwright, browser, context

        except Exception as e:
            raise Exception(f"Failed to setup Playwright browser: {str(e)}")

    def launch_browser_instance(self, instance_id, url, proxy=None, min_time=5, max_time=15, log_callback=None):
        """Launch a browser instance with specified parameters"""
        try:
            profile_id = f"profile_{instance_id}"
            
            # Setup browser
            playwright, browser, context = self._setup_playwright_browser(profile_id, proxy)
            page = context.new_page()
            
            browser_context = {
                'playwright': playwright,
                'browser': browser,
                'context': context,
                'page': page
            }

            # Store browser context
            self.active_browsers[instance_id] = browser_context

            # Navigate to URL
            page.goto(url)
            if log_callback:
                log_callback(f"Instance {instance_id}: Navigated to {url}")

            # Take screenshot for verification
            screenshot_path = f"instance_{instance_id}_screenshot.png"
            page.screenshot(path=screenshot_path)
            if log_callback:
                log_callback(f"Instance {instance_id}: Screenshot saved to {screenshot_path}")

            # Simulate human behavior
            self._simulate_human_behavior(instance_id)

            # Random close time
            close_time = random.uniform(min_time, max_time)
            time.sleep(close_time)

            # Close browser
            self.close_browser_instance(instance_id)
            if log_callback:
                log_callback(f"Instance {instance_id}: Closed after {close_time:.1f} seconds")

        except Exception as e:
            if log_callback:
                log_callback(f"Instance {instance_id} failed: {str(e)}")
            self.close_browser_instance(instance_id)
            raise

    def _simulate_human_behavior(self, instance_id):
        """Simulate random human-like behavior in the browser"""
        try:
            browser_context = self.active_browsers.get(instance_id)
            if not browser_context:
                return

            page = browser_context['page']
            actions = HumanAction()
            
            # Simulate scrolling
            actions.simulate_scroll(
                page,
                direction=random.choice(['up', 'down']),
                amount=random.randint(300, 1000)
            )
            
            # Random mouse movements
            actions.simulate_random_movement(page)
            
            # Random clicks (if needed)
            if random.random() < 0.3:  # 30% chance
                actions.simulate_click(page)

        except Exception as e:
            print(f"Failed to simulate human behavior: {str(e)}")

    def close_browser_instance(self, instance_id):
        """Close a specific browser instance"""
        try:
            browser_context = self.active_browsers.get(instance_id)
            if not browser_context:
                return

            # Save cookies before closing
            if self.profile_manager:
                cookies = browser_context['context'].cookies()
                self.profile_manager.update_cookies(f"profile_{instance_id}", cookies)
            
            # Close Playwright browser
            browser_context['page'].close()
            browser_context['context'].close()
            browser_context['browser'].close()
            browser_context['playwright'].stop()

            # Remove from active browsers
            del self.active_browsers[instance_id]

        except Exception as e:
            print(f"Failed to close browser instance {instance_id}: {str(e)}")

    def close_all_browsers(self):
        """Close all active browser instances"""
        instance_ids = list(self.active_browsers.keys())
        for instance_id in instance_ids:
            self.close_browser_instance(instance_id)