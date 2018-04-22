def get_cmd_name_from_excmd_node(excmd_node):
    # noed.ea.cmd is empty when line jump command such as 1
    return excmd_node['ea']['cmd'].get('name', None)
