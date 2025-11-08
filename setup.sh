#!/bin/bash
#
# Semantic Foragecast Engine - Automated Installation Script
#
# This script automates the installation of all dependencies required
# to run the Semantic Foragecast Engine on Linux and macOS.
#
# For Windows, please refer to README.md for manual installation steps.
#
# Author: Claude (Anthropic)
# Version: 1.0
# License: MIT
#

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_info() {
    echo -e "${BLUE}ℹ ${NC}$1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_header() {
    echo ""
    echo "========================================================================"
    echo "$1"
    echo "========================================================================"
    echo ""
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        print_info "Detected OS: Linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        print_info "Detected OS: macOS"
    else
        OS="unknown"
        print_error "Unsupported OS: $OSTYPE"
        print_info "For Windows, please refer to README.md for manual installation."
        exit 1
    fi
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python version
check_python() {
    print_header "Checking Python Installation"

    if ! command_exists python3; then
        print_error "Python 3 not found. Please install Python 3.9 or later."
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

    print_info "Found Python $PYTHON_VERSION"

    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
        print_error "Python 3.9 or later is required (found $PYTHON_VERSION)"
        exit 1
    fi

    print_success "Python version OK"
}

# Install Python dependencies
install_python_deps() {
    print_header "Installing Python Dependencies"

    if ! command_exists pip3; then
        print_error "pip3 not found. Please install pip3."
        exit 1
    fi

    print_info "Upgrading pip..."
    python3 -m pip install --upgrade pip

    print_info "Installing requirements..."
    pip3 install -r requirements.txt

    print_success "Python dependencies installed"
}

# Check and install FFmpeg
install_ffmpeg() {
    print_header "Checking FFmpeg Installation"

    if command_exists ffmpeg; then
        FFMPEG_VERSION=$(ffmpeg -version | head -n1)
        print_success "FFmpeg already installed: $FFMPEG_VERSION"
        return 0
    fi

    print_warning "FFmpeg not found. Attempting to install..."

    if [ "$OS" == "linux" ]; then
        if command_exists apt-get; then
            print_info "Installing via apt-get..."
            sudo apt-get update
            sudo apt-get install -y ffmpeg
        elif command_exists yum; then
            print_info "Installing via yum..."
            sudo yum install -y ffmpeg
        elif command_exists dnf; then
            print_info "Installing via dnf..."
            sudo dnf install -y ffmpeg
        elif command_exists pacman; then
            print_info "Installing via pacman..."
            sudo pacman -S --noconfirm ffmpeg
        else
            print_error "Could not detect package manager. Please install FFmpeg manually."
            return 1
        fi
    elif [ "$OS" == "macos" ]; then
        if command_exists brew; then
            print_info "Installing via Homebrew..."
            brew install ffmpeg
        else
            print_error "Homebrew not found. Please install Homebrew first: https://brew.sh"
            return 1
        fi
    fi

    if command_exists ffmpeg; then
        print_success "FFmpeg installed successfully"
    else
        print_error "FFmpeg installation failed"
        return 1
    fi
}

# Check and install Blender (optional)
install_blender() {
    print_header "Checking Blender Installation"

    if command_exists blender; then
        BLENDER_VERSION=$(blender --version | head -n1)
        print_success "Blender already installed: $BLENDER_VERSION"
        return 0
    fi

    print_warning "Blender not found"
    print_info "Blender 3.6+ is required for rendering (optional for testing)"
    print_info ""
    print_info "Installation options:"
    print_info "  1. Download from: https://www.blender.org/download/"
    print_info "  2. Linux (snap): sudo snap install blender --classic"
    print_info "  3. macOS (brew): brew install --cask blender"
    print_info ""

    read -p "Would you like to attempt automatic installation? (y/N): " -r
    echo

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Skipping Blender installation"
        return 0
    fi

    if [ "$OS" == "linux" ]; then
        if command_exists snap; then
            print_info "Installing via snap..."
            sudo snap install blender --classic
        else
            print_error "Snap not available. Please install Blender manually."
            return 1
        fi
    elif [ "$OS" == "macos" ]; then
        if command_exists brew; then
            print_info "Installing via Homebrew..."
            brew install --cask blender
        else
            print_error "Homebrew not found. Please install Blender manually."
            return 1
        fi
    fi

    if command_exists blender; then
        print_success "Blender installed successfully"
    else
        print_warning "Blender installation incomplete (may require PATH update)"
    fi
}

# Check Rhubarb Lip Sync (optional)
check_rhubarb() {
    print_header "Checking Rhubarb Lip Sync (Optional)"

    if command_exists rhubarb; then
        RHUBARB_VERSION=$(rhubarb --version 2>&1 | head -n1 || echo "Unknown version")
        print_success "Rhubarb found: $RHUBARB_VERSION"
        return 0
    fi

    print_warning "Rhubarb Lip Sync not found (optional)"
    print_info "Rhubarb provides accurate lip-sync animation"
    print_info "Without it, the engine will use mock phoneme generation"
    print_info ""
    print_info "To install Rhubarb:"
    print_info "  1. Download from: https://github.com/DanielSWolf/rhubarb-lip-sync/releases"
    print_info "  2. Extract and add to PATH"
    print_info ""
}

# Create sample assets
create_sample_assets() {
    print_header "Creating Sample Assets"

    if [ -d "assets" ] && [ -f "assets/fox.png" ]; then
        print_info "Sample assets already exist"
        return 0
    fi

    print_info "Generating sample assets..."

    python3 tests/generate_assets.py

    if [ -f "assets/fox.png" ]; then
        print_success "Sample assets created in assets/"
    else
        print_warning "Could not create sample assets (non-critical)"
    fi
}

# Run tests
run_tests() {
    print_header "Running Tests"

    print_info "Running unit tests..."

    if python3 -m pytest tests/test_prep_audio.py -v --tb=short; then
        print_success "Unit tests passed"
    else
        print_warning "Some unit tests failed (check output above)"
    fi

    print_info ""
    print_info "Running E2E tests..."

    if python3 tests/test_e2e_pipeline.py; then
        print_success "E2E tests passed"
    else
        print_warning "Some E2E tests failed (may require Blender)"
    fi
}

# Print summary
print_summary() {
    print_header "Installation Summary"

    echo "Python:       $(python3 --version)"

    if command_exists ffmpeg; then
        echo "FFmpeg:       ✓ Installed"
    else
        echo "FFmpeg:       ✗ Not found"
    fi

    if command_exists blender; then
        echo "Blender:      ✓ Installed"
    else
        echo "Blender:      ⚠ Not found (optional)"
    fi

    if command_exists rhubarb; then
        echo "Rhubarb:      ✓ Installed"
    else
        echo "Rhubarb:      ⚠ Not found (optional)"
    fi

    echo ""
    echo "Python packages:"
    pip3 list | grep -E "librosa|numpy|Pillow|PyYAML" || true

    echo ""
    print_header "Next Steps"

    echo "1. Review config.yaml and adjust settings as needed"
    echo ""
    echo "2. Run the pipeline:"
    echo "   $ python3 main.py --config config.yaml"
    echo ""
    echo "3. Generate a demo reel:"
    echo "   $ python3 create_demo_reel.py"
    echo ""
    echo "4. Run tests:"
    echo "   $ pytest tests/ -v"
    echo ""
    echo "5. Read the documentation:"
    echo "   $ cat README.md"
    echo ""

    print_success "Setup complete!"
}

# Main installation flow
main() {
    print_header "Semantic Foragecast Engine - Setup Script"

    echo "This script will install dependencies for the Semantic Foragecast Engine"
    echo ""

    detect_os
    check_python
    install_python_deps
    install_ffmpeg

    # Optional components
    install_blender
    check_rhubarb

    # Setup
    create_sample_assets

    # Offer to run tests
    echo ""
    read -p "Would you like to run tests now? (Y/n): " -r
    echo

    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        run_tests
    else
        print_info "Skipping tests (you can run them later with: pytest tests/)"
    fi

    print_summary
}

# Run main
main
