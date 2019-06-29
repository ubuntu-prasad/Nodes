#--------------------------------------#
#                                      #
#                                      #
#     .    .                           #
#     \\  //  .''-.     .-.            #
#     \ \/ /.'     '-.-'   '.          #
# ~__\(    )/ __~            '.    ..~ #
# (  . \!!/    . )     .-''-.  '..~~~~ #
#  \ | (--)---| /'-..-'BP    '-..-~'   #  
#   ^^^ ''   ^^^                       #
#--------------------------------------#
# MIDDLE SERVER FOR NODES              #
# By HD Dananjaya                      #
#--------------------------------------#                               

from google.cloud import firestore
import grpc
from flask import Flask
from flask import request
from flask import jsonify
from flask import make_response

import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from firebase_admin import firestore
from firebase_admin import messaging

import requests
import random
import string
import re
from threading import Thread

# WEB_API
WEB_API_KEY = "" # firebase web API key

# secret dict
SERVER_CONFIG = {
    #
    # firebase service.json
    #
}

# Check API keys
if (len(WEB_API_KEY) == 0 or len(SERVER_CONFIG) == 0):
    print ("Incorrect WEB_API_KEY, SERVER_CONFIG")
    exit(0)

# initialized using secret json
print ("- - - app init - - - ")
cred = credentials.Certificate(SERVER_CONFIG)
firebase_admin.initialize_app(cred)

# create a firestore client
db_ref = firestore.client()

app = Flask(__name__)


#--------------------------------#
#         User Manager           #
#--------------------------------#
# /user/signUp                   #
# send_verify_email()            #
# /user/login                    #
# /user/tokenVerify              #
# retrieve_new_id_token()        #
# /user/connectedNodes           #
# /user/setFCMToken              #
# /user/profileInfo/update       #
# /user/profileInfo/get          #
#--------------------------------#
@app.route('/user/signup', methods=['POST'])
def user_signup():
    """ Sign up new users """

    try:
        email = request.form['email']
        password = request.form['password']

        # Note : firbase-admin usage removed
        url = 'https://www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser'
        headers = {'Content-Type': 'application/x-www-form-urlencoded',}
        params = {
            'key': WEB_API_KEY,
            'email': email,
            'password': password,
            'returnSecureToken': 'true'
        }
        response = requests.post(url, headers=headers, params=params)
        response.raise_for_status()
        id_token = response.json().get('idToken')
        refresh_token = response.json().get('refreshToken') 
        uid = response.json().get('localId')

        # email name for full name
        full_name = email.split("@")[0]

        # add new user to db 
        users_coll = db_ref.collection(u'users')
        status = users_coll.add({"full_name": full_name,
                                 "connected_nodes":[],
                                 "profile_pic":"camera-placeholder.png",
                                 "fcm_token": "",
                                 "connected_nodes_data": [],
                                 "requested_nodes":[],
                                 "notifications": []
                                }, uid)
        
        print ("- - -  new user added to db  - - - ")

        send_email_thread = Thread(target=send_verify_email, args=[id_token])
        send_email_thread.start()

        return jsonify(
            operation="Create New User",
            status="SUCCESS",
            uid=uid,
            id_token=id_token,
            refresh_token=refresh_token
        )

    except Exception as e:
        return jsonify(
            status="FAILED"
        )


def send_verify_email(id_token):
    """ Send verify code to  user email address """

    try:
        url = 'https://www.googleapis.com/identitytoolkit/v3/relyingparty/getOobConfirmationCode'
        headers = {'Content-Type': 'application/json',}
        params = {
            'key': WEB_API_KEY,
            'requestType' : 'VERIFY_EMAIL',
            'idToken': id_token
        }
        response = requests.post(url, headers=headers, params=params)
        response.raise_for_status()
        
    except:
        pass


