#!/usr/bin/env python3
"""
Test script for cross-platform compatibility
"""
import pygame
import platform
import sys
import os

# Initialize pygame to test
pygame.init()

print(f"Pygame version: {pygame.version.ver}")
print(f"Platform: {platform.system()} {platform.release()}")
print(f"Python: {sys.version}")

# Test surface creation
try:
    test_surface = pygame.Surface((100, 100), pygame.SRCALPHA)
    print("✓ SRCALPHA surface creation successful")
except Exception as e:
    print(f"✗ SRCALPHA surface creation failed: {e}")

# Test display mode creation
try:
    test_screen = pygame.display.set_mode((240, 240))
    print("✓ Display mode creation successful")
    pygame.display.quit()
except Exception as e:
    print(f"✗ Display mode creation failed: {e}")

print("\nEnvironment variables:")
for var in ["SDL_VIDEODRIVER", "SDL_VIDEO_CENTERED", "DISPLAY", "WAYLAND_DISPLAY"]:
    value = os.getenv(var, "not set")
    print(f"  {var}: {value}")

pygame.quit()
print("\n✓ Compatibility test completed")
