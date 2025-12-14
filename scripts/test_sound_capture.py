"""
Test script for playing WAV files through the robot's speaker
Usage: python test_sound_capture.py <path_to_wav_file>
"""

import sys
import os
import argparse
import pygame
import time

# Add parent directory to path to import mini_bdx_runtime
parent_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, parent_dir)

from mini_bdx_runtime.mini_bdx_runtime.sounds import Sounds



def test_single_wav(wav_path, volume=1.0):
    """
    Test playing a single WAV file

    Args:
        wav_path: Path to the WAV file
        volume: Volume level (0.0 to 1.0)
    """
    if not os.path.exists(wav_path):
        print(f"Error: File '{wav_path}' not found!")
        return

    if not wav_path.endswith('.wav'):
        print("Warning: File does not have .wav extension")

    print(f"Testing WAV file: {wav_path}")
    print(f"Volume: {volume}")

    # Initialize pygame mixer
    pygame.mixer.init()
    pygame.mixer.music.set_volume(volume)

    try:
        # Load and play the sound
        sound = pygame.mixer.Sound(wav_path)
        print(f"Sound loaded successfully!")
        print(f"Duration: {sound.get_length():.2f} seconds")

        print("Playing sound...")
        sound.play()

        # Wait for sound to finish
        time.sleep(sound.get_length() + 0.5)
        print("Playback finished!")

    except pygame.error as e:
        print(f"Error playing sound: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        pygame.mixer.quit()


def test_with_sounds_class(wav_path, volume=1.0):
    """
    Test playing a WAV file using the Sounds class

    Args:
        wav_path: Path to the WAV file
        volume: Volume level (0.0 to 1.0)
    """
    if not os.path.exists(wav_path):
        print(f"Error: File '{wav_path}' not found!")
        return

    # Get directory and filename
    sound_dir = os.path.dirname(os.path.abspath(wav_path))
    sound_file = os.path.basename(wav_path)

    print(f"Testing with Sounds class...")
    print(f"Directory: {sound_dir}")
    print(f"File: {sound_file}")
    print(f"Volume: {volume}")

    # Initialize Sounds class with the directory containing the WAV file
    sounds = Sounds(volume=volume, sound_directory=sound_dir)

    if not sounds.ok:
        print("Error: Sounds class failed to initialize!")
        return

    # Play the sound
    sounds.play(sound_file)

    # Wait a bit for playback
    time.sleep(5)
    print("Test complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Test WAV file playback through the robot's speaker"
    )
    parser.add_argument(
        "wav_file",
        type=str,
        help="Path to the WAV file to play"
    )
    parser.add_argument(
        "-v", "--volume",
        type=float,
        default=1.0,
        help="Volume level (0.0 to 1.0, default: 1.0)"
    )
    parser.add_argument(
        "-m", "--method",
        type=str,
        choices=["direct", "class"],
        default="direct",
        help="Playback method: 'direct' (pygame directly) or 'class' (Sounds class)"
    )

    args = parser.parse_args()

    # Validate volume
    if not 0.0 <= args.volume <= 1.0:
        print("Error: Volume must be between 0.0 and 1.0")
        sys.exit(1)

    print("=" * 50)
    print("WAV File Speaker Test")
    print("=" * 50)

    if args.method == "direct":
        test_single_wav(args.wav_file, args.volume)
    else:
        test_with_sounds_class(args.wav_file, args.volume)
