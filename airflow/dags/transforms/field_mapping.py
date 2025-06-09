def field_mapping_helper(field_mappings, selected_columns=None, column_order=None):
    """
    Meghatározza, hogy a végső táblában milyen oszlopok legyenek, milyen néven és sorrendben.
    """
    # 1. Csak ahol nincs delete: true
    columns = [
        col for col, props in field_mappings.items()
        if not props.get("delete", False)
    ]

    # 2. Ha van selected_columns, csak azt tartsd meg
    if selected_columns:
        columns = [col for col in selected_columns if col in columns]

    # 3. Ha van column_order, abban a sorrendben (csak az előző listán lévők!)
    if column_order:
        columns = [col for col in column_order if col in columns]

    # 4. Rename-t is figyelembe lehet venni itt!
    result = []
    for col in columns:
        props = field_mappings.get(col, {})
        if props.get("rename", False) and props.get("newName"):
            result.append(props["newName"])
        else:
            result.append(col)
    return result