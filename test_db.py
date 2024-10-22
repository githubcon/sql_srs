import duckdb

con = duckdb.connect(database="data/exercises_sql_tables.duckdb", read_only=False)
test = con.execute("select * from memory_state").df()
print(test)