@app.route('/user/login', methods=['POST'])
def user_login():
    """ Sign in / login users """

    try:
        email = request.form['email']
        password = request.form['password']

        url = 'https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword'
        headers = {'Content-Type': 'application/x-www-form-urlencoded',}
        params = {
            'key': WEB_API_KEY,
            'email': email,
            'password': password,
            'returnSecureToken': 'true'
        }
        response = requests.post(url, headers=headers, params=params)
        response.raise_for_status()
        id_token = response.json().get('idToken')
        refresh_token = response.json().get('refreshToken')
        registered = response.json().get('registered')

        return jsonify(
            operation="login user",
            status="SUCCESS",
            id_token=id_token,
            refresh_token=refresh_token,
            registered=registered
        )
    except Exception as e:
        return jsonify(
            status="FAILED",
        )


@app.route('/user/tokenVerify')
def verify_token():
    """ verify auth token for login """

    id_token = request.args.get('id_token')
    refresh_token = request.args.get('refresh_token')

    try:
        decoded_token = auth.verify_id_token(id_token)
        return jsonify(
            operation="Verify User ID_TOKEN",
            status="SUCCESS"
        )

    except Exception as e:
        if ("Token expired" in str(e)):
            try:
                new_id_token = retrieve_new_id_token(refresh_token)
            except Exception as e:
                
                return jsonify(
                    status="FAILED",
                )
            return jsonify(
                operation="Verify User ID_TOKEN",
                status="RENEWED",
                id_token=new_id_token
            )
        return jsonify(
            error=str(e),
            status="FAILED",
        )


def retrieve_new_id_token(refresh_token):
    """ Retrive new id_token using refresh token and return it """

    url = 'https://securetoken.googleapis.com/v1/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded',}
    params = {
        'key': WEB_API_KEY,
        'grant_type' : 'refresh_token',
        'refresh_token': refresh_token
    }
    response = requests.post(url, headers=headers, params=params)
    response.raise_for_status()
    return(response.json().get('id_token'))



@app.route('/user/connectedNodes')
def get_connected_nodes():
    """ get user connected nodes """

    try:
        id_token =  request.args.get('id_token')
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']

        print ("uid = " + uid)
        user_doc_ref = db_ref.collection(u'users').document(uid)
        user_details = user_doc_ref.get().to_dict()
        node_list = user_details.get('connected_nodes_data')
        
        return jsonify(
            connected_nodes = node_list
            )
    
    except Exception as e:
        return jsonify(
            error=str(e),
            status="FAILED",
        )


@app.route('/user/setFCMToken')
def set_fcm_token():
    """ Set FCM token of a user """
    
    try:
        id_token =  request.args.get('id_token')
        fcm_token =  request.args.get('fcm_token')

        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        user_doc_ref = db_ref.collection(u'users').document(uid)

        user_details = user_doc_ref.get().to_dict()
        user_details['fcm_token'] = fcm_token
        user_doc_ref.update(user_details, option=None)

        return jsonify(
            status="SUCCESS",
            operaion="set FCM token"
        )
    except:
        return jsonify(
            status="FAILED"
        )


@app.route('/user/profileInfo/update')
def update_profile_info():
    """ Update full_name, profile of a user """

    try:
        id_token =  request.args.get('id_token')
        full_name =  request.args.get('full_name')
        profile_pic =  request.args.get('profile_pic')

        # Validate full name
        if (len(full_name) == 0 or len(full_name) > 100):
            raise Exception('User Full Name is not Vaild')

        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        user_doc_ref = db_ref.collection(u'users').document(uid)

        user_details = user_doc_ref.get().to_dict()
        user_details['full_name'] = full_name
        user_details['profile_pic'] = profile_pic
        
        user_doc_ref.update(user_details, option=None)

        return jsonify(
            status="SUCCESS",
            operation="Update user details"
        )
    except:
        return jsonify(
            status="FAILED"
        )


@app.route('/user/profileInfo/get')
def get_profile_info():
    """ Get full_name, profile of a user """

    try:
        id_token =  request.args.get('id_token')

        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        user_doc_ref = db_ref.collection(u'users').document(uid)

        user_details = user_doc_ref.get().to_dict()
        full_name = user_details.get('full_name')
        profile_pic = user_details.get('profile_pic')

        return jsonify(
            status="SUCCESS",
            operation="Get user details",
            full_name=full_name,
            profile_pic=profile_pic
        )
    except:
        return jsonify(
            status="FAILED"
        )


