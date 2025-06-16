"""
Macro playback module
"""
import time
import threading
from typing import List, Dict, Any, Callable, Optional
import pyautogui
from pynput.keyboard import Key, KeyCode
from pynput import keyboard


class MacroPlayer:
    def __init__(self):
        self.is_playing = False
        self.current_sequence: List[Dict[str, Any]] = []
        self.playback_speed = 1.0
        self.loop_count = 1
        self.current_loop = 0
        self.play_thread = None
        self.stop_requested = False
        self.on_playback_changed: Optional[Callable[[bool], None]] = None
        self.on_progress_changed: Optional[Callable[[int, int], None]] = None
        
        # PyAutoGUI safety settings
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.01
    
    def load_sequence(self, sequence: List[Dict[str, Any]]):
        self.current_sequence = sequence.copy()
    
    def set_playback_settings(self, speed: float = 1.0, loops: int = 1):
        self.playback_speed = max(0.1, min(15.0, speed))
        self.loop_count = max(0, loops)
    
    def play(self) -> bool:
        if self.is_playing or not self.current_sequence:
            return False
        
        self.is_playing = True
        self.stop_requested = False
        self.current_loop = 0
        
        self.play_thread = threading.Thread(target=self._play_sequence, daemon=True)
        self.play_thread.start()
        
        if self.on_playback_changed:
            self.on_playback_changed(True)
        
        return True
    
    def stop(self):
        if not self.is_playing:
            return
        
        self.stop_requested = True
    
    def _play_sequence(self):
        try:
            loops_to_do = self.loop_count if self.loop_count > 0 else float('inf')
            
            while self.current_loop < loops_to_do and not self.stop_requested:
                self.current_loop += 1
                
                if not self._execute_actions():
                    break
                
                # Pause between loops
                if self.loop_count > 1 and self.current_loop < loops_to_do:
                    time.sleep(0.5)
            
        except Exception as e:
            pass
        finally:
            self._cleanup_playback()
    
    def _execute_actions(self) -> bool:
        if not self.current_sequence:
            return False
        
        last_timestamp = 0
        
        for i, action in enumerate(self.current_sequence):
            if self.stop_requested:
                return False
            
            # Handle timing between actions
            current_timestamp = action.get('timestamp', 0)
            if i > 0:
                delay = (current_timestamp - last_timestamp) / self.playback_speed
                if delay > 0:
                    time.sleep(max(0.001, delay))
            
            last_timestamp = current_timestamp
            
            try:
                self._execute_action(action)
                
                if self.on_progress_changed:
                    self.on_progress_changed(i + 1, len(self.current_sequence))
                    
            except Exception as e:
                continue
        
        return True
    
    def _execute_action(self, action: Dict[str, Any]):
        action_type = action.get('type', '')
        
        if action_type == 'mouse_move':
            x, y = action.get('x', 0), action.get('y', 0)
            pyautogui.moveTo(x, y)
            
        elif action_type == 'mouse_press':
            x, y = action.get('x', 0), action.get('y', 0)
            button = action.get('button', 'left')
            pyautogui.mouseDown(x, y, button=button)
            
        elif action_type == 'mouse_release':
            x, y = action.get('x', 0), action.get('y', 0)
            button = action.get('button', 'left')
            pyautogui.mouseUp(x, y, button=button)
            
        elif action_type == 'mouse_scroll':
            x, y = action.get('x', 0), action.get('y', 0)
            dy = action.get('dy', 0)
            pyautogui.scroll(dy, x=x, y=y)
            
        elif action_type == 'key_press':
            key = action.get('key', '')
            self._press_key(key)
            
        elif action_type == 'key_release':
            key = action.get('key', '')
            self._release_key(key)
    
    def _press_key(self, key_str: str):
        try:
            if key_str.startswith('Key.'):
                key_name = key_str[4:].lower()
                if hasattr(pyautogui, key_name):
                    pyautogui.keyDown(key_name)
            else:
                if key_str and len(key_str) == 1:
                    pyautogui.keyDown(key_str)
        except Exception as e:
            pass
    
    def _release_key(self, key_str: str):
        try:
            if key_str.startswith('Key.'):
                key_name = key_str[4:].lower()
                if hasattr(pyautogui, key_name):
                    pyautogui.keyUp(key_name)
            else:
                if key_str and len(key_str) == 1:
                    pyautogui.keyUp(key_str)
        except Exception as e:
            pass
    
    def _cleanup_playback(self):
        self.is_playing = False
        self.stop_requested = False
        
        if self.on_playback_changed:
            self.on_playback_changed(False)
    
    def is_sequence_loaded(self) -> bool:
        return len(self.current_sequence) > 0
    
    def get_sequence_info(self) -> Dict[str, Any]:
        if not self.current_sequence:
            return {'loaded': False}
        
        total_time = 0
        if self.current_sequence:
            total_time = self.current_sequence[-1].get('timestamp', 0)
        
        return {
            'loaded': True,
            'total_actions': len(self.current_sequence),
            'duration': total_time,
            'current_loop': self.current_loop,
            'total_loops': self.loop_count,
            'is_playing': self.is_playing
        }
    
    def set_playback_callback(self, callback: Callable[[bool], None]):
        self.on_playback_changed = callback
    
    def set_progress_callback(self, callback: Callable[[int, int], None]):
        self.on_progress_changed = callback 