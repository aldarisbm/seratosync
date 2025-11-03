import os
import shutil
from pathlib import Path
from dotenv import load_dotenv
from serato_tools.database_v2 import DatabaseV2
from serato_tools.crate import Crate
from serato_tools.smart_crate import SmartCrate

load_dotenv()


class SeratoMetadataSync:
    """
    Syncs Serato metadata to work with rsync-copied music files.
    Preserves folder structure and updates paths to be relative.
    """

    def __init__(self, crate_prefix=""):
        self.source_music = os.getenv('source_music', '/Users/berrio/Music')
        self.target_drive = os.getenv('target', '/Volumes/sandisk')
        self.crate_prefix = os.getenv('crate_prefix', crate_prefix)

        self.source_serato = Path(self.source_music) / "_Serato_"
        self.target_serato = Path(self.target_drive) / "Music" / "_Serato_"
        self.target_music = Path(self.target_drive) / "Music"

    def validate_paths(self):
        """Validate that paths exist."""
        if not self.source_serato.exists():
            raise FileNotFoundError(f"Source Serato directory does not exist: {self.source_serato}")

        if not self.target_music.exists():
            raise FileNotFoundError(
                f"Target Music directory does not exist: {self.target_music}\n"
                f"Make sure you've run rsync first to copy your music files."
            )

        print(f"✓ Source Serato: {self.source_serato}")
        print(f"✓ Target Drive: {self.target_drive}")
        print(f"✓ Target Music: {self.target_music}")

    def remap_path(self, original_path: str) -> str:
        """
        Remap a path from the source to the target, making it relative to the drive.

        Example:
        /Users/berrio/Music/DJ Music/track.mp3
        -> /Music/DJ Music/track.mp3 (relative to drive root)
        """
        original_path = os.path.normpath(original_path)

        # Remove the source music base path
        if original_path.startswith(self.source_music):
            relative_part = original_path[len(self.source_music):]
            # Make it relative to the drive root
            new_path = "/Music" + relative_part
            return new_path

        # If path doesn't start with source, keep it as is
        return original_path

    def sync_crates(self):
        """Copy and update crate files."""
        source_crates_dir = self.source_serato / "Subcrates"
        target_crates_dir = self.target_serato / "Subcrates"

        if not source_crates_dir.exists():
            print("No Subcrates directory found")
            return 0

        target_crates_dir.mkdir(parents=True, exist_ok=True)

        crate_files = list(source_crates_dir.glob("*.crate"))
        print(f"\nProcessing {len(crate_files)} crate(s)...")

        for crate_file in crate_files:
            try:
                crate = Crate(str(crate_file))

                def modify_track(track: Crate.Track) -> Crate.Track:
                    new_path = self.remap_path(track.relpath)
                    track.set_path(new_path)
                    return track

                crate.modify_tracks(modify_track)

                # Save to target with optional prefix
                new_name = f"{self.crate_prefix}{crate_file.name}" if self.crate_prefix else crate_file.name
                target_file = target_crates_dir / new_name
                crate.save(str(target_file))
                if self.crate_prefix:
                    print(f"  ✓ {crate_file.name} -> {new_name}")
                else:
                    print(f"  ✓ {crate_file.name}")

            except Exception as e:
                print(f"  ✗ {crate_file.name}: {e}")

        return len(crate_files)

    def sync_smart_crates(self):
        """Copy and update smart crate files."""
        source_smart_dir = self.source_serato / "SmartCrates"
        target_smart_dir = self.target_serato / "SmartCrates"

        if not source_smart_dir.exists():
            print("No SmartCrates directory found")
            return 0

        target_smart_dir.mkdir(parents=True, exist_ok=True)

        smart_crate_files = list(source_smart_dir.glob("*.scrate"))

        if smart_crate_files:
            print(f"\nProcessing {len(smart_crate_files)} smart crate(s)...")

        for scrate_file in smart_crate_files:
            try:
                scrate = SmartCrate(str(scrate_file))

                def modify_track(track: SmartCrate.Track) -> SmartCrate.Track:
                    new_path = self.remap_path(track.relpath)
                    track.set_path(new_path)
                    return track

                scrate.modify_tracks(modify_track)

                # Save as smart crate with updated paths and optional prefix
                new_name = f"{self.crate_prefix}{scrate_file.name}" if self.crate_prefix else scrate_file.name
                target_file = target_smart_dir / new_name
                scrate.save(str(target_file))
                if self.crate_prefix:
                    print(f"  ✓ {scrate_file.name} -> {new_name}")
                else:
                    print(f"  ✓ {scrate_file.name}")

            except Exception as e:
                print(f"  ✗ {scrate_file.name}: {e}")

        return len(smart_crate_files)

    def sync_database(self):
        """Copy and update the main Serato database."""
        source_db = self.source_serato / "database V2"
        target_db = self.target_serato / "database V2"

        if not source_db.exists():
            print("No database V2 file found")
            return

        print("\nProcessing database...")

        try:
            db = DatabaseV2(str(source_db))

            def modify_track(track: DatabaseV2.Track) -> DatabaseV2.Track:
                new_path = self.remap_path(track.relpath)
                track.set_path(new_path)
                # Reset played status for fresh start on USB
                track.set_value(DatabaseV2.Fields.PLAYED, False)
                return track

            db.modify_tracks(modify_track)

            # Save to target
            self.target_serato.mkdir(parents=True, exist_ok=True)
            db.save(str(target_db))
            print(f"  ✓ database V2")

        except Exception as e:
            print(f"  ✗ database V2: {e}")

    def sync_other_files(self):
        """Copy other Serato preference and configuration files."""
        print("\nCopying other Serato files...")

        files_to_copy = [
            "neworder.pref",
            "window.pref",
            "collapsed.pref",
        ]

        copied = 0
        for filename in files_to_copy:
            source_file = self.source_serato / filename
            if source_file.exists():
                target_file = self.target_serato / filename
                shutil.copy2(source_file, target_file)
                print(f"  ✓ {filename}")
                copied += 1

        return copied

    def sync_all(self):
        """Perform a complete metadata sync."""
        print("=" * 60)
        print("Serato Metadata Sync")
        print("=" * 60)

        self.validate_paths()

        # Remove existing Serato folder on target to start fresh
        if self.target_serato.exists():
            print(f"\nRemoving existing Serato metadata at {self.target_serato}...")
            shutil.rmtree(self.target_serato)

        # Sync all components
        crate_count = self.sync_crates()
        smart_count = self.sync_smart_crates()
        self.sync_database()
        other_count = self.sync_other_files()

        print("\n" + "=" * 60)
        print("✓ Metadata sync complete!")
        print(f"  • {crate_count} crates synced")
        print(f"  • {smart_count} smart crates synced")
        print(f"  • {other_count} preference files synced")
        print(f"  • Database updated")
        print("\n✓ Your USB drive is now ready to use with Serato!")
        print("=" * 60)


def main():
    """Run metadata sync after rsync."""
    try:
        sync = SeratoMetadataSync()
        sync.sync_all()
    except Exception as e:
        print(f"\nError: {e}")
        return 1
    return 0


if __name__ == "__main__":
    exit(main())