@app.route('/user/getNotifications')
def get_notifications():
    """ Get notifications of a user """

    id_token =  request.args.get('id_token')

    decoded_token = auth.verify_id_token(id_token)
    uid = decoded_token['uid']
    user_doc_ref = db_ref.collection(u'users').document(uid)

    user_details = user_doc_ref.get().to_dict()
    notificaions = user_details.get('notifications')

    return jsonify(
        stauts="SUCCESS",
        operation="get user notifications",
        notificaions=notificaions
    )


#--------------------------------#
#         Node Manager           #
#--------------------------------#
# /node/create                   #
# /node/search                   #
# /node/checkAvailability        #
# send_push_notifications()      #
# /node/addPosts                 #
# /node/getPosts                 #
# /node/join                     #
# /node/leave                    #
# /node/memberCount              #
# /node/deleteAllPosts           #
# /node/acceptRequest            #
#--------------------------------#
@app.route('/node/create')
def create_node():
    """ Create a new Node """

    id_token =  request.args.get('id_token')
    node_name =  request.args.get('node_name')
    profile_pic =  request.args.get('profile_pic')
    node_description =  request.args.get('node_description')
    
    
    try:
        # validate node names
        if (re.match("^[A-Za-z0-9_]*$", node_name) == None or len(node_name) < 3):
            raise Exception('INVALID_NODE_NAME')

        if (profile_pic == None):
            profile_pic = "camera-placeholder.png"

        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']

        # request user must be in connected_users[]
        user_doc_ref = db_ref.collection(u'users').document(uid)
        node_coll_ref = db_ref.collection(u'nodes')

        node_coll_ref.add({"name":node_name,
                            "connected_users":[user_doc_ref],
                            "posts":[],
                            "profile_pic":profile_pic,
                            "node_description":node_description
                            }, node_name)

        # new node must be in connected_nodes[] in user
        user_details = user_doc_ref.get().to_dict()
        new_doc_ref = db_ref.collection(u'nodes').document(node_name)
        user_details.get('connected_nodes').append(new_doc_ref)

        # add details to connected_nodes_data (repeat data)
        user_details.get('connected_nodes_data').append({"name":node_name,
                                                        "profile_pic": profile_pic,
                                                        "node_description":node_description
                                                        })

        user_doc_ref.update(user_details, option=None)               

        return jsonify(
            operation="Create a new node",
            status="SUCCESS"
        )

    except:
        return jsonify(
            status="FAILED"
        )

@app.route('/node/search')
def search_node():
    """ Search for Nodes """

    try:
        search_name =  request.args.get('search_name')
        nodes_col_ref = db_ref.collection(u'nodes')

        search_query = nodes_col_ref.where(u'name', u'>=', search_name).limit(8).get()
        node_names = [{"name":i.to_dict().get('name'), "profile_pic":i.to_dict().get('profile_pic')} for i in search_query]

        return jsonify(
            matched_names=node_names,
            operation="search nodes",
            status="SUCCESS"
        )

    except:
        return jsonify(
            status="Failed"
        )


@app.route('/node/checkAvailability')
def check_availability():
    """ Check the availability for a node name"""

    try:
        is_available = False
        search_name =  request.args.get('search_name')
        nodes_col_ref = db_ref.collection(u'nodes')

        # validate node name
        if (re.match("^[A-Za-z0-9_]*$", search_name) == None or len(search_name) < 3):
            raise Exception('INVALID_NODE_NAME')

        search_query = nodes_col_ref.where(u'name', u'==', search_name).get()
        node_names = [i.to_dict().get('name') for i in search_query]

        if (len(node_names) == 0):
            is_available = True
        
        return jsonify(
            status="SUCCESS",
            operation="search for nodes",
            is_available=is_available
        )
    except Exception as e:
        return jsonify(
            reason=str(e),
            status="FAILED"
        )


 # send push notifications
