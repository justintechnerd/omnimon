from gpiozero import Button
import time

# Test GPIO pin mappings
button_pins = [16, 5, 13, 6, 26, 19, 21, 20, 15, 12, 14, 23]

# Create buttons with pull-up resistors
buttons = {pin: Button(pin, pull_up=True, bounce_time=0.05) for pin in button_pins}

# Callback functions
def button_pressed(pin):
    print(f"GPIO {pin} PRESSED!")

def button_released(pin):
    print(f"GPIO {pin} RELEASED!")

# Assign callbacks
for pin, button in buttons.items():
    button.when_pressed = lambda pin=pin: button_pressed(pin)
    button.when_released = lambda pin=pin: button_released(pin)

# Keep listening for input
try:
    while True:
        time.sleep(1)  # Prevent high CPU usage
except KeyboardInterrupt:
    print("Exited test script.")