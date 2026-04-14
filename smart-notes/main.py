# main.py — the CLI entry point.
# Parses command-line arguments and calls the right function from store.py.
# Never imports chromadb. Never touches embeddings. Pure CLI layer.
import argparse
import sys
from store import add_note, search_notes, list_notes, delete_note, count_notes

def print_separator():
    print("-" * 55)

def print_note(note:dict,show_similarity:bool=False):
    print(f" ID: {note['id']}")
    print(f"  Text:    {note['text']}")
    print(f"  Tag:     {note['tag']}")
    print(f"  Added:   {note['created_at']}")
    if show_similarity:
        score = note['similarity']
        # Visual bar — more intuitive than a raw number
        # int(score * 20) gives a bar width from 0 to 20 characters
        bar = "█" * int(score * 20) + "░" * (20 - int(score * 20))
        print(f" Similarity: {score:.4f} {bar}")

def cmd_add(args):
    if not args.text.strip():
        print("Error: Note text cannot be empty.")
        sys.exit(1)
    print(f'\nAdding note with tag "{args.tag}"...')
    note_id =add_note(args.text, args.tag)
    print(f"\nNote saved.")
    print(f"  ID:   {note_id}")
    print(f"  Text: {args.text}")
    print(f"  Tag:  {args.tag}\n")

def cmd_search(args):
    total = count_notes()
    if total == 0:
        print('\nNo notes yet. Add some with: python main.py add "your note"\n')
        return
    print(f'\nSearching {total} note(s) for: "{args.query}"\n')
    results = search_notes(args.query, args.top)
    if not results:
        print("No matches found.")
        return
    for i, note in enumerate(results, start=1):
        print(f"Result {i}:")
        print_note(note, show_similarity=True)
        print_separator()
    print()
def cmd_list(args):
    notes = list_notes()
    if not notes:
        print('\nNo notes yet. Add some with: python main.py add "your note"\n')
        return
    print(f'\nListing all {len(notes)} note(s):\n')
    for note in notes:
        print_note(note)
        print_separator()
    print()
def cmd_delete(args):
    print(f'\nDeleting note with ID: {args.id}...')
    success = delete_note(args.id)
    if success:
        print("Note deleted.")
    else:
        print(f"Error: no note found with ID '{args.id}'\n")
        sys.exit(1)

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="smart-notes",
        description="A semantically searchable personal notebook."
    )

    # add_subparsers creates the sub-command system.
    # dest="command" stores which sub-command the user typed.
    # required=True means the user must provide one.
    subparsers = parser.add_subparsers(dest="command", required=True)

    # "add" sub-command
    p_add = subparsers.add_parser("add", help="Add a new note")
    p_add.add_argument("text", help="The note text")
    # optional flag — if omitted, defaults to "general"
    p_add.add_argument("--tag", default="general", help="Tag (default: general)")
    p_add.set_defaults(func=cmd_add)

    # "search" sub-command
    p_search = subparsers.add_parser("search", help="Search notes by meaning")
    p_search.add_argument("query", help="What to search for")
    p_search.add_argument("--top", type=int, default=3, help="Number of results (default: 3)")
    p_search.set_defaults(func=cmd_search)

    # "list" sub-command
    p_list = subparsers.add_parser("list", help="List all notes")
    p_list.set_defaults(func=cmd_list)

    # "delete" sub-command
    p_delete = subparsers.add_parser("delete", help="Delete a note by ID")
    p_delete.add_argument("id", help="The note ID to delete")
    p_delete.set_defaults(func=cmd_delete)

    return parser
def main():
    parser = build_parser()

    # parse_args() reads sys.argv, matches the sub-command, validates arguments.
    # If anything is wrong it prints help and exits — we don't write that logic.
    args = parser.parse_args()

    # set_defaults(func=...) stored the handler function on the args object.
    # This calls whichever handler matches the sub-command — no if/elif chain needed.
    args.func(args)

if __name__ == "__main__":
    main()