def send_new_posts_notifications(node_name, user_full_name, posts_count):
    """ send push notifications to all devices in a node """

    try:
        node_doc_ref = db_ref.collection(u'nodes').document(node_name)
        node_details = node_doc_ref.get().to_dict()
        connected_users = node_details.get('connected_users')

        notification_body = "{} added {} photos".format(user_full_name, posts_count)

        fcm_tokens = [user_doc_ref.get().to_dict().get('fcm_token') for user_doc_ref in connected_users]
        for token in fcm_tokens:
            message = messaging.Message(
                android=messaging.AndroidConfig(
                    priority='normal',
                    notification=messaging.AndroidNotification(
                        title=node_name,    
                        body=notification_body,
                        icon='fcm_push_icon',
                        color='#364156'
                    ),
                ),
                token=token,
            )
            messaging.send(message)
    except:
        pass       


@app.route('/node/addPosts')
def add_posts():
    """ Add posts for a node """

    id_token =  request.args.get('id_token')
    node_name =  request.args.get('node_name')
    post_urls =  request.args.get('post_urls').split(',')

    try:
        # get users connected_nodes
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        user_doc_ref = db_ref.collection(u'users').document(uid)

        user_details = user_doc_ref.get().to_dict()
        connected_nodes = user_details.get('connected_nodes')

        # get these details to send notifications
        user_full_name = user_details.get('full_name')
        posts_count = len(post_urls)

        # get node using node_name
        node_doc_ref = db_ref.collection(u'nodes').document(node_name)

        # node should be in connected_nodes of user
        if (node_doc_ref in connected_nodes):

            node_details = node_doc_ref.get().to_dict()
            for each_post in post_urls:
                post_details_dict = {'pic_url': each_post,
                                    'posted_by': user_full_name,
                                    'comments': []
                                    }
                node_details.get('posts').append(post_details_dict)
            node_doc_ref.update(node_details, option=None)

            send_notif_thread = Thread(target=send_new_posts_notifications, args=[node_name, user_full_name, posts_count])
            send_notif_thread.start()

            return jsonify(
                operation="Add posts to a node",
                status="SUCCESS"
            )

        return jsonify(
            operation="Add posts to a node",
            status="FAILED",
            reason="unauthorized access"
        )
    except:
        return jsonify(
            operation="Add posts to a node",
            status="FAILED"
        )


@app.route('/node/getPosts')
def get_posts():
    """ Get posts of a node """

    id_token =  request.args.get('id_token')
    node_name =  request.args.get('node_name')

    try: 
        # get user connected_nodes
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        user_doc_ref = db_ref.collection(u'users').document(uid)

        user_details = user_doc_ref.get().to_dict()
        connected_nodes = user_details.get('connected_nodes')

        # get node using node_name
        node_doc_ref = db_ref.collection(u'nodes').document(node_name)

        # node should be in connected_nodes of user
        if (node_doc_ref in connected_nodes):

            node_details = node_doc_ref.get().to_dict()
            node_posts = node_details.get('posts')
            print (str(node_posts))
            # res_list = [{"post_url": i.get("pic_url"), "profile_pic": "XOX"} for i in node_posts]

            # reverse list to get recent posts first
            node_posts = node_posts[::-1]
            
            return jsonify(
                posts=node_posts
            )

        return jsonify(
            reson="unauthorized access",
            status="FAILED"
        )
    except Exception as e:
        return jsonify(
            err = str(e),
            status="FAILED"
        )


