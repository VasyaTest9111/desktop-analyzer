#!/usr/bin/env python3
"""
Command-line interface for DesktopAnalyzer.

Usage:
    python desktop_analyzer_cli.py /path/to/analyze [options]
    python desktop_analyzer_cli.py --help
"""

import argparse
import sys
from pathlib import Path
from desktop_analyzer import DesktopAnalyzer, AnalyzerConfig


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="OMEGA Desktop Analyzer - Analyze directory structures",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze current directory, output to console
  %(prog)s .

  # Analyze with JSON output to file
  %(prog)s /workspace --format json --output report.json

  # Analyze multiple paths
  %(prog)s /path1 /path2 --format markdown

  # Custom configuration
  %(prog)s /workspace --depth 5 --max-files 20 --extensions .py .json .md
        """
    )

    parser.add_argument(
        "paths",
        nargs="+",
        help="Target paths to analyze"
    )

    parser.add_argument(
        "--format", "-f",
        choices=["markdown", "json", "dict"],
        default="markdown",
        help="Output format (default: markdown)"
    )

    parser.add_argument(
        "--output", "-o",
        help="Output file (if not specified, prints to console)"
    )

    parser.add_argument(
        "--depth", "-d",
        type=int,
        default=3,
        help="Maximum directory depth (default: 3)"
    )

    parser.add_argument(
        "--max-files",
        type=int,
        default=15,
        help="Maximum files per directory (default: 15)"
    )

    parser.add_argument(
        "--extensions", "-e",
        nargs="+",
        help="File extensions to include (default: .md .py .json .html .txt .js)"
    )

    parser.add_argument(
        "--ignore",
        nargs="+",
        help="Additional directories to ignore"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    # Build configuration
    from desktop_analyzer import DEFAULT_IGNORE_DIRS
    ignore_dirs = DEFAULT_IGNORE_DIRS.copy()
    if args.ignore:
        ignore_dirs.update(args.ignore)

    from desktop_analyzer import DEFAULT_EXTENSIONS
    extensions = DEFAULT_EXTENSIONS
    if args.extensions:
        extensions = tuple(args.extensions)

    config = AnalyzerConfig(
        target_paths=args.paths,
        output_file=args.output,
        max_depth=args.depth,
        max_files_per_dir=args.max_files,
        extensions=extensions,
        output_format=args.format,
        ignore_dirs=ignore_dirs
    )

    try:
        # Run analysis
        if args.verbose:
            print(f"📊 Analyzing paths: {', '.join(args.paths)}", file=sys.stderr)
            print(f"📁 Max depth: {args.depth}", file=sys.stderr)
            print(f"📄 Max files: {args.max_files}", file=sys.stderr)
            print(f"📋 Format: {args.format}", file=sys.stderr)

        analyzer = DesktopAnalyzer(config)
        result = analyzer.analyze()

        if args.verbose:
            print(f"\n✅ Analysis complete:", file=sys.stderr)
            print(f"   Folders: {result.total_folders}", file=sys.stderr)
            print(f"   Files: {result.total_files}", file=sys.stderr)
            print(f"   Valid: {result.valid_folders}", file=sys.stderr)

        # Output result
        if args.format == "markdown":
            output = result.to_markdown()
        elif args.format == "json":
            output = result.to_json()
        else:  # dict
            import json
            output = json.dumps(result.to_dict(), indent=2, ensure_ascii=False)

        if args.output:
            # Save to file
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(output, encoding='utf-8')

            if args.verbose:
                print(f"\n💾 Saved to: {args.output}", file=sys.stderr)
            else:
                print(f"✅ Report saved to: {args.output}")
        else:
            # Print to console
            print(output)

        return 0

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
