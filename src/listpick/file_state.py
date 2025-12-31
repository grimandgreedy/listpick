"""
file_state.py
State management for files and sheets in listpick.

Author: GrimAndGreedy
License: MIT
"""

from dataclasses import dataclass, field
from typing import Optional
import hashlib
import json


@dataclass
class SheetState:
    """Represents the state of a single sheet within a file."""

    name: str                           # Sheet name (e.g., "Sheet1", "Summary")
    display_name: str = ""              # Cached display name (same as name for sheets)
    state_dict: dict = field(default_factory=dict)  # Lazy-loaded picker state

    def __post_init__(self):
        """Initialize computed fields after dataclass construction."""
        if not self.display_name:
            self.display_name = self.name


@dataclass
class FileState:
    """Represents the state of a single file in listpick."""

    # File identification
    path: str                           # Full path or "Untitled" or "Untitled-2", etc.
    display_name: str = ""              # Cached display name (basename)

    # Modified state tracking
    is_modified: bool = False           # Dirty flag for quick checks
    original_hash: Optional[str] = None # Hash of items+header when loaded/saved

    # Lazy-loaded state
    state_dict: dict = field(default_factory=dict)  # From get_function_data()

    # Untitled file tracking
    is_untitled: bool = False           # True if this is an "Untitled" file
    untitled_number: int = 0            # 0 for "Untitled", 1 for "Untitled-2", etc.

    # Sheet management (sheets belong to files)
    sheets: list['SheetState'] = field(default_factory=list)  # List of sheet states
    sheet_index: int = 0                # Current sheet index within this file

    def __post_init__(self):
        """Initialize computed fields after dataclass construction."""
        if not self.display_name:
            self.display_name = self.path.split("/")[-1]

        # Check if this is an untitled file
        if self.path.startswith("Untitled"):
            self.is_untitled = True
            if self.path == "Untitled":
                self.untitled_number = 0
            else:
                # Extract number from "Untitled-2", "Untitled-3", etc.
                try:
                    parts = self.path.split("-")
                    if len(parts) > 1:
                        self.untitled_number = int(parts[1]) - 1  # "Untitled-2" → number 1
                    else:
                        self.untitled_number = 0
                except (IndexError, ValueError):
                    self.untitled_number = 0

        # Initialize with at least one sheet if empty
        if not self.sheets:
            self.sheets = [SheetState(name="Untitled")]

    @staticmethod
    def compute_hash(items: list, header: list) -> str:
        """Compute a hash of items and header for change detection."""
        # Convert to JSON for stable hashing
        data_str = json.dumps({"items": items, "header": header}, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def update_hash(self, items: list, header: list) -> None:
        """Update the original hash and clear modified flag."""
        self.original_hash = self.compute_hash(items, header)
        self.is_modified = False

    def check_modified(self, items: list, header: list) -> bool:
        """
        Check if data has been modified since last save/load.
        Uses hybrid approach: checks dirty flag first, then verifies with hash.
        """
        if self.is_modified and self.original_hash:
            # Dirty flag is set, verify with hash
            current_hash = self.compute_hash(items, header)
            self.is_modified = (current_hash != self.original_hash)
        return self.is_modified

    def mark_modified(self) -> None:
        """Mark this file as modified (set dirty flag)."""
        self.is_modified = True

    def is_empty(self, items: list, header: list) -> bool:
        """Check if the file is empty (no data entered)."""
        # Empty if items is [[]] or [[""]...] and header is empty or all empty strings
        if not items or items == [[]]:
            return True
        if all(all(cell == "" or cell is None for cell in row) for row in items):
            if not header or all(cell == "" or cell is None for cell in header):
                return True
        return False

    def get_current_sheet(self) -> Optional[SheetState]:
        """Return the current SheetState object."""
        if 0 <= self.sheet_index < len(self.sheets):
            return self.sheets[self.sheet_index]
        return None

    def add_sheet(self, name: str) -> SheetState:
        """Add a new sheet to this file and return it."""
        new_sheet = SheetState(name=name)
        self.sheets.append(new_sheet)
        return new_sheet

    def get_sheet_names(self) -> list[str]:
        """Return list of sheet names for this file."""
        return [sheet.name for sheet in self.sheets]

    def get_current_sheet_name(self) -> str:
        """Return the name of the current sheet."""
        current_sheet = self.get_current_sheet()
        return current_sheet.name if current_sheet else "Untitled"
