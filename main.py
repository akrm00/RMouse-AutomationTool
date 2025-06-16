import customtkinter as ctk
import threading
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
from typing import Optional
import os
from pynput import keyboard
from pynput.keyboard import Key, KeyCode

from recorder import MacroRecorder
from player import MacroPlayer
from storage import MacroStorage


class MacroAutomationApp:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.recorder = MacroRecorder()
        self.player = MacroPlayer()
        self.storage = MacroStorage()
        
        self.current_sequence = []
        self.settings = self.storage.load_settings()
        
        self.hotkey_listener = None
        
        self.setup_main_window()
        self.setup_ui()
        self.setup_callbacks()
        self.setup_global_hotkeys()
        self.load_settings()
        
        self.load_last_sequence()
    
    def setup_main_window(self):
        self.root = ctk.CTk()
        self.root.title("RMouse Automation Tool")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
    
    def setup_ui(self):
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            main_frame, 
            text="Rmouse Tool",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        self.setup_main_buttons(main_frame)
        self.setup_settings_frame(main_frame)
        self.setup_info_frame(main_frame)
        self.setup_status_bar(main_frame)
    
    def setup_main_buttons(self, parent):
        buttons_frame = ctk.CTkFrame(parent)
        buttons_frame.pack(fill="x", pady=(0, 20))
        
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)
        buttons_frame.grid_columnconfigure(2, weight=1)
        buttons_frame.grid_columnconfigure(3, weight=1)
        
        self.play_button = ctk.CTkButton(
            buttons_frame,
            text="Play",
            command=self.toggle_play,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.play_button.grid(row=0, column=0, padx=5, pady=10, sticky="ew")
        
        self.admin_button = ctk.CTkButton(
            buttons_frame,
            text="Admin",
            command=self.show_admin_info,
            height=40,
            state="disabled",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.admin_button.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        
        self.record_button = ctk.CTkButton(
            buttons_frame,
            text="Record",
            command=self.toggle_record,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.record_button.grid(row=0, column=2, padx=5, pady=10, sticky="ew")
        
        self.saveload_button = ctk.CTkButton(
            buttons_frame,
            text="Save/Load",
            command=self.show_saveload_menu,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.saveload_button.grid(row=0, column=3, padx=5, pady=10, sticky="ew")
    
    def setup_settings_frame(self, parent):
        settings_frame = ctk.CTkFrame(parent)
        settings_frame.pack(fill="x", pady=(0, 20))
        
        settings_label = ctk.CTkLabel(
            settings_frame,
            text="Settings",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        settings_label.pack(pady=(10, 10))
        
        # Speed control
        speed_frame = ctk.CTkFrame(settings_frame)
        speed_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(speed_frame, text="Speed:").pack(side="left", padx=10)
        self.speed_slider = ctk.CTkSlider(
            speed_frame,
            from_=0.1,
            to=15.0,
            command=self.on_speed_changed
        )
        self.speed_slider.pack(side="left", fill="x", expand=True, padx=10)
        self.speed_value_label = ctk.CTkLabel(speed_frame, text="1.0x")
        self.speed_value_label.pack(side="right", padx=10)
        
        # Loop count
        loop_frame = ctk.CTkFrame(settings_frame)
        loop_frame.pack(fill="x", padx=20, pady=(5, 15))
        
        ctk.CTkLabel(loop_frame, text="Loops:").pack(side="left", padx=10)
        self.loop_entry = ctk.CTkEntry(loop_frame, width=80)
        self.loop_entry.pack(side="left", padx=10)
        self.loop_entry.bind("<KeyRelease>", self.on_loop_changed)
        
        ctk.CTkLabel(loop_frame, text="(0 = infinite)").pack(side="left", padx=5)
    
    def setup_info_frame(self, parent):
        info_frame = ctk.CTkFrame(parent)
        info_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            info_frame,
            text="Information",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))
        
        self.info_text = ctk.CTkTextbox(info_frame, height=80)
        self.info_text.pack(fill="x", padx=20, pady=(0, 15))
        self.update_info_display()
    
    def setup_status_bar(self, parent):
        self.status_label = ctk.CTkLabel(
            parent,
            text="Ready - Ctrl+S: Emergency stop",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=(0, 10))
    
    def setup_callbacks(self):
        self.recorder.set_recording_callback(self.on_recording_changed)
        self.player.set_playback_callback(self.on_playback_changed)
        self.player.set_progress_callback(self.on_progress_changed)
    
    def setup_global_hotkeys(self):
        try:
            # Emergency stop hotkey
            self.hotkey_listener = keyboard.GlobalHotKeys({
                '<ctrl>+s': self.emergency_stop,
                '<ctrl>+<shift>+s': self.emergency_stop
            })
            self.hotkey_listener.start()
        except Exception as e:
            pass
    
    def emergency_stop(self):
        try:
            stopped_something = False
            
            if self.recorder.is_recording:
                self.recorder.stop_recording()
                self.current_sequence = self.recorder.get_current_actions()
                self.update_info_display()
                stopped_something = True
            
            if self.player.is_playing:
                self.player.stop()
                stopped_something = True
            
            if stopped_something:
                self.root.after(0, self.update_ui_after_emergency_stop)
                
        except Exception as e:
            pass
    
    def update_ui_after_emergency_stop(self):
        try:
            self.play_button.configure(text="Play", state="normal")
            self.record_button.configure(text="Record", state="normal")
            self.status_label.configure(text="Emergency stop (Ctrl+S)")
            
        except Exception as e:
            pass
    
    def load_settings(self):
        try:
            speed = self.settings.get('playback_speed', 1.0)
            loops = self.settings.get('loop_count', 1)
            
            self.speed_slider.set(speed)
            self.loop_entry.insert(0, str(loops))
            
            self.player.set_playback_settings(speed, loops)
        except:
            pass
    
    def save_settings(self):
        try:
            self.settings['playback_speed'] = self.speed_slider.get()
            
            loop_text = self.loop_entry.get()
            self.settings['loop_count'] = int(loop_text) if loop_text.isdigit() else 1
            
            self.storage.save_settings(self.settings)
        except:
            pass
    
    def toggle_play(self):
        if self.player.is_playing:
            self.player.stop()
        else:
            if self.current_sequence:
                self.save_settings()
                if self.player.play():
                    pass
            else:
                messagebox.showwarning("No Sequence", "Please record or load a sequence first.")
    
    def toggle_record(self):
        if self.recorder.is_recording:
            self.current_sequence = self.recorder.stop_recording()
            if self.current_sequence:
                self.storage.save_last_sequence(self.current_sequence)
            self.update_info_display()
        else:
            self.recorder.start_recording()
    
    def show_admin_info(self):
        messagebox.showinfo("Admin Mode", "Admin mode not available in this version.")
    
    def show_saveload_menu(self):
        saveload_window = ctk.CTkToplevel(self.root)
        saveload_window.title("Save/Load Macros")
        saveload_window.geometry("400x300")
        saveload_window.transient(self.root)
        saveload_window.grab_set()
        
        main_frame = ctk.CTkFrame(saveload_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Save button
        save_button = ctk.CTkButton(
            main_frame,
            text="Save Current Sequence",
            command=self.save_sequence_as,
            height=35
        )
        save_button.pack(pady=10, padx=20, fill="x")
        
        # Load from file button
        load_file_button = ctk.CTkButton(
            main_frame,
            text="Load from File",
            command=self.load_sequence_from_file,
            height=35
        )
        load_file_button.pack(pady=5, padx=20, fill="x")
        
        # Available macros
        macros = self.storage.get_available_macros()
        if macros:
            ctk.CTkLabel(main_frame, text="Available Macros:", font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5))
            for macro in macros[:5]:  # Limit to 5 most recent
                macro_button = ctk.CTkButton(
                    main_frame,
                    text=f"{macro['name']} ({macro['modified']})",
                    command=lambda m=macro: self.load_macro(m, saveload_window),
                    height=30
                )
                macro_button.pack(pady=2, padx=20, fill="x")
    
    def on_recording_changed(self, is_recording: bool):
        if is_recording:
            self.record_button.configure(text="Stop Recording")
            self.play_button.configure(state="disabled")
            self.status_label.configure(text="Recording...")
        else:
            self.record_button.configure(text="Record")
            self.play_button.configure(state="normal")
            self.status_label.configure(text="Ready")
    
    def on_playback_changed(self, is_playing: bool):
        if is_playing:
            self.play_button.configure(text="Stop")
            self.record_button.configure(state="disabled")
            self.status_label.configure(text="Playing...")
        else:
            self.play_button.configure(text="Play")
            self.record_button.configure(state="normal")
            self.status_label.configure(text="Ready")
    
    def on_progress_changed(self, current: int, total: int):
        progress = f"Progress: {current}/{total}"
        self.status_label.configure(text=progress)
    
    def on_speed_changed(self, value):
        self.speed_value_label.configure(text=f"{value:.1f}x")
        self.player.set_playback_settings(value, int(self.loop_entry.get() or 1))
    
    def on_loop_changed(self, event=None):
        try:
            loop_count = int(self.loop_entry.get() or 1)
            self.player.set_playback_settings(self.speed_slider.get(), loop_count)
        except:
            pass
    
    def update_info_display(self):
        if self.current_sequence:
            duration = self.current_sequence[-1].get('timestamp', 0) if self.current_sequence else 0
            info_text = f"Actions: {len(self.current_sequence)}\n"
            info_text += f"Duration: {duration:.1f}s\n"
            info_text += f"Speed: {self.speed_slider.get():.1f}x\n"
            info_text += f"Loops: {self.loop_entry.get() or '1'}"
        else:
            info_text = "No sequence loaded.\nRecord or load a macro to start."
        
        self.info_text.delete("1.0", "end")
        self.info_text.insert("1.0", info_text)
    
    def load_last_sequence(self):
        last_sequence = self.storage.load_last_sequence()
        if last_sequence:
            self.current_sequence = last_sequence
            self.player.load_sequence(last_sequence)
            self.update_info_display()
    
    def save_sequence_as(self):
        if not self.current_sequence:
            messagebox.showwarning("No Sequence", "No sequence to save.")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save Macro As",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=self.storage.default_path
        )
        
        if filename:
            try:
                self.storage.save_sequence(self.current_sequence, os.path.basename(filename))
                messagebox.showinfo("Success", f"Macro saved: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {str(e)}")
    
    def load_sequence_from_file(self):
        filename = filedialog.askopenfilename(
            title="Load Macro",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=self.storage.default_path
        )
        
        if filename:
            try:
                sequence = self.storage.load_sequence(filename)
                self.current_sequence = sequence
                self.player.load_sequence(sequence)
                self.update_info_display()
                messagebox.showinfo("Success", f"Macro loaded: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load: {str(e)}")
    
    def load_macro(self, macro_info, window):
        try:
            sequence = self.storage.load_sequence(macro_info['filepath'])
            self.current_sequence = sequence
            self.player.load_sequence(sequence)
            self.update_info_display()
            window.destroy()
            messagebox.showinfo("Success", f"Macro loaded: {macro_info['name']}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load: {str(e)}")
    
    def run(self):
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.cleanup)
            self.root.mainloop()
        except KeyboardInterrupt:
            self.cleanup()
        except Exception as e:
            self.cleanup()
    
    def cleanup(self):
        try:
            if self.recorder.is_recording:
                self.recorder.stop_recording()
            
            if self.player.is_playing:
                self.player.stop()
            
            if self.hotkey_listener:
                self.hotkey_listener.stop()
            
            self.save_settings()
            
        except Exception as e:
            pass
        finally:
            try:
                self.root.quit()
                self.root.destroy()
            except:
                pass


def main():
    try:
        app = MacroAutomationApp()
        app.run()
    except Exception as e:
        pass
    finally:
        try:
            import sys
            sys.exit(0)
        except:
            pass


if __name__ == "__main__":
    main() 