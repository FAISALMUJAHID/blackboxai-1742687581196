import random
import time
from utils import generate_bezier_curve

class HumanAction:
    @staticmethod
    def random_delay(min_delay=0.1, max_delay=1.5):
        """Add a random delay between actions"""
        time.sleep(random.uniform(min_delay, max_delay))

    @staticmethod
    def get_random_point(page, margin=50):
        """Get a random point within the viewport"""
        viewport = page.viewport_size
        x = random.randint(margin, viewport['width'] - margin)
        y = random.randint(margin, viewport['height'] - margin)
        return x, y

    @classmethod
    def simulate_click(cls, page, x=None, y=None):
        """Simulate a human-like mouse click using Playwright"""
        try:
            if x is None or y is None:
                x, y = cls.get_random_point(page)

            # Add random delay before click
            cls.random_delay(0.1, 0.3)
            
            # Click with random delay
            page.mouse.click(x, y, delay=random.randint(100, 300))
            
            # Small delay after click
            cls.random_delay(0.1, 0.3)

        except Exception as e:
            raise Exception(f"Click simulation failed: {str(e)}")

    @classmethod
    def simulate_scroll(cls, page, direction='down', amount=None):
        """Simulate human-like scrolling using Playwright"""
        try:
            if amount is None:
                amount = random.randint(100, 500)

            # Convert direction to multiplier
            multiplier = -1 if direction == 'up' else 1
            
            # Break scrolling into smaller chunks
            chunks = random.randint(3, 7)
            chunk_size = amount // chunks
            
            for _ in range(chunks):
                # Random delay between chunks
                cls.random_delay(0.1, 0.5)
                
                # Scroll chunk with random variation
                variation = random.randint(-20, 20)
                page.mouse.wheel(0, (chunk_size + variation) * multiplier)

        except Exception as e:
            raise Exception(f"Scroll simulation failed: {str(e)}")

    @classmethod
    def simulate_keystrokes(cls, page, text, min_delay=0.1, max_delay=0.3):
        """Simulate human-like typing using Playwright"""
        try:
            for char in text:
                # Random delay between keystrokes
                cls.random_delay(min_delay, max_delay)
                
                # Type character
                page.keyboard.type(char, delay=random.randint(100, 300))
                
                # Occasional longer pause (simulating thinking)
                if random.random() < 0.1:  # 10% chance
                    cls.random_delay(0.5, 1.5)

        except Exception as e:
            raise Exception(f"Keystroke simulation failed: {str(e)}")

    @classmethod
    def simulate_random_movement(cls, page):
        """Simulate random mouse movement using Playwright"""
        try:
            x, y = cls.get_random_point(page)
            
            # Move with random duration
            page.mouse.move(x, y)
            cls.random_delay(0.5, 2.0)

        except Exception as e:
            raise Exception(f"Random movement simulation failed: {str(e)}")

    @classmethod
    def simulate_natural_behavior(cls, page, duration=5):
        """Simulate natural human behavior for a specified duration"""
        try:
            end_time = time.time() + duration
            while time.time() < end_time:
                # Choose a random action
                action = random.choice([
                    'move',
                    'click',
                    'scroll',
                    'pause'
                ])

                if action == 'move':
                    cls.simulate_random_movement(page)
                elif action == 'click':
                    cls.simulate_click(page)
                elif action == 'scroll':
                    cls.simulate_scroll(
                        page,
                        direction=random.choice(['up', 'down'])
                    )
                else:  # pause
                    cls.random_delay(0.5, 2.0)

        except Exception as e:
            raise Exception(f"Natural behavior simulation failed: {str(e)}")