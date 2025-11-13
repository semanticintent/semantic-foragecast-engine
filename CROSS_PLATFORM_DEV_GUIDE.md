# Cross-Platform Development Guide

This guide documents the key differences between Windows 11 and Linux development environments for the Semantic Foragecast Engine, enabling you to switch seamlessly between platforms.

---

## Philosophy

**Windows 11 is the primary development environment.** This guide exists to help you understand what changes when deploying to Linux (e.g., claude.ai/code containers) or collaborating with Linux-based developers.

---

## Quick Reference: Key Differences

| Aspect | Windows 11 | Linux (Ubuntu 22.04+) |
|--------|------------|----------------------|
| **Python Command** | `python` or `python3` | `python3` |
| **Blender Path** | `C:\Program Files\Blender Foundation\Blender 4.0\blender.exe` | `/usr/bin/blender` or `/snap/bin/blender` |
| **FFmpeg Path** | `C:\workspace\semantic-foragecast-engine\ffmpeg\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe` or `ffmpeg` if in PATH | `/usr/bin/ffmpeg` |
| **Path Separator** | Backslash `\` (but use `/` in code) | Forward slash `/` |
| **Line Endings** | CRLF (`\r\n`) | LF (`\n`) |
| **Package Manager** | `pip` (manual) or `choco` | `apt`, `snap`, `pip` |
| **Virtual Env Activation** | `venv\Scripts\activate` | `source venv/bin/activate` |
| **Python Version** | 3.13.9 (current) | 3.12.x (Ubuntu 24.04) or 3.11.x (Ubuntu 22.04) |

---

## Part 1: Windows 11 Setup (Primary)

### Prerequisites

- **OS**: Windows 11 (or Windows 10 21H2+)
- **Administrator access**: For installing software
- **Disk space**: ~15GB for tools and dependencies

### Installation Steps

#### Step 1: Install Python 3.11+

**Option A: Official Installer (Recommended)**

1. Download from [python.org](https://www.python.org/downloads/)
2. Run installer, **check "Add Python to PATH"**
3. Verify:
   ```cmd
   python --version
   pip --version
   ```

**Option B: Chocolatey**

```powershell
# Install Chocolatey first (admin PowerShell)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install Python
choco install python --version=3.11.0
```

#### Step 2: Install Blender 4.0+

**Download and Install:**

1. Download from [blender.org](https://www.blender.org/download/)
2. Install to default location: `C:\Program Files\Blender Foundation\Blender 4.0\`
3. Verify (CMD or PowerShell):
   ```cmd
   "C:\Program Files\Blender Foundation\Blender 4.0\blender.exe" --version
   ```

**Add to PATH (Optional):**

1. Search "Environment Variables" in Start Menu
2. Edit "Path" under "System variables"
3. Add: `C:\Program Files\Blender Foundation\Blender 4.0\`
4. Restart terminal, then run:
   ```cmd
   blender --version
   ```

#### Step 3: Install FFmpeg

**Option A: Portable (Current Setup)**

1. Download from [ffmpeg.org](https://ffmpeg.org/download.html#build-windows)
2. Extract to project folder: `C:\workspace\semantic-foragecast-engine\ffmpeg\`
3. FFmpeg binary at: `ffmpeg\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe`

**Option B: Add to PATH**

1. Download and extract FFmpeg anywhere (e.g., `C:\ffmpeg\`)
2. Add `C:\ffmpeg\bin\` to PATH
3. Verify:
   ```cmd
   ffmpeg -version
   ```

#### Step 4: Clone Repository

```cmd
cd C:\workspace
git clone https://github.com/semanticintent/semantic-foragecast-engine.git
cd semantic-foragecast-engine
```

#### Step 5: Set Up Python Environment

```cmd
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import librosa; print('LibROSA:', librosa.__version__)"
python -c "import numpy; print('NumPy:', numpy.__version__)"
```

#### Step 6: Configure Blender and FFmpeg Paths

Edit `config.yaml`:

```yaml
blender:
  # Windows - absolute path
  executable_path: "C:\\Program Files\\Blender Foundation\\Blender 4.0\\blender.exe"

  # Or if Blender is in PATH
  # executable_path: null

  background: true
  script_path: blender_script.py

