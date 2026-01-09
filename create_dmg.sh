#!/bin/bash
# Create DMG installer for MacDesktopWidget
# Usage: ./create_dmg.sh

set -e  # Exit on error

echo "======================================"
echo "MacDesktopWidget DMG Creator"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="MacDesktopWidget"
VERSION="1.0.0"
DMG_NAME="${APP_NAME}-${VERSION}.dmg"
VOLUME_NAME="${APP_NAME} ${VERSION}"
APP_PATH="dist/${APP_NAME}.app"
DMG_DIR="dist/dmg"
FINAL_DMG="dist/${DMG_NAME}"

# Check if app exists
if [ ! -d "$APP_PATH" ]; then
    echo -e "${RED}Error: ${APP_PATH} not found${NC}"
    echo "Run ./build.sh first to build the app"
    exit 1
fi

echo -e "${GREEN}Creating DMG installer...${NC}"

# Clean previous DMG builds
rm -rf "$DMG_DIR"
rm -f "$FINAL_DMG"
rm -f "dist/${APP_NAME}-temp.dmg"

# Create DMG staging directory
mkdir -p "$DMG_DIR"

# Copy app to staging directory
echo "Copying ${APP_NAME}.app to staging directory..."
cp -R "$APP_PATH" "$DMG_DIR/"

# Create Applications symlink for easy installation
echo "Creating Applications symlink..."
ln -s /Applications "$DMG_DIR/Applications"

# Create .DS_Store for nice DMG layout (optional)
# This would require a pre-configured .DS_Store file
# For now, we'll create a simple DMG

# Calculate required DMG size
APP_SIZE=$(du -sm "$APP_PATH" | awk '{print $1}')
DMG_SIZE=$((APP_SIZE + 50))  # Add 50MB buffer

echo "App size: ${APP_SIZE}MB"
echo "DMG size: ${DMG_SIZE}MB"

# Create temporary DMG
echo ""
echo "Creating temporary DMG..."
hdiutil create \
    -volname "$VOLUME_NAME" \
    -srcfolder "$DMG_DIR" \
    -ov \
    -format UDRW \
    -size ${DMG_SIZE}m \
    "dist/${APP_NAME}-temp.dmg"

# Mount the temporary DMG
echo "Mounting DMG..."
MOUNT_DIR=$(hdiutil attach -readwrite -noverify -noautoopen "dist/${APP_NAME}-temp.dmg" | grep Volumes | awk '{print $3}')

if [ -z "$MOUNT_DIR" ]; then
    echo -e "${RED}Error: Failed to mount DMG${NC}"
    exit 1
fi

echo "Mounted at: $MOUNT_DIR"

# Set DMG background and icon positions (optional)
# This requires additional tools like create-dmg or manual setup
# For now, we'll create a basic DMG

# Set custom DMG icon (optional)
if [ -f "resources/dmg-icon.icns" ]; then
    echo "Setting custom DMG icon..."
    cp resources/dmg-icon.icns "$MOUNT_DIR/.VolumeIcon.icns"
    SetFile -c icnC "$MOUNT_DIR/.VolumeIcon.icns"
    SetFile -a C "$MOUNT_DIR"
fi

# Wait a moment for filesystem to settle
sleep 2

# Unmount the temporary DMG
echo "Unmounting temporary DMG..."
hdiutil detach "$MOUNT_DIR"

# Convert to compressed read-only DMG
echo ""
echo "Compressing final DMG..."
hdiutil convert \
    "dist/${APP_NAME}-temp.dmg" \
    -format UDZO \
    -imagekey zlib-level=9 \
    -o "$FINAL_DMG"

# Clean up temporary files
rm -f "dist/${APP_NAME}-temp.dmg"
rm -rf "$DMG_DIR"

# Verify final DMG
if [ -f "$FINAL_DMG" ]; then
    DMG_FINAL_SIZE=$(du -sh "$FINAL_DMG" | awk '{print $1}')
    echo ""
    echo -e "${GREEN}✓ DMG created successfully!${NC}"
    echo ""
    echo "DMG location: $FINAL_DMG"
    echo "DMG size: $DMG_FINAL_SIZE"
    echo ""
    echo -e "${GREEN}Next steps:${NC}"
    echo "1. Test the DMG: open $FINAL_DMG"
    echo "2. (Optional) Notarize for distribution: xcrun notarytool submit $FINAL_DMG"
    echo "3. Distribute to users"
else
    echo -e "${RED}✗ DMG creation failed!${NC}"
    exit 1
fi

echo ""
echo "======================================"
echo "DMG Creation Complete"
echo "======================================"
