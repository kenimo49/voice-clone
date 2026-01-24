#!/bin/bash
# WSLg audio setup script for voice-clone
# This script configures PulseAudio and ALSA for audio recording in WSL

set -e

echo "=== Voice Clone WSLg Audio Setup ==="
echo

# Check if running in WSL
if [ ! -f /proc/version ] || ! grep -qi microsoft /proc/version; then
    echo "Warning: This script is designed for WSL. Continuing anyway..."
fi

# Install required packages
echo "[1/5] Installing audio packages..."
sudo apt-get update -qq
sudo apt-get install -y -qq pulseaudio pulseaudio-utils alsa-utils libportaudio2 > /dev/null 2>&1 || true
echo "Done."

# Create .asoundrc for ALSA -> PulseAudio routing
echo "[2/5] Configuring ALSA..."
cat > ~/.asoundrc << 'EOF'
pcm.!default {
    type pulse
}
ctl.!default {
    type pulse
}
EOF
echo "Created ~/.asoundrc"

# Check PulseAudio socket
echo "[3/5] Checking PulseAudio..."
PULSE_SOCKET="/mnt/wslg/PulseServer"
if [ -e "$PULSE_SOCKET" ]; then
    echo "WSLg PulseAudio socket found: $PULSE_SOCKET"
    export PULSE_SERVER="unix:$PULSE_SOCKET"
else
    echo "WSLg PulseAudio socket not found. Checking alternative..."
    # Try to start PulseAudio if not running
    if ! pgrep -x pulseaudio > /dev/null; then
        echo "Starting PulseAudio..."
        pulseaudio --start --exit-idle-time=-1 2>/dev/null || true
    fi
fi

# Add PULSE_SERVER to bashrc if not present
echo "[4/5] Updating shell configuration..."
if ! grep -q "PULSE_SERVER" ~/.bashrc 2>/dev/null; then
    echo '' >> ~/.bashrc
    echo '# WSLg PulseAudio configuration' >> ~/.bashrc
    echo 'export PULSE_SERVER="unix:/mnt/wslg/PulseServer"' >> ~/.bashrc
    echo "Added PULSE_SERVER to ~/.bashrc"
else
    echo "PULSE_SERVER already configured in ~/.bashrc"
fi

# Test audio
echo "[5/5] Testing audio configuration..."
export PULSE_SERVER="unix:/mnt/wslg/PulseServer"

echo
echo "=== Audio Sources ==="
pactl list sources short 2>/dev/null || echo "Could not list audio sources"

echo
echo "=== Audio Sinks ==="
pactl list sinks short 2>/dev/null || echo "Could not list audio sinks"

echo
echo "=== Setup Complete ==="
echo
echo "Next steps:"
echo "  1. Restart your terminal or run: source ~/.bashrc"
echo "  2. Test recording: voice-clone devices --audio"
echo "  3. If RDPSource is not listed, ensure Windows microphone is enabled"
echo
echo "Troubleshooting:"
echo "  - Enable microphone in Windows Settings > Privacy > Microphone"
echo "  - Restart WSL: wsl --shutdown (from PowerShell)"
echo "  - Check WSLg is enabled: /mnt/wslg should exist"
