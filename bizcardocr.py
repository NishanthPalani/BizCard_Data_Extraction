### Below libraries were used to work on this project

# !pip install streamlit -q
# !pip install easyocr
# !pip install streamlit_option_menu
# !pip install pymysql
# !pip install pyngrok  ## this is a tunnel used to bridge the streamlit app in colab


#%%writefile app.py    ## Since i am running this in colab am writing this to a temporary file and save it incolab

import os
import streamlit as st
import pandas as pd
import numpy as np
from streamlit_option_menu import option_menu
import easyocr   ## library used to read the text from images
from PIL import Image  ## used to read the image
from pyngrok import ngrok ## is a tunnel used to bridge the streamlit app in colab
import cv2  ## used as an interface to work with images
import re
import sqlite3
conn = sqlite3.connect('test.db')  ## creating a database using sqlite
cur = conn.cursor()


## Streamlit function to configure the streamlit app
st.set_page_config(page_title= "BIZCARD data Extraction & Deletion",
                   layout= "wide")

## Below configuration is used to set the background image
page_bg_img = '''
<style>
.stApp {
background-image: url("https://dm0qx8t0i9gc9.cloudfront.net/thumbnails/video/rN0W64K4ipau8gxv/data-mining-moving-abstract-squares-background_rixg6thdml_thumbnail-1080_01.png");
background-size: cover;
}
</style>
'''

st.markdown(page_bg_img, unsafe_allow_html=True)

## creating a dict variable to access the image data and store
dict1 = {"company_name":[], "card_holder_name":[], "designation":[], "mobile_number1":[],"mobile_number2":[],
         "email_address":[], "website_URL":[], "area":[], "city":[], "state":[], "pincode":[], "image":[]}

## Below fucntion is used to read the image in binary to store it in Database
def image_load(filepath):

  with open(filepath, 'rb') as file:
    binarydata = file.read()
    dict1["image"].append(binarydata)

## Below function is fully based on Regular expression to seggregate data from images
def get_details(res):

  dict1["card_holder_name"].append(res[0].lower().title())
  dict1["designation"].append(res[1].lower().title())

  if result[len(result)-1] != "St ,":
    dict1["company_name"].append(result[len(result)-1].lower().title())
  else:
    dict1["company_name"].append(result[len(result)-2].lower().title())

  for i in res:
      if re.match("^[+0-9][0-9]*[-]",i):   ## Used to find the mobile number
          dict1["mobile_number1"].append(i)
      if re.match("^[a-zA-Z][a-zA-Z0-9-_.]*@[a-zA-Z][a-zA-Z0-9]*[.]com$",i): ## Used to find the email address
          dict1["email_address"].append(i.lower())
      if re.match("^[a-zA-Z]*[.][a-zA-Z]*[.]com$|^[a-zA-Z]*[ ][a-zA-Z]*[.]com$|^[a-zA-Z]*[.][a-zA-Z]*com$",i): ## Used to find the Website address
          if re.match("^[a-zA-Z]*[.][a-zA-Z]*[.]com$",i):
              dict1["website_URL"].append(i.lower())
          else:
              dict1["website_URL"].append('.'.join([i.lower() for i in i.split(' ')]))
      if re.findall("^[a-zA-Z][a-zA-Z].*[ ]?[0-9]{4}[0-9]$",i):   ## Used to find the State and Pincode address
          dict1["state"].append(i[0:10].lower().title())
          dict1["pincode"].append(i[10:])
      elif re.findall("^[0-9][0-9]{4}[0-9]$",i):
          dict1["pincode"].append(i)
      if re.match("^[0-9].+[ ].+[a-zA-Z][,]$|^[0-9].+[ ].+[a-zA-Z][;]$|^[0-9].+[ ].+[a-zA-Z]$",i): ## Used to find the area 
          i = re.sub(" ,",",",re.sub(", ",",",re.sub(",,",",",re.sub(";",",",i))))
          if len(i.split(',')) == 2:
              dict1["area"].append(i.split(',')[0].lower().title())
              dict1["city"].append(i.split(',')[1].lower().title())
          elif len(i.split(',')) > 2:
              dict1["area"].append(i.split(',')[0].lower().title())
              dict1["city"].append(i.split(',')[1].lower().title())
              if i.split(',')[2] != "":
                  dict1["state"].append(i.split(',')[2].lower().title())
              else:
                  if (''.join(dict1["state"])) == " ":
                      dict1["state"].append(i.split(',')[2].lower().title())
                  else:
                      continue
          else:
              dict1["area"].append(i.lower().title())
      if re.match("^[Ee].*",i):
        dict1["city"].append(i.lower().replace(",","").title())

  if (len(dict1["mobile_number1"])) == 2:         ## will split the number number if the count is more than two and spearate with each fields
      dict1["mobile_number2"].append(dict1["mobile_number1"][1])
      dict1["mobile_number1"].pop()
  else:
      dict1["mobile_number2"].append("NA")

  dict1_pd=pd.DataFrame(dict1)

