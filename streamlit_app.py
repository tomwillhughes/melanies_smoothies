# Import python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(f":cup_with_straw: Smoothie Order App :cup_with_straw:")
st.write(
  """
  Use this app to make your smoothie order!
  """
)

name_on_order = st.text_input('Name on smoothie:')
st.write('The name on your smoothie will be', name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"),col("SEARCH_ON"))

# removed <.select(col('FRUIT_NAME'))> and replaced

#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()

# convert snowpark df to a pandas df to use loc

pd_df = my_dataframe.to_pandas()
st.dataframe(pd_df)
#st.stop()

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',

    pd_df["FRUIT_NAME"].tolist(),  
    # my_dataframe,
  
    max_selections = 5
    )

if ingredients_list:

    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
      
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    st.write(ingredients_string)

    #my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
    #                values ('""" + ingredients_string + """','"""+name_on_order+"""')"""

    my_insert_stmt = """
    INSERT INTO smoothies.public.orders
        (ingredients, name_on_order, order_filled)
    VALUES
        ('""" + ingredients_string + """',
         '""" + name_on_order + """',
         FALSE)
    """

    #st.write(my_insert_stmt)
    #st.stop()

    
    time_to_insert = st.button("Submit Order")
    if time_to_insert:
        session.sql(my_insert_stmt).collect()

        st.success('Your Smoothie is ordered', icon="✅")

    
    #if ingredients_string:
    #  session.sql(my_insert_stmt).collect()

