import tkinter as tk
import random
import math
from PIL import Image, ImageTk
import time
from pynput import keyboard
import pygame

class Monkey:
    def __init__(self, canvas, image, x=None, y=None):
        self.canvas = canvas
        self.image = image
        self.size = 50  # Small size
        
        # Random starting position if not specified
        if x is None or y is None:
            self.x = random.randint(50, canvas.winfo_screenwidth() - 100)
            self.y = random.randint(50, canvas.winfo_screenheight() - 100)
        else:
            self.x = x
            self.y = y
        
        # Random velocity
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        
        # Create the sprite on canvas
        self.sprite = canvas.create_image(self.x, self.y, image=self.image)
        
    def update(self, monkeys):
        screen_width = self.canvas.winfo_screenwidth()
        screen_height = self.canvas.winfo_screenheight()
        
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Bounce off walls
        if self.x <= self.size//2 or self.x >= screen_width - self.size//2:
            self.vx *= -1
            self.x = max(self.size//2, min(self.x, screen_width - self.size//2))
        
        if self.y <= self.size//2 or self.y >= screen_height - self.size//2:
            self.vy *= -1
            self.y = max(self.size//2, min(self.y, screen_height - self.size//2))
        
        # Check collision with other monkeys
        for other in monkeys:
            if other is not self:
                dx = self.x - other.x
                dy = self.y - other.y
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance < self.size:
                    # Simple elastic collision
                    angle = math.atan2(dy, dx)
                    
                    # Separate the monkeys
                    overlap = self.size - distance
                    self.x += math.cos(angle) * overlap / 2
                    self.y += math.sin(angle) * overlap / 2
                    other.x -= math.cos(angle) * overlap / 2
                    other.y -= math.sin(angle) * overlap / 2
                    
                    # Exchange velocities (simplified)
                    self.vx, other.vx = other.vx, self.vx
                    self.vy, other.vy = other.vy, self.vy
        
        # Update sprite position
        self.canvas.coords(self.sprite, self.x, self.y)

class MonkeyApp:
    def __init__(self, root, double_interval=60):
        """
        Initialize the Monkey Buddies app
        
        Args:
            root: tkinter root window
            double_interval: time in seconds between monkey doublings (default: 60)
        """
        self.root = root
        self.root.title("Monkey Buddies")
        self.double_interval = double_interval  # Configurable duplication time!
        
        # Initialize pygame mixer for audio
        pygame.mixer.init()
        
        # Load and play monkey sound on loop
        try:
            pygame.mixer.music.load("monkey.mp3")
            pygame.mixer.music.play(-1)  # -1 means loop forever
            print("🎵 Monkey sounds loaded and playing!")
        except Exception as e:
            print(f"Could not load monkey.mp3: {e}")
            print("Continuing without sound...")
        
        # Remove window decorations (no title bar, borders, close button)
        self.root.overrideredirect(True)
        
        # Make window transparent and always on top
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 1.0)
        
        # Fullscreen transparent canvas
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        
        # Create canvas
        self.canvas = tk.Canvas(root, width=screen_width, height=screen_height, 
                               bg='black', highlightthickness=0)
        self.canvas.pack()
        
        # Make canvas click-through (Windows specific - comment out on other OS)
        try:
            self.root.wm_attributes('-transparentcolor', 'black')
        except:
            pass
        
        # Disable window closing via standard methods
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # Load monkey image (you'll need to provide a monkey.png file)
        # For now, creating a simple placeholder
        self.monkey_image = self.create_placeholder_monkey()
        
        # Monkey list
        self.monkeys = []
        
        # Start with one monkey
        self.add_monkey()
        
        # Track time for doubling
        self.last_double_time = time.time()
        
        # Set up global keyboard listener for backslash
        self.setup_global_listener()
        
        # Start animation
        self.animate()
    
    def setup_global_listener(self):
        """Set up global keyboard listener that works anywhere"""
        def on_press(key):
            try:
                # Check if backslash is pressed
                if hasattr(key, 'char') and key.char == '\\':
                    print("Backslash detected! Closing...")
                    self.cleanup()
            except AttributeError:
                pass
        
        # Start the listener in a separate thread
        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.start()
        
    def create_placeholder_monkey(self):
        """Create a simple monkey-like image if no image is provided"""
        img = Image.new('RGBA', (50, 50), (0, 0, 0, 0))
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        
        # Draw a simple monkey face
        draw.ellipse([5, 5, 45, 45], fill='brown')  # Head
        draw.ellipse([15, 15, 22, 22], fill='white')  # Left eye
        draw.ellipse([28, 15, 35, 22], fill='white')  # Right eye
        draw.ellipse([17, 17, 20, 20], fill='black')  # Left pupil
        draw.ellipse([30, 17, 33, 20], fill='black')  # Right pupil
        draw.ellipse([20, 28, 30, 35], fill='tan')  # Snout
        draw.arc([22, 30, 28, 34], 0, 180, fill='black', width=2)  # Smile
        
        return ImageTk.PhotoImage(img)
    
    def load_custom_monkey(self, filepath):
        """Load a custom monkey image"""
        try:
            img = Image.open(filepath)
            img = img.resize((50, 50), Image.Resampling.LANCZOS)
            self.monkey_image = ImageTk.PhotoImage(img)
            print(f"Loaded custom monkey from {filepath}")
        except Exception as e:
            print(f"Error loading image: {e}")
            print("Using placeholder monkey instead")
    
    def add_monkey(self):
        """Add a new monkey to the screen"""
        monkey = Monkey(self.canvas, self.monkey_image)
        self.monkeys.append(monkey)
        print(f"Monkeys on screen: {len(self.monkeys)}")
    
    def animate(self):
        """Main animation loop"""
        # Update all monkeys
        for monkey in self.monkeys:
            monkey.update(self.monkeys)
        
        # Check if it's time to double
        current_time = time.time()
        if current_time - self.last_double_time >= self.double_interval:
            # Double the monkeys!
            current_count = len(self.monkeys)
            for _ in range(current_count):
                self.add_monkey()
            self.last_double_time = current_time
            print(f"🐵 DOUBLED! Now {len(self.monkeys)} monkeys!")
        
        # Continue animation
        self.root.after(16, self.animate)  # ~60 FPS
    
    def cleanup(self):
        """Clean exit"""
        print("Goodbye monkeys!")
        # Stop the music
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        # Stop keyboard listener
        if hasattr(self, 'listener'):
            self.listener.stop()
        self.root.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    
    # ⚙️ CONFIGURE DUPLICATION TIME HERE (in seconds)
    DUPLICATION_INTERVAL = 0.5  # Change this number!
    # Examples:
    # 10 = doubles every 10 seconds (chaos mode!)
    # 30 = doubles every 30 seconds (fast)
    # 60 = doubles every minute (default)
    # 120 = doubles every 2 minutes (slower)
    
    app = MonkeyApp(root, double_interval=DUPLICATION_INTERVAL)
    
    # Uncomment and modify this line to load your own monkey image:
    # app.load_custom_monkey("monkey.png")
    
    root.mainloop()