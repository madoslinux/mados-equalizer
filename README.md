# madOS Audio Equalizer

A professional 8-band parametric audio equalizer application for Linux with PipeWire/PulseAudio backend integration.

## Features

- **8-band Parametric EQ**: 60Hz, 170Hz, 310Hz, 600Hz, 1kHz, 3kHz, 6kHz, 12kHz
- **Audio Backend**: PipeWire filter-chain with PulseAudio fallback
- **10 Built-in Presets**: Flat, Rock, Pop, Jazz, Classical, Bass Boost, Treble Boost, Vocal, Electronic, Acoustic
- **Custom Presets**: Save and manage your own presets
- **Master Volume Control**: Volume slider with mute toggle
- **Visual Gain Indicators**: Color-coded bars showing EQ levels
- **Multi-language Support**: English, Spanish, French, German, Chinese, Japanese
- **Nord Theme**: Dark theme with Nord color palette

## Requirements

- Python 3.8+
- GTK 3.0
- PipeWire or PulseAudio
- wpctl (WirePlumber) for PipeWire systems
- pactl for PulseAudio systems

## Installation

```bash
# Clone the repository
git clone https://github.com/madoslinux/mados-equalizer.git
cd mados-equalizer

# Run the application
python3 -m mados_equalizer
```

Or run directly:

```bash
python3 __main__.py
```

## Usage

1. **Enable the Equalizer**: Click the "Enable" button to activate the EQ
2. **Adjust Bands**: Use the vertical sliders to adjust gain for each frequency band (-12dB to +12dB)
3. **Select Preset**: Choose from built-in presets or save custom presets
4. **Volume Control**: Adjust master volume with the vertical slider on the right
5. **Mute**: Click the mute button to silence audio

## Configuration

The application stores configuration in the following locations:

- **EQ Filter-chain Config**: `~/.config/mados/equalizer/filter-chain.conf`
- **Custom Presets**: `~/.config/mados/equalizer/presets.json`
- **State Database**: `~/.local/share/mados-equalizer/state.db`

## Architecture

### Components

- **app.py**: Main GTK3 application window and UI
- **backend.py**: PipeWire/PulseAudio audio processing backend
- **database.py**: SQLite state persistence
- **presets.py**: Preset management (built-in and custom)
- **translations.py**: Multi-language translation strings
- **theme.py**: Nord color theme CSS

### How It Works

The application creates a PipeWire filter-chain with 8 bq_peaking (peaking EQ) filters, one for each frequency band. When EQ is enabled:

1. A configuration file is generated with the current gain values
2. A lightweight `pipewire -c` subprocess is started to host the filter-chain
3. The EQ sink is set as the default audio output, routing all audio through the EQ

For PulseAudio systems, it falls back to using the LADSPA mbeq plugin.

See [SEQUENCE.md](SEQUENCE.md) for the internal sequence diagram.

## Development

See [AGENTS.md](AGENTS.md) for development guidelines.

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.