ffmpeg:
  # Windows - portable installation
  executable_path: "ffmpeg\\ffmpeg-master-latest-win64-gpl\\bin\\ffmpeg.exe"

  # Or if FFmpeg is in PATH
  # executable_path: null
```

#### Step 7: Test Installation

```cmd
# Test Phase 1 (audio prep)
python main.py --phase 1 --config demo_reel\config_3d_preview.yaml

# Test Phase 2 (Blender)
python main.py --phase 2 --config demo_reel\config_3d_preview.yaml

# Full pipeline
python main.py --config demo_reel\config_3d_preview.yaml
```

---

## Part 2: Linux Setup (Secondary/Cloud)

### Prerequisites

- **OS**: Ubuntu 22.04 LTS or Ubuntu 24.04 LTS
- **sudo access**: For installing packages
- **Disk space**: ~5GB for tools and dependencies

### Installation Steps

#### Step 1: Update System

```bash
sudo apt update && sudo apt upgrade -y
```

#### Step 2: Install Python 3.11+

```bash
# Ubuntu 24.04 has Python 3.12 by default
python3 --version

# Install pip and venv
sudo apt install -y python3-pip python3-venv

# Install build dependencies
sudo apt install -y build-essential pkg-config \
    libsndfile1 libsndfile1-dev portaudio19-dev
```

#### Step 3: Install Blender 4.0+

**Option A: Snap (Recommended)**

```bash
# Install Blender 4.0
sudo snap install blender --channel=4.0 --classic

# Install missing dependencies
sudo apt install -y libsm6 libxrender1 libxrandr2 libxi6 libgl1

# Verify
/snap/bin/blender --version
```

**Option B: Official Download**

```bash
# Download and extract
cd ~
wget https://download.blender.org/release/Blender4.0/blender-4.0.2-linux-x64.tar.xz
tar -xf blender-4.0.2-linux-x64.tar.xz

# Add to PATH (add to ~/.bashrc for persistence)
export PATH="$HOME/blender-4.0.2-linux-x64:$PATH"

# Verify
blender --version
```

#### Step 4: Install FFmpeg

```bash
# Install FFmpeg with full codec support
sudo apt install -y ffmpeg

# Verify
ffmpeg -version
```

#### Step 5: Clone Repository

```bash
cd ~
git clone https://github.com/semanticintent/semantic-foragecast-engine.git
cd semantic-foragecast-engine
```

#### Step 6: Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import librosa; print('LibROSA:', librosa.__version__)"
python -c "import numpy; print('NumPy:', numpy.__version__)"
```

#### Step 7: Configure Blender and FFmpeg Paths

Edit `config.yaml`:

```yaml
blender:
  # Linux - snap installation
  executable_path: /snap/bin/blender

  # Or portable installation
  # executable_path: /home/username/blender-4.0.2-linux-x64/blender

  # Or if Blender is in PATH
  # executable_path: null

  background: true
  script_path: blender_script.py

ffmpeg:
  # Linux - system installation
  executable_path: null  # Uses 'ffmpeg' from PATH
```

#### Step 8: Test Installation

```bash
# Test Phase 1 (audio prep)
python main.py --phase 1 --config demo_reel/config_3d_preview.yaml

# Test Phase 2 (Blender)
python main.py --phase 2 --config demo_reel/config_3d_preview.yaml

# Full pipeline
python main.py --config demo_reel/config_3d_preview.yaml
```

---

## Part 3: Cross-Platform Code Guidelines

### Path Handling (CRITICAL)

**❌ NEVER do this:**

```python
# Bad - Windows-specific
config_path = "demo_reel\\config_3d.yaml"
blender_path = "C:\\Program Files\\Blender\\blender.exe"

# Bad - Linux-specific
config_path = "/home/user/project/demo_reel/config_3d.yaml"
```

**✅ ALWAYS do this:**

```python
from pathlib import Path

# Good - cross-platform
project_root = Path(__file__).parent
config_path = project_root / "demo_reel" / "config_3d.yaml"

# Good - relative paths with forward slashes
config_path = "demo_reel/config_3d.yaml"  # Works on both platforms

# Good - absolute path resolution
config_path = Path("demo_reel/config_3d.yaml").resolve()
```

