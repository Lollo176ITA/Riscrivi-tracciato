#!/usr/bin/env python3
"""
CSV Column Rewriter
Riordina e filtra le colonne dei file CSV secondo la configurazione.
Gestisce la conversione di date (AAAAMMGG) e numeri (senza separatori).
Applica trasformazioni speciali (estrazione CF/PIVA, cognome/nome, etc).
"""

import os
import json
import csv
import zipfile
import time
import re
from pathlib import Path
from datetime import datetime


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


def convert_date(value: str) -> str:
    """
    Converte una data in formato AAAAMMGG.
    Supporta vari formati di input: DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD, DD.MM.YYYY
    """
    if not value or value.strip() == "":
        return ""
    
    value = value.strip()
    
    # Se è già in formato AAAAMMGG (8 cifre)
    if re.match(r'^\d{8}$', value):
        return value
    
    # Prova diversi formati di data
    date_formats = [
        "%d/%m/%Y",      # DD/MM/YYYY
        "%d-%m-%Y",      # DD-MM-YYYY
        "%Y-%m-%d",      # YYYY-MM-DD
        "%d.%m.%Y",      # DD.MM.YYYY
        "%Y/%m/%d",      # YYYY/MM/DD
        "%d/%m/%y",      # DD/MM/YY
        "%d-%m-%y",      # DD-MM-YY
        "%Y-%m-%d %H:%M:%S",  # YYYY-MM-DD HH:MM:SS
        "%d/%m/%Y %H:%M:%S",  # DD/MM/YYYY HH:MM:SS
    ]
    
    for fmt in date_formats:
        try:
            dt = datetime.strptime(value, fmt)
            return dt.strftime("%Y%m%d")
        except ValueError:
            continue
    
    # Se non riesce a convertire, ritorna il valore originale
    return value


def convert_number(value: str) -> str:
    """
    Converte un numero rimuovendo separatori decimali e delle migliaia.
    Es: 45,34 -> 4534, 1.234,56 -> 123456, 100,00 -> 10000
    """
    if not value or value.strip() == "":
        return ""
    
    value = value.strip()
    
    # Rimuove tutti i caratteri non numerici (punti, virgole, spazi)
    result = re.sub(r'[^\d]', '', value)
    
    return result


def is_codice_fiscale(value: str) -> bool:
    """Verifica se il valore è un codice fiscale (16 caratteri alfanumerici)."""
    if not value:
        return False
    value = value.strip().upper()
    # CF: 16 caratteri, con lettere e numeri in posizioni specifiche
    if len(value) == 16 and re.match(r'^[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]$', value):
        return True
    return False


def is_partita_iva(value: str) -> bool:
    """Verifica se il valore è una partita IVA (11 cifre)."""
    if not value:
        return False
    value = value.strip()
    # PIVA: 11 cifre numeriche
    if len(value) == 11 and value.isdigit():
        return True
    return False


