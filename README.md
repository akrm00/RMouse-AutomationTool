# Macro Automation Tool

A modern macro automation tool with graphical interface, similar to TinyTask or ReMouse.

## Features

- **Recording**: Captures mouse movements, clicks and keyboard inputs
- **Playback**: Replays recorded actions exactly
- **Advanced Settings**: Playback speed (0.1x to 15x) and repetitions
- **Save/Load**: Macro management in JSON format
- **Modern Interface**: Flat design with CustomTkinter
- **Auto-save**: Automatic saving of last session

## Installation

### Requirements
- Python 3.8 or higher
- Windows (tested on Windows 10/11)

### Installation Steps

1. **Clone the project**
```bash
git clone <repository-url>
cd AutomaticMouse
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python main.py
```

## Usage

### Main Interface

The interface contains 4 main buttons:

1. **Play**: Starts playback of the last recorded sequence
2. **Admin**: Administrator mode (disabled in this version)
3. **Record**: Starts/stops recording
4. **Save/Load**: Save and load menu

### Recording a Macro

1. Click on **Record**
2. Perform your actions (mouse movements, clicks, keyboard inputs)
3. Click on **Stop** to stop recording
4. The sequence is automatically saved

### Playing a Macro

1. Make sure a sequence is loaded
2. Adjust speed with the slider (0.1x to 15x)
3. Set number of repetitions (0 = infinite)
4. Click on **Play**

### Save/Load

- **Manual save**: Save/Load menu → "Save Current Sequence"
- **Loading**: Save/Load menu → Select an existing macro
- **Auto-save**: Last sequence is automatically saved

## Project Structure

```
AutomaticMouse/
├── main.py          # Main interface
├── recorder.py      # Recording module
├── player.py        # Playback module
├── storage.py       # Save/load management
├── settings.json    # Configuration
├── requirements.txt # Dependencies
├── macros/         # Saved macros folder
└── README.md       # This file
```

## Configuration

The `settings.json` file contains:
- **playback_speed**: Default playback speed
- **loop_count**: Default number of repetitions
- **auto_save**: Auto-save enabled
- **hotkey_play**: Keyboard shortcut (F8 by default)
- **emergency_stop**: Ctrl+S for emergency stop

## Security

- **Emergency stop**: **Ctrl+S** instantly stops recording or playback
- **PyAutoGUI Failsafe**: Quick movement to upper left corner stops execution
- **Input validation**: User parameter verification
- **Error handling**: Error capture and display

## Dependencies

- **customtkinter**: Modern graphical interface
- **pyautogui**: Mouse/keyboard action simulation
- **pynput**: Input event capture
- **Pillow**: Image processing (required by pyautogui)

## Macro Format

Macros are saved in JSON format with this structure:

```json
{
  "created_at": "2024-01-01T12:00:00",
  "version": "1.0",
  "total_actions": 25,
  "sequence": [
    {
      "type": "mouse_move",
      "x": 100,
      "y": 200,
      "timestamp": 0.0
    },
    {
      "type": "mouse_press",
      "x": 100,
      "y": 200,
      "button": "left",
      "timestamp": 0.5
    }
    // ... other actions
  ]
}
```

## Use Cases

- **Automated testing**: User interaction reproduction
- **Repetitive tasks**: Workflow automation
- **Demonstrations**: Tutorial recording
- **Gaming**: Repetitive task automation (according to ToS)

## Limitations

- **Windows only**: Tested primarily on Windows
- **Permissions**: Some protected applications may block automation
- **Performance**: Movement capture can generate many events

## Warnings

- Use this tool responsibly
- Respect third-party software terms of use
- Always test your macros before production use
- Regularly backup important macros

## License

This project is under MIT license. See the `LICENSE` file for more details.

## Support

For any questions or issues:
1. Check [existing issues](../../issues)
2. Create a new issue if necessary
3. Include error logs and your system configuration

---

**Developed by akrm00** 