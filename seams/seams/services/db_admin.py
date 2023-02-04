import streamlit as st
from seams.postgresql_tools import db_create_users_table, db_delete_users


def main():

    st.header('`seamsdb` postgresql preconfigured actions')
        
    selected_action = st.selectbox(
        label='**Postgresql admin actions**:',
        options=['< select action >', 'create users table', 'delete users'],
    )

    if selected_action == 'create users table': db_create_users_table()
    if selected_action == 'delete users': db_delete_users()


main()