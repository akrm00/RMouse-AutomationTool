"""
Macro sequence storage and management module
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional


class MacroStorage:
    def __init__(self, default_path: str = "macros"):
        self.default_path = default_path
        self.settings_file = "settings.json"
        self.ensure_directory_exists()
        
    def ensure_directory_exists(self):
        if not os.path.exists(self.default_path):
            os.makedirs(self.default_path)
    
    def save_sequence(self, sequence: List[Dict[str, Any]], filename: str = None) -> str:
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"macro_{timestamp}.json"
        
        if not filename.endswith('.json'):
            filename += '.json'
        
        filepath = os.path.join(self.default_path, filename)
        
        macro_data = {
            "created_at": datetime.now().isoformat(),
            "version": "1.0",
            "sequence": sequence,
            "total_actions": len(sequence)
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(macro_data, f, indent=2, ensure_ascii=False)
            return filepath
        except Exception as e:
            raise Exception(f"Error saving file: {str(e)}")
    
    def load_sequence(self, filepath: str) -> List[Dict[str, Any]]:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                macro_data = json.load(f)
            
            if isinstance(macro_data, list):
                # Legacy format compatibility
                return macro_data
            else:
                return macro_data.get('sequence', [])
                
        except FileNotFoundError:
            raise Exception(f"File not found: {filepath}")
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON file: {filepath}")
        except Exception as e:
            raise Exception(f"Error loading file: {str(e)}")
    
    def get_available_macros(self) -> List[Dict[str, str]]:
        macros = []
        
        if not os.path.exists(self.default_path):
            return macros
        
        for filename in os.listdir(self.default_path):
            if filename.endswith('.json'):
                filepath = os.path.join(self.default_path, filename)
                try:
                    stat = os.stat(filepath)
                    macros.append({
                        'name': filename[:-5],  # Remove .json extension
                        'filename': filename,
                        'filepath': filepath,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                    })
                except:
                    continue
        
        return sorted(macros, key=lambda x: x['modified'], reverse=True)
    
    def save_last_sequence(self, sequence: List[Dict[str, Any]]):
        settings = self.load_settings()
        last_file = settings.get('last_sequence_file', 'last_sequence.json')
        self.save_sequence(sequence, last_file)
    
    def load_last_sequence(self) -> Optional[List[Dict[str, Any]]]:
        settings = self.load_settings()
        last_file = settings.get('last_sequence_file', 'last_sequence.json')
        filepath = os.path.join(self.default_path, last_file)
        
        try:
            return self.load_sequence(filepath)
        except:
            return None
    
    def save_settings(self, settings: Dict[str, Any]):
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            pass
    
    def load_settings(self) -> Dict[str, Any]:
        default_settings = {
            "playback_speed": 1.0,
            "loop_count": 1,
            "auto_save": True,
            "hotkey_play": "F8",
            "last_sequence_file": "last_sequence.json"
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                # Merge with defaults for compatibility
                default_settings.update(settings)
            return default_settings
        except Exception as e:
            return default_settings
    
    def delete_macro(self, filepath: str) -> bool:
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception as e:
            return False 