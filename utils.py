import re
import random
from urllib.parse import urlparse

# List of modern user agents for rotation
USER_AGENTS = [
    # Windows Chrome
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Windows Firefox
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    # Windows Edge
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    # iPhone
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1.2 Mobile/15E148 Safari/604.1",
    # Android
    "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.144 Mobile Safari/537.36"
]

def rotate_user_agent():
    """Return a random user agent from the predefined list."""
    return random.choice(USER_AGENTS)

def parse_proxy(proxy_string):
    """
    Parse proxy string in format IP:PORT:USER:PASS
    Returns a dictionary with proxy configuration
    """
    if not proxy_string:
        return None
        
    try:
        parts = proxy_string.split(':')
        if len(parts) == 2:  # IP:PORT format
            return {
                'server': f'http://{parts[0]}:{parts[1]}',
                'username': None,
                'password': None
            }
        elif len(parts) == 4:  # IP:PORT:USER:PASS format
            return {
                'server': f'http://{parts[0]}:{parts[1]}',
                'username': parts[2],
                'password': parts[3]
            }
        else:
            raise ValueError("Invalid proxy format")
    except Exception as e:
        raise ValueError(f"Invalid proxy string format: {str(e)}")

def spoof_fingerprint():
    """
    Return a random device profile for browser spoofing
    """
    devices = [
        "iPhone 12",
        "Pixel 5",
        "iPad Pro",
        "Galaxy S20",
        "Desktop Windows"
    ]
    return random.choice(devices)

def validate_inputs(url, proxy, instance_count, min_time, max_time):
    """
    Validate all input parameters
    Returns: (bool, str) - (is_valid, error_message)
    """
    # Validate URL
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            return False, "Invalid URL format. Must include http:// or https://"
    except:
        return False, "Invalid URL format"

    # Validate proxy if provided
    if proxy:
        try:
            parse_proxy(proxy)
        except ValueError as e:
            return False, str(e)

    # Validate instance count
    if not isinstance(instance_count, int) or not 1 <= instance_count <= 10:
        return False, "Instance count must be between 1 and 10"

    # Validate time range
    try:
        min_time = float(min_time)
        max_time = float(max_time)
        if min_time < 0 or max_time < 0:
            return False, "Time values cannot be negative"
        if min_time > max_time:
            return False, "Minimum time cannot be greater than maximum time"
    except ValueError:
        return False, "Invalid time values"

    return True, ""

def generate_bezier_curve(start, end, num_points=20):
    """
    Generate a Bézier curve for smooth mouse movement
    Returns list of (x, y) coordinates
    """
    # Generate control points for natural curve
    control1 = (
        start[0] + (end[0] - start[0]) // 4 + random.randint(-50, 50),
        start[1] + (end[1] - start[1]) // 4 + random.randint(-50, 50)
    )
    control2 = (
        start[0] + 3 * (end[0] - start[0]) // 4 + random.randint(-50, 50),
        start[1] + 3 * (end[1] - start[1]) // 4 + random.randint(-50, 50)
    )
    
    points = []
    for i in range(num_points):
        t = i / (num_points - 1)
        # Cubic Bézier formula
        x = (1-t)**3 * start[0] + 3*(1-t)**2 * t * control1[0] + \
            3*(1-t) * t**2 * control2[0] + t**3 * end[0]
        y = (1-t)**3 * start[1] + 3*(1-t)**2 * t * control1[1] + \
            3*(1-t) * t**2 * control2[1] + t**3 * end[1]
        points.append((int(x), int(y)))
    
    return points