## Session state variable is kind of dictionary so this will help in multicall fucntions while passing data from one process to other
  if 'key' not in st.session_state:
    st.session_state['key'] = dict1_pd
  else:
    st.session_state['key'] = dict1_pd

  st.dataframe(dict1_pd.drop(columns=['image']))


## SQL Table definition function
def sql_table_def():
  cur.execute("drop table if exists image_db")
  conn.commit()
  cur.execute('''
      create table if not exists image_db(company_name VARCHAR(50),card_holder_name VARCHAR(50) primary key,
        designation VARCHAR(50),mobile_number1 VARCHAR(50), mobile_number2 VARCHAR(50),email_address text,
        website_URL text,area VARCHAR(100),city VARCHAR(50),state VARCHAR(50), pincode int, image BLOB)
    ''')
  conn.commit()

## SQL load which is used to store the text obtained from images to a database
def sql_load(load1):

  try:
    load1.to_sql(name="image_db",con=conn,if_exists='append',index=False)
    conn.commit()
    st.success(" Successfully uploaded to Database!!! ")

    cur.execute("select * from image_db order by card_holder_name;")
    df1 = cur.fetchall()
    #st.dataframe(df1)
  except:
    st.info("Value already uploaded in to table")


## Streamlit app configurations to setup the Main screen options
selected = option_menu(None,["Home","Data Extraction zone","Data Modification zone"],
            icons=["house","cloud-upload","pencil-square"],
            menu_icon= "menu-button-wide",
            orientation= "horizontal",
            default_index=0,
            styles={"nav-link": {"font-size": "20px", "text-align": "centre", "margin": "-2px", "--hover-color": "#3AB38D"},
                    "icon":{"font-size": "20px"}, "container":{"max-width":"6000px"},
                    "nav-link-selected": {"background-color": "#3AB38D"}})

if selected == "Home":

  st.markdown(page_bg_img, unsafe_allow_html=True)
  st.markdown("## :rainbow[BIZCARD - Data Extraction and Modification]")
  st.write(" ")
  st.markdown("### :rainbow[Overview :]")
  st.markdown(""" #### This streamlit app aims to give users a friendly environment which can be used to extract the details from Business card and make modifcation if needed. Also user can delete the card info stored if they done want.""")
  st.write(" ")
  st.markdown("### :rainbow[Technologies used :]")
  st.markdown("#### - ECOCR: for reading the text from images")
  st.markdown("#### - Python, Pandas")
  st.markdown("#### - MySQL for storing data")
  st.markdown("#### - Streamlit app GUI")



if selected == "Data Extraction zone":

  page_bg_img = '''
    <style>
    .stApp {
    background-image: url("https://jooinn.com/images/big-data-analytics-and-research-dark-background.jpg");
    background-size: cover;
    }
    </style>
    '''

  st.markdown(page_bg_img, unsafe_allow_html=True)

  st.write("### :rainbow[Welcome to the Business Card Data Extraction Page ]")

  col1,col2,col3 = st.columns([3,1,3],gap="small")
  with col1:
      st.write(" ")
      ## File uploaded is a fucntion used to upload the images/files
      import_image = st.file_uploader('**Upload a business card (Image file)**', type =['png','jpg', "jpeg"], accept_multiple_files=False)
      #st.markdown('''###### :red[Supported Formats: **PNG, JPG, JPEG**, Default-Language : **English**]''')
  with col3:
      st.write(" ")
      ## Below is used to load the image in
      if import_image is not None:
          st.markdown("#### :green[Your uploaded image]")
          st.image(import_image)    ## Will load the image in streamlit app
          with open(import_image.name,'wb') as file:
            file.write(import_image.getbuffer())
          image_load(import_image.name)   ## will write the file in colab path and get the binary value of image to load to db


  if import_image is not None:
    try:
        # Create the reader object with desired languages. 'en' Represents english
        reader = easyocr.Reader(['en'], gpu=False)

    except:
        st.info("Error: easyocr module is not installed. Please install it.")

    #try:
    # Read the image file as a PIL Image object
    if isinstance(import_image, str):
        image = Image.open(import_image)
    elif isinstance(import_image, Image.Image):
        image = import_image
    else:
        image = Image.open(import_image)

    image_array = np.array(image)    ## Read the pixel of the images
    text_read = reader.readtext(image_array)  ## using the pixel Readtext helps in identifying the text in pixels

    result = []
    for text in text_read:
        result.append(text[1])  ## will get only the text and skips the pixel

    st.write(" ")
    st.write(" ")
    st.markdown("###### :green[Below shows the Extracted values from the Business Card]")
    get_details(result)


  st.write('Click the :red[**Upload to MySQL DB**] button to upload the data')
  Upload = st.button('**Upload to MySQL DB**', key='upload_button')


  if Upload:
    sql_load(st.session_state['key'])

        #except:
          #   st.info("Error: Failed to process the image. Please try again with a different image.")

