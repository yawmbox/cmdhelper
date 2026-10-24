"""
Curses-based Interactive Terminal User Interface (TUI) for CMDHELPER.
Handles panels, search bar, command selection, parameter entry modal,
custom command editor, help modal, and keyboard input loop.
"""

import curses
import curses.textpad
import sys
import os
import re
from typing import List, Dict, Any, Optional, Tuple
from .db import CommandDatabase, extract_placeholders
from .runner import run_command_in_terminal


def init_colors():
    curses.start_color()
    curses.use_default_colors()

    # Define color pairs if terminal supports colors
    if curses.has_colors():
        # Pair 1: Title / Accent (Cyan)
        curses.init_pair(1, curses.COLOR_CYAN, -1)
        # Pair 2: Selected item (White on Blue)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)
        # Pair 3: Highlight / Category (Yellow)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)
        # Pair 4: Code / Command string (Green)
        curses.init_pair(4, curses.COLOR_GREEN, -1)
        # Pair 5: Footer / Status bar (Black on Cyan)
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_CYAN)
        # Pair 6: Warning / Error (Red)
        curses.init_pair(6, curses.COLOR_RED, -1)
        # Pair 7: Help / Key (Magenta)
        curses.init_pair(7, curses.COLOR_MAGENTA, -1)
        # Pair 8: Border (Blue)
        curses.init_pair(8, curses.COLOR_BLUE, -1)
        # Pair 9: Shadow (Dark Dim)
        curses.init_pair(9, curses.COLOR_BLACK, -1)


def draw_modal_shadow(stdscr, y: int, x: int, h: int, w: int):
    """Draws a visible 3D drop-shadow effect on stdscr behind/around a modal dialog."""
    max_y, max_x = stdscr.getmaxyx()
    shadow_attr = curses.color_pair(9) | curses.A_DIM
    shadow_char = "░"

    # Right side shadow (2 columns wide)
    for ry in range(y + 1, min(max_y, y + h + 1)):
        for rx in (x + w, x + w + 1):
            if 0 <= ry < max_y and 0 <= rx < max_x:
                try:
                    safe_addstr(stdscr, ry, rx, shadow_char, shadow_attr)
                except curses.error:
                    pass

    # Bottom shadow (1 row high)
    by = y + h
    if 0 <= by < max_y:
        for bx in range(x + 2, min(max_x, x + w + 2)):
            try:
                safe_addstr(stdscr, by, bx, shadow_char, shadow_attr)
            except curses.error:
                pass
    stdscr.refresh()


def draw_box(stdscr, y: int, x: int, h: int, w: int, title: str = "", color_pair: int = 8, is_modal: bool = False):
    """Draws a box with optional title border. Uses double-line UTF-8 borders for modals."""
    if h <= 1 or w <= 2:
        return
    attr = curses.color_pair(color_pair) | curses.A_BOLD if is_modal else curses.color_pair(color_pair)

    if is_modal:
        ul, ur, ll, lr = "╔", "╗", "╚", "╝"
        hl, vl = "═", "║"
        try:
            safe_addstr(stdscr, y, x, ul + hl * (w - 2) + ur, attr)
            for i in range(1, h - 1):
                safe_addstr(stdscr, y + i, x, vl, attr)
                safe_addstr(stdscr, y + i, x + w - 1, vl, attr)
            safe_addstr(stdscr, y + h - 1, x, ll + hl * (w - 2) + lr, attr)

            if title:
                title_text = f" 💡 {title[:w - 8]} "
                safe_addstr(stdscr, y, x + 3, title_text, attr | curses.A_REVERSE)
            return
        except (curses.error, UnicodeEncodeError):
            pass

    # Standard ACS box fallback
    try:
        stdscr.attron(attr)
        stdscr.addch(y, x, curses.ACS_ULCORNER)
        stdscr.addch(y, x + w - 1, curses.ACS_URCORNER)
        stdscr.addch(y + h - 1, x, curses.ACS_LLCORNER)
        stdscr.addch(y + h - 1, x + w - 1, curses.ACS_LRCORNER)

        for i in range(1, w - 1):
            stdscr.addch(y, x + i, curses.ACS_HLINE)
            stdscr.addch(y + h - 1, x + i, curses.ACS_HLINE)

        for i in range(1, h - 1):
            stdscr.addch(y + i, x, curses.ACS_VLINE)
            stdscr.addch(y + i, x + w - 1, curses.ACS_VLINE)

        if title:
            title_text = f" {title[:w - 4]} "
            stdscr.addstr(y, x + 2, title_text, attr | curses.A_BOLD)
        stdscr.attroff(attr)
    except curses.error:
        pass


