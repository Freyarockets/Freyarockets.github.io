import sys
import threading
import time
import numpy as np
import pygame
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai

# ==========================================
# 1. INITIALIZATION & CONFIGURATION
# ==========================================
# Configure Gemini AI Brain
genai.configure(api_key="YOUR_GEMINI_API_KEY")
model = genai.GenerativeModel('gemini-1.5-flash')
chat_session = model.start_chat(history=[])

# Configure Text-to-Speech Engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
# Try setting to a cleaner/cooler voice option if available
if len(voices) > 1:
    engine.setProperty('voice', voices[1].id) 
engine.setProperty('rate', 175) # Clear conversational speed

# Global App States
current_status = "IDLE"  # IDLE, LISTENING, THINKING, SPEAKING
audio_level = 10        # Base visualization wave amplitude
is_running = True

# ==========================================
# 2. CORE VOICE BOT WORKFLOW
# ==========================================
def run_voice_bot():
    global current_status, audio_level, is_running
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    
    # Let ambient noise adapt
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)

    while is_running:
        try:
            # --- STEP 1: Listen for voice ---
            current_status = "LISTENING"
            # Fake a little ripple effect for "Listening" state animation
            audio_level = 35 
            
            with mic as source:
                print("Listening...")
                audio_data = recognizer.listen(source, timeout=None, phrase_time_limit=7)
            
            # --- STEP 2: Process Voice to Text ---
            current_status = "THINKING"
            audio_level = 15
            print("Processing voice...")
            user_text = recognizer.recognize_google(audio_data)
            print(f"You: {user_text}")
            
            if any(word in user_text.lower() for word in ["exit", "goodbye", "quit", "bye"]):
                speak_response("Goodbye! System powering down.")
                is_running = False
                break

            # --- STEP 3: Get AI Brain Response ---
            prompt_modifier = f"Keep your answer short and conversational (1-2 sentences maximum). User said: {user_text}"
            response = chat_session.send_message(prompt_modifier)
            ai_text = response.text
            print(f"AI: {ai_text}")
            
            # --- STEP 4: Speak back to User ---
            speak_response(ai_text)
            
        except sr.UnknownValueError:
            print("Could not understand audio.")
        except Exception as e:
            print(f"System Error: {e}")
            time.sleep(1)

def speak_response(text):
    global current_status, audio_level
    current_status = "SPEAKING"
    
    # We use a separate thread or hook to simulate the waveform bounce while speaking
    def simulate_speaking_wave():
        while current_status == "SPEAKING":
            audio_level = np.random.randint(40, 110) # Heavy bouncing graphics
            time.sleep(0.05)
            
    wave_thread = threading.Thread(target=simulate_speaking_wave, daemon=True)
    wave_thread.start()
    
    engine.say(text)
    engine.runAndWait()
    
    current_status = "IDLE"
    audio_level = 10

# ==========================================
# 3. PYGAME NEON GRAPHICS VISUALIZER
# ==========================================
def draw_ui():
    global is_running, audio_level, current_status
    pygame.init()
    
    # UI Window Dimensions
    width, height = 700, 450
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("AI Core Voice Interface")
    clock = pygame.time.Clock()
    
    # Cool Sci-Fi Colors
    BG_COLOR = (10, 15, 28)
    TEXT_COLOR = (141, 169, 196)
    
    # Status Dependent Colors (Neon Glow palettes)
    STATUS_THEMES = {
        "IDLE": (0, 150, 255),        # Tech Blue
        "LISTENING": (0, 255, 127),   # Emerald Green
        "THINKING": (255, 165, 0),    # Warning Amber
        "SPEAKING": (238, 130, 238)   # Cyber Violet
    }
    
    font = pygame.font.SysFont("Consolas", 18, bold=True)
    status_font = pygame.font.SysFont("Consolas", 28, bold=True)
    
    # Time variable for smooth sin wave shifting
    time_tick = 0
    
    while is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
                
        screen.fill(BG_COLOR)
        time_tick += 0.15
        
        # Pull active neon color theme
        theme_color = STATUS_THEMES.get(current_status, (255, 255, 255))
        
        # ─── DRAW NEON AUDIO GRAPHIC RIPPLES ───
        # Draw multiple superimposed sine waves for a complex "living AI" appearance
        points = []
        for x in range(50, width - 50):
            # Form factor to pinch the ends of the sine wave together gracefully
            pinch_factor = np.sin(np.pi * (x - 50) / (width - 100)) 
            
            # Layered mathematical sin waves
            y = (height // 2) + int(
                audio_level * pinch_factor * np.sin(x * 0.04 + time_tick) * np.cos(x * 0.01 + time_tick * 0.5)
            )
            points.append((x, y))
            
        if len(points) > 1:
            # Draw glow backing lines
            pygame.draw.lines(screen, tuple(min(255, c + 40) for c in theme_color), False, points, 5)
            pygame.draw.lines(screen, theme_color, False, points, 2)
            
        # ─── DRAW TEXT METRICS ───
        # Header Box
        pygame.draw.rect(screen, (20, 30, 50), (40, 25, width-80, 50), border_radius=10)
        title_lbl = font.render("SYSTEM CORE // NEURAL VOICE LINK", True, (0, 210, 255))
        screen.blit(title_lbl, (60, 40))
        
        # Status Box
        status_lbl = status_font.render(f"AI STATUS: {current_status}", True, theme_color)
        screen.blit(status_lbl, (50, height - 70))
        
        hint_lbl = font.render("Say 'Exit' or close window to close connection.", True, TEXT_COLOR)
        screen.blit(hint_lbl, (50, height - 35))
        
        pygame.display.flip()
        clock.tick(60) # Smooth 60 FPS
        
    pygame.quit()
    sys.exit()

# ==========================================
# 4. EXECUTION
# ==========================================
if __name__ == "__main__":
    # Fire up the voice recording loop inside a background worker thread
    bot_thread = threading.Thread(target=run_voice_bot, daemon=True)
    bot_thread.start()
    
    # Run Pygame graphic updates in the main process thread
    draw_ui()
