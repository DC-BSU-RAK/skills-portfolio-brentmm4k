from tkinter import *
from pathlib import Path
import random
import threading
# Try to import pygame for audio playback; gracefully degrade if not available
try:
    import pygame
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
# Try to import PIL for image manipulation and fade effects; gracefully degrade if not available
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

"""
Simple Alexa-style joke teller GUI.
Refactored into a class so widgets and state are instance attributes
(`self.*`) and easy to reuse or embed. Keeps the original behaviour
but fixes an off-by-one bug when choosing random jokes and adds
inline comments explaining key parts.

Submitted by: Brent Muli
"""
class AlexaJokeApp:
    """Application class for the joke UI."""

    def __init__(self, root):
        self.root = root
        self.root.title("Alexa Joke")
        self.root.geometry("700x500")
        # Set background to yellow
        self.root.configure(bg='#FFE86B')

        # Load jokes from `randomJokes.txt` located next to this script
        self.joke_list, self.punchline_list = self._load_jokes()

        # Load paths to audio and image resources from A1 - Resources folder
        # These are used to play laugh sound and display laugh image on punchline
        self.resource_dir = Path(__file__).resolve().parent / "A1 - Resources"
        self.laugh_audio = self.resource_dir / "laughsfx.mp3"
        self.laugh_image = self.resource_dir / "laugh.png"

        # Current selected index (starts random)
        self.current_joke_index = random.randint(0, max(len(self.joke_list) - 1, 0))
        # Track whether punchline has been shown for current joke
        self.punchline_shown = False
        # Track whether joke has been displayed (needed before showing punchline)
        # This ensures the user must click "Alexa tell me a joke" before showing punchline
        self.joke_displayed = False

        # UI widgets stored as instance attributes
        self.joke_label = Label(self.root, text="", font=20, bg='#FFE86B')
        self.joke_label.pack(pady=25)

        self.punchline_label = Label(self.root, text="", font=20, bg='#FFE86B')
        self.punchline_label.pack()

        # Button frame with yellow background
        self.buttons = Frame(self.root, bg='#FFE86B')
        self.buttons.pack(pady=25)

        # Buttons trigger instance methods with darker yellow background and spacing
        self.joke_button = Button(self.buttons, text="Alexa tell me a joke",
                                command=self.display_joke, font=40,
                                bg='#FCD217', fg='black')
        self.joke_button.pack(side=LEFT, padx=10)

        self.punchline_button = Button(self.buttons, text="Show punchline",
                                    command=self.show_punchline, font=40,
                                    bg='#FCD217', fg='black')
        self.punchline_button.pack(side=RIGHT, padx=10)

        self.next_button = Button(self.root, text="Next joke",
                                command=self.next_joke, font=30,
                                bg='#FCD217', fg='black')
        self.next_button.pack(pady=10)

        # Message label below Next joke button (shows in red)
        self.message_label = Label(self.root, text="", font=12, fg='black', bg='#FFE86B')
        self.message_label.pack()

        # Laugh image label (overlay for fade effect)
        self.laugh_image_label = Label(self.root, bg='#FFE86B')
        self.laugh_image_label.pack(pady=10)

    def _load_jokes(self):
        """Read `randomJokes.txt` and return (joke_list, punchline_list) lists.

        Each line is expected to contain a joke and punchline separated by
        a question mark ('?'). Lines that don't match the expected format are
        skipped.
        """
        # Try to find randomJokes.txt in A1 - Resources subdirectory first
        script_dir = Path(__file__).resolve().parent
        txt_path = script_dir / "A1 - Resources" / "randomJokes.txt"
        
        # Fallback: look in the same directory as the script
        if not txt_path.exists():
            txt_path = script_dir / "randomJokes.txt"
        
        joke_list = []
        punchline_list = []

        try:
            with txt_path.open('r', encoding='utf-8') as file:
                txt_content = file.read()
        except FileNotFoundError:
            # If the file is missing, provide a tiny fallback so the UI still works
            txt_content = "Why did the chicken cross the road?To get to the other side"

        for line in txt_content.splitlines():
            line = line.strip()
            if not line:
                continue
            # Split on the first '?' to allow '?' inside punchlines
            if '?' in line:
                joke_text, punchline_text = line.split('?', 1)
                joke_list.append(joke_text + "?")
                punchline_list.append(punchline_text)
            else:
                # Skip malformed line but continue loading others
                continue

        return joke_list, punchline_list

    def display_joke(self):
        """Display the current joke text (without punchline)."""
        if not self.joke_list:
            self.joke_label.config(text="(No jokes available)")
            return
        # Show the current joke from the list
        self.joke_label.config(text=self.joke_list[self.current_joke_index])
        # Mark joke as displayed so punchline button can work
        # This enforces the requirement that joke must be shown before punchline
        self.joke_displayed = True
        # Reset punchline_shown flag when displaying a new joke
        self.punchline_shown = False
        # Clear any previous prompt message
        self.message_label.config(text="")

    def show_punchline(self):
        """Display the punchline for the current joke."""
        # Only show punchline if joke has been displayed first
        # This guard ensures the user workflow: joke -> punchline -> next joke
        if not self.joke_displayed:
            return
        
        if not self.punchline_list:
            self.punchline_label.config(text="")
            return
        # Display the punchline for the current joke
        self.punchline_label.config(text=self.punchline_list[self.current_joke_index])
        # Mark punchline as shown; now show the prompt message to continue
        self.punchline_shown = True
        self.message_label.config(text="Press 'Next joke' to continue the silliness!")
        
        # Play laugh sound in a separate thread to avoid blocking UI
        # Only attempt if pygame is available and the audio file exists
        if PYGAME_AVAILABLE and self.laugh_audio.exists():
            threading.Thread(target=self._play_laugh_sound, daemon=True).start()
        
        # Display and fade in the laugh image
        # Only attempt if PIL is available and the image file exists
        if PIL_AVAILABLE and self.laugh_image.exists():
            threading.Thread(target=self._fade_in_laugh_image, daemon=True).start()

    def _play_laugh_sound(self):
        """Play the laugh sound effect using pygame mixer.
        
        Runs on a separate thread to keep UI responsive.
        Gracefully handles errors if pygame is unavailable or file is missing.
        """
        try:
            # Load the audio file and play it
            pygame.mixer.music.load(str(self.laugh_audio))
            pygame.mixer.music.play()
        except Exception as e:
            # Silently fail if audio playback is not available
            print(f"Error playing laugh sound: {e}")

    def _fade_in_laugh_image(self):
        """Load and fade in the laugh image with opacity animation.
        
        Runs on a separate thread to keep UI responsive.
        Gradually increases image opacity from 0 to 255 for a smooth fade effect.
        """
        try:
            # Load image and resize it to fit nicely in the UI
            img = Image.open(str(self.laugh_image))
            img.thumbnail((200, 200), Image.Resampling.LANCZOS)
            
            # Fade in effect: gradually increase opacity from 0 to 255
            # Step by 15 for ~17 frames over ~500ms for smooth animation
            for alpha in range(0, 256, 15):
                # Create a copy with adjusted alpha (transparency) level
                img_with_alpha = img.copy()
                img_with_alpha.putalpha(alpha)
                # Convert to PhotoImage for tkinter display
                photo = ImageTk.PhotoImage(img_with_alpha)
                
                # Update label with new image
                self.laugh_image_label.config(image=photo)
                # Keep a reference to prevent garbage collection
                self.laugh_image_label.image = photo
                # Force UI refresh
                self.root.update()
                
                # Small delay between frames (30ms) for smooth fade animation
                self.root.after(30)
        except Exception as e:
            # Silently fail if image display is not available
            print(f"Error displaying laugh image: {e}")

    def next_joke(self):
        """Choose a new random joke and clear the displayed text."""
        if not self.joke_list:
            return
        # Choose a valid random index (fix off-by-one from original)
        self.current_joke_index = random.randint(0, len(self.joke_list) - 1)
        # Clear all displayed content
        self.joke_label.config(text="")
        self.punchline_label.config(text="")
        # Clear the laugh image when moving to next joke
        self.laugh_image_label.config(image="")
        self.laugh_image_label.image = None
        # Reset all flags for the new joke cycle
        # joke_displayed must be False so punchline button won't work until joke is shown
        self.joke_displayed = False
        self.punchline_shown = False
        # Clear any prompt messages
        self.message_label.config(text="")

if __name__ == "__main__":
    root = Tk()
    app = AlexaJokeApp(root)
    root.mainloop()