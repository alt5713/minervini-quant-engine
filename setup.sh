#!/bin/bash

# Antigravity Minervini Quant Engine Unified Setup Script
# Works on Mac and Linux

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================================================${NC}"
echo -e "${GREEN}🚀 Antigravity Minervini Quant Engine - One-Click Automated Setup${NC}"
echo -e "${BLUE}======================================================================${NC}"

# 0. Repository Auto-Clone Check (for raw curl installations)
if [ ! -f "02_Source_Code/scan_us_market.py" ]; then
    echo -e "${YELLOW} ⚠️  Codebase not found in current directory.${NC}"
    echo -e " > Cloning minervini-quant-engine repository automatically from GitHub..."
    if ! command -v git &> /dev/null
    then
        echo -e "${RED}❌ Git could not be found. Please install Git and try again.${NC}"
        exit 1
    fi
    git clone https://github.com/alt5713/minervini-quant-engine.git
    if [ $? -eq 0 ]; then
        cd minervini-quant-engine
        echo -e "${GREEN} ✔ Successfully cloned repository and entered the folder.${NC}"
    else
        echo -e "${RED}❌ Failed to clone repository. Please check your internet connection.${NC}"
        exit 1
    fi
fi

# 1. Check Python 3
echo -e " > Checking Python 3 installation..."
if ! command -v python3 &> /dev/null
then
    echo -e "${RED}❌ Python 3 could not be found. Please install Python 3 and try again.${NC}"
    exit 1
fi
python3_ver=$(python3 --version)
echo -e "${GREEN} ✔ Found $python3_ver${NC}"

# 2. Check pip
echo -e " > Checking pip3 installation..."
if ! command -v pip3 &> /dev/null
then
    echo -e "${YELLOW} ⚠️ pip3 not found. Trying 'python3 -m pip'...${NC}"
    PIP_CMD="python3 -m pip"
else
    echo -e "${GREEN} ✔ Found pip3${NC}"
    PIP_CMD="pip3"
fi

# 3. Install Dependencies
echo -e " > Installing python packages from requirements.txt..."
$PIP_CMD install -r requirements.txt
if [ $? -eq 0 ]; then
    echo -e "${GREEN} ✔ Successfully installed all dependencies!${NC}"
else
    echo -e "${RED}❌ Failed to install dependencies. Please check your internet connection or python permissions.${NC}"
    exit 1
fi

# 4. Create necessary folders
echo -e " > Creating output directories..."
mkdir -p rrg_charts
mkdir -p options_charts
echo -e "${GREEN} ✔ Folders './rrg_charts' and './options_charts' are ready.${NC}"

echo -e "${BLUE}======================================================================${NC}"
echo -e "${GREEN}🎉 SETUP COMPLETED SUCCESSFULLY!${NC}"
echo -e "${BLUE}======================================================================${NC}"

# 5. Ask to run the first scan
read -p "❓ Do you want to run your first Big 7 US Market Scan right now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo -e "🚀 Starting the market scan..."
    python3 02_Source_Code/scan_us_market.py
fi

echo -e "\n${GREEN}👍 All done! Enjoy your trading analysis!${NC}"
