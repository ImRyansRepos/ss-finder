# main.py

import argparse
import re
import sys
from datetime import datetime, timedelta
from typing import Optional, Tuple

from db import ImageDatabase
from openai_client import OpenAIClient
from indexer import ImageIndexer
from searcher import ImageSearcher


def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """
    Parse a YYYY-MM-DD date string into a datetime, or return None if not provided.
    """
    if not date_str:
        return None
    return datetime.strptime(date_str, "%Y-%m-%d")


def extract_time_window_from_query(query: str) -> Tuple[str, Optional[datetime], Optional[datetime]]:
    """
    Look for phrases like:
      - 'from 6 months ago'
      - 'from 2 weeks ago'
      - 'from 3 days ago'
      - 'from 1 year ago'

    Returns:
        (cleaned_query, from_datetime, to_datetime)

    The time window is approximate, centered around 'N units ago'
    with a +/- window that scales with distance.
    """
    pattern = r"from\s+(\d+)\s+(day|days|week|weeks|month|months|year|years)\s+ago"
    match = re.search(pattern, query, flags=re.IGNORECASE)

    if not match:
        # no time info, return query as-is
        return query.strip(), None, None

    amount = int(match.group(1))
    unit = match.group(2).lower()

    # Convert everything to rough days
    if "day" in unit:
        days = amount
    elif "week" in unit:
        days = amount * 7
    elif "month" in unit:
        days = amount * 30  # rough approximation
    elif "year" in unit:
        days = amount * 365
    else:
        days = 0

    now = datetime.now()
    center = now - timedelta(days=days)

    # Window size scales with distance: 30% of the distance, minimum 3 days
    if days > 0:
        window_days = max(3, int(days * 0.3))
    else:
        window_days = 3

    window = timedelta(days=window_days)
    from_dt = center - window
    to_dt = center + window

    # Remove the time phrase from the query text
    cleaned_query = re.sub(pattern, "", query, flags=re.IGNORECASE).strip()

    return cleaned_query, from_dt, to_dt


def cmd_index(args) -> None:
    """
    Handle the 'index' command: index one or more directories in parallel.
    """
    db = ImageDatabase(db_path=args.db)
    client = OpenAIClient()
    indexer = ImageIndexer(db, client)

    for directory in args.directories:
        print(f"\n=== Indexing directory: {directory} ===")
        indexer.index_directory(directory, max_workers=args.workers)


def cmd_search(args) -> None:
    """
    Handle the 'search' command: interactive or CLI-based query + optional time filter.
    """
    db = ImageDatabase(db_path=args.db)
    client = OpenAIClient()
    searcher = ImageSearcher(db, client)

    # If query wasn't given on the CLI, prompt the user
    if args.query:
        raw_query = args.query
    else:
        raw_query = input("Describe the image: ").strip()

    if not raw_query:
        print("No description provided. Exiting.")
        return

    # First, see if user also supplied an explicit --from-date / --to-date
    from_dt_cli = parse_date(args.from_date)
    to_dt_cli = parse_date(args.to_date)

    # If CLI dates are not given, we try to infer a time window from the query
    if from_dt_cli is None and to_dt_cli is None:
        cleaned_query, from_dt_auto, to_dt_auto = extract_time_window_from_query(raw_query)
        query_text = cleaned_query
        from_dt = from_dt_auto
        to_dt = to_dt_auto
    else:
        # If user explicitly provided dates, we don't touch the query
        query_text = raw_query
        from_dt = from_dt_cli
        to_dt = to_dt_cli

    print(f"\nSearching for: '{query_text}'")
    if from_dt or to_dt:
        print("Time filter:")
        if from_dt:
            print(f"  From: {from_dt.isoformat()}")
        if to_dt:
            print(f"  To:   {to_dt.isoformat()}")

    results = searcher.search(
        query=query_text,
        top_k=args.top_k,
        from_datetime=from_dt,
        to_datetime=to_dt,
    )

    if not results:
        print("\nNo results found.")
        return

    print("\nTop matches:\n")
    for idx, res in enumerate(results, start=1):
        rec = res.record
        print(f"{idx}. {rec.path}")
        print(f"   Score:      {res.score:.4f}")
        print(f"   Caption:    {rec.caption}")
        print(f"   Created at: {rec.created_at.isoformat()}")
        print("")


def build_arg_parser() -> argparse.ArgumentParser:
    """
    Build the top-level argument parser with 'index' and 'search' subcommands.
    """
    parser = argparse.ArgumentParser(
        description="Search your local .png/.jpg images by natural language description."
    )
    parser.add_argument(
        "--db",
        default="images.db",
        help="Path to the SQLite database file (default: images.db)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # index command
    p_index = subparsers.add_parser("index", help="Index images in one or more directories")
    p_index.add_argument(
        "directories",
        nargs="+",
        help="One or more root directories to scan for images",
    )
    p_index.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of parallel workers for indexing (default: 4)",
    )
    p_index.set_defaults(func=cmd_index)

    # search command
    p_search = subparsers.add_parser("search", help="Search indexed images")
    # query is optional; if not supplied, we prompt the user interactively
    p_search.add_argument(
        "query",
        nargs="?",
        help="Text description of the image you're looking for (optional; will prompt if omitted)",
    )
    p_search.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of results to return (default: 5)",
    )
    p_search.add_argument(
        "--from-date",
        help="Filter: earliest date (YYYY-MM-DD). If omitted, can be inferred from a phrase like 'from 6 months ago' in the description.",
    )
    p_search.add_argument(
        "--to-date",
        help="Filter: latest date (YYYY-MM-DD).",
    )
    p_search.set_defaults(func=cmd_search)

    return parser


def main():
    parser = build_arg_parser()

    # If run without any arguments, default to 'search' mode
    if len(sys.argv) == 1:
        # Inject "search" so we fall into interactive prompt mode
        sys.argv.append("search")

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
