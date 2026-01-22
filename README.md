# CSV Column Rewriter 

Un tool Python per riordinare e filtrare le colonne dei file CSV secondo una configurazione personalizzabile.

## Funzionalità

- Legge tutti i file CSV dalla cartella `input`
- Riordina e filtra le colonne secondo il file `config.json`
- Salva i risultati come file ZIP compressi nella cartella `output`
- Mostra il tempo di esecuzione nel terminale

## Utilizzo

### 1. Configura le colonne

Modifica il file `config.json` per specificare le colonne desiderate nell'ordine voluto:

```json
{
    "columns": [
        "numero",
        "cognome",
        "email"
    ],
    "zip_name": "output"
}
```

**Parametri di configurazione:**
- `columns`: Lista delle colonne da estrarre, nell'ordine desiderato (obbligatorio)
- `zip_name`: Nome personalizzato per il file ZIP di output (opzionale). Se non specificato, il nome sarà automaticamente generato dal nome del file CSV di input seguito da `_processed`

### 2. Aggiungi i file CSV

Posiziona i file CSV da processare nella cartella `input/`

### 3. Esegui lo script

```bash
python main.py
```

Oppure usa l'eseguibile `.exe` (disponibile negli artifact di GitHub Actions)

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

**Input CSV (`input/clienti.csv`):**
```csv
nome,cognome,numero,email
Mario,Rossi,123,mario@email.com
Luigi,Verdi,456,luigi@email.com
```

**Config (`config.json`):**
```json
{
    "columns": ["numero", "cognome"],
    "zip_name": "risultati"
}
```

**Output (`output/risultati.zip` → `clienti_processed.csv`):**
```csv
numero,cognome
123,Rossi
456,Verdi
```