@app.route('/node/join')
def join_node():
    """ Join a user to a node """

    id_token =  request.args.get('id_token')
    node_name =  request.args.get('node_name')

    try:
        # check whether user already connected to requested node
        node_doc_ref = db_ref.collection(u'nodes').document(node_name)
            
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']

        # if user hasnt verified email then avoid beign able to join nodes
        user_recode = auth.get_user(uid)
        if (not user_recode.email_verified):
            raise Exception('EMAIL_NOT_VERIFIED')

        user_doc_ref = db_ref.collection(u'users').document(uid)

        user_details = user_doc_ref.get().to_dict()
        connected_nodes = user_details.get('connected_nodes')

        if (node_doc_ref not in connected_nodes):
            # if user is not connected to the node but
            # already requested to join
            requested_nodes = user_details.get('requested_nodes')
            if (node_doc_ref not in requested_nodes):
                # if user not joined and not requested to the node

                # if noone in the node then requesting user must be able
                # to join without requesting permissions
                node_details = node_doc_ref.get().to_dict()
                connected_users = node_details.get('connected_users')
                if (len(connected_users) == 0):
                    # add node to connected nodes
                    user_details = user_doc_ref.get().to_dict()
                    #return (str(user_details))
                    user_details.get('connected_nodes').append(node_doc_ref)
                    user_doc_ref.update(user_details, option=None)

                    # add user to connected users in nodes coll
                    node_details = node_doc_ref.get().to_dict()
                    node_details.get('connected_users').append(user_doc_ref)

                    # add details to connected_nodes_data (repeat data)
                    node_profile_pic = node_details.get('profile_pic')
                    node_description = node_details.get('node_description')
                    user_details.get('connected_nodes_data').append({"name":node_name,
                                                                    "profile_pic": node_profile_pic,
                                                                    "node_description": node_description})
                    user_doc_ref.update(user_details, option=None)
                    node_doc_ref.update(node_details, option=None)
                                          
                    return jsonify(
                        status="SUCCESS",
                        operation="JOINED"
                    )

                # append requesting node to requested_nodes
                user_details.get('requested_nodes').append(node_doc_ref)

                # need to send join request to first user in connected_users in requested node
                node_details = node_doc_ref.get().to_dict()
                connected_users = node_details.get('connected_users')
                
                node_admin_user = connected_users[0]
                node_admin_user_details = node_admin_user.get().to_dict()

                requester_full_name = user_details.get('full_name')
                requester_profile_pic = user_details.get('profile_pic')
                request_id = random.randint(0,10000)

                # need to append notification details to notification array
                notification = {"type":"JOIN_REQUEST",
                                "requester_uid":uid,
                                "node_name":node_name,
                                "requester_name":requester_full_name,
                                "request_id":request_id,
                                "profile_pic":requester_profile_pic
                                }
                node_admin_user_details.get('notifications').append(notification)

                # save changes
                node_admin_user.update(node_admin_user_details, option=None)
                user_doc_ref.update(user_details, option=None)

                token = node_admin_user_details.get('fcm_token')
                message = messaging.Message(
                    android=messaging.AndroidConfig(
                        priority='normal',
                        notification=messaging.AndroidNotification(
                            title="Join Request",    
                            body="{} sent a join request".format(requester_full_name),
                            icon='fcm_push_icon',
                            color='#364156'
                        ),
                    ),
                    token=token,
                )
                messaging.send(message)

                return jsonify(
                    status="SUCCESS",
                    operation="Join request send"
                )
            return jsonify(
                status="FAILED",
                operation="Join request send",
                reason="ALREADY_REQUESTED"
            )
        return jsonify(
            status="FAILED",
            operation="Join request send",
            reason="ALREADY_JOINED"
        )
    except Exception as e:
        return jsonify(
            error=str(e),
            status="FAILED"
        )


@app.route('/node/leave')
def leave_node():
    """ Leave a node """

    try:
        id_token =  request.args.get('id_token')
        node_name =  request.args.get('node_name')
            
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        user_doc_ref = db_ref.collection(u'users').document(uid)

        user_details = user_doc_ref.get().to_dict()
        connected_nodes = user_details.get('connected_nodes')

        # remove leaving node from connected_nodes from user doc
        node_doc_ref = db_ref.collection(u'nodes').document(node_name)
        connected_nodes.remove(node_doc_ref)

        # remove from connected_nodes_data
        connected_nodes_data = user_details.get('connected_nodes_data')
        data_to_remove = [details for details in connected_nodes_data if details.get('name') == node_name]
        connected_nodes_data.remove(data_to_remove[0])

        # remove user from connected_users in nodes
        node_details = node_doc_ref.get().to_dict()
        connected_users = node_details.get('connected_users')
        connected_users.remove(user_doc_ref)

        # updating 
        user_doc_ref.update(user_details, option=None)
        node_doc_ref.update(node_details, option=None)

        return jsonify(
            status="SUCCESS",
            operation="Leave from a node"
        )
    except:
        return jsonify(
            status="FAILED"
        )


