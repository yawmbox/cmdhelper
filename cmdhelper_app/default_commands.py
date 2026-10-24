"""
Default command set pre-populated for CMDHELPER.
Contains categorized useful Linux/MX-Linux commands with placeholders.
"""

DEFAULT_COMMANDS = [
    # --- RETE & SSH ---
    {
        "id": "net_ports",
        "title": "Mostra porte di rete in ascolto",
        "category": "Rete & SSH",
        "command": "sudo ss -tulpn",
        "description": "Elenca tutti i socket/porte in ascolto TCP e UDP con relativi processi e PID.",
        "tags": ["netstat", "ss", "porte", "listening", "network", "rete"],
        "params": []
    },
    {
        "id": "net_ip_addr",
        "title": "Mostra indirizzi IP delle interfacce",
        "category": "Rete & SSH",
        "command": "ip -br a",
        "description": "Mostra gli indirizzi IP assegnati a ciascuna interfaccia di rete in formato sintetico.",
        "tags": ["ip", "ifconfig", "interfacce", "address", "network"],
        "params": []
    },
    {
        "id": "net_ping",
        "title": "Ping indirizzo IP o dominio",
        "category": "Rete & SSH",
        "command": "ping -c {conteggio} {host}",
        "description": "Verifica la connettività di rete inviando pacchetti ICMP.",
        "tags": ["ping", "icmp", "connettivita"],
        "params": [
            {"name": "conteggio", "default": "4", "description": "Numero di pacchetti da inviare"},
            {"name": "host", "default": "8.8.8.8", "description": "Indirizzo IP o nome di dominio"}
        ]
    },
    {
        "id": "net_scp",
        "title": "Copia file via SCP a un server remoto",
        "category": "Rete & SSH",
        "command": "scp -P {porta} {file_locale} {utente}@{host_remoto}:{percorso_remoto}",
        "description": "Trasferisce in modo sicuro un file da locale a un host SSH remoto.",
        "tags": ["scp", "ssh", "copia", "trasferimento", "remote"],
        "params": [
            {"name": "porta", "default": "22", "description": "Porta SSH del server remoto"},
            {"name": "file_locale", "default": "./documento.txt", "description": "File locale da inviare"},
            {"name": "utente", "default": "root", "description": "Nome utente remoto"},
            {"name": "host_remoto", "default": "192.168.1.100", "description": "IP o dominio del server remoto"},
            {"name": "percorso_remoto", "default": "~/destination/", "description": "Cartella di destinazione sul server remoto"}
        ]
    },
    {
        "id": "net_rsync",
        "title": "Sincronizza cartella via Rsync (con progresso)",
        "category": "Rete & SSH",
        "command": "rsync -avz --progress -e 'ssh -p {porta}' {sorgente} {utente}@{host_remoto}:{destinazione}",
        "description": "Sincronizza file e directory locali verso un server remoto mostrando la barra di avanzamento.",
        "tags": ["rsync", "sync", "backup", "ssh", "trasferimento"],
        "params": [
            {"name": "porta", "default": "22", "description": "Porta SSH"},
            {"name": "sorgente", "default": "./cartella/", "description": "Cartella locale da sincronizzare"},
            {"name": "utente", "default": "user", "description": "Nome utente remoto"},
            {"name": "host_remoto", "default": "192.168.1.50", "description": "IP del server remoto"},
            {"name": "destinazione", "default": "/backup/", "description": "Percorso remoto di destinazione"}
        ]
    },
    {
        "id": "net_ssh_copy_key",
        "title": "Copia chiave SSH per accesso senza password",
        "category": "Rete & SSH",
        "command": "ssh-copy-id -p {porta} {utente}@{host_remoto}",
        "description": "Installa la chiave pubblica SSH sul server remoto per abilitare il login autenticato senza password.",
        "tags": ["ssh", "key", "pubkey", "autenticazione", "ssh-copy-id"],
        "params": [
            {"name": "porta", "default": "22", "description": "Porta SSH"},
            {"name": "utente", "default": "user", "description": "Nome utente remoto"},
            {"name": "host_remoto", "default": "192.168.1.100", "description": "IP o nome host remoto"}
        ]
    },
    {
        "id": "net_curl_headers",
        "title": "Verifica gli header HTTP di un sito web",
        "category": "Rete & SSH",
        "command": "curl -I -L {url}",
        "description": "Mostra solo gli header HTTP di risposta (stato, server, cookie, redirect).",
        "tags": ["curl", "http", "headers", "web", "url"],
        "params": [
            {"name": "url", "default": "https://example.com", "description": "URL del sito da verificare"}
        ]
    },

    # --- FILE & ARCHIVI ---
    {
        "id": "archive_tar_gz_create",
        "title": "Crea archivio compresso .tar.gz",
        "category": "File & Archivi",
        "command": "tar -czvf {nome_archivio}.tar.gz {cartella_o_file}",
        "description": "Crea un file archivio compresso con gzip contenente la cartella o i file specificati.",
        "tags": ["tar", "gzip", "compress", "compressione", "archivio"],
        "params": [
            {"name": "nome_archivio", "default": "backup_files", "description": "Nome dell'archivio senza estensione"},
            {"name": "cartella_o_file", "default": "./documenti", "description": "Cartella o file da archiviare"}
        ]
    },
    {
        "id": "archive_tar_gz_extract",
        "title": "Estrai archivio .tar.gz",
        "category": "File & Archivi",
        "command": "tar -xzvf {file_archivio}.tar.gz -C {cartella_destinazione}",
        "description": "Estrae il contenuto di un archivio .tar.gz nella cartella specificata.",
        "tags": ["tar", "gzip", "extract", "estrazione", "decompressione"],
        "params": [
            {"name": "file_archivio", "default": "archivio", "description": "Nome del file archivio (senza .tar.gz)"},
            {"name": "cartella_destinazione", "default": ".", "description": "Cartella dove estrarre i file"}
        ]
    },
    {
        "id": "file_find_by_name",
        "title": "Cerca file per nome ricorsivamente",
        "category": "File & Archivi",
        "command": "find {percorso} -name \"{pattern}\" 2>/dev/null",
        "description": "Cerca ricorsivamente tutti i file la cui denominazione corrisponde al pattern inserito.",
        "tags": ["find", "cerca", "search", "file", "pattern"],
        "params": [
            {"name": "percorso", "default": ".", "description": "Directory da cui avviare la ricerca"},
            {"name": "pattern", "default": "*.log", "description": "Pattern di ricerca file (es. *.txt, *.log, *config*)"}
        ]
    },
    {
        "id": "file_find_large",
        "title": "Trova file più grandi di una certa dimensione",
        "category": "File & Archivi",
        "command": "find {percorso} -type f -size +{dimensione}M -exec ls -lh {} + 2>/dev/null",
        "description": "Elenca i file singoli che superano la dimensione in Megabyte indicata.",
        "tags": ["find", "large", "spazio", "dimensione", "file grandi"],
        "params": [
            {"name": "percorso", "default": "/", "description": "Percorso da scansionare"},
            {"name": "dimensione", "default": "100", "description": "Dimensione minima in Megabyte (MB)"}
        ]
    },
    {
        "id": "file_grep_text",
        "title": "Cerca testo all'interno di file ricorsivamente",
        "category": "File & Archivi",
        "command": "grep -rnw \"{testo_da_cercare}\" {directory}",
        "description": "Cerca la stringa di testo specificata all'interno di tutti i file presenti nella directory e sotto-directory.",
        "tags": ["grep", "testo", "ricerca", "search", "stringa"],
        "params": [
            {"name": "testo_da_cercare", "default": "ERROR", "description": "Parola o frase da cercare"},
            {"name": "directory", "default": "./", "description": "Directory in cui effettuare la ricerca"}
        ]
    },
    {
        "id": "file_symlink",
        "title": "Crea un collegamento simbolico (Symlink)",
        "category": "File & Archivi",
        "command": "ln -s {file_o_cartella_originale} {nome_symlink}",
        "description": "Crea un link simbolico verso un file o una directory esistente.",
        "tags": ["ln", "symlink", "link", "collegamento"],
        "params": [
            {"name": "file_o_cartella_originale", "default": "/var/log/syslog", "description": "Percorso del file o cartella sorgente reale"},
            {"name": "nome_symlink", "default": "./syslog_link", "description": "Nome del link da creare"}
        ]
    },

    # --- SISTEMA & PROCESSI ---
    {
        "id": "sys_top_procs",
        "title": "Mostra i primi processi per consumo CPU",
        "category": "Sistema & Processi",
        "command": "ps aux --sort=-%cpu | head -n {righe}",
        "description": "Elenca i processi in esecuzione ordinati per utilizzo percentuale di CPU.",
        "tags": ["ps", "cpu", "processi", "top", "risorse"],
        "params": [
            {"name": "righe", "default": "10", "description": "Numero di processi da mostrare"}
        ]
    },
    {
        "id": "sys_mem_procs",
        "title": "Mostra i primi processi per consumo RAM",
        "category": "Sistema & Processi",
        "command": "ps aux --sort=-%mem | head -n {righe}",
        "description": "Elenca i processi ordinati in base al consumo di memoria RAM.",
        "tags": ["ps", "ram", "memoria", "processi", "risorse"],
        "params": [
            {"name": "righe", "default": "10", "description": "Numero di processi da mostrare"}
        ]
    },
    {
        "id": "sys_systemctl_status",
        "title": "Verifica stato di un servizio Systemd",
        "category": "Sistema & Processi",
        "command": "systemctl status {servizio}",
        "description": "Mostra lo stato di esecuzione, i log recenti e l'abilitazione all'avvio di un servizio.",
        "tags": ["systemd", "systemctl", "servizio", "status", "daemon"],
        "params": [
            {"name": "servizio", "default": "ssh", "description": "Nome del servizio (es. ssh, nginx, apache2, docker)"}
        ]
    },
    {
        "id": "sys_systemctl_restart",
        "title": "Riavvia un servizio Systemd",
        "category": "Sistema & Processi",
        "command": "sudo systemctl restart {servizio}",
        "description": "Riavvia immediatamente il servizio specificato.",
        "tags": ["systemctl", "restart", "servizio", "riavvio"],
        "params": [
            {"name": "servizio", "default": "ssh", "description": "Nome del servizio da riavviare"}
        ]
    },
    {
        "id": "sys_journalctl_service",
        "title": "Mostra log di un servizio in tempo reale",
        "category": "Sistema & Processi",
        "command": "sudo journalctl -u {servizio} -f -n {righe}",
        "description": "Visualizza gli ultimi log di un servizio Systemd e rimane in ascolto per nuovi log.",
        "tags": ["journalctl", "log", "systemd", "follow", "servizio"],
        "params": [
            {"name": "servizio", "default": "ssh", "description": "Nome del servizio"},
            {"name": "righe", "default": "50", "description": "Numero di ultime righe da visualizzare"}
        ]
    },
    {
        "id": "sys_kill_process_name",
        "title": "Termina tutti i processi con un determinato nome",
        "category": "Sistema & Processi",
        "command": "sudo pkill -f {nome_processo}",
        "description": "Invia il segnale di terminazione a tutti i processi corrispondenti al nome inserito.",
        "tags": ["kill", "pkill", "processo", "termina", "arresta"],
        "params": [
            {"name": "nome_processo", "default": "firefox", "description": "Nome o pattern del processo da terminare"}
        ]
    },

    # --- DISCHI & STORAGE ---
    {
        "id": "disk_space_df",
        "title": "Mostra spazio libero sui dischi (df)",
        "category": "Dischi & Storage",
        "command": "df -h -T",
        "description": "Visualizza lo spazio totale, occupato e disponibile su tutti i filesystem montati.",
        "tags": ["df", "dischi", "spazio", "disk", "storage", "filesystem"],
        "params": []
    },
    {
        "id": "disk_partitions_lsblk",
        "title": "Elenca dischi e partizioni (lsblk)",
        "category": "Dischi & Storage",
        "command": "lsblk -o NAME,FSTYPE,SIZE,MOUNTPOINT,LABEL",
        "description": "Mostra in struttura ad albero i dispositivi di memorizzazione, le partizioni e i punti di montaggio.",
        "tags": ["lsblk", "partizioni", "dischi", "block", "devices"],
        "params": []
    },
    {
        "id": "disk_folder_usage",
        "title": "Mostra la dimensione delle cartelle principali",
        "category": "Dischi & Storage",
        "command": "du -h --max-depth=1 {percorso} 2>/dev/null | sort -hr",
        "description": "Calcola la dimensione totale di ogni sottocartella all'interno della directory specificata.",
        "tags": ["du", "dimensione", "cartelle", "spazio", "folder"],
        "params": [
            {"name": "percorso", "default": ".", "description": "Cartella da analizzare"}
        ]
    },
    {
        "id": "disk_mount_device",
        "title": "Monta una partizione o dispositivo esterno",
        "category": "Dischi & Storage",
        "command": "sudo mount {dispositivo} {punto_montaggio}",
        "description": "Collega una partizione di un disco o chiavetta USB a una cartella del sistema.",
        "tags": ["mount", "montaggio", "disco", "usb", "drive"],
        "params": [
            {"name": "dispositivo", "default": "/dev/sdb1", "description": "Dispositivo da montare (es. /dev/sdb1)"},
            {"name": "punto_montaggio", "default": "/mnt/usb", "description": "Directory di destinazione per il montaggio"}
        ]
    },

    # --- UTENTI & PERMESSI ---
    {
        "id": "user_chmod_recursive",
        "title": "Cambia permessi a file e sottocartelle ricorsivamente",
        "category": "Utenti & Permessi",
        "command": "chmod -R {permessi} {percorso}",
        "description": "Modifica i permessi di lettura/scrittura/esecuzione su tutti i file e cartelle del percorso.",
        "tags": ["chmod", "permessi", "755", "644", "ricorsivo"],
        "params": [
            {"name": "permessi", "default": "755", "description": "Notazione ottale (es. 755, 644, 700)"},
            {"name": "percorso", "default": "./cartella", "description": "Percorso su cui applicare i permessi"}
        ]
    },
    {
        "id": "user_chown_recursive",
        "title": "Cambia proprietario e gruppo ricorsivamente",
        "category": "Utenti & Permessi",
        "command": "sudo chown -R {utente}:{gruppo} {percorso}",
        "description": "Assegna la proprietà di un file o di un'intera struttura di directory a un utente e gruppo specifici.",
        "tags": ["chown", "proprietario", "utente", "gruppo", "owner"],
        "params": [
            {"name": "utente", "default": "$USER", "description": "Nome dell'utente proprietario"},
            {"name": "gruppo", "default": "$USER", "description": "Nome del gruppo proprietario"},
            {"name": "percorso", "default": "./cartella", "description": "Directory su cui cambiare la proprietà"}
        ]
    },
    {
        "id": "user_add_sudo",
        "title": "Aggiungi utente esistente al gruppo Sudo/Admin",
        "category": "Utenti & Permessi",
        "command": "sudo usermod -aG sudo {nome_utente}",
        "description": "Abilita un utente all'esecuzione dei comandi privilegiati via sudo.",
        "tags": ["usermod", "sudo", "utenti", "admin", "privilegi"],
        "params": [
            {"name": "nome_utente", "default": "nuovoutente", "description": "Nome utente a cui assegnare i privilegi sudo"}
        ]
    },

    # --- PACCHETTI APT ---
    {
        "id": "apt_update_upgrade",
        "title": "Aggiorna lista pacchetti e sistema APT",
        "category": "Pacchetti APT",
        "command": "sudo apt update && sudo apt upgrade -y",
        "description": "Aggiorna il database dei repository Debian/MX-Linux ed esegue l'aggiornamento dei pacchetti installati.",
        "tags": ["apt", "update", "upgrade", "aggiornamento", "pacchetti"],
        "params": []
    },
    {
        "id": "apt_search_pkg",
        "title": "Cerca un pacchetto nel repository APT",
        "category": "Pacchetti APT",
        "command": "apt search {nome_pacchetto}",
        "description": "Cerca nei repository disponibili i pacchetti il cui nome o descrizione corrisponde al termine indicato.",
        "tags": ["apt", "search", "cerca", "pacchetto"],
        "params": [
            {"name": "nome_pacchetto", "default": "htop", "description": "Nome o parola chiave del pacchetto da cercare"}
        ]
    },
    {
        "id": "apt_install_pkg",
        "title": "Installa un nuovo pacchetto",
        "category": "Pacchetti APT",
        "command": "sudo apt install -y {nome_pacchetto}",
        "description": "Scarica ed installa il pacchetto specificato e le sue dipendenze.",
        "tags": ["apt", "install", "pacchetto", "installazione"],
        "params": [
            {"name": "nome_pacchetto", "default": "curl", "description": "Nome esatto del pacchetto da installare"}
        ]
    },
    {
        "id": "apt_autoremove",
        "title": "Rimuovi pacchetti inutilizzati e pulisci la cache",
        "category": "Pacchetti APT",
        "command": "sudo apt autoremove -y && sudo apt clean",
        "description": "Rimuove le dipendenze non più necessarie e cancella i file .deb scaricati in cache liberando spazio su disco.",
        "tags": ["apt", "autoremove", "clean", "pulizia", "cache"],
        "params": []
    },

    # --- GIT ---
    {
        "id": "git_status_short",
        "title": "Git status sintetico",
        "category": "Git",
        "command": "git status -sb",
        "description": "Mostra lo stato del repository Git in forma compatta con informazioni sul branch corrente.",
        "tags": ["git", "status", "branch", "vcs"],
        "params": []
    },
    {
        "id": "git_log_pretty",
        "title": "Git log grafico a una riga",
        "category": "Git",
        "command": "git log --oneline --graph --decorate -n {limite}",
        "description": "Visualizza la cronologia dei commit in un formato grafico sintetico ed elegante.",
        "tags": ["git", "log", "commit", "history", "graph"],
        "params": [
            {"name": "limite", "default": "15", "description": "Numero di commit recenti da visualizzare"}
        ]
    },
    {
        "id": "git_commit_all",
        "title": "Aggiungi modifiche ed esegui il Commit",
        "category": "Git",
        "command": "git add . && git commit -m \"{messaggio}\"",
        "description": "Aggiunge tutti i file modificati e crea un nuovo commit con il messaggio specificato.",
        "tags": ["git", "commit", "add", "salva"],
        "params": [
            {"name": "messaggio", "default": "Aggiornamento file di configurazione", "description": "Messaggio descrittivo del commit"}
        ]
    },
    {
        "id": "git_undo_last_commit",
        "title": "Annulla l'ultimo commit mantenendo le modifiche ai file",
        "category": "Git",
        "command": "git reset --soft HEAD~1",
        "description": "Ripristina lo stato prima dell'ultimo commit lasciando le modifiche nel workspace per essere modificate.",
        "tags": ["git", "reset", "undo", "commit", "soft"],
        "params": []
    },

    # --- MX-LINUX & HARDWARE ---
    {
        "id": "mx_hardware_info",
        "title": "Informazioni complete sull'hardware del sistema (inxi)",
        "category": "MX-Linux & Hardware",
        "command": "inxi -Fxz",
        "description": "Report dettagliato su CPU, GPU, Scheda Madre, RAM, Dischi, Rete e versione Kernel/OS MX Linux.",
        "tags": ["inxi", "hardware", "system", "mx-linux", "specs", "cpu", "gpu"],
        "params": []
    },
    {
        "id": "mx_pci_devices",
        "title": "Elenca periferiche PCI (lspci)",
        "category": "MX-Linux & Hardware",
        "command": "lspci -nnk | grep -iA3 {tipo}",
        "description": "Mostra i dispositivi bus PCI (scheda video, scheda di rete, Wi-Fi) ed i relativi driver in uso.",
        "tags": ["lspci", "pci", "driver", "vga", "network", "hardware"],
        "params": [
            {"name": "tipo", "default": "vga", "description": "Filtro (es. vga, network, audio, wireless)"}
        ]
    },
    {
        "id": "mx_kernel_version",
        "title": "Mostra versione del Kernel e architettura",
        "category": "MX-Linux & Hardware",
        "command": "uname -srm",
        "description": "Visualizza il nome del kernel, la versione corrente e l'architettura della CPU (x86_64).",
        "tags": ["uname", "kernel", "mx-linux", "architettura", "system"],
        "params": []
    }
]
