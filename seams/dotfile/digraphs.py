# https://graphviz.org/doc/info/shapes.html
# https://dreampuf.github.io/GraphvizOnline/#digraph

defaults = '''
digraph {
    seams_toml -> seams_app; 
    seams_app -> initialize_seams;

    seams_toml [shape=note]
    seams_app [shape=component]
    initialize_seams [shape=box ]
}
'''

workflow = '''
digraph {
    
}
'''

photo_utils = '''
    digraph {
        read_photos

    }
'''

postgres_tools = '''
    digraph {
        init_postgres_connection
    }
'''

db_admin = """
    digraph {
        is_users_table_ready

    }
"""