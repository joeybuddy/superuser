#!/bin/bash

################################################################################
# Script: edge-storage-usage.sh
# Description: Calculate Microsoft Edge browser storage usage on macOS
# Usage: ./edge-storage-usage.sh [username1] [username2] ...
#        If no usernames provided, defaults to current user
################################################################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to format bytes to human-readable format
format_bytes() {
    local bytes=$1
    if [ "$bytes" -lt 1024 ]; then
        echo "${bytes}B"
    elif [ "$bytes" -lt 1048576 ]; then
        echo "$(awk "BEGIN {printf \"%.2f\", $bytes/1024}")KB"
    elif [ "$bytes" -lt 1073741824 ]; then
        echo "$(awk "BEGIN {printf \"%.2f\", $bytes/1048576}")MB"
    else
        echo "$(awk "BEGIN {printf \"%.2f\", $bytes/1073741824}")GB"
    fi
}

# Function to calculate directory size in bytes
get_dir_size() {
    local dir=$1
    if [ -d "$dir" ]; then
        # Use find and awk to sum up file sizes
        find "$dir" -type f -exec stat -f%z {} \; 2>/dev/null | awk '{sum+=$1} END {print sum+0}'
    else
        echo "0"
    fi
}

# Function to calculate Edge storage for a specific user
calculate_edge_storage() {
    local username=$1
    local home_dir
    
    # Determine home directory
    if [ "$username" = "$(whoami)" ]; then
        home_dir="$HOME"
    else
        # Try to get home directory from /Users
        home_dir="/Users/$username"
        if [ ! -d "$home_dir" ]; then
            # Try dscl command to get home directory
            home_dir=$(dscl . -read "/Users/$username" NFSHomeDirectory 2>/dev/null | awk '{print $2}')
            if [ -z "$home_dir" ] || [ ! -d "$home_dir" ]; then
                echo -e "${RED}✗ User '$username' not found or home directory doesn't exist${NC}"
                return 1
            fi
        fi
    fi
    
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}User: ${username}${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # Define Edge-related directories
    declare -A edge_dirs=(
        ["Application Support"]="$home_dir/Library/Application Support/Microsoft Edge"
        ["Caches"]="$home_dir/Library/Caches/Microsoft Edge"
        ["Cookies"]="$home_dir/Library/Cookies/com.microsoft.edgemac.binarycookies"
        ["HTTPStorages"]="$home_dir/Library/HTTPStorages/com.microsoft.edgemac"
        ["Preferences"]="$home_dir/Library/Preferences/com.microsoft.edgemac.plist"
        ["Saved Application State"]="$home_dir/Library/Saved Application State/com.microsoft.edgemac.savedState"
        ["WebKit"]="$home_dir/Library/WebKit/com.microsoft.edgemac"
    )
    
    local total_size=0
    local found_any=false
    
    # Calculate size for each directory
    for label in "${!edge_dirs[@]}"; do
        local path="${edge_dirs[$label]}"
        local size=0
        
        if [ -e "$path" ]; then
            found_any=true
            if [ -d "$path" ]; then
                size=$(get_dir_size "$path")
            elif [ -f "$path" ]; then
                size=$(stat -f%z "$path" 2>/dev/null || echo "0")
            fi
            
            if [ "$size" -gt 0 ]; then
                total_size=$((total_size + size))
                printf "  %-30s %15s\n" "$label:" "$(format_bytes "$size")"
            fi
        fi
    done
    
    if [ "$found_any" = false ]; then
        echo -e "  ${YELLOW}⚠ No Microsoft Edge data found for user '$username'${NC}"
        return 0
    fi
    
    echo -e "${BLUE}──────────────────────────────────────────────────────────────${NC}"
    printf "  ${GREEN}%-30s %15s${NC}\n" "TOTAL:" "$(format_bytes "$total_size")"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    return 0
}

# Main script
main() {
    # Check if running on macOS
    if [[ "$OSTYPE" != "darwin"* ]]; then
        echo -e "${RED}Error: This script is designed for macOS only${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║     Microsoft Edge Storage Usage Calculator for macOS     ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    
    # If no arguments provided, use current user
    if [ $# -eq 0 ]; then
        calculate_edge_storage "$(whoami)"
    else
        # Process each username provided
        for username in "$@"; do
            calculate_edge_storage "$username"
        done
    fi
    
    echo ""
}

# Run main function
main "$@"
