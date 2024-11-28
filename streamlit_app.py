# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize you Smoothie! :cup_with_straw:")
st.write(
    'Choose the fruits you want in your custom Smoothie!'
    )

name_on_order =st.text_input('Name on Smoothie:' )
st.write('the name on your smoothie will be:', name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()

#convert the snowpark dataframe to a Pandas dataframe so we can use the LOC function
pd_df=my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop()

ingredients_list = st.multiselect('Choose upto 5 ingredients:',
                                 my_dataframe,
                                 max_selections=5)
if ingredients_list:
    
    ingredients_string = ''
    for fruits_chosen in ingredients_list:
        ingredients_string += fruits_chosen + ' '
        

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruits_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruits_chosen,' is ', search_on, '.')        
        
        st.subheader(fruits_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/"+fruits_chosen)
        sf_df=st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
    #st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
            values ('""" + ingredients_string + """','""" + name_on_order + """')"""

    #st.write(my_insert_stmt)

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        
        st.success(f"Your Smoothie is ordered! {name_on_order}",icon="✅")
