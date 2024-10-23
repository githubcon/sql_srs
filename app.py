# pylint: disable = missing-module-docstring
# import io
# import ast
# from encodings.mac_greek import encoding_table

import os
import logging

from datetime import date, timedelta
import subprocess
import duckdb
import pandas as pd
import numpy as np
import streamlit as st


if "data" not in os.listdir():
    print("creating folder data")
    logging.error(os.listdir())
    logging.error("creating folder data")
    os.mkdir("data")

if "exercises_sql_tables.duckdb" not in os.listdir("data"):
    # with open("init_db.py", encoding="utf-8") as f:
    #     code = f.read()
    #     exec(code, {"__name__": "__main__"})  # Limiter le contexte d'exécution
    subprocess.run(["python", "init_db.py"], check=True)

con = duckdb.connect(database="data/exercises_sql_tables.duckdb", read_only=False)


ANSWER_STR = """
select * from beverages 
cross join food_items"""


def check_users_solution(user_query: str, correct_solution_df: pd.DataFrame) -> None:
    """
    1: checking columns
    2: checking the value
    :param user_query: a string containing the query inserted by the user
    """
    result = con.execute(user_query).df()
    st.dataframe(result)

    try:
        result = result[correct_solution_df.columns]
        st.dataframe(result.compare(correct_solution_df))
        if result.compare(correct_solution_df).shape == (0, 0):
            st.write("Correct !")
            st.balloons()
    except KeyError:
        st.write("Some columns are missing")
    n_lines_difference = result.shape[0] - correct_solution_df.shape[0]
    if n_lines_difference != 0:
        st.write(
            f"result has a {n_lines_difference} lines difference with "
            f"the solution_df"
        )


with st.sidebar:
    available_themes_df = con.execute("SELECT DISTINCT theme FROM memory_state").df()
    theme = st.selectbox(
        "What would you like to review ?",
        available_themes_df["theme"].unique(),
        index=None,
        placeholder="Select a theme...",
    )
    if theme:
        st.write(f"You selected {theme}")
        SELECT_EXERCISE_QUERY = f"SELECT * FROM memory_state WHERE theme = '{theme}'"
    else:
        SELECT_EXERCISE_QUERY = f"SELECT * FROM memory_state"

    # Récupérer les exercices correspondant au thème sélectionné
    exercices = (
        con.execute(f"select * from memory_state where theme = '{theme}'")
        .df()
        .sort_values("last_reviewed")
        .reset_index(drop=True)
    )

    solution_df = pd.DataFrame()  # Initialisation à un DataFrame vide
    # Vérifier si le DataFrame n'est pas vide avant d'accéder aux données
    if not exercices.empty:
        st.write(exercices)

        # Récupérer le nom de l'exercice
        exercise_name = exercices.loc[0, "exercise_name"]

        # Chemin du fichier SQL
        FILE_PATH = f"answers/{exercise_name}.sql"

        # Vérifier si le fichier existe
        if os.path.exists(FILE_PATH):
            # Lire et exécuter le fichier SQL si trouvé
            with open(FILE_PATH, "r", encoding="utf-8") as f:
                ANSWER = f.read()
            solution_df = con.execute(ANSWER).df()
        else:
            # Message d'erreur si le fichier est introuvable
            st.error(f"File not found: {FILE_PATH}")
            ANSWER = None

    else:
        st.write("No exercises found for this theme.")
        ANSWER = None

# Champ de texte pour entrer une requête SQL
st.header("Enter your code:")
form = st.form("my_form")
query = form.text_area(label="votre code SQL ici", key="user_input")
form.form_submit_button("Submit")


if query and not solution_df.empty:
    check_users_solution(query, solution_df)
else:
    st.error("Solution DataFrame not found.")


for n_days in [2, 7, 21]:
    if st.button(f"Revoir dans {n_days} jours"):
        next_review = date.today() + timedelta(days=n_days)
        con.execute(
            f"UPDATE memory_state SET last_reviewed = '{next_review}' \
             WHERE exercise_name = '{exercise_name}'"
        )

        st.rerun()

if st.button("Reset"):
    con.execute("UPDATE memory_state SET last_reviewed = '1970-01-01'")
    st.rerun()

tab2, tab3 = st.tabs(["Tables", "Solution"])
with tab2:
    if not exercices.empty:
        try:
            # Vérifier que l'index existe avant d'y accéder
            # exercice_tables = ast.literal_eval(exercices.loc[0, "tables"])
            # Utiliser directement la valeur sans passer par ast.literal_eval
            exercice_tables = exercices.loc[0, "tables"]

            # Si exercice_tables est un tableau numpy ou une liste
            if isinstance(exercice_tables, (list, pd.Series, np.ndarray)):
                # Afficher chaque table
                for table in exercice_tables:
                    st.write(f"table: {table}")
                    df_table = con.execute(f"select * from {table}").df()
                    st.dataframe(df_table)

            else:
                st.write(f"Unexpected format for tables: {exercice_tables}")

        except KeyError:
            st.write("The 'tables' column or index 0 was not found in the data.")
    else:
        st.write("No tables found to display.")


#
with tab3:
    st.write(ANSWER)