if selected == "Data Modification zone":
  st.write("### :rainbow[Welcome to the Business Card Data modification page ]")

  tab1, tab2 = st.tabs(["Data Modification", "Data Deletion"])
  st.write(" ")

  with tab1:
    col1,col2 = st.columns([3,1],gap="large")

    with col1:
      st.subheader(':red[You have selected Modification option]')
      cur.execute("select card_holder_name from image_db;")
      df1 = cur.fetchall()

      card_holder_names = ["Select from below Card Holder Name to Modify"]

      for i in df1:
        i = str(i).replace("('","")
        i = str(i).replace("',)","")
        card_holder_names.append(i)

      selected = st.selectbox("You can select the Card Holder Name to Modify",card_holder_names)

      try:

        if selected:
          cur.execute(f"select * from image_db where card_holder_name = '{selected}';")
          s1 = cur.fetchall()
          s1 = pd.DataFrame(s1).T

          dict2 = {"company_name1":[], "card_holder_name1":[], "designation1":[], "mobile_number11":[],"mobile_number12":[],
                  "email_address1":[], "website_URL1":[], "area1":[], "city1":[], "state1":[], "pincode1":[],"image":[]}

          ## Will dislpay the below items in screen for user to edit
          company_name1 = st.text_input("Company name", str(s1.iloc[0].values).replace("['","").replace("']",""))
          card_holder_name1 = st.text_input("Cardholder", str(s1.iloc[1].values).replace("['","").replace("']",""))
          designation1 = st.text_input("Designation", str(s1.iloc[2].values).replace("['","").replace("']",""))
          mobile_number11 = st.text_input("Mobile number1", str(s1.iloc[3].values).replace("['","").replace("']",""))
          mobile_number12 = st.text_input("Mobile number2", str(s1.iloc[4].values).replace("['","").replace("']",""))
          email_address1 = st.text_input("Email", str(s1.iloc[5].values).replace("['","").replace("']",""))
          website_URL1 = st.text_input("Website", str(s1.iloc[6].values).replace("['","").replace("']",""))
          area1 = st.text_input("Area", str(s1.iloc[7].values).replace("['","").replace("']",""))
          city1 = st.text_input("City", str(s1.iloc[8].values).replace("['","").replace("']",""))
          state1 = st.text_input("State", str(s1.iloc[9].values).replace("['","").replace("']",""))
          pincode1 = st.text_input("Pincode", str(s1.iloc[10].values).replace("[","").replace("]",""))

          dict2_pd=pd.DataFrame(dict2)

          ## session state object to pass the values for the next call in this case it will passed when "Update button" is pressed
          if 'key1' not in st.session_state:
            st.session_state['key1'] = dict2_pd
          else:
            st.session_state['key1'] = dict2_pd


          st.write('Click the :red[**Update**] button to update the modified data')
          update = st.button('**Update**')

        ## Update query is used to update the user values by themselves
          if update:
            cur.execute(f"""UPDATE image_db SET company_name = '{company_name1}', card_holder_name = '{card_holder_name1}',
                          designation = '{designation1}', mobile_number1 = '{mobile_number11}', mobile_number2 = '{mobile_number12}',
                          email_address = '{email_address1}', website_URL = '{website_URL1}', area= '{area1}', city = '{city1}',
                          state = '{state1}', pincode = {pincode1} where card_holder_name = '{card_holder_name1}';""")
            conn.commit()
            cur.execute(f"select company_name,card_holder_name,designation,mobile_number1,mobile_number2,email_address, website_URL,area,city,state,pincode from image_db where card_holder_name = '{card_holder_name1}';")
            s2 = cur.fetchall()
            s2 = pd.DataFrame(s2, columns =["company_name","card_holder_name","designation","mobile_number1","mobile_number2","email_address","website_URL","area","city","state","pincode"])
            st.markdown(" ### :green[Below shows the after update values of Table entry]")
            st.dataframe(s2)
      except:
        st.info('Select valid value')

    with col2:
      st.write(" ")


  with tab2:
      ### Below configuration is to add the image for the Data modification tab
      page_bg_img = '''
        <style>
        .stApp {
        background-image: url("https://thumbs.dreamstime.com/z/artificial-intelligence-data-mining-machine-learning-concept-digital-blue-human-brain-dark-background-microcircuit-d-278065303.jpg");
        background-size: cover;
        }
        </style>
        '''

      st.markdown(page_bg_img, unsafe_allow_html=True)

      col1,col2 = st.columns([5,5],gap="medium")

      with col1:
        st.subheader(':red[You have selected Delete option]')
        cur.execute("select card_holder_name from image_db;")
        df3 = cur.fetchall()

        try:
          card_holder_names = ["Select from below Card Holder Name to Delete"]

          for i in df3:
            i = str(i).replace("('","")
            i = str(i).replace("',)","")
            card_holder_names.append(i)

          selected = st.selectbox("You can select Card Holder Name to Delete from the list",card_holder_names)

          if selected:
            cur.execute(f"select * from image_db where card_holder_name = '{selected}';")
            s3 = cur.fetchall()
            s3 = pd.DataFrame(s3).T

            dict3 = {"company_name2":[], "card_holder_name2":[], "designation2":[], "mobile_number21":[],"mobile_number22":[],
                    "email_address2":[], "website_URL2":[], "area2":[], "city2":[], "state2":[], "pincode2":[],"image2":[]}

            ## Below items will be displayed to user to check and delete
            st.markdown("Company name")
            company_name2 = st.code(str(s3.iloc[0].values).replace("['","").replace("']",""),language="markdown")
            st.markdown("Cardholder")
            card_holder_name2 = st.code(str(s3.iloc[1].values).replace("['","").replace("']",""),language="markdown")
            st.markdown("Designation")
            designation2 = st.code(str(s3.iloc[2].values).replace("['","").replace("']",""),language="markdown")
            st.markdown("Mobile number1")
            mobile_number21 = st.code(str(s3.iloc[3].values).replace("['","").replace("']",""),language="markdown")
            st.markdown("Mobile number2")
            mobile_number22 = st.code(str(s3.iloc[4].values).replace("['","").replace("']",""),language="markdown")
            st.markdown("Email")
            email_address2 = st.code(str(s3.iloc[5].values).replace("['","").replace("']",""),language="markdown")
            st.markdown("Website")
            website_URL2 = st.code(str(s3.iloc[6].values).replace("['","").replace("']",""),language="markdown")
            st.markdown("Area")
            area2 = st.code(str(s3.iloc[7].values).replace("['","").replace("']",""),language="markdown")
            st.markdown("City")
            city2 = st.code(str(s3.iloc[8].values).replace("['","").replace("']",""),language="markdown")
            st.markdown("State")
            state2 = st.code(str(s3.iloc[9].values).replace("['","").replace("']",""),language="markdown")
            st.markdown("Pincode")
            pincode2 = st.code(str(s3.iloc[10].values).replace("[","").replace("]",""),language="markdown")
            #image2 =str(s3.iloc[10].values).replace("[","").replace("]","")

            dict3_pd=pd.DataFrame(dict3)

            ## session state object to pass the values for the next call in this case it will passed when "Delete button" is pressed
            if 'key1' not in st.session_state:
              st.session_state['key1'] = dict3_pd
            else:
              st.session_state['key1'] = dict3_pd

            st.write('Think twice before :red[**Deleting**]')
            delete = st.button('**Delete**')

            if delete:
              cur.execute(f"""DELETE FROM image_db where card_holder_name = '{selected}';""")
              conn.commit()
              st.success("Entry :green[successfully] Deleted.")

        except:
          st.info('Select valid value')

      with col2:
        st.write(" ")
        # image2 = bytes(str(s3.iloc[11].values).replace("[","").replace("]",""),encoding='utf8')

        # with open("testtest1.png", "wb") as f:
        #   f.write(image2)

        # st.image(r"/content/testtest1.png")

        #st.image(image)
        # st.write('Think twice before :red[**Deleting**]')
        # delete = st.button('**Delete**')

        # if delete:
        #   cur.execute(f"""DELETE FROM image_db where card_holder_name = '{selected}';""")
        #   conn.commit()
        #   st.success("Entry :green[successfully] Deleted from Table.")









