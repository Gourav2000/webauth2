from flask import *
from flask import session

import hashlib
import pyrebase
import firebase_admin
import string

import random
from firebase_admin import credentials, firestore, auth



config = {
    "apiKey": "AIzaSyBey9EgL5FDl0Fai6lavrI_gKJRqrrUfSM",
    "authDomain": "enigma-prod-305608.firebaseapp.com",
    "projectId": "enigma-prod-305608",
    "storageBucket": "enigma-prod-305608.appspot.com",
    "messagingSenderId": "41104534865",
    "appId": "1:41104534865:web:d75a198a0ad0b96aa1b770",
    "measurementId": "G-LC7SRZ3N6Y",
    "databaseURL": "https://enigma-prod-305608-default-rtdb.firebaseio.com",
    "serviceAccount": "enigma-prod-305608-firebase-adminsdk-nh0d2-23476d9ad0.json"
}

pb = pyrebase.initialize_app(config)


def IsUserNew(e_mail):
    try:
        auth.get_user_by_email(e_mail)
        return False
    
    except:
        return True



cred = credentials.Certificate(
    "enigma-prod-305608-firebase-adminsdk-nh0d2-23476d9ad0.json")
firebase_admin.initialize_app(cred)

app = Flask(__name__, template_folder="templates",
            static_folder="templates/static")
app.secret_key = '#d\xe9X\x00\xbe~Uq\xebX\xae\x81\x1fs\t\xb4\x99\xa3\x87\xe6.\xd1_'

firestoredb=firestore.client()

def writeProfileData(uid,profData):
    firestoredb.collection('UserDatabase').document(uid).update(profData)

@app.route('/')
def Main():
    if 'user' not in session:
        print(request.remote_addr)
        print(request.remote_user)
        return redirect(url_for('login'))
    
    else:
        print(request.remote_addr)
        print(request.remote_user)
        return redirect(url_for('profile'))

@app.route('/wrong', methods=['GET', 'POST'])
def wrong():
    msg=request.args['msg']
    return msg


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' not in session:
        return render_template("index.html")
    
    else:
        
        return redirect(url_for('profile'))


@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    if 'user' not in session:
        return render_template("sign_up.html")
    
    else:
        return redirect(url_for('profile'))


@app.route('/profile-signup', methods=['GET', 'POST'])
def profile_signup():
    if request.method == 'POST':
        if IsUserNew(request.form["email"]) == False:
            return 'user already present plz go to login page'

        req_data = request.form
        
        try:
            user_signup = auth.create_user(
                email=req_data['email'],
                email_verified=False,
                password=req_data['password'],
                display_name=req_data['name'],
                disabled=False)
            print('Sucessfully created new user: {0}'.format(user_signup.uid))
            print(user_signup.__dict__)
            user = pb.auth().sign_in_with_email_and_password(req_data['email'], req_data['password'])
            pb.auth().send_email_verification(user['idToken'])
            session['user']=user
            return redirect(url_for('profile'))
        
        except Exception as e:
            print('user creation failed')
            print(e)
            return redirect(url_for('wrong',msg='user creation failed'))
   
    else:
        abort(404)


@app.route('/profile-login', methods=['GET', 'POST'])
def profile_login():
    if request.method == 'POST':
        if IsUserNew(request.form["email"]) == True:
            return 'user not present plz go to signup page'

        req_data = request.form
        try:
            user = pb.auth().sign_in_with_email_and_password(req_data['email'], req_data['password'])
            print(user)
            session['user']=user
            return redirect(url_for('profile'))
        
        except Exception as e:
            print('user login failed')
            return redirect(url_for('wrong',msg='user login failed'))
    
    else:
        abort(404)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    
    if 'user' not in session:
        return redirect(url_for('login'))
    
    print(session['user']['email'])
    user_details=auth.get_user_by_email(session['user']['email'])
    
    if user_details.email_verified==False:
        return 'please verrify ur email before continuing'
    
    elif user_details.email_verified==True:
        return render_template("profile.html",user_main=session)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    del session['user']
    return redirect(url_for('Main'))

@app.route('/logincheck', methods=['GET', 'POST'])
def logincheck():
    if 'user' not in session:
        return {'login':'False'}
    else:
        newTokens=pb.auth().refresh(session['user']['refreshToken'])
        session['user']['idToken']=newTokens['idToken']
        session['user']['refreshToken']=newTokens['refreshToken']
        return {'login':'True','idToken':session['user']['idToken']}

@app.route('/profiledata', methods=['GET', 'POST'])
def profiledata():
    if request.method=='POST':
        req_data=request.json
        print(type(req_data['main']))
        ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 10))
        strrr=str(ran)+str(req_data['main'])
        keey=hashlib.md5(strrr.encode()).hexdigest()
        data_to_send={keey:req_data}
        token=req_data['session']['idToken']
        try:
            print(session['user'])
            if auth.verify_id_token(token)['uid']==session['user']['localId']:
                print('worked')
                writeProfileData(session['user']['localId'],data_to_send)

                #send post request to model server
                #get first line
                return 'sucess'
        except Exception as e:
            print('wtf')
            print(e)
            return 'failed'
    else:
        return 'wrong call'

if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=True, port=5000)
