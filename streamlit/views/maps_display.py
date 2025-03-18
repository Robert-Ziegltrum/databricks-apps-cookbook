
import streamlit as st
from databricks import sql
from databricks.sdk.core import Config
import numpy as np
import pandas as pd


st.header("Geo Visualization", divider=True)
st.subheader("Read a table and display as a map")
st.write("This receipt loads a table from a delta table and displays the data on a map.")

cfg = Config()

@st.cache_resource
def get_connection(http_path):
    return sql.connect(
        server_hostname=cfg.host,
        http_path=http_path,
        credentials_provider=lambda: cfg.authenticate,
    )


def read_table(table_name, conn):
    with conn.cursor() as cursor:
        query = f"SELECT * FROM {table_name}"
        cursor.execute(query)
        return cursor.fetchall_arrow().to_pandas()

data = {
    "ID": range(1, 11),
    "Name": ["Alice", "Bob", "Charlie", "David", "Emma", "Frank", "Grace", "Hannah", "Ian", "Jack"],
    "Latitude": np.random.uniform(-90, 90, 10),  # Random latitude values
    "Longitude": np.random.uniform(-180, 180, 10)  # Random longitude values
}



tab_a, tab_b, tab_c, tab_d = st.tabs(["**Try it**","**Try it with a delta table**", "**Code snippet**", "**Requirements**"])

with tab_a:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Try It with a random sample"):
            st.map(data, latitude="Latitude", longitude="Longitude")
            st.dataframe(data)


with tab_b:
    col1, col2 = st.columns(2)
    with col1:
        http_path_input = st.text_input(
            "Enter your Databricks HTTP Path:", placeholder="/sql/1.0/warehouses/xxxxxx"
        )

        table_name = st.text_input(
            "Specify a Unity Catalog table name:", placeholder="catalog.schema.table"
        )
        st.info("For displaying a sample, please use the table samples.accuweather.forecast_daily_calendar_metric")

        if http_path_input and table_name:
            conn = get_connection(http_path_input)
            df = read_table(table_name, conn)
            
            st.dataframe(df)

            if 'latitude' in df.columns and 'longitude' in df.columns:
                df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
                df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
                df = df.dropna(subset=['latitude', 'longitude'])
                
                if not df.empty:
                    st.map(df, latitude="latitude", longitude="longitude")
            else:
                st.warning("no longitude, latitude found in the table")


table = [
    {
        "type": "Get Tables",
        "param": "Get long lat from the tables",
        "description": "Get long lat from the tables.",
        "code": """
        ```python
        def read_table(table_name, conn):
            with conn.cursor() as cursor:
                query = f"SELECT * FROM {table_name} LIMIT 1000"
                cursor.execute(query)
                return cursor.fetchall_arrow().to_pandas()
        ```
        """,
    },
    {
        "type": "Display Maps",
        "param": "Display pandas df as maü",
        "description": "Display the streamlit map",
        "code": """
        ```python
         st.map(df, latitude="latitude", longitude="longitude")


        ```
        """,
    },
]

with tab_c:
    for i, row in enumerate(table):
        with st.expander(f"**{row['type']} ({row['param']})**", expanded=(i == 0)):
            st.markdown(f"**Description**: {row['description']}")
            st.markdown(row["code"])