### Line Endings

**Configure Git to handle line endings automatically:**

Windows:
```cmd
git config --global core.autocrlf true
```

Linux:
```bash
git config --global core.autocrlf input
```

Add to `.gitattributes` in project root:
```
# Auto detect text files and normalize line endings
* text=auto

# Force LF for specific files
*.py text eol=lf
*.sh text eol=lf
*.yaml text eol=lf
*.md text eol=lf

# Binary files
*.png binary
*.jpg binary
*.wav binary
*.mp4 binary
*.blend binary
```

### Python Virtual Environments

**Activation:**

Windows:
```cmd
venv\Scripts\activate
```

Linux/macOS:
```bash
source venv/bin/activate
```

**Cross-platform script:**

```python
# activate_venv.py
import sys
import os
from pathlib import Path

venv_path = Path(__file__).parent / "venv"

if sys.platform == "win32":
    activate_script = venv_path / "Scripts" / "activate.bat"
else:
    activate_script = venv_path / "bin" / "activate"

print(f"Run: {activate_script}")
```

### Executable Paths

**Always use configuration files:**

```yaml
# config.yaml (Windows version)
blender:
  executable_path: "C:\\Program Files\\Blender Foundation\\Blender 4.0\\blender.exe"

# config.yaml (Linux version)
blender:
  executable_path: /snap/bin/blender

# config.yaml (Cross-platform - use PATH)
blender:
  executable_path: null  # Auto-detects 'blender' from PATH
```

**Auto-detection in code:**

```python
import shutil
from pathlib import Path

def find_blender():
    """Find Blender executable cross-platform."""
    # Check config first
    config_path = config.get('blender', {}).get('executable_path')
    if config_path and Path(config_path).exists():
        return config_path

    # Try PATH
    blender_cmd = shutil.which('blender')
    if blender_cmd:
        return blender_cmd

    # Try common locations
    if sys.platform == "win32":
        common_paths = [
            "C:\\Program Files\\Blender Foundation\\Blender 4.0\\blender.exe",
            "C:\\Program Files\\Blender Foundation\\Blender 4.2\\blender.exe",
        ]
    else:
        common_paths = [
            "/snap/bin/blender",
            "/usr/bin/blender",
            str(Path.home() / "blender-4.0.2-linux-x64" / "blender"),
        ]

    for path in common_paths:
        if Path(path).exists():
            return path

    raise FileNotFoundError("Blender not found")
```

### Shell Commands

**Use Python's `subprocess` module:**

```python
import subprocess
import sys

# Cross-platform command execution
def run_command(cmd, **kwargs):
    """Run command cross-platform."""
    # On Windows, shell=True may be needed for certain commands
    shell = sys.platform == "win32" and isinstance(cmd, str)

    result = subprocess.run(
        cmd,
        shell=shell,
        capture_output=True,
        text=True,
        **kwargs
    )
    return result

# Example usage
if sys.platform == "win32":
    cmd = ["C:\\Program Files\\Blender\\blender.exe", "--version"]
else:
    cmd = ["blender", "--version"]

result = run_command(cmd)
print(result.stdout)
```

---

## Part 4: Environment-Specific Configuration

### Using Environment Variables

**Set environment variables:**

Windows (CMD):
```cmd
set FORAGECAST_ENV=windows
set BLENDER_PATH=C:\Program Files\Blender Foundation\Blender 4.0\blender.exe
```

Windows (PowerShell):
```powershell
$env:FORAGECAST_ENV = "windows"
$env:BLENDER_PATH = "C:\Program Files\Blender Foundation\Blender 4.0\blender.exe"
```

Linux:
```bash
export FORAGECAST_ENV=linux
export BLENDER_PATH=/snap/bin/blender
```

**Read in Python:**

```python
import os

env = os.getenv('FORAGECAST_ENV', 'unknown')
blender_path = os.getenv('BLENDER_PATH')

if blender_path is None:
    # Auto-detect
    blender_path = find_blender()
```

### Multiple Config Files

**Strategy: Environment-specific configs**

