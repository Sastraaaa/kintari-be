import sys
import subprocess
import os
from pathlib import Path


def main():
    """Entry point untuk command kintari"""

    if len(sys.argv) < 2:
        print_help()
        return

    command = sys.argv[1]

    if command == "dev":
        start_dev_server()
    elif command == "start":
        start_server()
    elif command == "help":
        print_help()
    else:
        print(f"❌ Command '{command}' tidak dikenal")
        print_help()


def start_dev_server():
    """Start server dengan reload mode"""
    print("\n" + "=" * 50)
    print("  🚀 KINTARI BACKEND - DEV MODE")
    print("=" * 50)
    print("📍 http://127.0.0.1:8000")
    print("📚 Docs: http://127.0.0.1:8000/docs")
    print("📖 ReDoc: http://127.0.0.1:8000/redoc")
    print("=" * 50 + "\n")

    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
        "--reload",
    ]

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\n✋ Server dihentikan")
    except Exception as e:
        print(f"❌ Error: {e}")


def start_server():
    """Start server tanpa reload mode (production)"""
    print("\n" + "=" * 50)
    print("  🚀 KINTARI BACKEND - PRODUCTION MODE")
    print("=" * 50)
    print("📍 http://127.0.0.1:8000")
    print("📚 Docs: http://127.0.0.1:8000/docs")
    print("=" * 50 + "\n")

    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
    ]

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\n✋ Server dihentikan")
    except Exception as e:
        print(f"❌ Error: {e}")


def print_help():
    """Tampilkan help message"""
    print("\n" + "=" * 50)
    print("  📖 KINTARI BACKEND CLI")
    print("=" * 50)
    print("\nGunakan: kintari <command>")
    print("\nCommands:")
    print("  dev    - Start server dengan reload mode (development)")
    print("  start  - Start server tanpa reload (production)")
    print("  help   - Tampilkan help ini")
    print("\nContoh:")
    print("  kintari dev")
    print("  kintari start")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
