"""
Data access layer for CMDHELPER.
Manages persistent JSON storage at ~/.config/cmdhelper/commands.json.
"""

import json
import os
import re
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
from .default_commands import DEFAULT_COMMANDS


def get_config_dir() -> Path:
    config_home = os.environ.get("XDG_CONFIG_HOME")
    if config_home:
        path = Path(config_home) / "cmdhelper"
    else:
        path = Path.home() / ".config" / "cmdhelper"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_commands_file_path() -> Path:
    return get_config_dir() / "commands.json"


def extract_placeholders(command_str: str) -> List[str]:
    """
    Extracts parameter placeholder names from a command string.
    E.g. "ping -c {count} {host}" -> ["count", "host"]
    """
    matches = re.findall(r"\{([a-zA-Z0-9_]+)\}", command_str)
    # Deduplicate preserving order
    seen = set()
    result = []
    for m in matches:
        if m not in seen:
            seen.add(m)
            result.append(m)
    return result


class CommandDatabase:
    def __init__(self, file_path: Optional[Path] = None):
        self.file_path = file_path or get_commands_file_path()
        self.commands: List[Dict[str, Any]] = []
        self.load()

    def load(self) -> None:
        """Loads commands from JSON. If not present or invalid, initializes defaults."""
        if not self.file_path.exists():
            self.commands = list(DEFAULT_COMMANDS)
            self.save()
            return

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "commands" in data:
                    self.commands = data["commands"]
                elif isinstance(data, list):
                    self.commands = data
                else:
                    self.commands = list(DEFAULT_COMMANDS)
        except Exception:
            # Fallback to default commands if corrupt
            self.commands = list(DEFAULT_COMMANDS)
            self.save()

    def save(self) -> None:
        """Saves current command list to JSON file."""
        data = {
            "version": 1,
            "commands": self.commands
        }
        temp_file = self.file_path.with_suffix(".tmp")
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        temp_file.replace(self.file_path)

    def get_categories(self) -> List[str]:
        """Returns sorted list of distinct category names."""
        categories = set()
        for cmd in self.commands:
            cat = cmd.get("category", "Generale").strip()
            if cat:
                categories.add(cat)
        sorted_cats = sorted(list(categories))
        return ["Tutti i comandi"] + sorted_cats

    def filter(self, category: Optional[str] = None, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Filters commands by category and/or free-text query.
        """
        results = list(self.commands)

        if category and category != "Tutti i comandi":
            results = [c for c in results if c.get("category", "") == category]

        if query:
            q = query.lower().strip()
            filtered = []
            for cmd in results:
                title = cmd.get("title", "").lower()
                cmd_str = cmd.get("command", "").lower()
                desc = cmd.get("description", "").lower()
                cat = cmd.get("category", "").lower()
                tags = [t.lower() for t in cmd.get("tags", [])]

                if (q in title or q in cmd_str or q in desc or q in cat or any(q in t for t in tags)):
                    filtered.append(cmd)
            results = filtered

        return results

    def add_command(
        self,
        title: str,
        category: str,
        command_str: str,
        description: str = "",
        tags: Optional[List[str]] = None,
        params: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Adds a new command entry."""
        cmd_id = f"custom_{uuid.uuid4().hex[:8]}"

        # Auto-extract params if not explicitly provided
        placeholders = extract_placeholders(command_str)
        if params is None:
            params = [{"name": p, "default": "", "description": f"Valore per {p}"} for p in placeholders]
        else:
            # Sync params with placeholders
            existing_names = {p["name"]: p for p in params}
            params = [
                existing_names.get(p, {"name": p, "default": "", "description": f"Valore per {p}"})
                for p in placeholders
            ]

        new_cmd = {
            "id": cmd_id,
            "title": title.strip() or "Comando personalizzato",
            "category": category.strip() or "Custom",
            "command": command_str.strip(),
            "description": description.strip(),
            "tags": tags or [],
            "params": params
        }
        self.commands.insert(0, new_cmd)
        self.save()
        return new_cmd

    def update_command(self, cmd_id: str, updated_data: Dict[str, Any]) -> bool:
        """Updates an existing command by ID."""
        for i, cmd in enumerate(self.commands):
            if cmd.get("id") == cmd_id:
                # Update params if command string changed
                if "command" in updated_data:
                    placeholders = extract_placeholders(updated_data["command"])
                    existing_params = {p["name"]: p for p in updated_data.get("params", cmd.get("params", []))}
                    updated_data["params"] = [
                        existing_params.get(p, {"name": p, "default": "", "description": f"Valore per {p}"})
                        for p in placeholders
                    ]
                cmd.update(updated_data)
                self.commands[i] = cmd
                self.save()
                return True
        return False

    def delete_command(self, cmd_id: str) -> bool:
        """Deletes a command by ID."""
        for i, cmd in enumerate(self.commands):
            if cmd.get("id") == cmd_id:
                del self.commands[i]
                self.save()
                return True
        return False
