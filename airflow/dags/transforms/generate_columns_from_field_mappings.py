def generate_columns_from_field_mappings(field_mappings, selected_columns=None, column_order=None):
    """
    Generálja az SQL tábla oszlopneveit:
    - Field Mappings szabályok figyelembe vételével
    - Selected Columns szűréssel
    - Column Order sorrenddel
    """
    columns = []
    concat_columns = {}

    # Először a concat mezők összeállítása
    for field, props in field_mappings.items():
        if props.get('concat', {}).get('enabled', False):
            with_field = props['concat'].get('with', '')
            concat_col = f"{field} {with_field}".strip()
            concat_columns[field] = concat_col  # Eltároljuk melyik field concatolt neve mi lesz

    for field, props in field_mappings.items():
        if props.get('delete', False):
            continue  # Delete = nem rakjuk bele

        # Ha rename van
        if props.get('rename', False) and props.get('newName'):
            final_field = props['newName']
        # Ha concatban van
        elif field in concat_columns:
            final_field = concat_columns[field]
        else:
            final_field = field

        columns.append(final_field)

    # --- Szűrés selected_columns szerint ---
    if selected_columns:
        columns = [col for col in columns if col in selected_columns]

    # --- Rendezés column_order szerint ---
    if column_order:
        ordered_columns = []
        for col in column_order:
            if col in columns:
                ordered_columns.append(col)
        columns = ordered_columns  # Csak a helyes sorrendben

    return columns