```
project/
├── config.yaml                    # Base config
├── config.windows.yaml            # Windows overrides
├── config.linux.yaml              # Linux overrides
└── config.claude.yaml             # claude.ai/code specific
```

**Load config in Python:**

```python
import sys
import yaml
from pathlib import Path

def load_config(base_config="config.yaml"):
    """Load config with environment-specific overrides."""
    config_path = Path(base_config)

    # Load base config
    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Determine environment
    if sys.platform == "win32":
        override_file = "config.windows.yaml"
    elif sys.platform.startswith("linux"):
        override_file = "config.linux.yaml"
    else:
        override_file = None

    # Apply overrides
    if override_file:
        override_path = config_path.parent / override_file
        if override_path.exists():
            with open(override_path) as f:
                overrides = yaml.safe_load(f)

            # Deep merge (simplified)
            config.update(overrides)

    return config
```

---

## Part 5: Testing Cross-Platform Compatibility

### Automated Testing

**Create a test script: `test_cross_platform.py`**

```python
#!/usr/bin/env python3
"""Test cross-platform compatibility."""

import sys
import subprocess
from pathlib import Path

def test_python():
    """Test Python installation."""
    print(f"✓ Python {sys.version}")
    assert sys.version_info >= (3, 11), "Python 3.11+ required"

def test_imports():
    """Test required packages."""
    required = ['librosa', 'numpy', 'yaml', 'soundfile', 'scipy']
    for pkg in required:
        try:
            __import__(pkg)
            print(f"✓ {pkg} installed")
        except ImportError:
            print(f"✗ {pkg} missing")
            sys.exit(1)

def test_blender():
    """Test Blender availability."""
    from main import PipelineOrchestrator

    orchestrator = PipelineOrchestrator('config.yaml')
    blender_path = orchestrator._find_blender()

    result = subprocess.run(
        [blender_path, '--version'],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print(f"✓ Blender found: {blender_path}")
        print(f"  {result.stdout.split(chr(10))[0]}")
    else:
        print(f"✗ Blender not working")
        sys.exit(1)

def test_ffmpeg():
    """Test FFmpeg availability."""
    result = subprocess.run(
        ['ffmpeg', '-version'],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print(f"✓ FFmpeg found")
        print(f"  {result.stdout.split(chr(10))[0]}")
    else:
        print(f"✗ FFmpeg not found")
        sys.exit(1)

def test_paths():
    """Test path handling."""
    test_path = Path("demo_reel") / "config_3d_preview.yaml"

    if test_path.exists():
        print(f"✓ Path handling works: {test_path}")
    else:
        print(f"✗ Path not found: {test_path}")
        sys.exit(1)

if __name__ == "__main__":
    print(f"=== Testing on {sys.platform} ===\n")

    test_python()
    test_imports()
    test_blender()
    test_ffmpeg()
    test_paths()

    print("\n✓ All tests passed!")
```

**Run test:**

Windows:
```cmd
python test_cross_platform.py
```

Linux:
```bash
python3 test_cross_platform.py
```

---

## Part 6: Switching Between Environments

### Scenario 1: Developing on Windows, Deploying to Linux

**On Windows:**

1. Develop normally with Windows paths in `config.yaml`
2. Use `pathlib` and relative paths in code
3. Test locally: `python main.py`
4. Commit and push to GitHub

**On Linux (e.g., claude.ai/code):**

1. Clone repository
2. Create `config.linux.yaml` with Linux paths:
   ```yaml
   blender:
     executable_path: /snap/bin/blender
   ```
3. Run: `python main.py --config config.linux.yaml`
4. Or set environment variable: `export FORAGECAST_CONFIG=config.linux.yaml`

### Scenario 2: Collaborating with Linux Developers

**Best Practice: Use PATH-based detection**

Edit `config.yaml`:
```yaml
blender:
  executable_path: null  # Auto-detect from PATH
ffmpeg:
  executable_path: null  # Auto-detect from PATH
```

Ensure Blender and FFmpeg are in PATH on both systems:
- Windows: Add to System PATH via Environment Variables
- Linux: Snap installations automatically add to PATH

### Scenario 3: CI/CD Pipeline

