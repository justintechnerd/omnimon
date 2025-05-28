import pygame
import platform

try:
    from gpiozero import Button  # type: ignore # Only works on Raspberry Pi
except ImportError:
    Button = None  # Ignore GPIOZero on non-Raspberry Pi systems

class InputManager:
    def __init__(self):
        self.device = "PC" if platform.system() != "Linux" else "Pi"

        self.key_map = {
            pygame.K_LEFT: "LEFT",
            pygame.K_RIGHT: "RIGHT",
            pygame.K_UP: "UP",
            pygame.K_DOWN: "DOWN",
            pygame.K_RETURN: "A",
            pygame.K_BACKSPACE: "START",
            pygame.K_LCTRL: "X",
            pygame.K_SPACE: "Y",
            pygame.K_LSHIFT: "R",
            pygame.K_ESCAPE: "B",
            pygame.K_TAB: "SELECT",
            pygame.K_F1: "F1", pygame.K_F2: "F2", pygame.K_F3: "F3", pygame.K_F4: "F4",
            pygame.K_F5: "F5", pygame.K_F6: "F6", pygame.K_F7: "F7", pygame.K_F8: "F8",
            pygame.K_F9: "F9", pygame.K_F10: "F10", pygame.K_F11: "F11", pygame.K_F12: "F12",
        }

        self.reverse_key_map = {v: k for k, v in self.key_map.items()}
        self.pin_map = {
            16: "LEFT", 13: "RIGHT", 5: "UP", 6: "DOWN",
            21: "A", 20: "B", 15: "X", 12: "Y",
            23: "L", 14: "R", 26: "START", 19: "SELECT"
        }

        self.just_pressed_gpio = set()
        self.active_gpio_inputs = set()  # ✅ Required for GPIO tracking
        self.buttons = {}

        try:
            from gpiozero import Button  # type: ignore
            if self.device == "Pi":
                for pin, action in self.pin_map.items():
                    btn = Button(pin, pull_up=True, bounce_time=0.05)
                    btn.when_pressed = self.make_gpio_handler(action, True)
                    btn.when_released = self.make_gpio_handler(action, False)
                    self.buttons[pin] = btn
        except ImportError:
            pass

    def make_gpio_handler(self, action, pressed):
        def handler():
            self.handle_gpio_input(action, pressed)
        return handler

    def handle_gpio_input(self, action, pressed):
        if pressed:
            if action not in self.active_gpio_inputs:
                self.just_pressed_gpio.add(action)
            self.active_gpio_inputs.add(action)
        else:
            self.active_gpio_inputs.discard(action)

    def get_just_pressed(self):
        pressed = list(self.just_pressed_gpio)
        self.just_pressed_gpio.clear()
        return pressed

    def process_event(self, event):
        # Handle keyboard normally
        if event.type == pygame.KEYDOWN and event.key in self.key_map:
            action = self.key_map[event.key]
            # Directly return the action instead of adding to gpio set
            return action
        return None  # No action from this event


