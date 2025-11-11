#!/bin/bash
# Raspberry Pi Setup Script
# Run this script on your Raspberry Pi to set up the connection to Neon

set -e  # Exit on error

echo "=========================================="
echo "Smart Plant Assistant - Raspberry Pi Setup"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ] || ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Warning: This doesn't appear to be a Raspberry Pi${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 1: Install dependencies
echo -e "${GREEN}[1/5] Installing Python dependencies...${NC}"
pip3 install --user psycopg2-binary python-dotenv || {
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    echo "Try: sudo apt update && sudo apt install python3-pip -y"
    exit 1
}
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Step 2: Create directory structure
echo -e "${GREEN}[2/5] Setting up directory structure...${NC}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="$HOME/smart_plant_pi"
mkdir -p "$WORK_DIR"
echo -e "${GREEN}✅ Directory created: $WORK_DIR${NC}"
echo ""

# Step 3: Copy files
echo -e "${GREEN}[3/5] Copying files...${NC}"
if [ -f "$SCRIPT_DIR/send_sensor_data.py" ]; then
    cp "$SCRIPT_DIR/send_sensor_data.py" "$WORK_DIR/"
    cp "$SCRIPT_DIR/test_connection.py" "$WORK_DIR/" 2>/dev/null || echo "test_connection.py not found, will create"
    echo -e "${GREEN}✅ Files copied${NC}"
else
    echo -e "${YELLOW}⚠️  Files not found in script directory${NC}"
    echo "Make sure you're running this from the raspberry_pi directory"
fi
echo ""

# Step 4: Create .env file
echo -e "${GREEN}[4/5] Setting up environment variables...${NC}"
ENV_FILE="$WORK_DIR/.env"

if [ -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}⚠️  .env file already exists${NC}"
    read -p "Overwrite? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing .env file"
    else
        rm "$ENV_FILE"
    fi
fi

if [ ! -f "$ENV_FILE" ]; then
    echo "Creating .env file..."
    cat > "$ENV_FILE" << 'EOF'
# Neon Database Connection String
# Replace with your actual connection string from your Mac's .env file
DATABASE_URL=postgresql://username:password@ep-xxxxx.us-east-2.aws.neon.tech/neondb?sslmode=require

# Your Plant ID (get this from your Flask app after creating a plant)
PLANT_ID=1
EOF
    echo -e "${GREEN}✅ .env file created at $ENV_FILE${NC}"
    echo -e "${YELLOW}⚠️  Please edit $ENV_FILE and verify DATABASE_URL is correct${NC}"
fi
echo ""

# Step 5: Make scripts executable
echo -e "${GREEN}[5/5] Making scripts executable...${NC}"
chmod +x "$WORK_DIR/send_sensor_data.py" 2>/dev/null || true
chmod +x "$WORK_DIR/test_connection.py" 2>/dev/null || true
echo -e "${GREEN}✅ Scripts are executable${NC}"
echo ""

# Summary
echo "=========================================="
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file: nano $WORK_DIR/.env"
echo "2. Verify DATABASE_URL matches your Mac's .env file"
echo "3. Get your Plant ID from your Flask app"
echo "4. Update PLANT_ID in .env file"
echo "5. Test connection: cd $WORK_DIR && python3 test_connection.py"
echo "6. Test sensor data: cd $WORK_DIR && python3 send_sensor_data.py 1"
echo ""
echo "For automated readings, see RASPBERRY_PI_SETUP.md"