**GitHub Actions example: `.github/workflows/test.yml`**

```yaml
name: Cross-Platform Tests

on: [push, pull_request]

jobs:
  test-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Install Blender
        run: |
          choco install blender --version=4.0.2
      - name: Install FFmpeg
        run: |
          choco install ffmpeg
      - name: Run tests
        run: python test_cross_platform.py

  test-linux:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          sudo apt update
          sudo apt install -y ffmpeg libsndfile1 build-essential
          pip install -r requirements.txt
      - name: Install Blender
        run: |
          sudo snap install blender --channel=4.0 --classic
          sudo apt install -y libsm6 libxrender1
      - name: Run tests
        run: python test_cross_platform.py
```

---

## Part 7: Common Issues and Solutions

### Issue 1: Different Python Versions

**Problem:** Windows has Python 3.13, Linux has Python 3.11

**Solution:** Use version-agnostic code

```python
# Avoid version-specific features
# Instead of (Python 3.10+ only):
match value:
    case "foo": return 1
    case "bar": return 2

# Use (Python 3.8+):
value_map = {"foo": 1, "bar": 2}
return value_map.get(value, 0)
```

### Issue 2: Unicode Characters in Windows Console

**Problem:** Windows console can't display Unicode checkmarks (✓)

**Solution:** Conditional output

```python
import sys

if sys.platform == "win32":
    CHECK = "[OK]"
    CROSS = "[FAIL]"
else:
    CHECK = "✓"
    CROSS = "✗"

print(f"{CHECK} Test passed")
```

### Issue 3: Blender Python Environment

**Problem:** Blender has its own Python, can't find installed packages

**Solution:** Use `--python-use-system-env` flag

```python
# In blender_script.py or when calling Blender
blender_cmd = [
    blender_path,
    '--background',
    '--python-use-system-env',  # Use system Python packages
    '--python', 'blender_script.py'
]
```

### Issue 4: File Permission Issues

**Problem:** Linux requires executable permissions for scripts

**Solution:** Set permissions in Git

```bash
# Make script executable
chmod +x main.py setup.sh

# Commit with execute permission
git add main.py
git commit -m "Add execute permission"
```

Add to `.gitattributes`:
```
*.sh text eol=lf
*.py text eol=lf
```

### Issue 5: Missing System Libraries (Linux)

**Problem:** Blender or libraries won't run due to missing dependencies

**Solution:** Install common dependencies

```bash
sudo apt install -y \
    libsm6 libxrender1 libxrandr2 libxi6 libgl1 \
    libsndfile1 libsndfile1-dev portaudio19-dev \
    libgomp1 libglu1-mesa
```

---

## Summary

### Windows 11 (Primary Development)

**Strengths:**
- ✅ Familiar GUI tools
- ✅ VS Code, Git for Windows work great
- ✅ Blender GUI available for manual testing
- ✅ No overhead

**Setup:**
1. Install Python 3.11+ (python.org)
2. Install Blender 4.0+ (blender.org)
3. Install FFmpeg (portable or PATH)
4. Use `python` and `pip` commands
5. Activate venv: `venv\Scripts\activate`

### Linux (Secondary/Cloud)

**Strengths:**
- ✅ Matches claude.ai/code containers
- ✅ Better package management (apt, snap)
- ✅ Native deployment environment

**Setup:**
1. Install Python 3.11+ (apt)
2. Install Blender 4.0+ (snap)
3. Install FFmpeg (apt)
4. Use `python3` and `pip3` commands
5. Activate venv: `source venv/bin/activate`

### Key Principles for Cross-Platform Code

1. **Always use `pathlib.Path`** for file paths
2. **Use forward slashes `/`** in string paths (works on both)
3. **Set `executable_path: null`** in config to auto-detect from PATH
4. **Test on both platforms** before major releases
5. **Use `.gitattributes`** to normalize line endings
6. **Avoid platform-specific features** when possible
7. **Document platform differences** in comments

---

**Last Updated:** November 12, 2025
**Primary Platform:** Windows 11
**Secondary Platform:** Linux (Ubuntu 22.04/24.04)
**Project:** Semantic Foragecast Engine v4.0
