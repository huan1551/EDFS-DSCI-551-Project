import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import streamlit as st
import json
import pandas as pd
import math 

st.set_page_config(
    page_icon="👾",
    layout="wide",
)
#Connect to firestore database (using streamlit's secreat keeping system)
key_dict = json.loads(st.secrets["textkey"])
cred = credentials.Certificate(key_dict)

#Make sure we only initialize once our database
@st.cache
def firebase_init (cred):
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://dsci-551-finalproject-default-rtdb.firebaseio.com/'
    })
firebase_init(cred)

st.title("✨ Here is the EDFS Interface, Let's Play With Those Commands!! ✨")
st.header("Commands That You Can Give It A Try")
st.subheader('📝NOTE: After the execution of the command, please delete the command you entered. Forgot to delete the command will affect the proformace of the database')
st.subheader('mkdir | ls | cat | rm')
command = st.text_input("Enter Your Command Here then press enter", key = 'base', placeholder='mkdir /user/john || ls /user || cat /user/john/cars.csv || rm /user/john/cars.csv')
#mkdir, cat, rm
if command[:5] == 'mkdir':
    mkdir_ref = db.reference(command[6:])
    mkdir_ref.set('')
    st.success('Directory '+command[6:]+' has been created')
elif command[:2] == 'ls':
    ls = command[3:]
    ls_ref = db.reference(ls)
    whole = ls_ref.get()
    try:
        st.write(list(whole.keys()))
    except:
        st.write(whole)
elif command[:3] == 'cat':
    temp = command[4:].replace('.','_').split('/')
    st.text(temp[-1])
    cat_ref = db.reference(temp[-1])
    st.write(cat_ref.get())
elif command[:2] == 'rm':
    temp = command[3:].replace('.','_')
    part_ref = db.reference(temp)
    loc_info = part_ref.get()
    for path in loc_info:
        file_path = loc_info[path]
        rm_ref = db.reference(file_path)  
        rm_ref.delete()
    meta_ref = db.reference(temp)
    meta_ref.delete()
    st.success('Content of '+command[3:]+' are successfully removed')

#put
##command and file upload
st.subheader('put')

uploaded_file = st.file_uploader('First please upload your csv file here')
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    desc = st.checkbox("Check Here if you want the data being sorted in DESC order based on a numeric variable", key='desc')
    asc = st.checkbox("Check Here if you want the data being sorted in ASC order based on a numeric variable", key='asc')
    sorted = st.text_input("Enter exact name of the numeric variable",key = 'sort')
    if desc and sorted:
        df = df.sort_values(by=sorted, ascending=False)
    elif asc and sorted:
        df = df.sort_values(by=sorted, ascending=True)
    #Deal with partition
    put_command = st.text_input('Enter Your Command Here and press enter', key='put', placeholder='e.g. put(cars.csv, /user/john, k = 3)')
    if put_command:
        command_segment = put_command[4:-1].replace(' ','').replace('.','_').split(',')
        filename = command_segment[0]
        dir = command_segment[1]
        partition = int(command_segment[2][2:])
        nrow_per_p = math.ceil(len(df)/partition)
        i = 0
        end_row = nrow_per_p-1
        for p in range(partition):
            #First put metadata
            meta_ref = db.reference(dir+'/'+filename+'/p'+str(p+1))
            meta_ref.set('/'+filename+'/p'+str(p+1))
            p_ref = db.reference('/'+filename+'/p'+str(p+1))
            if p < (partition-1):
                df_part = df.iloc[i:end_row]
                json_data = df_part.to_dict(orient='records')
                p_ref.set(json_data)
                i += nrow_per_p-1
                end_row += nrow_per_p-1
            #if rows are not evenly divisble for # of partitions
            #just take the leftover rows for last partition
            if p == (partition-1):
                df_part = df.iloc[i:len(df)]
                json_data = df_part.to_dict(orient='records')
                p_ref.set(json_data)

st.subheader('getPartitionLocations(file, path) | readPartition(file, path, partition#)')
get_read_command = st.text_input("Enter Your Command Here",key='partition', placeholder='getPartitionLocation(cars.csv, /user/john) || readPartition(cars.csv, /user/john, 3)')
#get partition location
if get_read_command[:3] == 'get':
    content = get_read_command.split('(')[1][:-1].replace('.','_').replace(' ','').split(',')
    file = content[0]
    path = content[1]+'/'+file
    get_part_ref = db.reference(path)
    loc_info = get_part_ref.get()
    st.write(loc_info)
if get_read_command[:4] == 'read':
    content = get_read_command.split('(')[1][:-1].replace('.','_').replace(' ','').split(',')
    file = content[0]
    path = content[1]+'/'+file+'/p'+str(content[2])
    get_loc_ref = db.reference(path)
    actual_file_path = get_loc_ref.get()
    actual_file_ref = db.reference(actual_file_path)
    partition_content = actual_file_ref.get()
    st.write(partition_content)


