#!/usr/bin/env python3
"""
Verify Offline Wikipedia MCP Server environment, dependencies, and ZIM archives.

Usage:
    python scripts/verify_setup.py [--zim-dir PATH] [--zim-path PATH]
"""

import os
import sys
import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        description="Verify Offline Wikipedia MCP setup and archives."
    )
    parser.add_argument(
        "--zim-dir",
        default=os.environ.get("WIKI_ZIM_DIR"),
        help="Directory containing .zim archives (or set WIKI_ZIM_DIR env var)",
    )
    parser.add_argument(
        "--zim-path",
        default=os.environ.get("WIKI_ZIM_PATH"),
        help="Path to a single .zim archive (or set WIKI_ZIM_PATH env var)",
    )
    return parser.parse_args()


def main():
    print("=" * 60)
    print(" Offline Wikipedia MCP Setup Verifier")
    print("=" * 60)

    # 1. Python version check
    py_ver = sys.version_info
    print(f"\n[1/4] Python Version: {py_ver.major}.{py_ver.minor}.{py_ver.micro}")
    if py_ver < (3, 10):
        print("  ❌ ERROR: Python 3.10+ is required.")
        return 1
    print("  ✅ Python version is supported.")

    # 2. Dependency check
    print("\n[2/4] Checking Dependencies:")
    missing = []
    try:
        import mcp
        print(f"  ✅ mcp SDK: available ({getattr(mcp, '__version__', 'installed')})")
    except ImportError:
        missing.append("mcp")
        print("  ❌ mcp SDK: MISSING")

    try:
        import bs4
        print(f"  ✅ beautifulsoup4: available ({getattr(bs4, '__version__', 'installed')})")
    except ImportError:
        missing.append("beautifulsoup4")
        print("  ❌ beautifulsoup4: MISSING")

    try:
        import libzim
        from libzim.reader import Archive
        from libzim.search import Query, Searcher
        from libzim.suggestion import SuggestionSearcher
        print("  ✅ libzim: available and reader/searcher components loaded")
    except ImportError as e:
        missing.append("libzim")
        print(f"  ❌ libzim: MISSING ({e})")

    if missing:
        print(f"\n  Run: pip install -r requirements.txt")
        return 1

    # 3. ZIM Archive Resolution
    args = parse_args()
    print("\n[3/4] Locating ZIM Archives:")
    paths = []

    if args.zim_dir:
        zim_dir = os.path.expanduser(args.zim_dir)
        print(f"  Checking WIKI_ZIM_DIR: {zim_dir}")
        if not os.path.isdir(zim_dir):
            print(f"  ❌ ERROR: Directory does not exist: {zim_dir}")
            return 1
        
        found = [
            os.path.join(zim_dir, f)
            for f in sorted(os.listdir(zim_dir))
            if f.endswith(".zim")
        ]
        if not found:
            print(f"  ❌ ERROR: No .zim files found in: {zim_dir}")
            return 1
        paths.extend(found)
        print(f"  ✅ Found {len(found)} archive file(s)")

    elif args.zim_path:
        zim_path = os.path.expanduser(args.zim_path)
        print(f"  Checking WIKI_ZIM_PATH: {zim_path}")
        if not os.path.exists(zim_path):
            print(f"  ❌ ERROR: Archive file does not exist: {zim_path}")
            return 1
        paths.append(zim_path)
        print("  ✅ Archive file found")
    else:
        # Check standard default fallback ~/kiwix-zim/
        default_dir = os.path.expanduser("~/kiwix-zim")
        if os.path.isdir(default_dir):
            found = [
                os.path.join(default_dir, f)
                for f in sorted(os.listdir(default_dir))
                if f.endswith(".zim")
            ]
            if found:
                print(f"  ℹ️ Found default archives in {default_dir}")
                paths.extend(found)

        if not paths:
            print("  ❌ ERROR: Neither WIKI_ZIM_DIR nor WIKI_ZIM_PATH is set.")
            print("  Provide --zim-dir or set export WIKI_ZIM_DIR=~/kiwix-zim/")
            return 1

    # 4. Open and inspect archives
    print("\n[4/4] Validating Archive Integrity:")
    all_ok = True
    for p in paths:
        basename = os.path.basename(p)
        try:
            archive = Archive(p)
            has_index = archive.has_fulltext_index
            count = archive.entry_count
            print(f"  • {basename}")
            print(f"      Entries: {count:,}")
            print(f"      Full-text index: {'✅ Yes' if has_index else '⚠️ No (fallback to title prefix)'}")
        except Exception as e:
            all_ok = False
            print(f"  • {basename} - ❌ Failed to open: {e}")
            if "Permission denied" in str(e) or "Operation not permitted" in str(e):
                print("      Tip: macOS restricts access to ~/Documents, ~/Desktop, and ~/Downloads.")
                print("      Move archives to a dedicated folder like ~/kiwix-zim/.")

    print("\n" + "=" * 60)
    if all_ok:
        print(" 🎉 Setup verification successful! Server is ready.")
        print("=" * 60)
        return 0
    else:
        print(" ⚠️ Verification encountered issues. Review errors above.")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
