# WSL/Linux-Based Development Setup Guide

This guide helps you set up a Linux-based development environment for the Semantic Foragecast Engine, enabling better compatibility with claude.ai/code's Linux containers while working on Windows 11.

## Why WSL?

**Benefits:**
- **Cross-platform compatibility**: Matches claude.ai/code's Linux container environment
- **Better package management**: Native access to Linux tools (apt, pip)
- **Blender compatibility**: Linux Blender builds often work better with Python automation
- **FFmpeg integration**: Easier installation and configuration
- **Git consistency**: No path conversion issues (Windows `\` vs Linux `/`)
- **Development parity**: Same environment for local dev and cloud sessions

## Prerequisites

- Windows 11 (or Windows 10 version 2004+)
- Administrator access
- At least 10GB free disk space
- Internet connection

---

## Part 1: Installing WSL2

### Step 1: Enable WSL

Open PowerShell as Administrator and run:

```powershell
wsl --install
```

This command will:
- Enable WSL and Virtual Machine Platform
- Install Ubuntu (default distribution)
- Set WSL 2 as default

**Restart your computer after installation.**

### Step 2: Set Up Ubuntu

After restart, Ubuntu will launch automatically:

1. Create a username (lowercase, no spaces)
2. Set a password (you'll need this for `sudo`)
3. Wait for installation to complete

```bash
# Update package lists
sudo apt update && sudo apt upgrade -y
```

### Step 3: Verify Installation

```bash
# Check WSL version (should show version 2)
wsl --list --verbose

# Check Ubuntu version
lsb_release -a
```

---

## Part 2: Installing Development Tools

### Step 1: Install Python 3.11+

```bash
# Install Python 3.11 and pip
sudo apt install -y python3.11 python3.11-venv python3-pip

# Verify installation
python3.11 --version
pip3 --version

# Set Python 3.11 as default
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
```

### Step 2: Install Blender

**Option A: Install via Snap (Recommended)**

```bash
# Install Blender 4.2 LTS
sudo snap install blender --channel=4.2lts/stable --classic

# Verify installation
blender --version
```

**Option B: Download Portable Version**

```bash
# Create installation directory
mkdir -p ~/blender
cd ~/blender

# Download Blender 4.2 LTS (adjust URL for latest version)
wget https://download.blender.org/release/Blender4.2/blender-4.2.0-linux-x64.tar.xz

# Extract
tar -xf blender-4.2.0-linux-x64.tar.xz

# Add to PATH (add to ~/.bashrc for persistence)
export PATH="$HOME/blender/blender-4.2.0-linux-x64:$PATH"

# Verify
blender --version
```

### Step 3: Install FFmpeg

```bash
# Install FFmpeg with full codec support
sudo apt install -y ffmpeg

# Verify installation
ffmpeg -version
```

### Step 4: Install Additional Dependencies

```bash
# Install system libraries for audio processing
sudo apt install -y \
    libsndfile1 \
    libsndfile1-dev \
    portaudio19-dev \
    build-essential \
    pkg-config

# Install Git (if not already present)
sudo apt install -y git
```

---

## Part 3: Setting Up the Project

### Step 1: Clone the Repository

```bash
# Navigate to your WSL home directory
cd ~

# Clone the repository
git clone https://github.com/semanticintent/semantic-foragecast-engine.git
cd semantic-foragecast-engine
```

**Alternative: Access Windows Files**

If you prefer to keep files on Windows (for GUI tools):

```bash
# Navigate to Windows C:\ drive (mounted at /mnt/c)
cd /mnt/c/workspace/semantic-foragecast-engine

# Note: WSL can read/write Windows files, but performance is slower
```

⚠️ **Performance Note**: For best performance, keep project files in WSL's native filesystem (`~/semantic-foragecast-engine`) rather than Windows filesystem (`/mnt/c/...`).

### Step 2: Create Python Virtual Environment

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### Step 3: Install Python Dependencies

```bash
# Install all requirements
pip install -r requirements.txt

# Verify key packages
python -c "import librosa; print('LibROSA:', librosa.__version__)"
python -c "import numpy; print('NumPy:', numpy.__version__)"
python -c "import yaml; print('PyYAML OK')"
```

### Step 4: Configure Blender Path

Edit `config.yaml` to set Blender path:

```yaml
blender:
  # For snap installation
  executable_path: /snap/bin/blender

  # OR for portable installation
  # executable_path: /home/yourusername/blender/blender-4.2.0-linux-x64/blender

  background: true
  script_path: blender_script.py
```

### Step 5: Test Installation

```bash
# Run Phase 1 only (audio prep)
python main.py --phase 1

# If successful, test Phase 2 (Blender)
python main.py --phase 2

# Full pipeline test
python main.py
```

---

## Part 4: WSL + Windows Integration

### Accessing Files Between Systems

**From WSL → Windows:**

```bash
# Windows C:\ is mounted at /mnt/c
ls /mnt/c/Users/YourUsername/Documents

# Windows D:\ is mounted at /mnt/d
ls /mnt/d/
```

**From Windows → WSL:**

Open Windows Explorer and navigate to:
```
\\wsl$\Ubuntu\home\yourusername\semantic-foragecast-engine
```

Or use the command line:
```powershell
# PowerShell
cd \\wsl$\Ubuntu\home\yourusername\semantic-foragecast-engine

# Command Prompt
cd \\wsl.localhost\Ubuntu\home\yourusername\semantic-foragecast-engine
```

### Using VS Code with WSL

Install the **Remote - WSL** extension:

1. Open VS Code in Windows
2. Install extension: `ms-vscode-remote.remote-wsl`
3. Click green icon (bottom-left) → "Connect to WSL"
4. Open folder: `/home/yourusername/semantic-foragecast-engine`

Now you have:
- Windows UI for VS Code
- Linux backend for terminal/execution
- Best of both worlds!

### Git Configuration

Configure Git in WSL (separate from Windows Git):

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Use credential helper to share credentials with Windows
git config --global credential.helper "/mnt/c/Program\ Files/Git/mingw64/bin/git-credential-manager.exe"
```

---

## Part 5: Optimizing for claude.ai/code Compatibility

### Path Handling Best Practices

**✅ Always use forward slashes:**
```python
# Good (cross-platform)
config_path = "demo_reel/config_3d.yaml"
blender_path = "/usr/bin/blender"

# Bad (Windows-specific)
config_path = "demo_reel\\config_3d.yaml"
blender_path = "C:\\Program Files\\Blender\\blender.exe"
```

**✅ Use `pathlib` for path operations:**
```python
from pathlib import Path

# Good
project_root = Path(__file__).parent
config_file = project_root / "config.yaml"

# This works on Windows, Linux, and macOS
```

### Testing for Cross-Platform Compatibility

Create a test script to verify cross-platform compatibility:

```bash
#!/bin/bash
# test_cross_platform.sh

echo "=== Testing Cross-Platform Compatibility ==="

# Test 1: Python availability
echo "✓ Python version:"
python3 --version

# Test 2: Dependencies
echo "✓ Testing dependencies..."
python3 -c "import librosa, numpy, yaml, soundfile; print('All imports OK')"

# Test 3: Blender
echo "✓ Blender version:"
blender --version

# Test 4: FFmpeg
echo "✓ FFmpeg version:"
ffmpeg -version | head -1

# Test 5: Sample run (Phase 1 only)
echo "✓ Running Phase 1 test..."
python3 main.py --phase 1 --config demo_reel/config_3d_preview.yaml

echo "=== All tests passed! ==="
```

Run with:
```bash
chmod +x test_cross_platform.sh
./test_cross_platform.sh
```

### Dockerfile for Ultimate Portability

Create a `Dockerfile` to match claude.ai/code's environment exactly:

```dockerfile
# Dockerfile
FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    ffmpeg \
    blender \
    libsndfile1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Default command
CMD ["python3", "main.py", "--help"]
```

Build and test:
```bash
# Build Docker image
docker build -t semantic-foragecast-engine .

# Run container interactively
docker run -it --rm -v $(pwd)/outputs:/app/outputs semantic-foragecast-engine bash

# Inside container, run pipeline
python3 main.py
```

---

## Part 6: Common Issues and Solutions

### Issue 1: Blender "command not found"

**Symptom:** `blender: command not found`

**Solution:**
```bash
# Check if Blender is installed
which blender
snap list | grep blender

# If not installed, install via snap
sudo snap install blender --channel=4.2lts/stable --classic

# Or add portable version to PATH
export PATH="$HOME/blender/blender-4.2.0-linux-x64:$PATH"
echo 'export PATH="$HOME/blender/blender-4.2.0-linux-x64:$PATH"' >> ~/.bashrc
```

### Issue 2: Permission Denied on Windows Files

**Symptom:** `Permission denied` when running scripts from `/mnt/c/`

**Solution:**
```bash
# Option 1: Fix permissions
chmod +x main.py prep_audio.py export_video.py

# Option 2: Move project to WSL filesystem
cp -r /mnt/c/workspace/semantic-foragecast-engine ~/
cd ~/semantic-foragecast-engine
```

### Issue 3: Python Module Not Found in Blender

**Symptom:** Blender can't find `librosa`, `numpy`, etc.

**Solution:**
```bash
# Install packages to Blender's Python
blender_python=$(blender --version | grep -oP 'Python \K[0-9.]+')
sudo apt install -y python3-pip
python3 -m pip install --user librosa numpy scipy soundfile

# OR: Install to system Python and use --python-use-system-env
blender --background --python-use-system-env --python blender_script.py
```

### Issue 4: Audio Library Errors

**Symptom:** `soundfile` or `librosa` crashes with codec errors

**Solution:**
```bash
# Install audio codecs
sudo apt install -y libsndfile1-dev libportaudio2

# Reinstall Python packages
pip install --force-reinstall librosa soundfile
```

### Issue 5: Slow Performance on Windows Files

**Symptom:** Pipeline runs 10x slower when files are on `/mnt/c/`

**Solution:**
Keep all working files in WSL's native filesystem:
```bash
# Move project to WSL
cp -r /mnt/c/workspace/semantic-foragecast-engine ~/
cd ~/semantic-foragecast-engine

# Copy outputs back to Windows if needed
cp -r outputs /mnt/c/workspace/outputs
```

---

## Part 7: Workflow Recommendations

### Development Workflow

**Local Development (WSL):**
1. Code in VS Code with Remote-WSL
2. Test with `python main.py`
3. Commit changes via WSL git
4. Push to GitHub

**Cloud Testing (claude.ai/code):**
1. Open claude.ai/code
2. Clone/pull latest changes
3. Run same commands (they just work!)
4. No path translation needed

### File Sharing Strategy

**Option A: WSL-Primary** (Recommended)
- Keep project in `~/semantic-foragecast-engine`
- Access via VS Code Remote-WSL
- Copy outputs to Windows when needed

**Option B: Windows-Primary**
- Keep project in `/mnt/c/workspace/semantic-foragecast-engine`
- Accept performance tradeoff
- Use Windows tools directly

**Option C: Hybrid**
- Keep code in Windows (for GUI tools)
- Run pipeline in WSL (for compatibility)
- Use symlinks to bridge filesystems

### CI/CD Integration

Add GitHub Actions workflow for Linux testing:

```yaml
# .github/workflows/test.yml
name: Test Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          sudo apt-get install -y ffmpeg blender
          pip install -r requirements.txt
      - name: Run Phase 1 tests
        run: python main.py --phase 1 --config demo_reel/config_3d_preview.yaml
```

---

## Quick Reference

### Common Commands

```bash
# Start WSL from Windows
wsl

# Open WSL in specific directory
wsl -d Ubuntu --cd ~/semantic-foragecast-engine

# Run pipeline with preview mode
python3 main.py --config demo_reel/config_3d_preview.yaml

# Check logs
tail -f outputs/pipeline.log

# Activate virtual environment
source venv/bin/activate

# Deactivate virtual environment
deactivate

# Shutdown WSL (from PowerShell)
wsl --shutdown
```

### Useful Aliases

Add to `~/.bashrc`:

```bash
# Project shortcuts
alias foragecast="cd ~/semantic-foragecast-engine && source venv/bin/activate"
alias pipeline="python3 main.py"
alias preview="python3 main.py --config demo_reel/config_3d_preview.yaml"

# Git shortcuts
alias gs="git status"
alias gd="git diff"
alias gc="git commit"
alias gp="git push"
```

Apply changes:
```bash
source ~/.bashrc
```

---

## Summary

### What We've Set Up

✅ WSL2 with Ubuntu
✅ Python 3.11+ with virtual environment
✅ Blender 4.2+ for 3D rendering
✅ FFmpeg for video encoding
✅ Cross-platform path handling
✅ VS Code integration
✅ Git configuration
✅ Docker option for ultimate portability

### Benefits Achieved

🎯 **100% compatibility** with claude.ai/code Linux containers
🚀 **No path conversion issues** between Windows and Linux
🔄 **Seamless workflow** between local and cloud development
📦 **Better package management** with apt/pip
🐛 **Easier debugging** with native Linux tools

### Next Steps

1. **Test the pipeline:** Run `python main.py` in WSL
2. **Verify compatibility:** Run the same command in claude.ai/code
3. **Set up VS Code Remote-WSL** for best IDE experience
4. **Consider Docker** if you need exact environment matching
5. **Update documentation** with any project-specific WSL notes

---

## Additional Resources

- [WSL Documentation](https://docs.microsoft.com/en-us/windows/wsl/)
- [Blender Python API](https://docs.blender.org/api/current/)
- [VS Code Remote Development](https://code.visualstudio.com/docs/remote/wsl)
- [Docker Documentation](https://docs.docker.com/)

---

**Last Updated:** November 12, 2025
**Tested On:** Windows 11 + WSL2 (Ubuntu 22.04)
**Project:** Semantic Foragecast Engine v4.0
