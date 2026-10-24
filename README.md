# CMDHELPER - Command Helper per Console e SSH (MX-Linux / Debian)

**CMDHELPER** è un'applicazione terminale TUI (Terminal User Interface) leggera ed estremamente veloce progettata per MX-Linux e qualsiasi sistema basato su Debian. È pensata per essere invocata da console locale o da una sessione **SSH**.

Consente di memorizzare, scorrere, cercare, personalizzare ed eseguire rapidamente comandi shell senza dover ricordare a memoria la sintassi esatta o scorrere infinitamente lo storico dei comandi.

---

## 🌟 Caratteristiche Principali

- 🚀 **Zero dipendenze esterne**: Sviluppato in Python 3 puro (`curses`, `json`, `subprocess`). Funziona immediatamente su qualsiasi server SSH senza dover installare librerie terze o virtual environment.
- 🔍 **Ricerca Istantanea**: Digita `/` o `s` per cercare qualsiasi comando per titolo, tag, categoria o parola chiave.
- 📋 **Compilazione Guidata Parametri**: Riconosce i segnaposto tra graffe (es. `{percorso}`, `{ip_host}`) e mostra una finestra modale per inserire o modificare i valori prima di eseguire il comando.
- ✏️ **Modifica Rapida "on-the-fly"**: Permette di modificare liberamente la riga di comando finale prima dell'invio alla shell.
- 💾 **Database JSON Personalizzabile**: I comandi sono salvati in `~/.config/cmdhelper/commands.json`. Puoi aggiungere, modificare ed eliminare comandi sia dall'interfaccia TUI sia modificando direttamente il file JSON.
- 🌐 **Pre-popolato con comandi utili**: Include già comandi essenziali per:
  - Rete & SSH (`ss`, `ip`, `scp`, `rsync`, `ping`, `ssh-copy-id`, `curl`)
  - File & Archivi (`tar.gz`, `find`, `grep`, `ln -s`)
  - Sistema & Processi (`ps`, `top`, `systemctl`, `journalctl`, `pkill`)
  - Dischi & Storage (`df`, `lsblk`, `du`, `mount`)
  - Utenti & Permessi (`chmod -R`, `chown -R`, `usermod`)
  - Pacchetti APT (`apt update/upgrade`, `apt search/install`)
  - Git (`status`, `log --graph`, `commit`, `undo reset`)
  - MX-Linux & Hardware (`inxi`, `lspci`, `uname`)

---

## 📦 Installazione Rapida

È sufficiente eseguire lo script di installazione incluso:

```bash
./install.sh
```

Lo script installerà `cmdhelper` in `~/.local/bin` (o `/usr/local/bin` se eseguito da `root`) e aggiungerà l'alias breve **`ch`** nel tuo file `~/.bashrc` e `~/.zshrc`.

Per ricaricare l'alias nella sessione corrente:
```bash
source ~/.bashrc
```

---

## ⌨️ Modalità di Utilizzo

### 1. Interfaccia Grafica da Terminale (TUI)

Per avviare l'interfaccia completa:
```bash
cmdhelper
# oppure con l'alias breve
ch
```

#### Tastiera e Scorciatoie nella TUI:

| Tasto | Azione |
| :--- | :--- |
| **`SU` / `GIÙ`** oppure **`k` / `j`** | Scorrere la lista comandi o le categorie |
| **`TAB`** / **`FRECCIA SINISTRA / DESTRA`** | Spostarsi tra il pannello Categorie e la Lista Comandi |
| **`/`** oppure **`s`** | Attiva la ricerca in tempo reale |
| **`INVIO` / `ENTER`** | Apri la compilazione dei parametri ed esegui il comando |
| **`e`** | Modifica rapida del testo del comando prima di eseguirlo |
| **`a`** | Aggiungi un nuovo comando personalizzato |
| **`m`** | Modifica il comando selezionato |
| **`d`** oppure **`CANC`** | Elimina il comando selezionato |
| **`c`** | Apre l'editor nano sul file di configurazione dei comandi |
| **`?`** oppure **`h`** | Mostra la schermata di aiuto e scorciatoie |
| **`q`** oppure **`ESC`** | Esci dall'applicazione |

---

### 2. Uso da Riga di Comando (CLI Direct)

È anche possibile interagire con CMDHELPER senza aprire l'interfaccia grafica:

- **Cerca un comando specifico:**
  ```bash
  ch search ping
  ```

- **Elenca tutti i comandi salvati:**
  ```bash
  ch list
  ```

- **Aggiungi un nuovo comando da riga di comando:**
  ```bash
  ch add -t "Crea archivio zip" -c "zip -r {archivio}.zip {cartella}" -cat "Archivi" -d "Comprime una cartella in formato zip"
  ```

---

## 💡 Creazione di Comandi Personalizzati con Segnaposto

Quando aggiungi un comando (dalla TUI premendo `a` o dal file `~/.config/cmdhelper/commands.json`), puoi utilizzare la sintassi `{nome_parametro}`.

Esempio di comando:
```bash
rsync -avz --progress -e 'ssh -p {porta}' {sorgente} {utente}@{host_remoto}:{destinazione}
```

Quando selezionerai questo comando in CMDHELPER, l'applicazione ti mostrerà un dialogo modale chiedendoti di inserire i valori per:
- `{porta}`
- `{sorgente}`
- `{utente}`
- `{host_remoto}`
- `{destinazione}`

Mostrandoti anche i valori di default forniti!

---

## 🔧 File di Configurazione

Tutti i dati sono salvati in formato JSON leggibile nell'Home dell'utente:
`~/.config/cmdhelper/commands.json`

Puoi fare un backup o condividere il tuo file `commands.json` tra diversi server Linux o sessioni SSH.
