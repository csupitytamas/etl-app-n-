
def get_final_selected_columns(selected_columns, field_mappings):
    """
    Visszaadja a végleges oszlopneveket a selected_columns alapján,
    figyelembe véve a field_mappings-beli rename-t és delete-et.
    """
    final_cols = []
    for col in selected_columns:
        mapping = field_mappings.get(col, {})
        if mapping.get("delete", False):
            continue
        if mapping.get("rename", False) and mapping.get("newName"):
            final_cols.append(mapping["newName"])
        else:
            final_cols.append(col)
    return final_cols

def get_final_column_order(column_order, field_mappings):
    """
    Átfordítja a column_order nevű listát végleges oszlopnevekre (átnevezés, törlés figyelembevételével).
    """
    result = []
    for col in column_order:
        mapping = field_mappings.get(col, {})
        if mapping.get("delete", False):
            continue
        if mapping.get("rename", False) and mapping.get("newName"):
            result.append(mapping["newName"])
        else:
            result.append(col)
    return result

def resolve_final_column_name(column, field_mappings):
    mapping = field_mappings.get(column, {})
    if mapping.get("delete", False):
        return None
    if mapping.get("rename", False) and mapping.get("newName"):
        return mapping["newName"]
    return column

def field_mapping_helper(field_mappings, selected_columns=None, column_order=None):
    """
    Meghatározza, hogy a végső táblában milyen oszlopok legyenek, milyen néven és sorrendben,
    beleértve a concat-ált oszlopokat is (alapverzió: csak rename/delete!).
    """
    columns = []
    for col, props in field_mappings.items():
        if props.get("delete", False):
            continue
        if props.get("concat", {}).get("enabled", False):
            continue  # ha bővíteni akarod, ide jön a concat logika!
        if props.get("rename", False) and props.get("newName"):
            columns.append(props["newName"])
        else:
            columns.append(col)

    columns = list(dict.fromkeys(columns))  # duplikációt szűrünk

    if selected_columns:
        columns = [col for col in selected_columns if col in columns]
    if column_order:
        columns = [col for col in column_order if col in columns]

    return columns