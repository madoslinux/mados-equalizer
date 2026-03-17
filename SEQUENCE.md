# Sequence Diagrams

This document contains Mermaid sequence diagrams showing the internal operation of the madOS Audio Equalizer.

## EQ Enable Flow

```mermaid
sequenceDiagram
    participant U as User
    participant A as EqualizerApp
    participant B as AudioBackend
    participant P as PipeWire
    participant W as wpctl

    U->>A: Click "Enable" button
    A->>B: enable_eq()
    B->>B: _save_original_default_sink()
    B->>B: _generate_filter_chain_config()
    B->>B: _write_config()
    B->>P: pipewire -c filter-chain.conf
    P-->>B: Filter-chain started
    B->>W: wpctl set-default <eq-node-id>
    B-->>A: (True, "eq_applied")
    A->>A: _update_enable_button(True)
    A->>A: _set_status("eq_applied")
    A->>A: state_db.save_enabled(True)
```

## Slider Change Flow (Debounced)

```mermaid
sequenceDiagram
    participant U as User
    participant A as EqualizerApp
    participant B as AudioBackend
    participant D as StateDB

    U->>A: Move band slider
    A->>A: _on_band_changed()
    A->>A: Update dB label
    A->>A: Update gain indicator
    alt EQ is enabled
        A->>A: Cancel pending timeout
        A->>A: Schedule 150ms debounce
    end

    Note over A: 150ms elapse

    A->>A: _apply_eq_debounced()
    A->>D: state_db.save_gains(gains)
    A->>B: apply_eq_async(gains)
    B-->>A: callback(success, message)
    A->>A: _on_eq_applied()
    A->>A: _set_status(message)
```

## Preset Selection Flow

```mermaid
sequenceDiagram
    participant U as User
    participant A as EqualizerApp
    participant P as PresetManager
    participant D as StateDB
    participant B as AudioBackend

    U->>A: Select preset from combo
    A->>A: _on_preset_changed()
    A->>P: preset_manager.get_preset(key)
    P-->>A: preset data
    A->>A: _set_slider_values(gains)
    A->>D: state_db.save_preset(key)
    A->>D: state_db.save_gains(gains)
    alt EQ enabled
        A->>B: apply_eq_async(gains)
    end
```

## Save Custom Preset Flow

```mermaid
sequenceDiagram
    participant U as User
    participant A as EqualizerApp
    participant P as PresetManager
    participant F as File System

    U->>A: Click "Save Preset"
    A->>A: Show dialog
    U->>A: Enter name, click Save
    A->>P: save_custom_preset(name, gains)
    P->>P: Validate name
    P->>F: Write presets.json
    F-->>P: Success
    P-->>A: (True, "preset_saved", key)
    A->>A: _populate_preset_combo()
    A->>A: preset_combo.set_active_id(key)
    A->>A: _set_status("preset_saved")
```

## Volume Control Flow

```mermaid
sequenceDiagram
    participant U as User
    participant A as EqualizerApp
    participant B as AudioBackend
    participant W as wpctl

    U->>A: Move volume slider
    A->>A: _on_volume_changed()
    A->>A: Update volume label
    A->>B: threading.Thread(set_volume)
    B->>W: wpctl set-volume <volume>
    W-->>B: Success
```

## Device Detection Flow

```mermaid
sequenceDiagram
    participant A as EqualizerApp
    participant B as AudioBackend
    participant W as wpctl

    A->>A: _refresh_device_info()
    A->>B: threading.Thread(refresh_output_device)
    B->>W: wpctl inspect @DEFAULT_AUDIO_SINK@
    alt Success
        W-->>B: Device info
        B->>B: Parse sink name
    else Fallback
        B->>W: wpctl status
        W-->>B: Sink list
    end
    B-->>A: callback with device name
    A->>A: _update_device_label()
```

## Application Startup Flow

```mermaid
sequenceDiagram
    participant Main as __main__.py
    participant A as EqualizerApp
    participant D as StateDB
    participant B as AudioBackend
    participant P as PresetManager

    Main->>A: EqualizerApp()
    A->>D: EqualizerStateDB()
    A->>B: AudioBackend()
    A->>P: PresetManager()
    A->>D: load_state()
    D-->>A: {gains, enabled, preset, language}
    A->>A: _build_window()
    A->>A: _build_ui()
    A->>A: apply_theme()
    A->>A: _restore_saved_state()
    A->>A: _refresh_device_info()
    A->>A: _refresh_volume()
    A->>A: window.show_all()
```

## Window Close / State Persistence Flow

```mermaid
sequenceDiagram
    participant U as User
    participant A as EqualizerApp
    participant D as StateDB
    participant B as AudioBackend

    U->>A: Close window
    A->>A: _on_delete()
    A->>A: Cancel pending debounce timeout
    A->>A: Collect current gains
    A->>A: Get active preset key
    A->>D: save_state(gains, enabled, preset, language)
    A->>D: close()
    A->>B: cleanup()
    A->>A: window.destroy()
    A->>A: Gtk.main_quit()
```

## Mute Toggle Flow

```mermaid
sequenceDiagram
    participant U as User
    participant A as EqualizerApp
    participant B as AudioBackend
    participant W as wpctl

    U->>A: Click mute button
    A->>B: threading.Thread(toggle_mute)
    B->>W: wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle
    W-->>B: New mute state
    B-->>A: callback (muted)
    A->>A: _update_mute_button(muted)
```