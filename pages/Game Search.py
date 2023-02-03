import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import streamlit as st
import json

st.set_page_config(
    page_title='Meet Your Next Game',
    layout="wide"
)
#Connect to firestore database (using streamlit's secreat keeping system)
key_dict = json.loads(st.secrets["textkey"])
cred = credentials.Certificate(key_dict)


def mapPartition(requests):
    ref = db.reference('/user/Susan/steam_csv')
    Data = ref.get()
    ans = []
    i = 1
    refer = {}
    a = {}
    c,p,g=[],[],[]
    def check_request(requests, i):
        
        if i > len(Data):
            return
        
        ref = db.reference(Data['p'+f'{i}'])
        partition = ref.get()
       
        ls =[]
        for item in partition:
            #cate
            ls = item['categories']
            if requests[0] != []:
                count = 0
                for j in requests[0]:
                    if j in ls:
                        count+=1
                    else:
                        break
                if count == len(requests[0]):
                    c.append(item['appid'])
                    refer[item['appid']] = item
            
            #platform
            ls = item['platforms']
            if requests[1] != []:
                count = 0
                for j in requests[1]:
                    if j in ls:
                        count+=1
                    else:
                        break
                if count == len(requests[1]):
                    p.append(item['appid'])
                    refer[item['appid']] = item
            
            #genre
            ls = item['genres']
            if requests[2] != []:
                count = 0
                for j in requests[2]:
                    if j in ls:
                        count+=1
                    else:
                        break
                if count == len(requests[2]):
                    g.append(item['appid'])
                    refer[item['appid']] = item
            
        res = [i for i in c if i in g]
        res = [i for i in res if i in p]
        
        ans.append(res)
        
        
        def reduce(ans):
            if len(ans[-1])<15:
                check_request(requests, i+1)
            else:
                for k in refer.keys():
                    if k in ans[-1][:15]:
                        a[k] = refer[k]
                return a

                
        return reduce(ans)
            
    check_request(requests,i)
    return a
    

def get_all(a):
       
    def check_range(appid):
        
        if appid not in range(0,1069460):
            return 
        if appid in range(0,341940):
            ref = db.reference('/user/Susan/steam_media_data_csv/p1')
            
        elif appid in range(341940,468920):
            ref = db.reference('/user/Susan/steam_media_data_csv/p2')
        elif appid in range(468920,601940):
            ref = db.reference('/user/Susan/steam_media_data_csv/p3')
        elif appid in range(601940,737600):
            ref = db.reference('/user/Susan/steam_media_data_csv/p4')
        elif appid in range(737600,868980):
            ref = db.reference('/user/Susan/steam_media_data_csv/p5')
        elif appid in range(868980,1069460):
            ref = db.reference('/user/Susan/steam_media_data_csv/p6')
        return ref.get()

    if a:
        for i in a.keys():
            # print(i)
            ref = check_range(i)
            if ref:
                kref = db.reference(ref)
                link = kref.order_by_child("steam_appid").equal_to(i).get()
                v = list(link.values())
                
                a[i]['url'] = v[0]['header_image']

    return a


st.title("🎮 Let's Try Some NEW GAMES!!!")
platforms = st.multiselect(
    'Choose Your Platform(s), default is Windows',
    options=['windows','mac','linux'],default=['windows'],key='platform')

all_genre = ['Accounting', 'Action', 'Adventure', 'Animation & Modeling', 'Audio Production', 'Casual', 'Design & Illustration', 'Documentary', 'Early Access', 'Education', 'Free to Play', 'Game Development', 'Gore', 'Indie', 'Massively Multiplayer', 'Nudity', 'Photo Editing', 'RPG', 'Racing', 'Sexual Content', 'Simulation', 'Software Training', 'Sports', 'Strategy', 'Tutorial', 'Utilities', 'Video Production', 'Violent', 'Web Publishing']

genre = st.multiselect(
    'Choose Your genre(s), defualt is Action',
    options=all_genre,default=['Action'], key='genre')

all_catagories = ['Captions available', 'Co-op', 'Commentary available', 'Cross-Platform Multiplayer', 'Full controller support', 'In-App Purchases', 'Includes Source SDK', 'Includes level editor', 'Local Co-op', 'Local Multi-Player', 'MMO', 'Mods', 'Mods (require HL2)', 'Multi-player', 'Online Co-op', 'Online Multi-Player', 'Partial Controller Support', 'Shared/Split Screen', 'Single-player', 'Stats', 'Steam Achievements', 'Steam Cloud', 'Steam Leaderboards', 'Steam Trading Cards', 'Steam Turn Notifications', 'Steam Workshop', 'SteamVR Collectibles', 'VR Support', 'Valve Anti-Cheat enabled']
catagories = st.multiselect(
    'Choose Your catagory(s), defualt is Single-player',
    options=all_catagories,default=['Single-player'], key='catagory')

request =[catagories, platforms, genre]

st.header("Below are the games that we recommended to you with highest positive ratings! (Maximum 15 games)")

temp_result = mapPartition(request)
selected_games = get_all(temp_result)

if temp_result == {}:
    st.write('No Games Found, Try other combinations')
else:
    for key in selected_games:
        with st.expander(selected_games[key]['name']):
            st.image(selected_games[key]['url'])
            st.write('Support Platforms:',selected_games[key]['platforms'])
            st.write('Release Date:',selected_games[key]['release_date'])
            st.write('Developer:',selected_games[key]['developer'])
            st.write('Publisher:',selected_games[key]['publisher'])
            st.write('Genre:',selected_games[key]['genres'])
            st.write('Categories:',selected_games[key]['categories'])
            st.write('Positive Ratings:',selected_games[key]['positive_ratings'])
            st.write('Negative Ratings:',selected_games[key]['negative_ratings'])
            st.write('Owners:',selected_games[key]['owners'])
            st.write('Price:',selected_games[key]['price'])

st.subheader('How Search Results are Obtained')
st.write("""
1. requests: 
After choosing your targeted genres, categories, and platform, the platform would generate requests that pass through each partition of the datasets.  

2. mapPartition function:
As the dataset is partitioned based on the descending positive rating with 2000 records per set, the mapPartition function would search from p1 to the end based on the requests. If the system finds a match game, it would store the info in the reference dictionary (key: appid, value: all info). 

3. reduce for analytics:
The reduce function inside is used to check whether the records reach the top 15. If we haven't got enough records, it would automatically check the next partition of the dataset; if we get enough data from the dataset and have larger than 15 results, then we would reduce to only the first(top)15 records. """)
