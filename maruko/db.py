def make_table_name(plugin_name: str, table_name: str) -> str:
    return f'{plugin_name.lower()}_{table_name.lower()}'