@app.route('/node/memberCount')
def get_node_member_count():
    """ Get number of members in a node """

    try:
        id_token =  request.args.get('id_token')
        node_name =  request.args.get('node_name')

        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        user_doc_ref = db_ref.collection(u'users').document(uid)

        node_doc_ref = db_ref.collection(u'nodes').document(node_name)
        node_details = node_doc_ref.get().to_dict()
        connected_users = node_details.get('connected_users')

        if (user_doc_ref in connected_users):
            return jsonify(
                status="SUCCESS",
                member_count=len(connected_users)
            )

        return jsonify(
            status="FAILED"
        )

    except:
        return jsonify(
            status="FAILED"
        )


@app.route('/node/deleteAllPosts')
def delete_all_posts():
    """ Delete all posts in a node """

    id_token =  request.args.get('id_token')
    node_name =  request.args.get('node_name')

    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        user_doc_ref = db_ref.collection(u'users').document(uid)

        user_details = user_doc_ref.get().to_dict()
        connected_nodes = user_details.get('connected_nodes')

        node_doc_ref = db_ref.collection(u'nodes').document(node_name)

        if (node_doc_ref in connected_nodes):
            # remove posts[]
            node_details = node_doc_ref.get().to_dict()
            node_details['posts'] = []
            node_doc_ref.update(node_details, option=None)

            return jsonify(
                status="SUCCESS"
            )
        return jsonify(
            status="FAILED",
            reason="unauthorized access"
        )
        
    except:
        return jsonify(
            status="FAILED"
        )


@app.route('/node/acceptRequest')
def accept_request():
    """ Accept join request """

    id_token =  request.args.get('id_token')
    request_id =  request.args.get('request_id')
    response =  request.args.get('response')
    
    decoded_token = auth.verify_id_token(id_token)
    uid = decoded_token['uid']
    user_doc_ref = db_ref.collection(u'users').document(uid)

    user_details = user_doc_ref.get().to_dict()
    notificaions = user_details.get('notifications')

    notification_to_react_ = [i for i in notificaions if str(i.get('request_id')) == request_id]
    notification_to_react = notification_to_react_[0]

    # requester information
    requester_uid = notification_to_react.get('requester_uid')
    requested_node_name = notification_to_react.get('node_name')

    requester_user_doc_ref = db_ref.collection(u'users').document(requester_uid)
    requester_user_details = requester_user_doc_ref.get().to_dict()

    node_doc_ref = db_ref.collection(u'nodes').document(requested_node_name)

    if (response == "accept"):
        # add node to connected nodes
        requester_user_details.get('connected_nodes').append(node_doc_ref)
        requester_user_doc_ref.update(user_details, option=None)

        # add user to connected users in nodes coll
        node_details = node_doc_ref.get().to_dict()
        node_details.get('connected_users').append(requester_user_doc_ref)

        # add details to connected_nodes_data (repeat data)
        node_profile_pic = node_details.get('profile_pic')
        node_description = node_details.get('node_description')
        requester_user_details.get('connected_nodes_data').append({"name":requested_node_name,
                                                                   "profile_pic": node_profile_pic,
                                                                   "node_description": node_description})

        requester_user_details.get('requested_nodes').remove(node_doc_ref)

        node_doc_ref.update(node_details, option=None)
        requester_user_doc_ref.update(requester_user_details, option=None)

        # remove the notificaiton
        user_details.get('notifications').remove(notification_to_react)
        user_doc_ref.update(user_details, option=None)

        token = requester_user_details.get('fcm_token')
        full_name = user_details.get('full_name')
        message = messaging.Message(
            android=messaging.AndroidConfig(
                priority='normal',
                notification=messaging.AndroidNotification(
                    title="Request Accepted! - {}".format(requested_node_name),    
                    body="Your join request was accepted by {}".format(full_name),
                    icon='fcm_push_icon',
                    color='#364156'
                ),
            ),
            token=token,
        )
        messaging.send(message)

        return jsonify(
            status="SUCCESS",
            operation="accept user join request"
        )

    if (response == "notAccept"):
        # remove the notificaiton
        user_details.get('notifications').remove(notification_to_react)
        user_doc_ref.update(user_details, option=None)

        requester_user_details.get('requested_nodes').remove(node_doc_ref)
        requester_user_doc_ref.update(requester_user_details, option=None)

        token = requester_user_details.get('fcm_token')
        message = messaging.Message(
            android=messaging.AndroidConfig(
                priority='normal',
                notification=messaging.AndroidNotification(
                    title="Sorry! - {}".format(requested_node_name),    
                    body="Your request was not accepted.",
                    icon='fcm_push_icon',
                    color='#364156'
                ),
            ),
            token=token,
        )
        messaging.send(message)

        return jsonify(
            status="SUCCESS",
            operation="ignore join request"
        )


