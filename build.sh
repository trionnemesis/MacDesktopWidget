#!/bin/bash
# Build script for MacDesktopWidget using py2app
# Usage: ./build.sh

set -e  # Exit on error

echo "======================================"
echo "MacDesktopWidget Build Script"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}Error: This script must run on macOS${NC}"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}Python version: $PYTHON_VERSION${NC}"

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${YELLOW}Warning: Virtual environment not activated${NC}"
    echo "Activating venv..."
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        echo -e "${RED}Error: venv not found. Run: python3 -m venv venv${NC}"
        exit 1
    fi
fi

# Install/update py2app
echo ""
echo -e "${GREEN}Installing py2app...${NC}"
pip install --upgrade py2app setuptools wheel

# Clean previous builds
echo ""
echo -e "${GREEN}Cleaning previous builds...${NC}"
rm -rf build dist

# Create resources directory if it doesn't exist
mkdir -p resources

# Generate a simple icon if it doesn't exist (optional)
# Users can replace resources/icon.icns with their own icon
if [ ! -f "resources/icon.icns" ]; then
    echo -e "${YELLOW}Note: resources/icon.icns not found. App will use default icon.${NC}"
    echo "To add custom icon: Place your .icns file at resources/icon.icns"
fi

# Build the app
echo ""
echo -e "${GREEN}Building MacDesktopWidget.app...${NC}"
python3 setup.py py2app

# Verify build
if [ -d "dist/MacDesktopWidget.app" ]; then
    echo ""
    echo -e "${GREEN}✓ Build successful!${NC}"
    echo ""
    echo "App location: dist/MacDesktopWidget.app"

    # Get app size
    APP_SIZE=$(du -sh dist/MacDesktopWidget.app | awk '{print $1}')
    echo "App size: $APP_SIZE"

    # Test if app is signed (optional)
    echo ""
    echo "Checking code signature..."
    codesign -dvvv dist/MacDesktopWidget.app 2>&1 | grep -E "Signature|Identifier" || echo "App is not signed"

    echo ""
    echo -e "${GREEN}Next steps:${NC}"
    echo "1. Test the app: open dist/MacDesktopWidget.app"
    echo "2. Create DMG: ./create_dmg.sh"
    echo "3. (Optional) Sign the app: codesign --deep --force --sign 'Your Identity' dist/MacDesktopWidget.app"
else
    echo -e "${RED}✗ Build failed!${NC}"
    echo "Check the error messages above."
    exit 1
fi

echo ""
echo "======================================"
echo "Build Complete"
echo "======================================"
