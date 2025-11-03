# SeratoSync

A Python tool for backing up your Serato DJ library to external drives with proper metadata preservation and folder structure intact.

## Features

- **Complete Backup**: Copies your entire music library with folder structure preserved
- **Metadata Preservation**: Updates Serato metadata (crates, playlists, database) to work on USB drives
- **Portable**: USB drives work on any computer running Serato DJ
- **Smart Path Remapping**: Converts absolute paths to relative paths for portability
- **Smart Crate Support**: Automatically converts smart crates to regular crates for USB compatibility
- **Efficient**: Uses rsync for fast, incremental file copying

## How It Works

1. **rsync** copies all your music files to the USB drive, preserving folder structure (excludes `_Serato_` folder)
2. **Python script** copies and updates the Serato metadata:
   - Remaps all file paths from `/Users/you/Music/...` to `/Music/...` (relative to drive)
   - Processes all crates and smart crates
   - Updates the Serato database
   - Copies preference files

## Requirements

- Python 3.12+
- Poetry (for dependency management)
- rsync (comes with macOS)
- Serato DJ library

## Installation

1. Clone or download this repository:
```bash
cd /Users/berrio/Develop/seratosync
```

2. Install dependencies:
```bash
poetry install
```

3. Configure your paths in `.env`:
```bash
cp .env.example .env  # If you don't have .env yet
```

Edit `.env`:
```
source=/Users/your-username/Music/_Serato_
source_music=/Users/your-username/Music
target=/Volumes/your-usb-drive/
```

## Usage

### Option 1: All-in-One Script (Recommended)

Run the complete backup (rsync + metadata sync):

```bash
/Users/berrio/Develop/seratosync/sync_serato.sh
```

### Option 2: Manual Steps

If you prefer to run steps separately:

1. **First, run rsync** to copy music files:
```bash
rsync -ahP --exclude '.DS_Store' --exclude '.tmp.driveupload' --exclude '_Serato_' /Users/berrio/Music /Volumes/sandisk/
```

2. **Then, sync Serato metadata**:
```bash
cd /Users/berrio/Develop/seratosync
poetry run python src/seratosync/main.py
```

### Option 3: Create an Alias

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
alias seratosync='/Users/berrio/Develop/seratosync/sync_serato.sh'
```

Then reload your shell and run:
```bash
seratosync
```

## What Gets Backed Up

### Music Files (via rsync)
- All audio files in your Music folder
- Complete folder structure preserved
- Metadata tags intact

### Serato Metadata (via Python)
- **Crates**: All your crates with updated file paths
- **Smart Crates**: Converted to regular crates (USB compatible)
- **Database**: Main Serato database with remapped paths
- **Preferences**: Crate order, window settings, etc.

### Excluded from Backup
- `.DS_Store` files
- `.tmp.driveupload` files
- Original `_Serato_` folder (recreated with updated paths)

## Project Structure

```
```
seratosync/
├── src/
│   └── seratosync/
│       ├── main.py
│       ├── metadata_sync.py
│       └── backup.py
├── sync_serato.sh
├── .env
├── .gitignore
├── pyproject.toml
└── README.md
```
```

## Configuration

### Environment Variables

Create a `.env` file with:

| Variable | Description | Example |
|----------|-------------|---------|
| `source` | Serato library directory | `/Users/you/Music/_Serato_` |
| `source_music` | Music root directory | `/Users/you/Music` |
| `target` | USB drive mount point | `/Volumes/sandisk/` |
| `crate_prefix` | Optional prefix for crate names on USB | `ext_` (or leave empty for no prefix) |

### Customization

You can customize the metadata sync behavior by editing `src/seratosync/metadata_sync.py`:

- **Path remapping logic**: Modify `remap_path()` method
- **Files to sync**: Add/remove files in `sync_other_files()` method
- **Crate filtering**: Customize which crates to sync

## How Path Remapping Works

The tool converts absolute paths to relative paths:

**Before (on your computer):**
```
Users/berrio/Music/DJ Music/House/track.mp3
```

**After (on USB drive):**
```
Music/DJ Music/House/track.mp3
```

This makes the drive work on any computer, since Serato reads paths relative to the drive root. Note that Serato stores paths without leading slashes in its metadata files.

## Troubleshooting

### "No crate files found"
- Check that `source` in `.env` points to your `_Serato_` directory
- Verify you have crates in `~/Music/_Serato_/Subcrates/`

### "Target directory does not exist"
- Make sure your USB drive is mounted
- Check that the `target` path in `.env` matches your drive's mount point
- Run `ls /Volumes/` to see available drives

### rsync errors
- Check the error file at `/Users/berrio/Desktop/error.txt`
- Ensure you have read permissions on source files
- Verify USB drive has enough space

### Serato doesn't see the USB library
- Make sure the `_Serato_` folder exists on the USB drive
- Check that music files are in `/Volumes/your-drive/Music/`
- Try ejecting and reconnecting the USB drive

## Development

### Running Tests
```bash
poetry run pytest
```

### Adding Dependencies
```bash
poetry add package-name
```

### Code Structure

**`metadata_sync.py`** contains:
- `SeratoMetadataSync`: Main class for metadata operations
- `remap_path()`: Converts absolute paths to relative
- `sync_crates()`: Processes crate files
- `sync_smart_crates()`: Processes and converts smart crates
- `sync_database()`: Updates main Serato database
- `sync_other_files()`: Copies preference files

## Dependencies

- **[serato-tools](https://github.com/Holzhaus/serato-tools)**: Library for reading/writing Serato files
- **python-dotenv**: Environment variable management

## FAQ

**Q: Will this work on Windows?**
A: The rsync script is macOS/Linux specific. You'd need to modify it for Windows (use robocopy instead).

**Q: Can I backup to multiple USB drives?**
A: Yes! Just change the `target` in `.env` or run the script multiple times with different targets.

**Q: Does this backup my track analysis (beatgrids, cue points)?**
A: Yes! All metadata including beatgrids, cue points, loops, and track colors are preserved in the database.

**Q: Can I use this for syncing between computers?**
A: Not directly. This tool is designed for USB drives. For computer-to-computer sync, you'd need different path remapping logic.

**Q: What if I add new tracks after backing up?**
A: Just run the script again. rsync will only copy new/changed files, making it fast for incremental backups.

**Q: Will this delete files from my USB drive?**
A: No, rsync doesn't delete by default. If you want to mirror (delete files not in source), add `--delete` flag to rsync.

## License

MIT License - feel free to use and modify as needed.

## Contributing

This is a personal project, but contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## Credits

Built with:
- [serato-tools](https://github.com/Holzhaus/serato-tools) by Jan Holthuis
- Python 3.12
- Poetry for dependency management

## Support

If you encounter issues:
1. Check the Troubleshooting section above
2. Review the error messages carefully
3. Verify your `.env` configuration
4. Check that all paths exist and are accessible

---

**Happy DJing!** 🎵
