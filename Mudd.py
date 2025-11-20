import tkinter as tk
import random
from PIL import Image, ImageTk
import time
from pynput import keyboard
import pygame

class CheemCheem:
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
    
    # Update position
    def update(self, cheems):
        screen_width = self.canvas.winfo_screenwidth()
        screen_height = self.canvas.winfo_screenheight()
        
        # Move cheem
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

class CheemApp:
    def __init__(self, root, double_interval=60):
        self.root = root
        self.double_interval = double_interval
        
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Load monkey sound
        try:
            self.cheem_sound = pygame.mixer.Sound("monkey.mp3")
            print("🐵 Cheem Cheem sound loaded!")
        except Exception as e:
            print(f"Could not load monkey.mp3: {e}")
            self.cheem_sound = None
        
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
        
        # Load Cheem image
        self.cheem_image = self.load_cheem("cheem.png")
        
        # Cheem Cheem list
        self.cheems = []
        self.add_cheem()
        
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
    
    def load_cheem(self, filepath):
        try:
            img = Image.open(filepath)
            img = img.resize((50, 50), Image.Resampling.LANCZOS)
            print(f"Loaded Cheem Cheem from {filepath}")
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error loading image: {e}")
            print("Using placeholder brown circle instead")
            img = Image.new('RGBA', (50, 50), (0, 0, 0, 0))
            from PIL import ImageDraw
            draw = ImageDraw.Draw(img)
            draw.ellipse([0, 0, 50, 50], fill='brown')
            return ImageTk.PhotoImage(img)
    
    def add_cheem(self):
        cheem = CheemCheem(self.canvas, self.cheem_image)
        self.cheems.append(cheem)
        print(f"Cheem Cheems on screen: {len(self.cheems)}")
    
    def animate(self):
        for cheem in self.cheems:
            cheem.update(self.cheems)
        
        current_time = time.time()
        if current_time - self.last_double_time >= self.double_interval:
            current_count = len(self.cheems)
            for _ in range(current_count):
                self.add_cheem()
            
            # Play sound once per doubling
            if self.cheem_sound:
                self.cheem_sound.play()
            
            self.last_double_time = current_time
            print(f"🐵 DOUBLED! Now {len(self.cheems)} Cheem Cheems!")
        
        # Continue animation
        self.root.after(16, self.animate)
    
    def cleanup(self):
        print("Goodbye Cheem Cheems!")
        if self.cheem_sound:
            self.cheem_sound.stop()
        pygame.mixer.quit()
        if hasattr(self, 'listener'):
            self.listener.stop()
        self.root.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    
    # ⚙️ Set how fast Cheems double (in seconds)
    DUPLICATION_INTERVAL = 1  # doubles every 1 second
    
    app = CheemApp(root, double_interval=DUPLICATION_INTERVAL)
    
    root.mainloop()
