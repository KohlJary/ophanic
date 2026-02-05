"""Command-line interface for Ophanic parser."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .parser import parse_file
from .errors import OphanicError


def main(args: list[str] | None = None) -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="ophanic",
        description="Parse Ophanic layout files and generate code",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # parse command
    parse_cmd = subparsers.add_parser(
        "parse",
        help="Parse an Ophanic file to JSON IR",
    )
    parse_cmd.add_argument(
        "file",
        type=Path,
        help="Path to .ophanic or .oph file",
    )
    parse_cmd.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file (default: stdout)",
    )
    parse_cmd.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output",
    )
    parse_cmd.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate without producing output",
    )

    # generate command
    gen_cmd = subparsers.add_parser(
        "generate",
        help="Generate code from an Ophanic file",
    )
    gen_cmd.add_argument(
        "file",
        type=Path,
        help="Path to .ophanic or .oph file",
    )
    gen_cmd.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file (default: stdout)",
    )
    gen_cmd.add_argument(
        "--target",
        choices=["react"],
        default="react",
        help="Target framework (default: react)",
    )
    gen_cmd.add_argument(
        "--no-tailwind",
        action="store_true",
        help="Don't include Tailwind CSS classes",
    )

    # reverse command (unified: auto-detects CSS Modules vs Tailwind)
    rev_cmd = subparsers.add_parser(
        "reverse",
        help="Convert React/JSX code to Ophanic diagram",
    )
    rev_cmd.add_argument(
        "file",
        type=Path,
        help="Path to .jsx or .tsx file",
    )
    rev_cmd.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file (default: stdout)",
    )
    rev_cmd.add_argument(
        "--css",
        type=Path,
        help="Path to CSS file (auto-detected from imports)",
    )
    rev_cmd.add_argument(
        "--tailwind",
        action="store_true",
        help="Force Tailwind parsing (skip CSS file detection)",
    )
    rev_cmd.add_argument(
        "--width",
        type=int,
        default=80,
        help="Diagram width in characters (default: 80)",
    )

    # 'analyze' is an alias for 'reverse' (backwards compatibility)
    analyze_cmd = subparsers.add_parser(
        "analyze",
        help="(Alias for 'reverse') Convert React/JSX to Ophanic diagram",
    )
    analyze_cmd.add_argument("file", type=Path, help="Path to .tsx/.jsx file")
    analyze_cmd.add_argument("--css", type=Path, help="Path to CSS file")
    analyze_cmd.add_argument("-o", "--output", type=Path, help="Output file")
    analyze_cmd.add_argument("--width", type=int, default=80, help="Diagram width")

    # figma command
    figma_cmd = subparsers.add_parser(
        "figma",
        help="Import a Figma file to Ophanic diagram",
    )
    figma_cmd.add_argument(
        "file_key",
        help="Figma file key or URL (e.g., abc123XYZ or https://figma.com/file/abc123XYZ/...)",
    )
    figma_cmd.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file (default: stdout)",
    )
    figma_cmd.add_argument(
        "--token",
        help="Figma personal access token (or set FIGMA_TOKEN env var)",
    )
    figma_cmd.add_argument(
        "--width",
        type=int,
        default=80,
        help="Diagram width in characters (default: 80)",
    )
    figma_cmd.add_argument(
        "--depth",
        type=int,
        help="Limit traversal depth (default: full tree)",
    )
    figma_cmd.add_argument(
        "--node",
        dest="node_ids",
        action="append",
        help="Specific node ID to fetch (can be repeated)",
    )
    figma_cmd.add_argument(
        "--page",
        dest="pages",
        action="append",
        help="Filter by page name (can be repeated)",
    )
    figma_cmd.add_argument(
        "--tokens",
        choices=["css", "tailwind", "json"],
        help="Output only design tokens in specified format",
    )
    figma_cmd.add_argument(
        "--no-cache",
        action="store_true",
        help="Bypass cache and fetch fresh data",
    )
    figma_cmd.add_argument(
        "--json",
        type=Path,
        help="Use local Figma JSON file instead of fetching (for rate limit bypass)",
    )

    # tokens command - extract tokens from .oph files
    tokens_cmd = subparsers.add_parser(
        "tokens",
        help="Extract design tokens from .oph file to CSS or Tailwind config",
    )
    tokens_cmd.add_argument(
        "file",
        type=Path,
        help="Path to .oph file",
    )
    tokens_cmd.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file (default: stdout)",
    )
    tokens_cmd.add_argument(
        "--format",
        choices=["css", "tailwind", "json"],
        default="css",
        help="Output format (default: css)",
    )

    parsed = parser.parse_args(args)

    if parsed.command == "parse":
        return _handle_parse(parsed)
    if parsed.command == "generate":
        return _handle_generate(parsed)
    if parsed.command in ("reverse", "analyze"):
        return _handle_reverse(parsed)
    if parsed.command == "figma":
        return _handle_figma(parsed)
    if parsed.command == "tokens":
        return _handle_tokens(parsed)

    return 0


def _handle_parse(args: argparse.Namespace) -> int:
    """Handle the parse command."""
    try:
        document = parse_file(args.file)

        if args.validate_only:
            print(f"Valid: {args.file}")
            return 0

        indent = 2 if args.pretty else None
        output = document.to_json(indent=indent)

        if args.output:
            args.output.write_text(output, encoding="utf-8")
            print(f"Written to: {args.output}")
        else:
            print(output)

        return 0

    except OphanicError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError:
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 1


def _handle_generate(args: argparse.Namespace) -> int:
    """Handle the generate command."""
    try:
        from .adapters.react import generate_react, ReactOptions

        document = parse_file(args.file)

        if args.target == "react":
            options = ReactOptions(tailwind=not args.no_tailwind)
            output = generate_react(document, options)
        else:
            print(f"Error: Unknown target: {args.target}", file=sys.stderr)
            return 1

        if args.output:
            args.output.write_text(output, encoding="utf-8")
            print(f"Written to: {args.output}")
        else:
            print(output)

        return 0

    except OphanicError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError:
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 1


def _detect_css_file(jsx_path: Path, jsx_content: str) -> Path | None:
    """Auto-detect CSS file from JSX imports.

    Looks for patterns like:
    - import './Component.css'
    - import styles from './Component.module.css'
    - import '../styles/Component.css'
    """
    import re

    # Match CSS imports
    patterns = [
        r"import\s+['\"]([^'\"]+\.css)['\"]",  # import './file.css'
        r"import\s+\w+\s+from\s+['\"]([^'\"]+\.css)['\"]",  # import styles from './file.css'
    ]

    for pattern in patterns:
        match = re.search(pattern, jsx_content)
        if match:
            css_import = match.group(1)
            # Resolve relative path
            css_path = (jsx_path.parent / css_import).resolve()
            if css_path.exists():
                return css_path

    # Fallback: check for same-name CSS file
    css_same_name = jsx_path.with_suffix(".css")
    if css_same_name.exists():
        return css_same_name

    return None


def _handle_reverse(args: argparse.Namespace) -> int:
    """Handle the reverse command (unified CSS Modules + Tailwind)."""
    try:
        from .adapters.react_reverse import ReverseOptions

        jsx_path: Path = args.file
        jsx_content = jsx_path.read_text(encoding="utf-8")
        options = ReverseOptions(diagram_width=args.width)

        # Determine which parser to use
        use_tailwind = getattr(args, "tailwind", False)
        css_path = getattr(args, "css", None)

        if not use_tailwind and css_path is None:
            # Auto-detect CSS file
            css_path = _detect_css_file(jsx_path, jsx_content)

        if css_path is not None and not use_tailwind:
            # Use CSS Modules analyzer
            from .adapters.component_analyzer import component_to_ophanic

            output = component_to_ophanic(
                jsx_path,
                css_path=css_path,
                options=options,
            )
        else:
            # Use Tailwind parser
            from .adapters.react_reverse import react_to_ophanic

            output = react_to_ophanic(jsx_content, options)

        if args.output:
            args.output.write_text(output, encoding="utf-8")
            print(f"Written to: {args.output}")
        else:
            print(output)

        return 0

    except FileNotFoundError:
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _handle_figma(args: argparse.Namespace) -> int:
    """Handle the figma command."""
    try:
        from .adapters.figma import (
            figma_to_diagram,
            figma_to_ophanic,
            FigmaOptions,
            FigmaAPIError,
            FigmaConverter,
        )
        from .adapters.react_reverse import DiagramGenerator, ReverseOptions
        import json as json_module

        options = FigmaOptions(
            token=args.token,
            depth=args.depth,
            node_ids=args.node_ids or [],
            include_pages=args.pages or [],
            diagram_width=args.width,
            use_cache=not args.no_cache,
        )

        # If --json flag, load from local file instead of API
        if args.json:
            print(f"Loading from local JSON: {args.json}")
            file_data = json_module.loads(args.json.read_text(encoding="utf-8"))
            converter = FigmaConverter(options)
            doc = converter.convert(file_data)

            if args.tokens:
                if not doc.tokens:
                    print("No design tokens found in file.", file=sys.stderr)
                    return 1
                if args.tokens == "css":
                    output = doc.tokens.to_css_vars()
                elif args.tokens == "tailwind":
                    output = json_module.dumps(doc.tokens.to_tailwind_config(), indent=2)
                else:
                    output = json_module.dumps(doc.tokens.to_dict(), indent=2)
            else:
                max_depth = options.depth if options.depth else 4
                reverse_opts = ReverseOptions(
                    diagram_width=options.diagram_width,
                    max_nesting_depth=max_depth,
                )
                generator = DiagramGenerator(reverse_opts)
                output = generator.generate(doc)
        else:
            # Fetch from Figma API
            if args.tokens:
                doc = figma_to_ophanic(args.file_key, options)
                if not doc.tokens:
                    print("No design tokens found in file.", file=sys.stderr)
                    return 1

                if args.tokens == "css":
                    output = doc.tokens.to_css_vars()
                elif args.tokens == "tailwind":
                    output = json_module.dumps(doc.tokens.to_tailwind_config(), indent=2)
                else:  # json
                    output = json_module.dumps(doc.tokens.to_dict(), indent=2)
            else:
                output = figma_to_diagram(args.file_key, options)

        if args.output:
            args.output.write_text(output, encoding="utf-8")
            print(f"Written to: {args.output}")
        else:
            print(output)

        return 0

    except FigmaAPIError as e:
        print(f"Figma API error: {e.message}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def _handle_tokens(args: argparse.Namespace) -> int:
    """Handle the tokens command - extract tokens from .oph files."""
    import json

    try:
        doc = parse_file(args.file)

        if not doc.tokens:
            print(f"No @tokens section found in {args.file}", file=sys.stderr)
            return 1

        if args.format == "css":
            output = doc.tokens.to_css_vars()
        elif args.format == "tailwind":
            output = json.dumps(doc.tokens.to_tailwind_config(), indent=2)
        else:  # json
            output = json.dumps(doc.tokens.to_dict(), indent=2)

        if args.output:
            args.output.write_text(output, encoding="utf-8")
            print(f"Written to: {args.output}")
        else:
            print(output)

        return 0

    except FileNotFoundError:
        print(f"File not found: {args.file}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