def apply_transform(value: str, transform: str, row: dict, tipo_persona_col: str = None) -> str:
    """
    Applica una trasformazione speciale al valore.
    
    Args:
        value: Valore da trasformare
        transform: Tipo di trasformazione
        row: Riga completa (per accedere ad altri campi)
        tipo_persona_col: Valore della colonna tipo persona (F/G)
    
    Returns:
        Valore trasformato
    """
    if not transform:
        return value
    
    # Determina il tipo persona dalla riga
    tipo_persona_value = row.get("codESoggPagIdUnivPagTipoIdUnivocoE", "").strip().upper()
    is_giuridica = tipo_persona_value == "G"
    
    if transform == "extract_belfiore":
        # Estrae la PRIMA sequenza di esattamente 4 caratteri tra underscore
        # Es: "_c_Ciaa_aa_bbb_" -> "Ciaa" (unica con 4 caratteri)
        # Es: "FLUSSO_H501_2025" -> "H501"
        if value:
            parts = value.split("_")
            for part in parts:
                if len(part) == 4:
                    return part
        return ""
    
    elif transform == "tipo_persona":
        # Converte F->1, G->2
        if value:
            v = value.strip().upper()
            if v == "F":
                return "1"
            elif v == "G":
                return "2"
        return ""
    
    elif transform == "extract_cf":
        # Estrae il codice fiscale solo se è persona fisica (F)
        if value and not is_giuridica:
            if is_codice_fiscale(value):
                return value.strip().upper()
        return ""
    
    elif transform == "extract_piva":
        # Estrae la partita IVA solo se è persona giuridica (G)
        if value and is_giuridica:
            if is_partita_iva(value):
                return value.strip()
        return ""
    
    elif transform == "extract_ragione_sociale":
        # Ragione sociale solo se è persona giuridica (PIVA)
        if value and is_giuridica:
            return value.strip()
        return ""
    
    elif transform == "extract_cognome":
        # Cognome: se più di 2 parole, prende le ultime 2; altrimenti l'ultima
        # Solo se persona fisica
        if value and not is_giuridica:
            parts = value.strip().split()
            if len(parts) > 2:
                return " ".join(parts[-2:])  # Ultime 2 parole = cognome
            elif parts:
                return parts[-1]  # Solo ultima parola = cognome
        return ""
    
    elif transform == "extract_nome":
        # Nome: se più di 2 parole, tutto tranne le ultime 2; altrimenti tutto tranne l'ultima
        # Solo se persona fisica
        if value and not is_giuridica:
            parts = value.strip().split()
            if len(parts) > 2:
                return " ".join(parts[:-2])  # Tutto tranne le ultime 2 = nome
            elif len(parts) > 1:
                return " ".join(parts[:-1])  # Tutto tranne l'ultima = nome
        return ""
    
    return value


def format_value(value: str, col_type: str, col_dim: int) -> str:
    """
    Formatta il valore secondo il tipo e la dimensione massima.
    """
    if not value:
        return ""
    
    value = str(value).strip()
    
    if col_type == "data":
        value = convert_date(value)
    
    elif col_type == "numerico":
        value = convert_number(value)
    
    elif col_type == "booleano":
        value = value.strip().lower()
        if value in ["1", "true", "si", "sì", "s", "yes", "y"]:
            value = "1"
        elif value in ["0", "false", "no", "n"]:
            value = "0"
        else:
            value = value[:1] if value else ""
    
    # Tronca se supera la dimensione massima
    if len(value) > col_dim:
        value = value[:col_dim]
    
    return value


