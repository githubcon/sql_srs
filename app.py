# pylint: disable = missing-module-docstring
import io
import ast

# import numpy as np
import duckdb
import pandas as pd
import numpy as np
import streamlit as st


CSV = """
beverage,price
orange juice,2.5
Expresso,2
Tea,3
"""
beverages = pd.read_csv(io.StringIO(CSV))

CSV2 = """
food_item,food_price
cookie juice,2.5
chocolatine,2
muffin,3
"""
food_items = pd.read_csv(io.StringIO(CSV2))

ANSWER_STR = """
select * from beverages 
cross join food_items"""

con = duckdb.connect(database="data/exercises_sql_tables.duckdb", read_only=True)

#solution_df = duckdb.sql(ANSWER_STR).df()

with st.sidebar:
    theme = st.selectbox(
        "What would you like to review ?",
        ("cross_joins", "GroupBy", "Windows Function"),
        index=None,
        placeholder="Select a theme...",
    )
    st.write("You selected:", theme)

    # Récupérer les exercices correspondant au thème sélectionné
    exercices = con.execute(f"select * from memory_state where theme = '{theme}'").df()

    # Vérifier si le DataFrame n'est pas vide avant d'accéder aux données
    if not exercices.empty:
        st.write(exercices)
    else:
        st.write("No exercises found for this theme.")


st.header("Enter your code:")

query = st.text_area(label="votre code SQL ici", key="user_input")
if query:
    result = con.execute(query).df()
    st.dataframe(result)
#
#     if len(result.columns) != len(solution_df.columns):
#         # replace with try result = result(solution_df.columns)
#         st.write("Some columns are missing")
#
#         n_lines_difference = result.shape[0] - solution_df.shape[0]
#     try:
#         result = result[solution_df.columns]
#         st.dataframe(result.compare(solution_df))
#     except KeyError as e:
#         st.write("Some columns are missing")
#
#     n_lines_difference = result.shape[0] - solution_df.shape[0]
#     if n_lines_difference != 0:
#         st.write(
#             f"result has a {n_lines_difference} lines difference with "
#             f"the solution_df"
#         )
#
#
tab2, tab3 = st.tabs(["Tables", "Solution"])
with tab2:
    if not exercices.empty:
        try:
            # Vérifier que l'index existe avant d'y accéder
            #exercice_tables = ast.literal_eval(exercices.loc[0, "tables"])
            # Utiliser directement la valeur sans passer par ast.literal_eval
            exercice_tables = exercices.loc[0, "tables"]


            # Si exercice_tables est un tableau numpy ou une liste
            if isinstance(exercice_tables, (list, pd.Series, np.ndarray)):
                # Afficher chaque table
                for table in exercice_tables:
                    st.write(f"table: {table}")
                    # Vous pouvez afficher les DataFrames ici si nécessaire
                    st.dataframe(beverages)

            else:
                st.write(f"Unexpected format for tables: {exercice_tables}")

        except KeyError:
            st.write("The 'tables' column or index 0 was not found in the data.")
    else:
        st.write("No tables found to display.")


#
with tab3:
    exercise_name = exercices.loc[0, "exercise_name"]
    with open(f"answers/{exercise_name}.sql","r") as f:
        answer = f.read()
    st.write(answer)
