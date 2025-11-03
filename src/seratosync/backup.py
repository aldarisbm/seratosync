import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from serato_tools.usb_export import copy_crates_to_usb, get_crate_files

load_dotenv()


class SeratoBackup:
    def __init__(self):
        self.source = os.getenv('source')
        self.target = os.getenv('target')

        if not self.source:
            raise ValueError("Environment variable 'source' is not set")
        if not self.target:
            raise ValueError("Environment variable 'target' is not set")

        self.source_path = Path(self.source)
        self.target_path = Path(self.target)

    def validate_paths(self):
        """Validate that source and target paths exist and are accessible."""
        if not self.source_path.exists():
            raise FileNotFoundError(f"Source directory does not exist: {self.source_path}")

        if not self.target_path.exists():
            raise FileNotFoundError(f"Target directory does not exist: {self.target_path}")

        if not os.access(self.target_path, os.W_OK):
            raise PermissionError(f"Target directory is not writable: {self.target_path}")

        print(f"✓ Source: {self.source_path}")
        print(f"✓ Target: {self.target_path}")

    def create_backup(self, tracks_subfolder="Serato Music", backup_all_crates=True):
        """
        Create a backup of the Serato library using serato_tools to preserve metadata.

        Args:
            tracks_subfolder: Subfolder name on the USB drive where tracks will be stored.
                            Default is "Serato Music".
            backup_all_crates: If True, backs up all crates. If False, backs up only
                             crates matching a specific pattern.
        """
        self.validate_paths()

        print(f"\nStarting Serato backup with metadata preservation...")
        print(f"Source library: {self.source_path}")
        print(f"Target drive: {self.target_path}")
        print(f"Music folder: {tracks_subfolder}")

        try:
            # Get all crate files - get_crate_files() uses regex pattern on filenames
            # Use ".*\.crate$" to match all .crate files
            if backup_all_crates:
                crate_pattern = r".*\.crate$"  # Regex to match all .crate files
            else:
                crate_pattern = r".*\.crate$"  # Can be customized

            print(f"\nSearching for crates with pattern: {crate_pattern}")
            crate_files = get_crate_files(crate_pattern)

            if not crate_files:
                print("Warning: No crate files found.")
                print("This might mean:")
                print("  - Your Serato library has no crates")
                print("  - The source path is incorrect")
                print(f"  - Expected crates in: {self.source_path / 'Subcrates'}")

                # List what's actually there
                subcrates_dir = self.source_path / "Subcrates"
                if subcrates_dir.exists():
                    actual_crates = list(subcrates_dir.glob("*.crate"))
                    if actual_crates:
                        print(f"\nFound {len(actual_crates)} crate files manually:")
                        for crate in actual_crates[:10]:
                            print(f"  • {crate.name}")
                        # Use these instead
                        crate_files = [str(c) for c in actual_crates]
                        print(f"\nUsing {len(crate_files)} crates found manually")
            else:
                print(f"Found {len(crate_files)} crate(s)")
                for crate in crate_files[:10]:
                    print(f"  • {Path(crate).name}")
                if len(crate_files) > 10:
                    print(f"  ... and {len(crate_files) - 10} more")

            # Create the music directory on the target drive
            dest_tracks_dir = str(self.target_path / tracks_subfolder)
            os.makedirs(dest_tracks_dir, exist_ok=True)

            # Use serato_tools to copy crates to USB with proper metadata
            print(f"\nCopying library with Serato metadata...")
            if crate_files:
                copy_crates_to_usb(
                    crate_files=crate_files,
                    dest_drive_dir=str(self.target_path),
                    dest_tracks_dir=dest_tracks_dir
                )
            else:
                print("No crates to copy. Backup incomplete.")
                return None

            # Calculate backup size
            total_size = sum(
                f.stat().st_size
                for f in self.target_path.rglob('*')
                if f.is_file()
            )
            size_mb = total_size / (1024 * 1024)
            size_gb = size_mb / 1024

            print(f"\n✓ Backup completed successfully!")
            print(f"✓ Drive: {self.target_path}")
            print(f"✓ Music folder: {tracks_subfolder}")
            print(f"✓ Total size: {size_gb:.2f} GB ({size_mb:.2f} MB)")
            print(f"\n✓ Your Serato library is now backed up and playable from the USB drive!")

            return self.target_path

        except Exception as e:
            print(f"\n✗ Backup failed: {str(e)}")
            raise

    def get_backup_info(self):
        """Get information about the backup on the target drive."""
        serato_dir = self.target_path / "_Serato_"

        if not serato_dir.exists():
            print(f"No Serato backup found at {self.target_path}")
            return None

        print(f"\nBackup information:")
        print(f"Location: {self.target_path}")

        # Check for Serato directory
        if serato_dir.exists():
            print(f"✓ Serato metadata folder exists")

            # List crates
            subcrates_dir = serato_dir / "Subcrates"
            if subcrates_dir.exists():
                crates = list(subcrates_dir.glob("*.crate"))
                print(f"✓ Found {len(crates)} crate(s)")
                for crate in crates[:10]:  # Show first 10
                    print(f"  • {crate.stem}")
                if len(crates) > 10:
                    print(f"  ... and {len(crates) - 10} more")

        # Check for music files
        music_folders = [
            "Serato Music",
            "Music",
            "DJ Music"
        ]

        for folder in music_folders:
            music_dir = self.target_path / folder
            if music_dir.exists():
                music_files = list(music_dir.rglob("*.mp3")) + \
                             list(music_dir.rglob("*.m4a")) + \
                             list(music_dir.rglob("*.flac")) + \
                             list(music_dir.rglob("*.wav"))
                if music_files:
                    print(f"✓ Found {len(music_files)} track(s) in '{folder}'")
                    break

        return True


def main():
    """Run a backup with Serato metadata preservation."""
    try:
        backup = SeratoBackup()
        backup.create_backup()
    except Exception as e:
        print(f"Error: {e}")
        return 1
    return 0


if __name__ == "__main__":
    exit(main())
