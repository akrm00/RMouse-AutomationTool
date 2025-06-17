import customtkinter as ctk
import threading
import tkinter.messagebox as messagebox
import tkinter.filedialog as filedialog
from typing import Optional
import os
from pynput import keyboard
from pynput.keyboard import Key, KeyCode
import tkinter as tk
from PIL import Image, ImageTk

from recorder import MacroRecorder
from player import MacroPlayer
from storage import MacroStorage


class ModernButton(ctk.CTkButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_fg_color = kwargs.get('fg_color', ("#1f538d", "#1f538d"))
        
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event=None):
        self.configure(fg_color=("#2d6bb4", "#2d6bb4"))
    
    def _on_leave(self, event=None):
        self.configure(fg_color=self._original_fg_color)


class GlassFrame(ctk.CTkFrame):
    def __init__(self, *args, **kwargs):
        kwargs['fg_color'] = kwargs.get('fg_color', ("#1a1a1a", "#1a1a1a"))
        kwargs['border_width'] = kwargs.get('border_width', 1)
        kwargs['border_color'] = kwargs.get('border_color', ("#3a3a3a", "#3a3a3a"))
        super().__init__(*args, **kwargs)


class MacroAutomationApp:
    def __init__(self):
        # Set appearance
        ctk.set_appearance_mode("dark")
        
        # Initialize components
        self.recorder = MacroRecorder()
        self.player = MacroPlayer()
        self.storage = MacroStorage()
        
        self.current_sequence = []
        self.settings = self.storage.load_settings()
        
        self.hotkey_listener = None
        
        # Colors theme
        self.colors = {
            'bg_primary': "#0a0a0f",
            'bg_secondary': "#1a1a1f",
            'bg_tertiary': "#2a2a2f",
            'accent_primary': "#8b5cf6",
            'accent_secondary': "#7c3aed",
            'accent_gradient_start': "#a78bfa",
            'accent_gradient_mid': "#8b5cf6",
            'accent_gradient_end': "#7c3aed",
            'accent_orange': "#32175f",
            'accent_success': "#10b981",
            'text_primary': "#ffffff",
            'text_secondary': "#b3b3b3",
            'border': "#404040",
            'glass': "#1a1a1f"
        }
        
        self.setup_main_window()
        self.setup_ui()
        self.setup_callbacks()
        self.setup_global_hotkeys()
        self.load_settings()
        
        self.load_last_sequence()
    
    def setup_main_window(self):
        self.root = ctk.CTk()
        self.root.title("RMouse by akrm00")
        self.root.geometry("600x550")
        self.root.resizable(False, False)
        
        # Set window background
        self.root._fg_color = self.colors['bg_primary']
        self.root.configure(fg_color=self.colors['bg_primary'])
        
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
    
    def setup_ui(self):
        # Main container with padding
        main_container = ctk.CTkFrame(self.root, fg_color=self.colors['bg_primary'])
        main_container.pack(fill="both", expand=True)
        
        # Header section
        self.setup_header(main_container)
        
        # Content section
        content_frame = ctk.CTkFrame(main_container, fg_color=self.colors['bg_primary'])
        content_frame.pack(fill="both", expand=True, padx=30, pady=0)
        
        # Main controls
        self.setup_main_controls(content_frame)
        
        # Settings section
        self.setup_settings_section(content_frame)
    
    def setup_header(self, parent):
        header_frame = GlassFrame(
            parent, 
            fg_color=self.colors['bg_secondary'],
            corner_radius=0,
            height=100
        )
        header_frame.pack(fill="x", pady=(0, 30))
        header_frame.pack_propagate(False)
        
        # Title with gradient effect
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(expand=True)
        
        # Icon placeholder
        icon_label = ctk.CTkLabel(
            title_frame,
            text="🖱️",
            font=ctk.CTkFont(family="Segoe UI", size=32),
            text_color="#a78bfa"
        )
        icon_label.pack(side="left", padx=(20, 10))
        
        # Title
        title_label = ctk.CTkLabel(
            title_frame,
            text="RMouse",
            font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),
            text_color=self.colors['text_primary']
        )
        title_label.pack(side="left")
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="Automation Tool",
            font=ctk.CTkFont(family="Segoe UI", size=16),
            text_color=self.colors['text_secondary']
        )
        subtitle_label.pack(side="left", padx=(10, 0))
    
    def setup_main_controls(self, parent):
        # Controls section
        controls_frame = GlassFrame(
            parent,
            fg_color=self.colors['bg_secondary'],
            corner_radius=15
        )
        controls_frame.pack(fill="x", pady=(0, 20))
        
        # Section title
        section_title = ctk.CTkLabel(
            controls_frame,
            text="CONTROLS",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=self.colors['text_secondary']
        )
        section_title.pack(pady=(20, 15), padx=25, anchor="w")
        
        # Buttons container
        buttons_container = ctk.CTkFrame(controls_frame, fg_color="transparent")
        buttons_container.pack(fill="x", padx=25, pady=(0, 25))
        
        # Play button with gradient
        self.play_button = ModernButton(
            buttons_container,
            text="▶  PLAY",
            command=self.toggle_play,
            height=50,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color=("#a78bfa", "#7c3aed"),
            hover_color=("#c4b5fd", "#9333ea"),
            text_color="#ffffff",
            corner_radius=25
        )
        self.play_button._hover_color = ("#c4b5fd", "#9333ea")
        self.play_button.pack(side="left", expand=True, fill="x", padx=(0, 10))
        
        # Record button with orange color
        self.record_button = ModernButton(
            buttons_container,
            text="⏺  RECORD",
            command=self.toggle_record,
            height=50,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color=("#3e1d77", "#3e1d77"),
            hover_color=("#fb923c", "#32175f"),
            text_color="#ffffff",
            corner_radius=25
        )
        self.record_button._hover_color = ("#fb923c", "#32175f")
        self.record_button.pack(side="left", expand=True, fill="x", padx=(0, 10))
        
        # Save/Load button
        self.saveload_button = ModernButton(
            buttons_container,
            text="💾  SAVE/LOAD",
            command=self.show_saveload_menu,
            height=50,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color=(self.colors['bg_tertiary'], self.colors['bg_tertiary']),
            hover_color=("#404040", "#404040"),
            text_color="#ffffff",
            corner_radius=25
        )
        self.saveload_button._hover_color = ("#404040", "#404040")
        self.saveload_button.pack(side="left", expand=True, fill="x")
    
    def setup_settings_section(self, parent):
        # Settings frame
        settings_frame = GlassFrame(
            parent,
            fg_color=self.colors['bg_secondary'],
            corner_radius=15
        )
        settings_frame.pack(fill="x", pady=(0, 20))
        
        # Header with title and help icon
        header_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=25, pady=(20, 15))
        
        # Section title
        section_title = ctk.CTkLabel(
            header_frame,
            text="SETTINGS",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=self.colors['text_secondary']
        )
        section_title.pack(side="left")
        
        # Help button
        self.help_button = ctk.CTkButton(
            header_frame,
            text="?",
            width=30,
            height=30,
            corner_radius=15,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color=(self.colors['bg_tertiary'], self.colors['bg_tertiary']),
            hover_color=(self.colors['accent_gradient_start'], self.colors['accent_gradient_start']),
            text_color=self.colors['text_secondary'],
            command=self.show_help_popup
        )
        self.help_button.pack(side="right")
        
        # Speed control
        speed_container = ctk.CTkFrame(settings_frame, fg_color="transparent")
        speed_container.pack(fill="x", padx=25, pady=(0, 15))
        
        speed_label = ctk.CTkLabel(
            speed_container,
            text="Playback Speed",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=self.colors['text_primary']
        )
        speed_label.pack(anchor="w", pady=(0, 5))
        
        speed_frame = ctk.CTkFrame(speed_container, fg_color="transparent")
        speed_frame.pack(fill="x")
        
        self.speed_slider = ctk.CTkSlider(
            speed_frame,
            from_=0.1,
            to=15.0,
            command=self.on_speed_changed,
            button_color=self.colors['accent_gradient_start'],
            button_hover_color=self.colors['accent_gradient_end'],
            progress_color=(self.colors['accent_gradient_start'], self.colors['accent_gradient_end']),
            fg_color=(self.colors['bg_tertiary'], self.colors['bg_tertiary'])
        )
        self.speed_slider.pack(side="left", fill="x", expand=True, padx=(0, 15))
        
        self.speed_value_label = ctk.CTkLabel(
            speed_frame,
            text="1.0x",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=self.colors['accent_gradient_start'],
            width=50
        )
        self.speed_value_label.pack(side="right")
        
        # Loop control
        loop_container = ctk.CTkFrame(settings_frame, fg_color="transparent")
        loop_container.pack(fill="x", padx=25, pady=(0, 25))
        
        loop_label = ctk.CTkLabel(
            loop_container,
            text="Loop Count",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=self.colors['text_primary']
        )
        loop_label.pack(anchor="w", pady=(0, 5))
        
        loop_input_frame = ctk.CTkFrame(loop_container, fg_color="transparent")
        loop_input_frame.pack(fill="x")
        
        self.loop_entry = ctk.CTkEntry(
            loop_input_frame,
            width=100,
            height=35,
            font=ctk.CTkFont(family="Segoe UI", size=14),
            fg_color=self.colors['bg_tertiary'],
            border_color=self.colors['border'],
            text_color=self.colors['text_primary']
        )
        self.loop_entry.pack(side="left", padx=(0, 10))
        self.loop_entry.bind("<KeyRelease>", self.on_loop_changed)
        
        loop_hint = ctk.CTkLabel(
            loop_input_frame,
            text="0 = infinite loops",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=self.colors['text_secondary']
        )
        loop_hint.pack(side="left")
    
    def show_help_popup(self):
        # Create help popup window
        help_window = ctk.CTkToplevel(self.root)
        help_window.title("Help")
        help_window.geometry("350x200")
        help_window.configure(fg_color=self.colors['bg_primary'])
        help_window.transient(self.root)
        help_window.grab_set()
        
        # Position relative to main window
        x = self.root.winfo_x() + 125
        y = self.root.winfo_y() + 150
        help_window.geometry(f"+{x}+{y}")
        
        # Content frame
        content_frame = GlassFrame(
            help_window,
            fg_color=self.colors['bg_secondary'],
            corner_radius=15
        )
        content_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Title
        title_label = ctk.CTkLabel(
            content_frame,
            text="⌨️ Keyboard Shortcuts",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=self.colors['text_primary']
        )
        title_label.pack(pady=(20, 15))
        
        # Hotkey info
        hotkey_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        hotkey_frame.pack(pady=(0, 10))
        
        ctk.CTkLabel(
             hotkey_frame,
             text="Ctrl + S",
             font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
             text_color=self.colors['accent_gradient_start']
         ).pack()
        
        ctk.CTkLabel(
            hotkey_frame,
            text="Emergency stop all operations",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=self.colors['text_secondary']
        ).pack(pady=(5, 0))
        
        # Close button
        close_button = ModernButton(
            content_frame,
            text="Got it",
            command=help_window.destroy,
            width=100,
            height=35,
            fg_color=(self.colors['accent_gradient_start'], self.colors['accent_gradient_end']),
            hover_color=("#a855f7", "#818cf8"),
            text_color=self.colors['text_primary'],
            corner_radius=18,
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        close_button._hover_color = ("#a855f7", "#818cf8")
        close_button.pack(pady=(20, 0))
    
    def setup_status_section(self, parent):
        # Status frame
        status_frame = GlassFrame(
            parent,
            fg_color=self.colors['bg_secondary'],
            corner_radius=15,
            height=120
        )
        status_frame.pack(fill="x")
        status_frame.pack_propagate(False)
        
        # Status content
        status_content = ctk.CTkFrame(status_frame, fg_color="transparent")
        status_content.pack(expand=True)
        
        # Status icon
        self.status_icon = ctk.CTkLabel(
            status_content,
            text="✓",
            font=ctk.CTkFont(family="Segoe UI", size=24),
            text_color=self.colors['accent_success']
        )
        self.status_icon.pack()
        
        # Status text
        self.status_label = ctk.CTkLabel(
            status_content,
            text="Ready",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=self.colors['text_primary']
        )
        self.status_label.pack(pady=(5, 0))
        
        # Hotkey hint
        hotkey_label = ctk.CTkLabel(
            status_content,
            text="Ctrl+S: Emergency Stop",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=self.colors['text_secondary']
        )
        hotkey_label.pack(pady=(5, 0))
    
    def show_saveload_menu(self):
        saveload_window = ctk.CTkToplevel(self.root)
        saveload_window.title("Save/Load Macros")
        saveload_window.geometry("500x600")
        saveload_window.configure(fg_color=self.colors['bg_primary'])
        saveload_window.transient(self.root)
        saveload_window.grab_set()
        
        # Header
        header_frame = GlassFrame(
            saveload_window,
            fg_color=self.colors['bg_secondary'],
            corner_radius=0,
            height=80
        )
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(expand=True)
        
        ctk.CTkLabel(
            header_content,
            text="💾",
            font=ctk.CTkFont(family="Segoe UI", size=24),
            text_color=self.colors['accent_gradient_start']
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(
            header_content,
            text="Macro Manager",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=self.colors['text_primary']
        ).pack(side="left")
        
        # Content
        content_frame = ctk.CTkFrame(saveload_window, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Actions
        actions_frame = GlassFrame(
            content_frame,
            fg_color=self.colors['bg_secondary'],
            corner_radius=15
        )
        actions_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            actions_frame,
            text="ACTIONS",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=self.colors['text_secondary']
        ).pack(pady=(15, 10), padx=20, anchor="w")
        
        # Save button
        save_button = ModernButton(
            actions_frame,
            text="💾  Save Current Sequence",
            command=self.save_sequence_as,
            height=40,
            fg_color=(self.colors['accent_gradient_start'], self.colors['accent_gradient_end']),
            hover_color=("#a855f7", "#818cf8"),
            text_color=self.colors['text_primary'],
            corner_radius=20,
            font=ctk.CTkFont(family="Segoe UI", size=14)
        )
        save_button._hover_color = ("#a855f7", "#818cf8")
        save_button.pack(pady=(0, 10), padx=20, fill="x")
        
        # Load button
        load_button = ModernButton(
            actions_frame,
            text="📁  Load from File",
            command=self.load_sequence_from_file,
            height=40,
            fg_color=(self.colors['bg_tertiary'], self.colors['bg_tertiary']),
            hover_color=("#374151", "#374151"),
            text_color=self.colors['text_primary'],
            corner_radius=20,
            font=ctk.CTkFont(family="Segoe UI", size=14)
        )
        load_button._hover_color = ("#374151", "#374151")
        load_button.pack(pady=(0, 20), padx=20, fill="x")
        
        # Recent macros
        macros = self.storage.get_available_macros()
        if macros:
            recent_frame = GlassFrame(
                content_frame,
                fg_color=self.colors['bg_secondary'],
                corner_radius=15
            )
            recent_frame.pack(fill="both", expand=True)
            
            ctk.CTkLabel(
                recent_frame,
                text="RECENT MACROS",
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color=self.colors['text_secondary']
            ).pack(pady=(15, 10), padx=20, anchor="w")
            
            # Scrollable frame for macros
            macros_container = ctk.CTkScrollableFrame(
                recent_frame,
                fg_color="transparent",
                height=200
            )
            macros_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
            
            for macro in macros[:10]:
                macro_frame = ctk.CTkFrame(
                    macros_container,
                    fg_color=self.colors['bg_tertiary'],
                    corner_radius=8,
                    height=50
                )
                macro_frame.pack(fill="x", pady=5)
                macro_frame.pack_propagate(False)
                
                macro_info = ctk.CTkFrame(macro_frame, fg_color="transparent")
                macro_info.pack(side="left", fill="both", expand=True, padx=15)
                
                ctk.CTkLabel(
                    macro_info,
                    text=macro['name'],
                    font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                    text_color=self.colors['text_primary'],
                    anchor="w"
                ).pack(fill="x", pady=(10, 0))
                
                ctk.CTkLabel(
                    macro_info,
                    text=macro['modified'],
                    font=ctk.CTkFont(family="Segoe UI", size=11),
                    text_color=self.colors['text_secondary'],
                    anchor="w"
                ).pack(fill="x", pady=(0, 10))
                
                load_macro_btn = ModernButton(
                    macro_frame,
                    text="Load",
                    command=lambda m=macro: self.load_macro(m, saveload_window),
                    width=60,
                    height=30,
                    fg_color=(self.colors['accent_gradient_start'], self.colors['accent_gradient_end']),
                    hover_color=("#a855f7", "#818cf8"),
                    text_color=self.colors['text_primary'],
                    corner_radius=15,
                    font=ctk.CTkFont(family="Segoe UI", size=12)
                )
                load_macro_btn._hover_color = ("#a855f7", "#818cf8")
                load_macro_btn.pack(side="right", padx=10)
    
    def setup_callbacks(self):
        self.recorder.set_recording_callback(self.on_recording_changed)
        self.player.set_playback_callback(self.on_playback_changed)
        self.player.set_progress_callback(self.on_progress_changed)
    
    def setup_global_hotkeys(self):
        try:
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
            self.play_button.configure(text="▶  PLAY", state="normal")
            self.record_button.configure(text="⏺  RECORD", state="normal")
            
        except Exception as e:
            pass
    
    def on_recording_changed(self, is_recording: bool):
        if is_recording:
            self.record_button.configure(text="⏹  STOP RECORDING")
            self.play_button.configure(state="disabled")
        else:
            self.record_button.configure(text="⏺  RECORD")
            self.play_button.configure(state="normal")
    
    def on_playback_changed(self, is_playing: bool):
        if is_playing:
            self.play_button.configure(text="⏹  STOP")
            self.record_button.configure(state="disabled")
        else:
            self.play_button.configure(text="▶  PLAY")
            self.record_button.configure(state="normal")
    
    def on_progress_changed(self, current: int, total: int):
        # Could update button text or add progress indicator if needed
        pass
    
    def on_speed_changed(self, value):
        self.speed_value_label.configure(text=f"{value:.1f}x")
        self.player.set_playback_settings(value, int(self.loop_entry.get() or 1))
    
    def on_loop_changed(self, event=None):
        try:
            loop_count = int(self.loop_entry.get() or 1)
            self.player.set_playback_settings(self.speed_slider.get(), loop_count)
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
        else:
            self.recorder.start_recording()
    
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
    
    def load_last_sequence(self):
        last_sequence = self.storage.load_last_sequence()
        if last_sequence:
            self.current_sequence = last_sequence
            self.player.load_sequence(last_sequence)
    
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
                messagebox.showinfo("Success", f"Macro loaded: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load: {str(e)}")
    
    def load_macro(self, macro_info, window):
        try:
            sequence = self.storage.load_sequence(macro_info['filepath'])
            self.current_sequence = sequence
            self.player.load_sequence(sequence)
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