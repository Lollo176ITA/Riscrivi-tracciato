#!/usr/bin/env python3
"""
CSV Column Rewriter
Riordina e filtra le colonne dei file CSV secondo la configurazione.
"""

import os
import json
import csv
import zipfile
import time
from pathlib import Path


def load_config(config_path: str = "config.json") -> dict:
    """Carica la configurazione dal file JSON."""
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_directories():
    """Crea le cartelle input e output se non esistono."""
    Path("input").mkdir(exist_ok=True)
    Path("output").mkdir(exist_ok=True)


def get_csv_files(input_folder: str = "input") -> list:
    """Restituisce la lista dei file CSV nella cartella input."""
    return list(Path(input_folder).glob("*.csv"))


def process_csv(input_path: Path, columns: list, output_folder: str = "output", zip_name: str = None) -> str:
    """
    Processa un singolo file CSV:
    - Legge il file
    - Riordina/filtra le colonne secondo la configurazione
    - Salva il risultato in un file ZIP
    
    Args:
        input_path: Percorso del file CSV di input
        columns: Lista delle colonne da estrarre
        output_folder: Cartella di output
        zip_name: Nome personalizzato per il file ZIP (opzionale)
    
    Returns:
        Il nome del file ZIP creato
    """
    rows = []
    
    # Leggi il CSV originale
    with open(input_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        original_columns = reader.fieldnames
        
        # Verifica che le colonne richieste esistano
        missing_columns = [col for col in columns if col not in original_columns]
        if missing_columns:
            print(f"Attenzione: colonne mancanti in {input_path.name}: {missing_columns}")
            # Usa solo le colonne che esistono
            valid_columns = [col for col in columns if col in original_columns]
        else:
            valid_columns = columns
        
        # Leggi tutte le righe
        for row in reader:
            rows.append(row)
    
    # Crea il nuovo CSV con le colonne riordinate
    output_csv_name = input_path.stem + "_processed.csv"
    
    # Usa il nome dello ZIP dalla configurazione se fornito, altrimenti usa il nome del file
    if zip_name:
        # Se il nome personalizzato non ha estensione .zip, aggiungila
        base_zip_name = Path(zip_name).stem
        output_zip_name = f"{base_zip_name}_{input_path.stem}.zip"
    else:
        output_zip_name = input_path.stem + "_processed.zip"
    
    output_zip_path = Path(output_folder) / output_zip_name
    
    # Scrivi direttamente nel file ZIP
    with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Crea il contenuto CSV in memoria
        csv_content = []
        csv_content.append(",".join(valid_columns))
        
        for row in rows:
            csv_content.append(",".join(str(row.get(col, "")) for col in valid_columns))
        
        # Aggiungi al ZIP
        zf.writestr(output_csv_name, "\n".join(csv_content))
    
    return output_zip_name


def main():
    """Funzione principale."""
    print("=" * 50)
    print("CSV Column Rewriter")
    print("=" * 50)
    
    start_time = time.time()
    
    # Assicurati che le cartelle esistano
    ensure_directories()
    
    # Carica la configurazione
    try:
        config = load_config()
        columns = config.get("columns", [])
        if not columns:
            print("Errore: nessuna colonna specificata in config.json")
            return
        print(f"Colonne da estrarre: {columns}")
        
        # Carica il nome dello ZIP se presente
        zip_name = config.get("zip_name")
        if zip_name:
            print(f"Nome ZIP personalizzato: {zip_name}")
    except FileNotFoundError:
        print("Errore: file config.json non trovato")
        return
    except json.JSONDecodeError as e:
        print(f"Errore nel parsing di config.json: {e}")
        return
    
    # Trova i file CSV
    csv_files = get_csv_files()
    
    if not csv_files:
        print("\nNessun file CSV trovato nella cartella 'input'")
        print("   Aggiungi i file CSV da processare nella cartella 'input'")
        elapsed_time = time.time() - start_time
        print(f"\nProcesso completato in {elapsed_time:.2f} secondi")
        return
    
    print(f"\nTrovati {len(csv_files)} file CSV da processare\n")
    
    # Processa ogni file
    processed_count = 0
    for csv_file in csv_files:
        print(f"Processando: {csv_file.name}")
        try:
            output_name = process_csv(csv_file, columns, zip_name=zip_name)
            print(f"     Creato: {output_name}")
            processed_count += 1
        except Exception as e:
            print(f"     Errore: {e}")
    
    # Tempo di esecuzione
    elapsed_time = time.time() - start_time
    
    print("\n" + "=" * 50)
    print(f"Processati {processed_count}/{len(csv_files)} file")
    print(f"Processo completato in {elapsed_time:.2f} secondi")
    print("=" * 50)


if __name__ == "__main__":
    main()
