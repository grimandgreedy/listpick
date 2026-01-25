"""
picker_state.py
State management for different picker data sources in listpick.

Replaces and extends FileState with a more flexible architecture.

Author: GrimAndGreedy
License: MIT
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Callable, Tuple
import hashlib
import json
import os
import time
import threading


@dataclass
class SubState:
    """Base class for sub-states (sheets, tabs, etc.)"""

    name: str
    display_name: str = ""
    state_dict: dict = field(default_factory=dict)

    def __post_init__(self):
        """Initialize computed fields after dataclass construction."""
        if not self.display_name:
            self.display_name = self.name


@dataclass
class SheetState(SubState):
    """Sheet within a file (for Excel, ODS)"""

    pass


@dataclass
class PickerState(ABC):
    """Base class for all picker states"""

    # === Identity & Display ===
    path: str  # Unique identifier (file path, URI, or name)
    display_name: str = ""  # Human-readable name for footer

    # === Modification Tracking ===
    is_modified: bool = False
    track_modifications: bool = False  # Subclass sets this

    # === State Storage ===
    state_dict: dict = field(
        default_factory=dict
    )  # Complete Picker state from get_function_data()

    # === Sub-states (Sheets/Tabs) ===
    sub_states: list[SubState] = field(default_factory=list)
    sub_state_index: int = 0

    # === Startup Function ===
    startup_function: Optional[Callable] = (
        None  # Called when switching to this state or starting run loop
    )

    def __post_init__(self):
        """Initialize computed fields. Subclasses should call super().__post_init__()"""
        if not self.display_name:
            self.display_name = (
                self.path.split("/")[-1] if "/" in self.path else self.path
            )

    @abstractmethod
    def load_data(self) -> Tuple[list, list]:
        """
        Load items and header from data source.
        Returns: (items, header)
        """
        pass

    @abstractmethod
    def can_save(self) -> bool:
        """Whether this state supports saving to disk."""
        pass

    @abstractmethod
    def should_prompt_on_exit(self) -> bool:
        """Whether to prompt user about unsaved changes on exit."""
        pass

    def mark_modified(self) -> None:
        """Mark as modified if tracking is enabled."""
        if self.track_modifications:
            self.is_modified = True

    def get_footer_info(self) -> dict:
        """Return footer display information."""
        return {
            "display_name": self.display_name,
            "modified_indicator": " *" if self.is_modified else "",
            "has_sub_states": len(self.sub_states) > 0,
        }

    def export(
        self, file_path: str, items: list, header: list, format: str = "csv"
    ) -> str:
        """
        Export data to file. Available to all PickerState types.
        Returns: error message or empty string on success
        """
        from listpick.utils.dump import dump_data

        function_data = {"items": items, "header": header}
        return dump_data(function_data, file_path, format=format)


@dataclass
class FilePickerState(PickerState):
    """State for file-based pickers (CSV, Excel, JSON, etc.)"""

    # File-specific attributes
    original_hash: Optional[str] = None
    is_untitled: bool = False
    untitled_number: int = 0
    file_format: str = "csv"

    # Sheets for multi-sheet files
    sheets: list[SheetState] = field(default_factory=list)

    def __post_init__(self):
        """Initialize file-specific state."""
        # Set defaults for files
        self.track_modifications = True

        # Set display name
        if not self.display_name:
            self.display_name = self.path.split("/")[-1]

        # Handle untitled files
        if self.path.startswith("Untitled"):
            self.is_untitled = True
            if self.path == "Untitled":
                self.untitled_number = 0
            else:
                # Extract number from "Untitled-2", "Untitled-3", etc.
                try:
                    parts = self.path.split("-")
                    if len(parts) > 1:
                        self.untitled_number = (
                            int(parts[1]) - 1
                        )  # "Untitled-2" → number 1
                    else:
                        self.untitled_number = 0
                except (IndexError, ValueError):
                    self.untitled_number = 0

        # Initialize with at least one sheet if empty
        if not self.sheets:
            self.sheets = [SheetState(name="Untitled")]

        # Alias sheets as sub_states for base class compatibility
        self.sub_states = self.sheets

    def load_data(self) -> Tuple[list, list]:
        """Load from disk or return empty data for untitled."""
        if self.is_untitled:
            return [[""]], []

        # Load file from disk
        from listpick.utils.table_to_list_of_lists import table_to_list
        from listpick.utils.utils import guess_file_type

        try:
            filetype = guess_file_type(self.path)
            items, header, sheets = table_to_list(
                self.path, file_type=filetype, first_row_is_header=True
            )

            # Update sheets if multi-sheet file
            if len(sheets) > 1:
                self.sheets = [SheetState(name=name) for name in sheets]
                self.sub_states = self.sheets

            # Ensure header elements are strings
            if header:
                header = [str(h) if h is not None else "" for h in header]

            return items, header
        except Exception as e:
            # If file doesn't exist or can't be loaded, return empty
            return [[""]], []

    def can_save(self) -> bool:
        """Files can be saved to disk."""
        return True

    def should_prompt_on_exit(self) -> bool:
        """Files prompt if modified."""
        return self.is_modified

    def save(self, items: list, header: list, sheet_states: list = None) -> str:
        """
        Save to disk.
        Returns: error message or empty string on success
        """
        # Determine format from extension
        ext = os.path.splitext(self.path)[1].lower()
        format_map = {
            ".csv": "csv",
            ".tsv": "tsv",
            ".json": "json",
            ".xlsx": "xlsx",
            ".ods": "ods",
            ".parquet": "parquet",
            ".feather": "feather",
            ".msgpack": "msgpack",
            ".pkl": "pickle",
        }
        save_format = format_map.get(ext, "csv")

        # Prepare function_data
        from listpick.utils.dump import dump_data

        function_data = {"items": items, "header": header}

        # For multi-sheet formats, include sheet data
        if save_format in ["xlsx", "ods"] and len(self.sheets) > 1 and sheet_states:
            function_data["sheets"] = [s.name for s in self.sheets]
            function_data["sheet_states"] = sheet_states
            function_data["original_file_path"] = self.path

        error = dump_data(function_data, self.path, format=save_format)

        if not error:
            # Update hash and clear modified flag
            self.update_hash(items, header)

        return error

    def update_hash(self, items: list, header: list) -> None:
        """Update the original hash and clear modified flag."""
        self.original_hash = self.compute_hash(items, header)
        self.is_modified = False

    @staticmethod
    def compute_hash(items: list, header: list) -> str:
        """Compute a hash of items and header for change detection."""
        data_str = json.dumps({"items": items, "header": header}, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def check_modified(self, items: list, header: list) -> bool:
        """
        Check if data has been modified since last save/load.
        Uses hybrid approach: checks dirty flag first, then verifies with hash.
        """
        if self.is_modified and self.original_hash:
            # Dirty flag is set, verify with hash
            current_hash = self.compute_hash(items, header)
            self.is_modified = current_hash != self.original_hash
        return self.is_modified

    def is_empty(self, items: list, header: list) -> bool:
        """Check if the file is empty (no data entered)."""
        if not items or items == [[]]:
            return True
        if all(all(cell == "" or cell is None for cell in row) for row in items):
            if not header or all(cell == "" or cell is None for cell in header):
                return True
        return False

    def get_current_sheet(self) -> Optional[SheetState]:
        """Return the current SheetState object."""
        if 0 <= self.sub_state_index < len(self.sheets):
            return self.sheets[self.sub_state_index]
        return None

    def add_sheet(self, name: str) -> SheetState:
        """Add a new sheet to this file and return it."""
        new_sheet = SheetState(name=name)
        self.sheets.append(new_sheet)
        self.sub_states = self.sheets
        return new_sheet


@dataclass
class StaticPickerState(PickerState):
    """State for static, in-memory data (no refresh, no disk operations)"""

    # Data stored in-memory
    items: list = field(default_factory=list)
    header: list = field(default_factory=list)

    def __post_init__(self):
        """Initialize static state."""
        super().__post_init__()
        # Don't track modifications - export is optional
        self.track_modifications = False

    def load_data(self) -> Tuple[list, list]:
        """Return stored data."""
        return self.items, self.header

    def can_save(self) -> bool:
        """Can export but not save."""
        return False

    def should_prompt_on_exit(self) -> bool:
        """Never prompt - data is ephemeral or export is optional."""
        return False


@dataclass
class DynamicPickerState(PickerState):
    """State for dynamically refreshed data (APIs, monitoring, etc.)"""

    # Refresh configuration
    refresh_function: Optional[Callable] = None
    auto_refresh: bool = False
    refresh_timer: float = 5.0
    last_refresh_time: float = 0.0

    def __post_init__(self):
        """Initialize dynamic state."""
        super().__post_init__()
        # Don't track modifications - data is dynamic
        self.track_modifications = False

    def load_data(self) -> Tuple[list, list]:
        """
        Load using refresh function.
        Note: Initial load may need to be handled specially since refresh_function
        typically takes (items, header, visible_rows, getting_data, state) params.
        """
        if self.refresh_function:
            try:
                # Try calling refresh function
                # For initial load, pass empty data
                result = self.refresh_function([], [], [], threading.Event(), {})

                # Handle different return formats
                if isinstance(result, tuple) and len(result) >= 2:
                    return result[0], result[1]
                elif isinstance(result, list):
                    return result, []
            except Exception as e:
                # If refresh function fails, return empty
                return [[]], []

        return [[]], []

    def can_save(self) -> bool:
        """Can export snapshot but not save."""
        return False

    def should_prompt_on_exit(self) -> bool:
        """Never prompt for dynamic data."""
        return False

    def should_refresh(self, current_time: float) -> bool:
        """Check if auto-refresh timer has elapsed."""
        if not self.auto_refresh or not self.refresh_function:
            return False
        return (current_time - self.last_refresh_time) >= self.refresh_timer

    def refresh(self) -> Tuple[list, list]:
        """Manually refresh data."""
        self.last_refresh_time = time.time()
        return self.load_data()
