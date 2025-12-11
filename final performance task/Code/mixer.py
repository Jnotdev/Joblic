import pygame
pygame.init()
pygame.mixer.init()

music_file = "sound/bosa_nova.wav" 
try:
    pygame.mixer.music.load(music_file)
    print(f"Loaded music: {music_file}")
    
except pygame.error as e:
    print(f"Error loading music: {e}")
    
pygame.mixer.music.play(-1)  # loop indefinitely
pygame.mixer.music.set_volume(0.5)  # set to 50% volume