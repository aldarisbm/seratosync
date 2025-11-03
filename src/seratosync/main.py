from dotenv import load_dotenv
from seratosync.metadata_sync import SeratoMetadataSync

load_dotenv()


def main():
    """Run Serato metadata sync after rsync."""
    try:
        sync = SeratoMetadataSync()
        sync.sync_all()
    except Exception as e:
        print(f"\nError: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

