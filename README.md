# CSV Column Rewriter 

Un tool Python per riordinare e filtrare le colonne dei file CSV secondo una configurazione personalizzabile. Gestisce automaticamente la conversione di date e numeri, trasformazioni speciali e mapping di codici.

## Funzionalita

- Legge tutti i file CSV dalla cartella `input` (separatore `;`)
- Riordina e filtra le colonne secondo il file `config.json`
- **Converte le date** in formato `AAAAMMGG` (es: `15/01/2025` -> `20250115`)
- **Converte i numeri** rimuovendo separatori (es: `1.234,56` -> `123456`)
- **Trasformazioni speciali**: estrazione CF/PIVA, cognome/nome, codice Belfiore, etc.
- **Mapping codici**: converte codici tipo dovuto in descrizioni leggibili
- **Doppi apici**: applica virgolette su colonne specifiche per gestire il separatore `;` nei valori
- **Pulizia cartelle**: opzioni per cancellare automaticamente i file prima/dopo l'elaborazione
- Salva i risultati come file ZIP compressi nella cartella `output`

## Utilizzo

### 1. Configura le colonne

Modifica il file `config.json`:

```json
{
    "pulisci_input": false,
    "pulisci_output": false,
    "columns": [
        {"name": "Progressivo*", "type": "numerico", "dim": 4, "source": "_auto_progressivo"},
        {"name": "Codice_Fiscale*", "type": "alfabetico", "dim": 16, "source": "codESoggPagIdUnivPagCodiceIdUnivocoE", "transform": "extract_cf"},
        ...
    ],
    "tipo_dovuto_mapping": {
        "1486": "Mensa scolastica",
        "2335": "Cosap",
        ...
    }
}
```

**Parametri principali:**
- **pulisci_input**: `true` per cancellare TUTTI i file e cartelle dalla cartella input dopo l'elaborazione (preserva `.gitkeep`)
- **pulisci_output**: `true` per cancellare TUTTI i file e cartelle dalla cartella output prima dell'elaborazione (preserva `.gitkeep`)
- **columns**: Array di configurazione colonne con:
  - `name`: Nome colonna output
  - `type`: Tipo dato (`alfabetico`, `numerico`, `data`, `booleano`, `alfanumerico`)
  - `dim`: Dimensione massima
  - `source`: Colonna sorgente nel CSV input (o `_auto_progressivo` per numerazione automatica)
  - `default`: Valore predefinito se il campo e vuoto
  - `transform`: Trasformazione speciale da applicare
- **tipo_dovuto_mapping**: Tabella di conversione codice -> descrizione

**Trasformazioni disponibili:**
- `extract_belfiore`: Estrae il codice Belfiore (4 caratteri) dal nome flusso
- `tipo_persona`: Converte F->1, G->2
- `extract_cf`: Estrae codice fiscale (solo persone fisiche)
- `extract_piva`: Estrae partita IVA (solo persone giuridiche)
- `extract_ragione_sociale`: Estrae ragione sociale (solo persone giuridiche)
- `extract_cognome`: Estrae cognome (solo persone fisiche)
- `extract_nome`: Estrae nome (solo persone fisiche)
- `map_tipo_dovuto`: Converte codice tipo dovuto usando la tabella di mapping

### 2. Aggiungi i file CSV

Posiziona i file CSV da processare nella cartella `input/`
(Il separatore deve essere `;`)

### 3. Esegui lo script

```bash
python main.py
```

Oppure usa l'eseguibile `.exe` (disponibile su GitHub dopo ogni push)

### 4. Risultato

I file processati saranno disponibili nella cartella `output/` come file ZIP.

## Struttura del progetto

```
Riscrivi-tracciato/
├── main.py           # Script principale
├── config.json       # Configurazione colonne
├── requirements.txt  # Dipendenze Python
├── input/            # Cartella per i CSV di input
├── output/           # Cartella per i risultati (ZIP)
└── .github/
    └── workflows/
        └── build-exe.yml  # GitHub Action per creare .exe
```

## Build manuale dell'eseguibile

```bash
pip install pyinstaller
pyinstaller --onefile --name csv-rewriter main.py
```

L'eseguibile sarà disponibile in `dist/csv-rewriter.exe`

## GitHub Actions

Ad ogni commit su `main` o `master`, viene automaticamente creato un eseguibile Windows `.exe` disponibile come artifact nella sezione Actions del repository.

## Esempio

**Input CSV (`input/documenti.csv`):**

```csv
Progressivo;Codice_Fiscale;Data_Emissione;Importo_Totale;Rateizzazione;Numero_Rata
1;RSSMRA80A01H501U;15/01/2025;1.234,56;3;1
2;VRDLGU75B02H501X;20/01/2025;500,00;2;1
```

**Output (`output/documenti_processed.zip` → `documenti_processed.csv`):**

```csv
Progressivo;Codice_Fiscale;Data_Emissione;Importo_Totale;Rateizzazione;Numero_Rata
1;RSSMRA80A01H501U;20250115;123456;3;1
1;RSSMRA80A01H501U;20250115;123456;3;2
1;RSSMRA80A01H501U;20250115;123456;3;3
2;VRDLGU75B02H501X;20250120;50000;2;1
2;VRDLGU75B02H501X;20250120;50000;2;2
```

Nota: Il documento 1 con 3 rate viene replicato 3 volte, il documento 2 con 2 rate viene replicato 2 volte.
