#!/usr/bin/env bash
# ==============================================================================
# CMDHELPER Installer Script for MX-Linux / Debian
# Installs cmdhelper executable and sets up user alias 'ch'.
# ==============================================================================

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Installation directory selection
if [ "$(id -u)" -eq 0 ]; then
    INSTALL_DIR="/usr/local/bin"
    LIB_DIR="/usr/local/lib/cmdhelper"
else
    INSTALL_DIR="$HOME/.local/bin"
    LIB_DIR="$HOME/.local/share/cmdhelper"
fi

echo -e "\033[1;34m===================================================\033[0m"
echo -e "\033[1;32m[CMDHELPER] Installazione in corso...\033[0m"
echo -e "\033[1;34m===================================================\033[0m"

# Create directories
mkdir -p "$INSTALL_DIR"
mkdir -p "$LIB_DIR"

# Copy python application module and entrypoint
cp -r "$PROJECT_DIR/cmdhelper_app" "$LIB_DIR/"
cp "$PROJECT_DIR/cmdhelper" "$LIB_DIR/cmdhelper"
chmod +x "$LIB_DIR/cmdhelper"

# Create wrapper binary in INSTALL_DIR
WRAPPER_FILE="$INSTALL_DIR/cmdhelper"

cat << EOF > "$WRAPPER_FILE"
#!/usr/bin/env bash
export PYTHONPATH="$LIB_DIR:\$PYTHONPATH"
exec python3 "$LIB_DIR/cmdhelper" "\$@"
EOF

chmod +x "$WRAPPER_FILE"

echo -e "\033[1;32m✓ Eseguibile creato in: $WRAPPER_FILE\033[0m"

# Function to add PATH and alias to a given rc file
setup_user_rc() {
    local rc_file="$1"
    if [ -f "$rc_file" ]; then
        # Add PATH if missing
        if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]] && ! grep -q "$INSTALL_DIR" "$rc_file"; then
            echo "" >> "$rc_file"
            echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> "$rc_file"
            echo -e "\033[1;32m✓ PATH $INSTALL_DIR aggiunto a $rc_file\033[0m"
        fi

        # Add Alias if missing
        if ! grep -q "alias ch='cmdhelper'" "$rc_file"; then
            echo "# Alias per CMDHELPER" >> "$rc_file"
            echo "alias ch='cmdhelper'" >> "$rc_file"
            echo -e "\033[1;32m✓ Alias 'ch' aggiunto a $rc_file\033[0m"
        else
            echo -e "\033[1;34mℹ Alias 'ch' già presente in $rc_file\033[0m"
        fi
    fi
}

# Setup PATH and Alias for current user
setup_user_rc "$HOME/.bashrc"
setup_user_rc "$HOME/.zshrc"

# If invoked with sudo, also setup for real user
if [ -n "$SUDO_USER" ] && [ "$SUDO_USER" != "root" ]; then
    REAL_HOME=$(eval echo "~$SUDO_USER")
    setup_user_rc "$REAL_HOME/.bashrc"
    setup_user_rc "$REAL_HOME/.zshrc"
fi

echo -e "\033[1;34m===================================================\033[0m"
echo -e "\033[1;32mInstallazione completata con successo!\033[0m"
echo -e "Per attivare l'alias nella finestra di terminale corrente esegui:"
echo -e "  \033[1;33msource ~/.bashrc\033[0m"
echo -e ""
echo -e "Dopodiché potrai avviarla semplicemente digitando:"
echo -e "  \033[1;33mcmdhelper\033[0m   oppure   \033[1;33mch\033[0m"
echo -e "\033[1;34m===================================================\033[0m"
