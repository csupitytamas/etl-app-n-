def field_mapping_helper(field_mappings, selected_columns=None, column_order=None):
    """
    Meghatározza, hogy a végső táblában milyen oszlopok legyenek, milyen néven és sorrendben,
    beleértve a concat-ált oszlopokat is.
    """
    print("FIELD_MAPPINGS:", field_mappings)
    columns = []
    '''
    seen_concat_targets = set()  # hogy ne legyen két oszlop ugyanabból a párosból
    
    for col, props in field_mappings.items():
        print(f"\n[CONCAT CHECK] {col=}, {props=}")
        concat = props.get("concat", {})
        if concat.get("enabled", False):
            with_col = concat["with"]
            print(f" -> CONCAT enabled! with_col={with_col}")
            first = props["newName"] if props.get("rename", False) and props.get("newName") else col
            with_props = field_mappings.get(with_col, {})
            second = with_props["newName"] if with_props.get("rename", False) and with_props.get("newName") else with_col
            sep = concat["separator"]
            concat_col_name = f"{first}{sep}{second}".strip()
            print(f" ---> GEN CONCAT COL: '{concat_col_name}' (first: '{first}', second: '{second}', sep: '{sep}')")
            if concat_col_name not in seen_concat_targets:
                print(f" ----> ADDING concat col: {concat_col_name}")
                columns.append(concat_col_name)
                seen_concat_targets.add(concat_col_name)
            else:
                print(f" ----> SKIP, already seen: {concat_col_name}")
    '''
    for col, props in field_mappings.items():
        print(f"\n[NORMAL COL CHECK] {col=}, {props=}")
        if props.get("delete", False):
            print(f" -> SKIP, marked for delete")
            continue
        if props.get("concat", {}).get("enabled", False):
            print(f" -> SKIP, already handled in concat")
            continue  # ezt már concat-oltuk
        if props.get("rename", False) and props.get("newName"):
            print(f" -> ADD RENAMED COL: {props['newName']}")
            columns.append(props["newName"])
        else:
            print(f" -> ADD COL: {col}")
            columns.append(col)

    columns = list(dict.fromkeys(columns))
    print(f"\n[ALL COLS BEFORE SELECTION]: {columns}")

    # selected_columns, column_order szűrés, ha kell
    if selected_columns:
        columns = [col for col in selected_columns if col in columns]
        print(f"[FILTERED BY SELECTED_COLS]: {columns}")
    if column_order:
        columns = [col for col in column_order if col in columns]
        print(f"[FILTERED BY COLUMN_ORDER]: {columns}")
    print("[FINAL COLUMN LIST]:", columns)
    print("======= FIELD_MAPPING_HELPER DEBUG END =======\n")
    return columns