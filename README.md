# CSV Column Rewriter 

Un tool Python per riordinare e filtrare le colonne dei file CSV secondo una configurazione personalizzabile. Gestisce automaticamente la conversione di date e numeri, e replica le righe in base al numero di rate.

## Funzionalità

- Legge tutti i file CSV dalla cartella `input` (separatore `;`)
- Riordina e filtra le colonne secondo il file `config.json`
- **Converte le date** in formato `AAAAMMGG` (es: `15/01/2025` → `20250115`)
- **Converte i numeri** rimuovendo separatori (es: `1.234,56` → `123456`)
- **Replica le righe** in base al numero di rate del documento
- Salva i risultati come file ZIP compressi nella cartella `output`
- Mostra il tempo di esecuzione nel terminale

## Utilizzo

### 1. Configura le colonne

Modifica il file `config.json`:

```json
{
    "columns": ["Progressivo", "Codice_Fiscale", "Data_Emissione", "Importo_Totale", ...],
    "date_columns": ["Data_Emissione", "Scadenza_Rata", ...],
    "numeric_columns": ["Importo_Totale", "Importo_Rata", ...],
    "rate_column": "Numero_Rata",
    "total_rate_column": "Rateizzazione"
}
```

- **columns**: Colonne da includere nell'output, nell'ordine desiderato
- **date_columns**: Colonne da convertire in formato `AAAAMMGG`
- **numeric_columns**: Colonne numeriche da cui rimuovere separatori (`.`, `,`)
- **rate_column**: Nome della colonna che indica il numero rata corrente
- **total_rate_column**: Nome della colonna che indica il totale delle rate

### 2. Aggiungi i file CSV

Posiziona i file CSV da processare nella cartella `input/`
(Il separatore deve essere `;`)

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
