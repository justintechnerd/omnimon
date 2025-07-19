#!/usr/bin/env python3
"""
FPS Profiler for Omnimon
This script helps identify performance bottlenecks in the game.
"""

import cProfile
import pstats
import io
import pygame
import time
from vpet import VirtualPetGame
from core.constants import *
from core import game_globals, runtime_globals
from core.input.system_stats import get_system_stats

def profile_main_loop():
    """Profile the main game loop to identify bottlenecks."""
    
    # Initialize pygame
    pygame.init()
    pygame.mouse.set_visible(False)
    
    # Set up display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Omnimon FPS Profiler")
    
    game = VirtualPetGame()
    clock = pygame.time.Clock()
    
    # Profile for 30 seconds
    profile_duration = 30
    start_time = time.time()
    frame_count = 0
    
    print(f"Starting FPS profiling for {profile_duration} seconds...")
    print("This will help identify performance bottlenecks.")
    
    # Create profiler
    profiler = cProfile.Profile()
    
    profiler.enable()
    
    while time.time() - start_time < profile_duration:
        game.update()
        game.draw(screen)
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break
            game.handle_event(event)
        
        clock.tick(30)  # Target 30 FPS
        frame_count += 1
    
    profiler.disable()
    
    # Calculate actual FPS
    actual_fps = frame_count / profile_duration
    
    print(f"\n--- FPS PROFILING RESULTS ---")
    print(f"Target FPS: 30")
    print(f"Actual FPS: {actual_fps:.2f}")
    print(f"Frame drop: {((30 - actual_fps) / 30) * 100:.1f}%")
    
    # Get system stats
    temp, cpu, memory = get_system_stats()
    print(f"\nSystem Stats:")
    print(f"CPU Temperature: {temp}°C" if temp else "CPU Temperature: N/A")
    print(f"CPU Usage: {cpu:.1f}%" if cpu else "CPU Usage: N/A")
    print(f"Memory Usage: {memory:.1f}%" if memory else "Memory Usage: N/A")
    
    # Save profiling results
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s).sort_stats('tottime')
    ps.print_stats(20)  # Top 20 slowest functions
    
    with open('fps_profile_results.txt', 'w') as f:
        f.write(f"FPS Profiling Results\n")
        f.write(f"====================\n")
        f.write(f"Target FPS: 30\n")
        f.write(f"Actual FPS: {actual_fps:.2f}\n")
        f.write(f"Frame drop: {((30 - actual_fps) / 30) * 100:.1f}%\n\n")
        f.write("Top 20 performance bottlenecks:\n")
        f.write(s.getvalue())
    
    print(f"\nDetailed profiling results saved to 'fps_profile_results.txt'")
    print("\nTop 5 performance bottlenecks:")
    
    # Print top 5 slowest functions
    lines = s.getvalue().split('\n')
    for i, line in enumerate(lines):
        if i > 5 and i < 11 and line.strip():  # Skip header lines
            print(f"  {line}")
    
    pygame.quit()

if __name__ == "__main__":
    try:
        profile_main_loop()
    except Exception as e:
        print(f"Error during profiling: {e}")
        print("Make sure to run this from the omnimon directory.")
