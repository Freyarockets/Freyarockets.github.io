import string
import random
import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By

# Initialize the browser driver
driver = webdriver.Chrome()

# Target URL containing the HTML form
TARGET_URL = "http://example.com" 
driver.get(TARGET_URL)

# --- Reinforcement Learning Configurations ---
ALPHABET = string.ascii_lowercase + string.digits
STRING_LENGTH = 3     # Shorter length simplifies state transitions for Q-learning demonstration
MAX_ATTEMPTS = 500
LEARNING_RATE = 0.1   # Alpha: how quickly the agent updates its beliefs
DISCOUNT_FACTOR = 0.9 # Gamma: priority given to future expected rewards
EPSILON = 0.2         # Exploration rate: 20% random choices vs 80% learned choices

# Initialize Q-Table: Maps state-action transitions
# Structure: { "current_partial_string": { "next_char": quality_score } }
q_table = {}
wrong_guesses_cache = set()

def get_q_values(state):
    """Retrieves or initializes the actions dictionary for a given state."""
    if state not in q_table:
        q_table[state] = {char: 0.0 for char in ALPHABET}
    return q_table[state]

def select_next_char(state):
    """Epsilon-Greedy choice: Explores randomly or exploits the best learned choice."""
    actions = get_q_values(state)
    if random.random() < EPSILON:
        return random.choice(ALPHABET)
    # Exploit: pick the letter with the highest Q-value
    return max(actions, key=actions.get)

def generate_rl_string():
    """Generates a complete string character-by-character based on the Q-table."""
    state = ""  # Start state is an empty string
    built_string = ""
    for _ in range(STRING_LENGTH):
        action = select_next_char(state)
        built_string += action
        state = built_string  # The state progresses as letters are appended
    return built_string

def update_q_table(sequence, reward):
    """Applies the Bellman Equation variant to penalize or reward sequence steps."""
    state = ""
    for i, char in enumerate(sequence):
        actions = get_q_values(state)
        old_q = actions[char]
        
        # Look ahead to the next state's maximum potential value
        next_state = state + char
        next_max = max(get_q_values(next_state).values()) if i < (STRING_LENGTH - 1) else 0
        
        # Temporal Difference update rule
        actions[char] = old_q + LEARNING_RATE * (reward + (DISCOUNT_FACTOR * next_max) - old_q)
        state = next_state

# --- Main Automation Loop ---
print("Running Reinforcement Learning Form Automation...", flush=True)

for attempt in range(1, MAX_ATTEMPTS + 1):
    current_guess = generate_rl_string()
    
    # Avoid testing identical duplicates if generated via random exploration
    while current_guess in wrong_guesses_cache:
        current_guess = generate_rl_string()
        
    print(f"Attempt {attempt}: Evaluating sequence '{current_guess}'...", flush=True)

    try:
        # Locate your target components
        input_field = driver.find_element(By.NAME, "input_field_name")
        submit_button = driver.find_element(By.ID, "submit_button_id")

        input_field.clear()
        input_field.send_keys(current_guess)
        submit_button.click()
        
        time.sleep(1) # Allow DOM mutation / network overhead
        page_source = driver.page_source

        if "Success" in page_source or "Correct" in page_source:
            print(f"\n🎉 Success! Correct string resolved: {current_guess}", flush=True)
            # Apply maximum positive reward to reinforce this path
            update_q_table(current_guess, reward=100)
            break
        else:
            # Storing the wrong guess inside our memory structures
            wrong_guesses_cache.add(current_guess)
            
            # Penalize the entire string trajectory for this wrong guess
            update_q_table(current_guess, reward=-10)
            
            # Reset page route if form breaks on submit
            # driver.get(TARGET_URL)

    except Exception as e:
        print(f"Automation execution halted: {e}", file=sys.stderr)
        break
else:
    print(f"\nReached execution limit ({MAX_ATTEMPTS}) without solving.", flush=True)

time.sleep(3)
driver.quit()
