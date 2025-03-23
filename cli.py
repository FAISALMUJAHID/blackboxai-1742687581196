import sys
import argparse
from browser_manager import BrowserManager
from profiles import ProfileManager
from utils import validate_inputs

def log_callback(message):
    """Print log messages to console"""
    print(message)

def main():
    parser = argparse.ArgumentParser(description='Anti-Detect Browser Automation CLI')
    parser.add_argument('url', help='URL to visit')
    parser.add_argument('--proxy', help='Proxy in format IP:PORT:USER:PASS (optional)', default='')
    parser.add_argument('--instances', type=int, help='Number of browser instances (1-10)', default=1)
    parser.add_argument('--min-time', type=int, help='Minimum time in seconds (5-300)', default=5)
    parser.add_argument('--max-time', type=int, help='Maximum time in seconds (5-300)', default=15)
    
    args = parser.parse_args()

    # Validate inputs
    valid, error_message = validate_inputs(
        args.url,
        args.proxy,
        args.instances,
        args.min_time,
        args.max_time
    )

    if not valid:
        print(f"Error: {error_message}")
        sys.exit(1)

    print("Starting browser automation...")
    browser_manager = BrowserManager(ProfileManager())

    try:
        for i in range(args.instances):
            instance_id = i + 1
            print(f"\nLaunching instance {instance_id}...")
            
            browser_manager.launch_browser_instance(
                instance_id,
                args.url,
                args.proxy,
                args.min_time,
                args.max_time,
                log_callback
            )

    except KeyboardInterrupt:
        print("\nStopping automation...")
        browser_manager.close_all_browsers()
    except Exception as e:
        print(f"\nError: {str(e)}")
        browser_manager.close_all_browsers()
        sys.exit(1)

    print("\nAutomation completed successfully!")

if __name__ == '__main__':
    main()