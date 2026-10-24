"""
Execution handler for CMDHELPER.
Suspends curses terminal mode, runs command in bash shell, and restores TUI state.
"""

import os
import sys
import subprocess
import curses


def run_command_in_terminal(stdscr, command_str: str) -> int:
    """
    Temporarily suspends curses, executes command_str via bash shell,
    waits for user to press ENTER, then restores curses mode.
    Returns the process returncode.
    """
    # 1. Exit curses mode temporarily
    curses.endwin()
    sys.stdout.write("\033[H\033[2J")  # Clear terminal screen
    sys.stdout.flush()

    border = "=" * 70
    print(f"\033[1;34m{border}\033[0m")
    print(f"\033[1;32m[CMDHELPER] Esecuzione comando shell:\033[0m")
    print(f"\033[1;33m  $ {command_str}\033[0m")
    print(f"\033[1;34m{border}\033[0m\n")

    shell = os.environ.get("SHELL", "/bin/bash")

    returncode = -1
    try:
        res = subprocess.run(command_str, shell=True, executable=shell)
        returncode = res.returncode
    except KeyboardInterrupt:
        print("\n\033[1;31mEsecuzione interrotta dall'utente (Ctrl+C).\033[0m")
    except Exception as e:
        print(f"\n\033[1;31mErrore durante l'esecuzione: {e}\033[0m")

    print(f"\n\033[1;34m{border}\033[0m")
    if returncode == 0:
        print(f"\033[1;32mComando completato con successo (Codice di uscita: 0).\033[0m")
    elif returncode > 0:
        print(f"\033[1;31mComando terminato con codice di errore: {returncode}.\033[0m")
    print(f"\033[1;34m{border}\033[0m")

    try:
        input("\n\033[1;36mPremere INVIO per tornare a CMDHELPER...\033[0m")
    except (KeyboardInterrupt, EOFError):
        pass

    # Re-initialize curses screen
    stdscr.clear()
    curses.doupdate()
    return returncode
