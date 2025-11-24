# Superuser Tools

A collection of useful scripts and tools for power users.

## Scripts

### edge-storage-usage.py

Calculate Microsoft Edge browser storage usage on macOS.

#### Features

- Calculate total Microsoft Edge storage usage for one or more users
- Breaks down storage by category (Application Support, Caches, Cookies, etc.)
- Colorized, human-readable output
- Supports multiple user accounts

#### Usage

```bash
# Calculate Edge storage for current user
./edge-storage-usage.py

# Calculate Edge storage for specific user(s)
./edge-storage-usage.py username1

# Calculate Edge storage for multiple users
./edge-storage-usage.py username1 username2 username3
```

#### Requirements

- macOS operating system
- Python 3.6 or higher
- Read permissions for the target user directories

#### Output Example

The script provides a detailed breakdown of Microsoft Edge storage including:
- Application Support data
- Cache files
- Cookies
- HTTP Storages
- Preferences
- Saved Application State
- WebKit data

Each category shows its size, and a total is displayed at the end.

## Other Tools

### karabiner-rules

Custom Karabiner-Elements rules for keyboard customization on macOS.
