import tkinter as tk
import random
from PIL import Image, ImageTk
import time
from pynput import keyboard
import pygame

class Monkey:
    def __init__(self, canvas, image, x=None, y=None):
        self.canvas = canvas
        self.image = image
        self.size = 50
        
        # Random starting position
        if x is None or y is None:
            self.x = random.randint(50, canvas.winfo_screenwidth() - 100)
            self.y = random.randint(50, canvas.winfo_screenheight() - 100)
        else:
            self.x = x
            self.y = y
        
        # Random velocity
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        
        # Create canvas image
        self.sprite = canvas.create_image(self.x, self.y, image=self.image)
    
    # Update position without monkey-to-monkey collision
    def update(self, monkeys):
        screen_width = self.canvas.winfo_screenwidth()
        screen_height = self.canvas.winfo_screenheight()
        
        # Move monkey
        self.x += self.vx
        self.y += self.vy
        
        # Bounce off walls
        if self.x <= self.size//2 or self.x >= screen_width - self.size//2:
            self.vx *= -1
            self.x = max(self.size//2, min(self.x, screen_width - self.size//2))
        
        if self.y <= self.size//2 or self.y >= screen_height - self.size//2:
            self.vy *= -1
            self.y = max(self.size//2, min(self.y, screen_height - self.size//2))
        
        # Update sprite position
        self.canvas.coords(self.sprite, self.x, self.y)

class MonkeyApp:
    def __init__(self, root, double_interval=60):
        self.root = root
        self.double_interval = double_interval
        
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Load monkey sound
        try:
            self.monkey_sound = pygame.mixer.Sound("monkey.mp3")
            print("🐵 Monkey sound loaded!")
        except Exception as e:
            print(f"Could not load monkey.mp3: {e}")
            self.monkey_sound = None
        
        # Remove window decorations
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 1.0)
        
        # Fullscreen canvas
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        self.canvas = tk.Canvas(root, width=screen_width, height=screen_height, 
                               bg='black', highlightthickness=0)
        self.canvas.pack()
        
        # Make black color transparent (Windows)
        try:
            self.root.wm_attributes('-transparentcolor', 'black')
        except:
            pass
        
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # Placeholder monkey image
        self.monkey_image = self.create_placeholder_monkey()
        
        # Monkey list
        self.monkeys = []
        self.add_monkey()
        
        # Track doubling time
        self.last_double_time = time.time()
        
        # Global listener for backslash
        self.setup_global_listener()
        
        # Start animation
        self.animate()
    
    def setup_global_listener(self):
        def on_press(key):
            try:
                if hasattr(key, 'char') and key.char == '\\':
                    print("Backslash detected! Exiting...")
                    self.cleanup()
            except AttributeError:
                pass
        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.start()
    
    def create_placeholder_monkey(self):
        img = Image.new('RGBA', (50, 50), (0, 0, 0, 0))
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        draw.ellipse([5, 5, 45, 45], fill='brown')  # Head
        draw.ellipse([15, 15, 22, 22], fill='white')  # Left eye
        draw.ellipse([28, 15, 35, 22], fill='white')  # Right eye
        draw.ellipse([17, 17, 20, 20], fill='black')  # Left pupil
        draw.ellipse([30, 17, 33, 20], fill='black')  # Right pupil
        draw.ellipse([20, 28, 30, 35], fill='tan')  # Snout
        draw.arc([22, 30, 28, 34], 0, 180, fill='black', width=2)  # Smile
        return ImageTk.PhotoImage(img)
    
    def load_custom_monkey(self, filepath):
        try:
            img = Image.open(filepath)
            img = img.resize((50, 50), Image.Resampling.LANCZOS)
            self.monkey_image = ImageTk.PhotoImage(img)
            print(f"Loaded custom monkey from {filepath}")
        except Exception as e:
            print(f"Error loading image: {e}")
            print("Using placeholder monkey instead")
    
    def add_monkey(self):
        monkey = Monkey(self.canvas, self.monkey_image)
        self.monkeys.append(monkey)
        print(f"Monkeys on screen: {len(self.monkeys)}")
    
    def animate(self):
        for monkey in self.monkeys:
            monkey.update(self.monkeys)
        
        current_time = time.time()
        if current_time - self.last_double_time >= self.double_interval:
            current_count = len(self.monkeys)
            for _ in range(current_count):
                self.add_monkey()
            
            # Play sound once per doubling
            if self.monkey_sound:
                self.monkey_sound.play()
            
            self.last_double_time = current_time
            print(f"🐵 DOUBLED! Now {len(self.monkeys)} monkeys!")
        
        # Continue animation
        self.root.after(16, self.animate)
    
    def cleanup(self):
        print("Goodbye monkeys!")
        if self.monkey_sound:
            self.monkey_sound.stop()
        pygame.mixer.quit()
        if hasattr(self, 'listener'):
            self.listener.stop()
        self.root.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    
    # ⚙️ Set how fast monkeys double (in seconds)
    DUPLICATION_INTERVAL = 1.0  # doubles every 1 second
    
    app = MonkeyApp(root, double_interval=DUPLICATION_INTERVAL)
    
    # Optional: load your own monkey image
    # app.load_custom_monkey("monkey.png")
    
    root.mainloop()