def safe_addstr(stdscr, y: int, x: int, text: str, attr: int = 0, max_w: int = -1):
    """Safely adds a string to curses window within bounds."""
    max_y, max_x = stdscr.getmaxyx()
    if y < 0 or y >= max_y or x < 0 or x >= max_x:
        return

    available_width = max_x - x
    if max_w > 0:
        available_width = min(available_width, max_w)

    if available_width <= 0:
        return

    clipped_text = text[:available_width]
    try:
        stdscr.addstr(y, x, clipped_text, attr)
    except curses.error:
        if len(clipped_text) > 1:
            try:
                stdscr.addstr(y, x, clipped_text[:-1], attr)
            except curses.error:
                pass


def prompt_input(stdscr, title: str, prompt_text: str, default_val: str = "") -> Optional[str]:
    """
    Renders a modal popup dialog to prompt user for single line input.
    Enables visible terminal cursor during editing and handles horizontal scrolling without flickering.
    """
    try:
        curses.curs_set(1)  # Enable visible cursor
    except curses.error:
        pass

    max_y, max_x = stdscr.getmaxyx()
    box_h = 7
    box_w = min(74, max_x - 4)
    box_y = max(1, (max_y - box_h) // 2)
    box_x = max(1, (max_x - box_w) // 2)

    win = curses.newwin(box_h, box_w, box_y, box_x)
    win.keypad(True)

    input_val = list(default_val)
    cursor_pos = len(input_val)
    view_offset = 0
    input_w = box_w - 6

    # Draw modal drop-shadow and static box frame ONCE to avoid flickering
    draw_modal_shadow(stdscr, box_y, box_x, box_h, box_w)
    win.erase()
    draw_box(win, 0, 0, box_h, box_w, title, 3, is_modal=True)
    safe_addstr(win, 2, 2, prompt_text[:box_w - 4], curses.color_pair(3) | curses.A_BOLD)
    safe_addstr(win, 5, 2, "[ENTER] Conferma   [ESC] Annulla", curses.color_pair(7))

    try:
        while True:
            # Adjust horizontal scroll view offset to keep cursor visible
            if cursor_pos - view_offset >= input_w:
                view_offset = cursor_pos - input_w + 1
            elif cursor_pos < view_offset:
                view_offset = cursor_pos

            visible_chars = input_val[view_offset : view_offset + input_w]
            display_str = "".join(visible_chars)

            # Redraw ONLY the input field text line (no screen clear = zero flicker)
            padded_text = display_str.ljust(input_w)
            safe_addstr(win, 4, 2, "[", curses.color_pair(8))
            safe_addstr(win, 4, 3, padded_text, curses.A_BOLD, input_w)
            safe_addstr(win, 4, 3 + input_w, "]", curses.color_pair(8))

            # Position hardware cursor
            win.move(4, 3 + (cursor_pos - view_offset))
            win.refresh()

            key = win.getch()
            if key in (27,):  # ESC
                return None
            elif key in (10, 13, curses.KEY_ENTER):  # ENTER
                return "".join(input_val)
            elif key in (curses.KEY_BACKSPACE, 127, 8):
                if cursor_pos > 0:
                    input_val.pop(cursor_pos - 1)
                    cursor_pos -= 1
            elif key == curses.KEY_DC:  # DELETE key
                if cursor_pos < len(input_val):
                    input_val.pop(cursor_pos)
            elif key == curses.KEY_LEFT:
                if cursor_pos > 0:
                    cursor_pos -= 1
            elif key == curses.KEY_RIGHT:
                if cursor_pos < len(input_val):
                    cursor_pos += 1
            elif key == curses.KEY_HOME:
                cursor_pos = 0
            elif key == curses.KEY_END:
                cursor_pos = len(input_val)
            elif 32 <= key <= 126:
                input_val.insert(cursor_pos, chr(key))
                cursor_pos += 1
    finally:
        try:
            curses.curs_set(0)  # Hide cursor on dialog exit
        except curses.error:
            pass


def prompt_parameter_values(stdscr, cmd_data: Dict[str, Any]) -> Optional[str]:
    """
    Displays a modal dialog to fill parameters for a command template.
    Returns the compiled command string or None if cancelled.
    """
    raw_cmd = cmd_data.get("command", "")
    placeholders = extract_placeholders(raw_cmd)
    if not placeholders:
        return raw_cmd

    params_info = {p.get("name"): p for p in cmd_data.get("params", [])}

    # Store user values for each placeholder
    values = {}
    for p in placeholders:
        default_val = params_info.get(p, {}).get("default", "")
        values[p] = default_val

    # Single-parameter shortcut: direct prompt dialog without double-modal overlay
    if len(placeholders) == 1:
        p_curr = placeholders[0]
        p_meta = params_info.get(p_curr, {})
        p_desc = p_meta.get("description", f"Parametro {{{p_curr}}}")
        new_val = prompt_input(stdscr, f"Valore per {{{p_curr}}}", p_desc, values[p_curr])
        if new_val is None:
            return None
        return raw_cmd.replace(f"{{{p_curr}}}", new_val)

    # Multi-parameter dialog loop
    current_idx = 0

    while True:
        max_y, max_x = stdscr.getmaxyx()
        box_h = min(max_y - 2, max(12, len(placeholders) * 3 + 7))
        box_w = min(76, max_x - 4)
        box_y = max(1, (max_y - box_h) // 2)
        box_x = max(1, (max_x - box_w) // 2)

        stdscr.touchwin()
        draw_modal_shadow(stdscr, box_y, box_x, box_h, box_w)

        win = curses.newwin(box_h, box_w, box_y, box_x)
        win.keypad(True)
        win.erase()

        draw_box(win, 0, 0, box_h, box_w, f"Compilazione Parametri: {cmd_data.get('title', '')[:30]}", 3, is_modal=True)

        safe_addstr(win, 1, 2, "Inserisci i valori per ciascun parametro:", curses.color_pair(3))

        # Draw parameter input fields
        start_y = 3
        for i, p_name in enumerate(placeholders):
            if start_y + i * 3 >= box_h - 4:
                break

            p_meta = params_info.get(p_name, {})
            p_desc = p_meta.get("description", f"Parametro {p_name}")
            is_active = (i == current_idx)

            field_attr = curses.color_pair(2) if is_active else curses.A_NORMAL
            label_attr = curses.color_pair(1) | curses.A_BOLD if is_active else curses.color_pair(3)

            label = f"{{{p_name}}}: {p_desc}"
            safe_addstr(win, start_y + i * 2, 2, label[:box_w - 4], label_attr)

            val_str = values[p_name]
            val_box = f"[{val_str:<{box_w - 6}}]"
            safe_addstr(win, start_y + i * 2 + 1, 2, val_box[:box_w - 4], field_attr)

        # Show current preview of compiled command
        preview_cmd = raw_cmd
        for k, v in values.items():
            preview_cmd = preview_cmd.replace(f"{{{k}}}", v)

        prev_y = box_h - 3
        safe_addstr(win, prev_y, 2, "Anteprima: ", curses.color_pair(3) | curses.A_BOLD)
        safe_addstr(win, prev_y, 13, preview_cmd, curses.color_pair(4) | curses.A_BOLD, box_w - 15)

        safe_addstr(win, box_h - 2, 2, "[SU/GIU] Naviga  [INVIO] Modifica  [C] Conferma/Esegui  [E] Raw  [ESC] Annulla", curses.color_pair(7))
        win.refresh()

        key = win.getch()

        if key in (27,):  # ESC
            return None
        elif key in (curses.KEY_UP, 107):  # UP or 'k'
            current_idx = (current_idx - 1) % len(placeholders)
        elif key in (curses.KEY_DOWN, 106, 9):  # DOWN or 'j' or TAB
            current_idx = (current_idx + 1) % len(placeholders)
        elif key in (ord('c'), ord('C')):  # Explicit confirm & execute
            return preview_cmd
        elif key in (10, 13, curses.KEY_ENTER):  # ENTER on field -> edit
            p_curr = placeholders[current_idx]
            p_meta = params_info.get(p_curr, {})
            p_desc = p_meta.get("description", f"Parametro {p_curr}")

            new_val = prompt_input(stdscr, f"Valore per {{{p_curr}}}", p_desc, values[p_curr])
            if new_val is not None:
                values[p_curr] = new_val
                # Recalculate preview_cmd immediately with updated values
                preview_cmd = raw_cmd
                for k, v in values.items():
                    preview_cmd = preview_cmd.replace(f"{{{k}}}", v)

                if current_idx < len(placeholders) - 1:
                    current_idx += 1
                else:
                    return preview_cmd
        elif key in (ord('e'), ord('E')):
            # Raw edit preview command
            raw_edited = prompt_input(stdscr, "Modifica Comando Finale", "Modifica il comando prima dell'esecuzione:", preview_cmd)
            if raw_edited is not None:
                return raw_edited


def prompt_add_edit_command(stdscr, db: CommandDatabase, existing_cmd: Optional[Dict[str, Any]] = None) -> bool:
    """
    Modal dialog to add a new custom command or edit an existing command.
    """
    is_edit = existing_cmd is not None
    title_modal = "Modifica Comando" if is_edit else "Aggiungi Nuovo Comando"

    title_val = existing_cmd.get("title", "") if is_edit else ""
    cat_val = existing_cmd.get("category", "Custom") if is_edit else "Custom"
    cmd_val = existing_cmd.get("command", "") if is_edit else ""
    desc_val = existing_cmd.get("description", "") if is_edit else ""
    tags_val = ", ".join(existing_cmd.get("tags", [])) if is_edit else ""

    # Prompt step by step
    t = prompt_input(stdscr, title_modal, "1. Titolo del comando (es. Backup cartella):", title_val)
    if t is None or not t.strip():
        return False

    c = prompt_input(stdscr, title_modal, "2. Categoria (es. Rete, Archivi, Custom):", cat_val)
    if c is None or not c.strip():
        c = "Custom"

    cmd_str = prompt_input(stdscr, title_modal, "3. Sintassi del comando (usa {param} per i segnaposto):", cmd_val)
    if cmd_str is None or not cmd_str.strip():
        return False

    d = prompt_input(stdscr, title_modal, "4. Descrizione (opzionale):", desc_val) or ""

    tg = prompt_input(stdscr, title_modal, "5. Tag separati da virgola (opzionale):", tags_val) or ""
    tags_list = [x.strip() for x in tg.split(",") if x.strip()]

    if is_edit:
        db.update_command(existing_cmd["id"], {
            "title": t.strip(),
            "category": c.strip(),
            "command": cmd_str.strip(),
            "description": d.strip(),
            "tags": tags_list
        })
    else:
        db.add_command(
            title=t.strip(),
            category=c.strip(),
            command_str=cmd_str.strip(),
            description=d.strip(),
            tags=tags_list
        )
    return True


def show_help_modal(stdscr):
    """Displays a scrollable help modal window."""
    while True:
        max_y, max_x = stdscr.getmaxyx()
        box_h = min(max_y - 2, 22)
        box_w = min(78, max_x - 4)
        box_y = max(1, (max_y - box_h) // 2)
        box_x = max(1, (max_x - box_w) // 2)

        draw_modal_shadow(stdscr, box_y, box_x, box_h, box_w)
        win = curses.newwin(box_h, box_w, box_y, box_x)
        win.keypad(True)
        win.erase()

        draw_box(win, 0, 0, box_h, box_w, "Guida & Scorciatoie CMDHELPER", 3, is_modal=True)

        help_lines = [
            ("Scorciatoie di Navigazione:", curses.color_pair(3) | curses.A_BOLD),
            ("  SU / GIU / k / j     : Scorrere tra i comandi o categorie", curses.A_NORMAL),
            ("  TAB / SINISTRA / DES : Passare dal pannello Categorie al pannello Lista", curses.A_NORMAL),
            ("  /  oppure  s        : Attivare la ricerca in tempo reale", curses.A_NORMAL),
            ("  ESC                  : Annullare ricerca o chiudere i menu", curses.A_NORMAL),
            ("", curses.A_NORMAL),
            ("Azioni sui Comandi:", curses.color_pair(3) | curses.A_BOLD),
            ("  INVIO / ENTER        : Apri dialogo parametri ed esegui il comando", curses.A_NORMAL),
            ("  e                    : Modifica rapida della riga di comando prima dell'esecuzione", curses.A_NORMAL),
            ("  a                    : Aggiungi un nuovo comando personalizzato", curses.A_NORMAL),
            ("  m                    : Modifica il comando selezionato nel database", curses.A_NORMAL),
            ("  d / DELETE           : Elimina il comando selezionato", curses.A_NORMAL),
            ("  c                    : Apri il file di configurazione JSON in nano", curses.A_NORMAL),
            ("  ? / h                : Mostra questa schermata di aiuto", curses.A_NORMAL),
            ("  q                    : Esci da CMDHELPER", curses.A_NORMAL),
            ("", curses.A_NORMAL),
            ("Uso dei Segnaposto nei Comandi Personalizzati:", curses.color_pair(3) | curses.A_BOLD),
            ("  Inserisci parametri tra graffe, ad esempio: rsync -avz {sorgente} {destinazione}", curses.A_NORMAL),
            ("  Quando selezioni il comando, CMDHELPER ti chiederà i valori!", curses.A_NORMAL)
        ]

        for idx, (line_text, attr) in enumerate(help_lines):
            if idx + 2 >= box_h - 2:
                break
            safe_addstr(win, idx + 2, 2, line_text[:box_w - 4], attr)

        safe_addstr(win, box_h - 2, 2, "Premere un tasto qualsiasi per tornare a CMDHELPER...", curses.color_pair(7))
        win.refresh()

        key = win.getch()
        if key:
            break


class CmdHelperTUI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.db = CommandDatabase()

        # UI State
        self.categories = self.db.get_categories()
        self.selected_cat_idx = 0
        self.selected_cmd_idx = 0
        self.active_panel = "commands"  # "categories" or "commands"

        self.query = ""
        self.search_mode = False

        self.status_msg = "Premere INVIO per compilare ed eseguire il comando. Premi '?' per l'aiuto."

    def get_current_category(self) -> str:
        if 0 <= self.selected_cat_idx < len(self.categories):
            return self.categories[self.selected_cat_idx]
        return "Tutti i comandi"

    def get_filtered_commands(self) -> List[Dict[str, Any]]:
        cat = self.get_current_category()
        return self.db.filter(category=cat, query=self.query)

    def run(self):
        init_colors()
        curses.curs_set(0)
        self.stdscr.keypad(True)

        while True:
            self.categories = self.db.get_categories()
            # Ensure indices stay in bounds
            if self.selected_cat_idx >= len(self.categories):
                self.selected_cat_idx = max(0, len(self.categories) - 1)

            filtered_cmds = self.get_filtered_commands()
            if self.selected_cmd_idx >= len(filtered_cmds):
                self.selected_cmd_idx = max(0, len(filtered_cmds) - 1)

            self.draw_ui(filtered_cmds)

            key = self.stdscr.getch()

            if self.search_mode:
                self.handle_search_input(key)
                continue

            if key in (ord('q'), ord('Q')):
                break
            elif key in (ord('?'), ord('h'), ord('H')):
                show_help_modal(self.stdscr)
            elif key in (ord('/'), ord('s'), ord('S')):
                self.search_mode = True
                self.status_msg = "Modalità ricerca attiva. Digita per filtrare. [ESC] per uscire."
            elif key in (9, curses.KEY_LEFT, curses.KEY_RIGHT):  # TAB or Left/Right
                self.active_panel = "categories" if self.active_panel == "commands" else "commands"
            elif key == curses.KEY_UP or key == ord('k'):
                if self.active_panel == "categories":
                    if self.selected_cat_idx > 0:
                        self.selected_cat_idx -= 1
                        self.selected_cmd_idx = 0
                else:
                    if self.selected_cmd_idx > 0:
                        self.selected_cmd_idx -= 1
            elif key == curses.KEY_DOWN or key == ord('j'):
                if self.active_panel == "categories":
                    if self.selected_cat_idx < len(self.categories) - 1:
                        self.selected_cat_idx += 1
                        self.selected_cmd_idx = 0
                else:
                    if self.selected_cmd_idx < len(filtered_cmds) - 1:
                        self.selected_cmd_idx += 1
            elif key == curses.KEY_PPAGE:  # PAGE UP
                self.selected_cmd_idx = max(0, self.selected_cmd_idx - 8)
            elif key == curses.KEY_NPAGE:  # PAGE DOWN
                self.selected_cmd_idx = min(len(filtered_cmds) - 1, self.selected_cmd_idx + 8) if filtered_cmds else 0
            elif key in (10, 13, curses.KEY_ENTER):  # ENTER -> execute/fill params
                if filtered_cmds and 0 <= self.selected_cmd_idx < len(filtered_cmds):
                    cmd_data = filtered_cmds[self.selected_cmd_idx]
                    compiled_cmd = prompt_parameter_values(self.stdscr, cmd_data)
                    if compiled_cmd:
                        run_command_in_terminal(self.stdscr, compiled_cmd)
                        self.status_msg = f"Eseguito: {compiled_cmd[:40]}"
            elif key in (ord('e'), ord('E')):  # Fast edit before execute
                if filtered_cmds and 0 <= self.selected_cmd_idx < len(filtered_cmds):
                    cmd_data = filtered_cmds[self.selected_cmd_idx]
                    raw = prompt_input(self.stdscr, "Modifica Rapida Comando", "Modifica il comando da eseguire:", cmd_data.get("command", ""))
                    if raw:
                        run_command_in_terminal(self.stdscr, raw)
                        self.status_msg = f"Eseguito: {raw[:40]}"
            elif key in (ord('a'), ord('A')):  # Add custom command
                if prompt_add_edit_command(self.stdscr, self.db):
                    self.status_msg = "Nuovo comando aggiunto con successo!"
            elif key in (ord('m'), ord('M')):  # Edit existing command
                if filtered_cmds and 0 <= self.selected_cmd_idx < len(filtered_cmds):
                    cmd_data = filtered_cmds[self.selected_cmd_idx]
                    if prompt_add_edit_command(self.stdscr, self.db, existing_cmd=cmd_data):
                        self.status_msg = "Comando aggiornato con successo!"
            elif key in (ord('d'), ord('D'), curses.KEY_DC):  # Delete command
                if filtered_cmds and 0 <= self.selected_cmd_idx < len(filtered_cmds):
                    cmd_data = filtered_cmds[self.selected_cmd_idx]
                    confirm = prompt_input(
                        self.stdscr,
                        "Conferma Eliminazione",
                        f"Eliminare '{cmd_data.get('title')}'? Digita 'si' per confermare:",
                        ""
                    )
                    if confirm and confirm.lower().strip() in ("si", "sì", "yes", "y"):
                        self.db.delete_command(cmd_data["id"])
                        self.status_msg = "Comando eliminato."
            elif key in (ord('c'), ord('C')):  # Open config file in nano
                config_path = str(self.db.file_path)
                curses.endwin()
                os.system(f'nano "{config_path}"')
                # Reinitialise curses and reload DB after editing
                self.stdscr = curses.initscr()
                self.stdscr.keypad(True)
                init_colors()
                curses.curs_set(0)
                self.db.load()
                self.categories = self.db.get_categories()
                self.selected_cmd_idx = 0
                self.status_msg = f"File di configurazione riaperto: {config_path}"

    def handle_search_input(self, key):
        if key == 27:  # ESC
            self.search_mode = False
            self.status_msg = "Filtro di ricerca completato."
        elif key in (10, 13, curses.KEY_ENTER):
            self.search_mode = False
            self.active_panel = "commands"
            self.selected_cmd_idx = 0
            self.status_msg = f"Filtro applicato: '{self.query}'"
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            if len(self.query) > 0:
                self.query = self.query[:-1]
                self.selected_cmd_idx = 0
        elif 32 <= key <= 126:
            self.query += chr(key)
            self.selected_cmd_idx = 0

    def draw_ui(self, filtered_cmds: List[Dict[str, Any]]):
        self.stdscr.erase()
        max_y, max_x = self.stdscr.getmaxyx()

        if max_y < 12 or max_x < 50:
            safe_addstr(self.stdscr, 0, 0, "Ridimensionare il terminale (Minimo 50x12)", curses.color_pair(6))
            self.stdscr.refresh()
            return

        # 1. Header Bar (Row 0)
        header_text = f" CMDHELPER v1.0 - Helper Comandi Shell "
        search_status = f" [Cerca: '{self.query}']" if self.query else " [Premi '/' per cercare]"
        if self.search_mode:
            search_status = f" [RICERCA: {self.query}_]"

        safe_addstr(self.stdscr, 0, 0, " " * max_x, curses.color_pair(1) | curses.A_REVERSE)
        safe_addstr(self.stdscr, 0, 1, header_text, curses.color_pair(1) | curses.A_REVERSE | curses.A_BOLD)
        safe_addstr(self.stdscr, 0, max_x - len(search_status) - 2, search_status, curses.color_pair(3) | curses.A_REVERSE | curses.A_BOLD)

        # Main Layout Geometry
        main_y = 1
        main_h = max_y - 3

        # Left Column width (Categories + Commands List) vs Right Column (Detail View)
        left_w = max(30, int(max_x * 0.45))
        right_w = max_x - left_w

        # Divide Left Column into Categories (top 30%) and Commands List (bottom 70%)
        cat_h = max(5, int(main_h * 0.35))
        cmd_h = main_h - cat_h

        # Draw Borders
        cat_active_color = 1 if self.active_panel == "categories" else 8
        cmd_active_color = 1 if self.active_panel == "commands" else 8

        draw_box(self.stdscr, main_y, 0, cat_h, left_w, "Categorie", cat_active_color)
        draw_box(self.stdscr, main_y + cat_h, 0, cmd_h, left_w, f"Comandi ({len(filtered_cmds)})", cmd_active_color)
        draw_box(self.stdscr, main_y, left_w, main_h, right_w, "Dettaglio Comando", 8)

        # Render Category List
        for idx, cat_name in enumerate(self.categories):
            line_y = main_y + 1 + idx
            if line_y >= main_y + cat_h - 1:
                break
            is_selected = (idx == self.selected_cat_idx)
            attr = curses.color_pair(2) if (is_selected and self.active_panel == "categories") else (curses.color_pair(3) | curses.A_BOLD if is_selected else curses.A_NORMAL)
            prefix = "> " if is_selected else "  "
            safe_addstr(self.stdscr, line_y, 2, f"{prefix}{cat_name}", attr, left_w - 4)

        # Render Command List
        cmd_start_y = main_y + cat_h + 1
        max_visible_cmds = cmd_h - 2

        scroll_offset = max(0, self.selected_cmd_idx - max_visible_cmds + 1) if max_visible_cmds > 0 else 0

        for i in range(max_visible_cmds):
            cmd_idx = scroll_offset + i
            if cmd_idx >= len(filtered_cmds):
                break
            cmd_item = filtered_cmds[cmd_idx]
            line_y = cmd_start_y + i

            is_selected = (cmd_idx == self.selected_cmd_idx)
            attr = curses.color_pair(2) if (is_selected and self.active_panel == "commands") else (curses.A_BOLD if is_selected else curses.A_NORMAL)
            prefix = "> " if is_selected else "  "
            title = cmd_item.get("title", "Senza Titolo")
            safe_addstr(self.stdscr, line_y, 2, f"{prefix}{title}", attr, left_w - 4)

        # Render Right Detail View
        if filtered_cmds and 0 <= self.selected_cmd_idx < len(filtered_cmds):
            curr_cmd = filtered_cmds[self.selected_cmd_idx]
            rx = left_w + 2
            ry = main_y + 1
            max_rw = right_w - 4

            # Title & Category
            safe_addstr(self.stdscr, ry, rx, "Titolo: ", curses.color_pair(3) | curses.A_BOLD)
            safe_addstr(self.stdscr, ry, rx + 8, curr_cmd.get("title", ""), curses.A_BOLD, max_rw - 8)

            safe_addstr(self.stdscr, ry + 1, rx, "Categoria: ", curses.color_pair(3) | curses.A_BOLD)
            safe_addstr(self.stdscr, ry + 1, rx + 11, curr_cmd.get("category", ""), curses.A_NORMAL, max_rw - 11)

            # Command Box / String
            safe_addstr(self.stdscr, ry + 3, rx, "Sintassi Comando:", curses.color_pair(1) | curses.A_BOLD)
            cmd_str = curr_cmd.get("command", "")
            safe_addstr(self.stdscr, ry + 4, rx + 1, f"$ {cmd_str}", curses.color_pair(4) | curses.A_BOLD, max_rw - 1)

            # Description
            safe_addstr(self.stdscr, ry + 6, rx, "Descrizione:", curses.color_pair(3) | curses.A_BOLD)
            desc_text = curr_cmd.get("description", "Nessuna descrizione fornita.")
            # Wrap description across lines if long
            desc_lines = []
            words = desc_text.split()
            cur_line = ""
            for w in words:
                if len(cur_line) + len(w) + 1 <= max_rw:
                    cur_line += (" " if cur_line else "") + w
                else:
                    desc_lines.append(cur_line)
                    cur_line = w
            if cur_line:
                desc_lines.append(cur_line)

            for d_idx, d_line in enumerate(desc_lines[:4]):
                safe_addstr(self.stdscr, ry + 7 + d_idx, rx + 2, d_line, curses.A_NORMAL, max_rw - 2)

            params = curr_cmd.get("params", [])
            placeholders = extract_placeholders(cmd_str)

            p_start_y = ry + 12
            safe_addstr(self.stdscr, p_start_y, rx, "Parametri Segnaposto:", curses.color_pair(3) | curses.A_BOLD)

            if not placeholders:
                safe_addstr(self.stdscr, p_start_y + 1, rx + 2, "(Nessun parametro richiesto)", curses.A_DIM)
            else:
                params_dict = {p.get("name"): p for p in params}
                for p_i, p_name in enumerate(placeholders[:5]):
                    p_info = params_dict.get(p_name, {})
                    p_default = p_info.get("default", "")
                    p_desc = p_info.get("description", "")
                    p_line = f"• {{{p_name}}}: {p_desc} (def: '{p_default}')"
                    safe_addstr(self.stdscr, p_start_y + 1 + p_i, rx + 2, p_line, curses.color_pair(1), max_rw - 2)

            # Tags at bottom of detail panel
            tags = curr_cmd.get("tags", [])
            if tags:
                tags_str = "Tag: " + ", ".join(tags)
                safe_addstr(self.stdscr, main_y + main_h - 2, rx, tags_str, curses.color_pair(7), max_rw)
        else:
            rx = left_w + 2
            ry = main_y + 2
            safe_addstr(self.stdscr, ry, rx, "Nessun comando trovato.", curses.color_pair(6))

        # Bottom Bar: Shortcuts & Status
        footer_y = max_y - 2
        safe_addstr(self.stdscr, footer_y, 0, " " * max_x, curses.color_pair(5))
        shortcuts = "[ENTER] Compila/Esegui  [E] Modifica Rapida  [A] Nuovo  [M] Modifica  [D] Elimina  [C] Config  [?] Guida  [Q] Esci"
        safe_addstr(self.stdscr, footer_y, 1, shortcuts[:max_x - 2], curses.color_pair(5) | curses.A_BOLD)

        # Status line (Last row)
        safe_addstr(self.stdscr, max_y - 1, 0, " " * max_x, curses.A_NORMAL)
        safe_addstr(self.stdscr, max_y - 1, 1, self.status_msg[:max_x - 2], curses.color_pair(3))

        if self.search_mode:
            try:
                curses.curs_set(1)
            except curses.error:
                pass
            cursor_col = (max_x - len(search_status) - 2) + len(" [RICERCA: ") + len(self.query)
            if 0 <= cursor_col < max_x:
                self.stdscr.move(0, cursor_col)
        else:
            try:
                curses.curs_set(0)
            except curses.error:
                pass

        self.stdscr.refresh()


def launch_tui():
    try:
        curses.wrapper(lambda stdscr: CmdHelperTUI(stdscr).run())
    except KeyboardInterrupt:
        pass