@app.route('/node/getUsers')
def get_connected_users():
    """ Get connected users of a Node """

    id_token =  request.args.get('id_token')
    node_name =  request.args.get('node_name')
    offset =  request.args.get('offset')

    try:    
        if (int(offset) < 0):
            raise Exception ('invalid offset')

        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        user_doc_ref = db_ref.collection(u'users').document(uid)

        # get Node details
        node_doc_ref = db_ref.collection(u'nodes').document(node_name)
        node_details = node_doc_ref.get().to_dict()
        # print ('----node details:' + node_details)
        connected_users = node_details.get('connected_users')

        # requesting user must be in conencted_users[]
        if (user_doc_ref not in connected_users):
            raise Exception ('unauthorized access')

        # IndexOutoftheBound will be automatically handled 
        connected_users_limited = connected_users[int(offset)-10:int(offset)]

        # refactor this with list comprehention
        connected_user_details = []
        for i in connected_users_limited:
            temp_details = i.get().to_dict()
            connected_user_details.append({'full_name':temp_details.get('full_name'), 'profile_pic':temp_details.get('profile_pic')})
    
        return jsonify(
            status="SUCCESS",
            connected_users=connected_user_details
        )

    except Exception as e:
        return jsonify(
            status="FAILED",
            error=str(e)
        )


@app.route('/node/post/addComment')
def add_post_comment():
    """ Add a comment to a post """


    id_token =  request.args.get('id_token')
    node_name =  request.args.get('node_name')
    pic_url =  request.args.get('pic_url')
    comment =  request.args.get('comment')
    
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        user_doc_ref = db_ref.collection(u'users').document(uid)
        user_details = user_doc_ref.get().to_dict()
        connected_nodes = user_details.get('connected_nodes')

        node_doc_ref = db_ref.collection(u'nodes').document(node_name)
        # check whether node is in connected_nodes
        if (node_doc_ref in connected_nodes):
            
            full_name = user_details.get('full_name')
            profile_pic = user_details.get('profile_pic')

            node_details = node_doc_ref.get().to_dict()
            posts = node_details.get('posts')
            search_post = [i for i in posts if i.get('pic_url') == pic_url][0]
            node_details.get('posts')[posts.index(search_post)].get('comments').append({
                'comment':comment,
                'profile_pic': profile_pic,
                'full_namae': full_name
            })

            node_doc_ref.update(node_details, option=None)

            return jsonify(
                status="SUCCESS"
            )
        return jsonify(
            status="FAILED",
            reason="unauthorized access"
        )
    except:
        return jsonify(
            status="FAILED"
        )


@app.after_request
def add_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    return response

if __name__ == '__main__':
    app.debug = True
    app.run()