def process_csv(input_path: Path, config: dict, output_folder: str = "output", zip_name: str = None) -> tuple:
    """
    Processa un singolo file CSV.
    """
    columns_config = config.get("columns", [])
    
    # Estrai i nomi delle colonne di OUTPUT
    column_names = [col["name"] if isinstance(col, dict) else col for col in columns_config]
    
    # Crea dizionario per metadati colonne
    column_meta = {}
    for col in columns_config:
        if isinstance(col, dict):
            column_meta[col["name"]] = {
                "type": col.get("type", "alfabetico"),
                "dim": col.get("dim", 255),
                "source": col.get("source"),
                "default": col.get("default", ""),
                "transform": col.get("transform")
            }
        else:
            column_meta[col] = {
                "type": "alfabetico", 
                "dim": 255, 
                "source": col,
                "default": "",
                "transform": None
            }
    
    rows = []
    
    # Leggi il CSV originale
    with open(input_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=';')
        original_columns = reader.fieldnames or []
        
        for row in reader:
            rows.append(row)
    
    # Processa le righe
    processed_rows = []
    progressivo = 0
    
    for row in rows:
        progressivo += 1
        new_row = {}
        
        for col_name in column_names:
            meta = column_meta.get(col_name, {"type": "alfabetico", "dim": 255, "source": None, "default": "", "transform": None})
            source_col = meta.get("source")
            default_val = meta.get("default", "")
            transform = meta.get("transform")
            
            # Gestione progressivo automatico
            if source_col == "_auto_progressivo":
                value = str(progressivo)
            elif source_col and source_col in original_columns:
                value = row.get(source_col, "")
                if not value and default_val:
                    value = default_val
            else:
                value = default_val
            
            # Applica trasformazione se presente
            if transform:
                value = apply_transform(value, transform, row)
            
            # Formatta il valore
            value = format_value(value, meta["type"], meta["dim"])
            
            new_row[col_name] = value
        
        processed_rows.append(new_row)
    
    # Crea output
    output_csv_name = input_path.stem + "_processed.csv"
    
    if zip_name:
        base_zip_name = Path(zip_name).stem
        output_zip_name = f"{base_zip_name}_{input_path.stem}.zip"
    else:
        output_zip_name = input_path.stem + "_processed.zip"
    
    output_zip_path = Path(output_folder) / output_zip_name
    
    with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        csv_content = []
        # Header senza apici
        csv_content.append(";".join(column_names))
        
        # Dati con apici doppi SOLO per la colonna CAUSALE_DOVUTO
        for row in processed_rows:
            row_values = []
            for col in column_names:
                value = str(row.get(col, ""))
                # Solo la colonna CAUSALE_DOVUTO ha le virgolette
                if col == "CAUSALE_DOVUTO":
                    # Escapa gli apici doppi raddoppiandoli (standard CSV)
                    value = value.replace('"', '""')
                    row_values.append(f'"{value}"')
                else:
                    row_values.append(value)
            csv_content.append(";".join(row_values))
        
        zf.writestr(output_csv_name, "\n".join(csv_content))
    
    return output_zip_name, len(rows), len(processed_rows)


def main():
    """Funzione principale."""
    print("=" * 60)
    print("CSV Column Rewriter")
    print("=" * 60)
    
    start_time = time.time()
    
    ensure_directories()
    
    try:
        config = load_config()
        columns_config = config.get("columns", [])
        if not columns_config:
            print("Errore: nessuna colonna specificata in config.json")
            return
        
        # Conta i tipi di colonne
        type_counts = {}
        for col in columns_config:
            if isinstance(col, dict):
                col_type = col.get("type", "alfabetico")
                type_counts[col_type] = type_counts.get(col_type, 0) + 1
        
        print(f"Colonne output: {len(columns_config)} colonne configurate")
        for t, count in type_counts.items():
            print(f"  - {t}: {count}")
        
        zip_name = config.get("zip_name")
        if zip_name:
            print(f"Nome ZIP personalizzato: {zip_name}")
    except FileNotFoundError:
        print("Errore: file config.json non trovato")
        return
    except json.JSONDecodeError as e:
        print(f"Errore nel parsing di config.json: {e}")
        return
    
    csv_files = get_csv_files()
    
    if not csv_files:
        print("\nNessun file CSV trovato nella cartella 'input'")
        print("Aggiungi i file CSV da processare nella cartella 'input'")
        elapsed_time = time.time() - start_time
        print(f"\nProcesso completato in {elapsed_time:.2f} secondi")
        return
    
    print(f"\nTrovati {len(csv_files)} file CSV da processare\n")
    
    processed_count = 0
    total_rows_in = 0
    total_rows_out = 0
    
    for csv_file in csv_files:
        print(f"Processando: {csv_file.name}")
        try:
            output_name, rows_in, rows_out = process_csv(csv_file, config, zip_name=zip_name)
            print(f"  -> Creato: {output_name}")
            print(f"     Righe: {rows_in} -> {rows_out}")
            processed_count += 1
            total_rows_in += rows_in
            total_rows_out += rows_out
        except Exception as e:
            print(f"  -> Errore: {e}")
            import traceback
            traceback.print_exc()
    
    elapsed_time = time.time() - start_time
    
    print("\n" + "=" * 60)
    print(f"Processati {processed_count}/{len(csv_files)} file")
    print(f"Totale righe: {total_rows_in} -> {total_rows_out}")
    print(f"Processo completato in {elapsed_time:.2f} secondi")
    print("=" * 60)


if __name__ == "__main__":
    main()
