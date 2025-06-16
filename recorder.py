"""
Mouse and keyboard action recording module
"""
import time
import threading
from typing import List, Dict, Any, Callable, Optional
from pynput import mouse, keyboard
from pynput.mouse import Button
from pynput.keyboard import Key


class MacroRecorder:
    def __init__(self):
        self.is_recording = False
        self.actions: List[Dict[str, Any]] = []
        self.start_time = 0
        self.mouse_listener = None
        self.keyboard_listener = None
        self.on_recording_changed: Optional[Callable[[bool], None]] = None
        
    def start_recording(self) -> bool:
        if self.is_recording:
            return False
        
        self.actions.clear()
        self.is_recording = True
        self.start_time = time.time()
        
        self._start_mouse_listener()
        self._start_keyboard_listener()
        
        if self.on_recording_changed:
            self.on_recording_changed(True)
        
        return True
    
    def stop_recording(self) -> List[Dict[str, Any]]:
        if not self.is_recording:
            return self.actions
        
        self.is_recording = False
        
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
        
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None
        
        if self.on_recording_changed:
            self.on_recording_changed(False)
        
        return self.actions.copy()
    
    def _start_mouse_listener(self):
        try:
            self.mouse_listener = mouse.Listener(
                on_move=self._on_mouse_move,
                on_click=self._on_mouse_click,
                on_scroll=self._on_mouse_scroll
            )
            self.mouse_listener.start()
        except Exception as e:
            pass
    
    def _start_keyboard_listener(self):
        try:
            self.keyboard_listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            self.keyboard_listener.start()
        except Exception as e:
            pass
    
    def _get_timestamp(self) -> float:
        return time.time() - self.start_time
    
    def _on_mouse_move(self, x: int, y: int):
        if not self.is_recording:
            return
        
        action = {
            'type': 'mouse_move',
            'x': x,
            'y': y,
            'timestamp': self._get_timestamp()
        }
        self.actions.append(action)
    
    def _on_mouse_click(self, x: int, y: int, button: Button, pressed: bool):
        if not self.is_recording:
            return
        
        button_name = 'left' if button == Button.left else 'right' if button == Button.right else 'middle'
        action_type = 'mouse_press' if pressed else 'mouse_release'
        
        action = {
            'type': action_type,
            'x': x,
            'y': y,
            'button': button_name,
            'timestamp': self._get_timestamp()
        }
        self.actions.append(action)
    
    def _on_mouse_scroll(self, x: int, y: int, dx: int, dy: int):
        if not self.is_recording:
            return
        
        action = {
            'type': 'mouse_scroll',
            'x': x,
            'y': y,
            'dx': dx,
            'dy': dy,
            'timestamp': self._get_timestamp()
        }
        self.actions.append(action)
    
    def _on_key_press(self, key):
        if not self.is_recording:
            return
        
        try:
            key_name = key.char if hasattr(key, 'char') and key.char else str(key)
        except AttributeError:
            key_name = str(key)
        
        action = {
            'type': 'key_press',
            'key': key_name,
            'timestamp': self._get_timestamp()
        }
        self.actions.append(action)
    
    def _on_key_release(self, key):
        if not self.is_recording:
            return
        
        try:
            key_name = key.char if hasattr(key, 'char') and key.char else str(key)
        except AttributeError:
            key_name = str(key)
        
        action = {
            'type': 'key_release',
            'key': key_name,
            'timestamp': self._get_timestamp()
        }
        self.actions.append(action)
    
    def get_current_actions(self) -> List[Dict[str, Any]]:
        return self.actions.copy()
    
    def clear_actions(self):
        self.actions.clear()
    
    def set_recording_callback(self, callback: Callable[[bool], None]):
        self.on_recording_changed = callback 