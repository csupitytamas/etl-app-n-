import json
import sys,os
from sqlalchemy.orm import Session
from src.models.etl_config_model import ETLConfig
from src.database.connection import Base
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend/src')))


# --- TRANSFORM FŐ FÜGGVÉNY ---

def transform_data(pipeline_id, **kwargs):
    """
    ETL Pipeline transzformációs lépése.
    Extractált adatok feldolgozása field mapping, oszlopválasztás, group by, és oszlopsorrend alapján.
    """
    print("\n\n[DEBUG] --- transform_data ELINDULT ---\n\n")

    ti = kwargs['ti']  # Airflow Task Instance, XCom eléréshez

    # EXTRACT fázisból származó adatok lekérése
    extracted_data = ti.xcom_pull(key='extracted_data', task_ids=f"extract_data_{pipeline_id}")
    print("[DEBUG] Extracted Data:", extracted_data[:2])  # Csak mintapéldányokat írunk ki logba

    if not extracted_data:
        raise Exception("No extracted data to transforms!")

    # Adatbázis kapcsolat (session)
    session = Session(bind=kwargs['engine'])

    # Lekérjük az ETL pipeline-hoz tartozó konfigurációt
    etl_config = session.query(ETLConfig).filter(ETLConfig.id == pipeline_id).first()
    if not etl_config:
        raise Exception(f"ETLConfig not found for pipeline_id {pipeline_id}")

    print("[DEBUG] field_mappings:", etl_config.field_mappings)
    print("[DEBUG] selected_columns:", etl_config.selected_columns)

    # --- TRANZFORMÁCIÓ LÉPÉSEK ---

    transformed_data = extracted_data

    # 1. Field Mappings (delete, rename, split, concat kezelése)
    transformed_data = apply_field_mappings(transformed_data, etl_config.field_mappings)
    print("[DEBUG] After field_mappings:", transformed_data[:2])

    # 2. Csak bizonyos oszlopok megtartása (SELECT)
    transformed_data = apply_selected_columns(transformed_data, etl_config.selected_columns)
    print("[DEBUG] After selected_columns:", transformed_data[:2])

    # 3. Group by művelet (aggregálás)
    transformed_data = apply_group_by(transformed_data, etl_config.group_by_columns)
    print("[DEBUG] After group_by:", transformed_data[:2])

    # 4. Oszlopok rendezése megadott sorrend alapján
    transformed_data = apply_column_order(transformed_data, etl_config.column_order)
    print("[DEBUG] After column_order:", transformed_data[:2])

    # Visszatesszük XCom-ba a load lépés számára
    ti.xcom_push(key='transformed_data', value=transformed_data)
    print("[DEBUG] Transformed Data Sample:", transformed_data[:2])


# --- SEGÉDFÜGGVÉNYEK A RÉSZLÉPÉSEKHEZ ---

def apply_field_mappings(data, field_mappings):
    """
    Mezők kezelése:
    - Új mezők összefűzése (concat)
    - Mezők törlése (delete)
    - Mezők átnevezése (rename)
    """
    result = []
    for row in data:
        new_row = {}

        # 1. Concat mezők létrehozása (új mezőként)
        for field, props in field_mappings.items():
            concat_cfg = props.get('concat', {})
            if concat_cfg.get('enabled'):
                with_field = concat_cfg.get('with')  # Melyik mezővel fűzzük össze
                separator = concat_cfg.get('separator', ' ')
                val1 = row.get(field, '')  # Első érték
                val2 = row.get(with_field, '')  # Második érték
                new_col = f"{field} {with_field}"  # Új mező neve (concatolt)
                new_row[new_col] = f"{val1}{separator}{val2}".strip()

        # 2. Eredeti mezők kezelése (delete, rename)
        for field, value in row.items():
            props = field_mappings.get(field, {})

            # Ha delete: true --> kihagyjuk ezt a mezőt
            if props.get('delete', False):
                continue

            # Ha rename: true --> átnevezzük
            rename = props.get('rename', False)
            new_name = props.get('newName') if rename else field

            new_row[new_name] = value

        result.append(new_row)

    return result


def apply_selected_columns(data, selected_columns):
    """
    Csak a megadott oszlopokat tartjuk meg.
    Ha nincs megadva, akkor minden oszlop megmarad.
    """
    if not selected_columns:
        return data

    result = []
    for row in data:
        selected_row = {col: row.get(col) for col in selected_columns if col in row}
        result.append(selected_row)
    return result


def apply_group_by(data, group_by_columns):
    """
    Group by megadott oszlopok alapján.
    Aggregálás: darabszám (count) hány sor esik ugyanarra a kulcsra.
    """
    if not group_by_columns:
        return data

    grouped = {}
    for row in data:
        key = tuple(row.get(col) for col in group_by_columns)  # Csoportosító kulcs
        grouped.setdefault(key, []).append(row)

    aggregated = []
    for key, rows in grouped.items():
        aggregated_row = dict(zip(group_by_columns, key))
        aggregated_row['count'] = len(rows)  # Hány sor volt ebben a csoportban
        aggregated.append(aggregated_row)

    return aggregated


def apply_column_order(data, column_order):
    """
    Oszlopok rendezése megadott sorrendben.
    Csak a megadott sorrend szerint szerepelnek az oszlopok.
    """
    if not column_order:
        return data

    result = []
    for row in data:
        ordered_row = {col: row[col] for col in column_order if col in row}
        result.append(ordered_row)

    return result