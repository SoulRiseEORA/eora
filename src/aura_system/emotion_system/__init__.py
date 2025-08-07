import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aura_system")))

from .emotion_core import EmotionCore, get_emotion_core

__all__ = ['EmotionCore', 'get_emotion_core']