## Table of contents

- <b>[What is this?](#what-is-this)</b>
- <b>[Features](#features)</b>
- <b>[Security](#security)</b>
    * <b>[Application Security](#application-security)</b>
    * <b>[Data Security](#data-security)</b>
- <b>[API Documentation](#api-documentation)</b>
    - Users
        * <b>[User Signup](#user-signup)</b>
        * <b>[User Login](#user-login)</b>
        * <b>[User Token Verify](#user-token-verify)</b>
        * <b>[Connected Nodes](#connected-nodes)</b>
        * <b>[Set User FCM Token](#set-user-fcm-token)</b>
        * <b>[Connected Nodes](#connected-nodes-1)</b>
        * <b>[Update profile](#update-profile)</b>
        * <b>[Get profile](#get-profile)</b>
        * <b>[Get Notifications](#get-notifications)</b>
    - Nodes
        * <b>[Create Node](#create-node)</b>
        * <b>[Search Nodes](#search-nodes)</b>
        * <b>[Check Node Availability](#check-node-availability)</b>
        * <b>[Add Photos](#add-photos)</b>
        * <b>[Get Photos](#get-photos)</b>
        * <b>[Join Node](#join-node)</b>
        * <b>[Leave Node](#leave-node)</b>
        * <b>[Delete All Photos](#delete-all-photos)</b>
        * <b>[Accept Request](#accept-request)</b>
        * <b>[Get Node users](#get-node-users)</b>
        * <b>[Add Comments](#Add-Comments)</b>

## What is this?
This is a REST API for a Photo Sharing Network. Work as a middle server between backend and frontend application. Uses Firebase services as the backend (Firestore NoSQL database, authentication and storage). Initial project was deployed in Google AppEngine. With NoSQL database, database structure is extremly flexible. So you can customize as wish. The whole purpose of this project is to give a quick startup to your app idea. Feel free to leave a Star if you enjoy.

## Features

- Users
    * SignIn signUp using email and password
    * Token based authentication
    * Upload photos to Nodes
    * Comment for photos
    
- Nodes
    * Nodes are equal to groups in similar social networks
    * Create new Nodes
    * Search Nodes
    * Request to join Nodes
    * Leave

## Security
##### Application Security
All application logic of your app will be handled inside this Flask REST API, which you need to deploy on a server. So ability to bypass application logic is very low. 

- Here are already included basic rules


    * The unique identifer of users `id_token`, expires within 1 hour and need to retrive a new token using `refresh_token`
    * Other users can't join Nodes until the `join request` get accepted by the Node's owner
    * Restricted to
        * See photos
        * Upload photos
        * See comments
        * Add comments
        * Get connected users
    <br>
    if user hasn't join the Node

##### Data Security
Save photos in Firebase storage with public read and write access, but listing is denied. 

## API Documentation

### User Signup
Create a new user

* **URL**

  /user/signup

* **Method:**

  `POST`
  

* **Data Params**

    `email=[email]` <br>
    `password=[password]`

* **Success Response:**

  * Code: 200 <br />
    Content: <br>
    `{ operation="Create New User", status="SUCCESS", uid=uid, id_token=id_token, refresh_token=refresh_token }`
 
* **Error Response:**

  * Code: 200 <br />
    Content: `{ status : "FAILED" }`


### User Login
Login a registered user

* **URL**

  /user/login

* **Method:**

  `POST`
  

* **Data Params**

    `email=[email]` <br>
    `password=[password]`

* **Success Response:**

  * Code: 200 <br />
    Content: <br>
    `{ operation="login user", status="SUCCESS", id_token=id_token, refresh_token=refresh_token,registered=registered }`
 
* **Error Response:**

  * Code: 200 <br />
    Content: `{ status : "FAILED" }`


### User Token Verify
Verify id_token of a user

* **URL**

  /user/tokenVerify

* **Method:**

  `GET`
  

* **URL Params**

    `id_token=[id_token]` <br>
    `refresh_token=[refresh_token]`

* **Success Response:**

  * Code: 200 <br />
    Content: <br>
    `{ operation="Verify User ID_TOKEN", status="SUCCESS" }`
    or

  * Code: 200 <br />
    Content: <br>
    `{ operation="Verify User ID_TOKEN", status="RENEWED", id_token=new_id_token }`


* **Error Response:**

  * Code: 200 <br />
    Content: `{ status : "FAILED" }`

### Connected Nodes
Get user connected Nodes

* **URL**

  /user/connectedNodes

* **Method:**

  `GET`
  

* **URL Params**

    `id_token=[id_token]`

* **Success Response:**

  * Code: 200 <br />
    Content: <br>
    `{ connected_nodes = <node_list>, status="SUCCESS" }`

* **Error Response:**

  * Code: 200 <br />
    Content: `{ status : "FAILED" }`


### Set User FCM Token
Set user Firebase cloud messaging token

* **URL**

  /user/setFCMToken'

* **Method:**

  `GET`
  

* **URL Params**

    `id_token=[id_token]`<br>
    `fcm_token=[fcm_token]`


* **Success Response:**

  * Code: 200 <br />
    Content: <br>
    `{ operaion="set FCM token", status="SUCCESS" }`

* **Error Response:**

  * Code: 200 <br />
    Content: `{ status : "FAILED" }`


### Connected Nodes
Get user connected Nodes

* **URL**

  /user/connectedNodes

* **Method:**

  `GET`
  

* **URL Params**

    `id_token=[id_token]`

* **Success Response:**

  * Code: 200 <br />
    Content: <br>
    `{ connected_nodes = <node_list>, status="SUCCESS" }`

* **Error Response:**

  * Code: 200 <br />
    Content: `{ status : "FAILED" }`


### Update profile
Update user profile info

* **URL**

  /user/profileInfo/update

* **Method:**

  `GET`
  

* **URL Params**

    `id_token=[id_token]`<br>
    `full_name=[full_name]`<br>
    `profile_pic=[profile_pic]`

* **Success Response:**

  * Code: 200 <br />
    Content: <br>
    `{ operaion="Update user details", status="SUCCESS" }`

* **Error Response:**

  * Code: 200 <br />
    Content: `{ status : "FAILED" }`



### Get profile 
Get user profile info

* **URL**

  /user/profileInfo/get

* **Method:**

  `GET`
  

* **URL Params**

    `id_token=[id_token]`<br>

* **Success Response:**

  * Code: 200 <br />
    Content: <br>
    `{ status="SUCCESS", operation="Get user details" full_name=full_name, profile_pic=profile_pic }`

* **Error Response:**

  * Code: 200 <br />
    Content: `{ status : "FAILED" }`


### Get Notifications
Get avaiable notifications for user

* **URL**

  /user/getNotifications

* **Method:**

  `GET`
  

* **URL Params**

    `id_token=[id_token]`<br>

* **Success Response:**

  * Code: 200 <br />
    Content: <br>
    `{ stauts="SUCCESS", operation="get user notifications", notificaions=<notificaions> }`

* **Error Response:**

  * Code: 200 <br />
    Content: `{ status : "FAILED" }`




### Create Node
Create a new Node

* **URL**

  /node/create

* **Method:**

  `GET`
  

* **URL Params**

    `id_token=[id_token]`<br>
    `node_name=[node_name]`<br>
    `profile_pic=[profile_pic]`<br>
    `node_description=[node_description]`<br>   

* **Success Response:**

  * Code: 200 <br />
    Content: <br>
    `{ stauts="SUCCESS", operation="Create a new node" }`

* **Error Response:**

  * Code: 200 <br />
    Content: `{ status : "FAILED" }`    


### Search Nodes
Search Nodes

* **URL**

  /node/search

* **Method:**

  `GET`
  

* **URL Params**

    `search_name=[search_name]`<br>

* **Success Response:**

  * Code: 200 <br />
    Content: <br>
    `{ matched_names=<[node_names]>, operation="search nodes",status="SUCCESS" }`

* **Error Response:**

  * Code: 200 <br />
    Content: `{ status : "FAILED" }`    


### Check Node Availability
Check the availability of a Node

* **URL**

  /node/checkAvailability

* **Method:**

  `GET`
  

* **URL Params**

    `search_name=[search_name]`<br>

* **Success Response:**

  * Code: 200 <br />
    Content: <br>
    `{ is_available=<is_available>, operation="search nodes",status="SUCCESS" }`

* **Error Response:**

  * Code: 200 <br />
    Content: `{ status : "FAILED" }`   


### Add Photos
Add photos to a Node

* **URL**

  /node/addPosts

* **Method:**

  `GET`
  

* **URL Params**

    `id_token=[id_token]`<br>
    `node_name=[node_name]`<br>

* **Success Response:**

  * Code: 200 <br />
    Content: <br>
    `{ operation="Add posts to a node", status="SUCCESS" }`

* **Error Response:**

  * Code: 200 <br />
    Content: `{ status : "FAILED" }` or

  * Code: 200 <br />
    Content: <br>
    `{ operation="Add posts to a node", status="FAILED", reason="unauthorized access" }`


### Get Photos
Get photos of a Node

* **URL**

  /node/getPosts

* **Method:**

  `GET`
  

* **URL Params**

    `id_token=[id_token]`<br>
    `node_name=[node_name]`<br>

* **Success Response:**

  * Code: 200 <br />
    Content: <br>
    `{ posts=<[node_posts]>, status="SUCCESS" }`

* **Error Response:**

  * Code: 200 <br />
    Content: `{ status : "FAILED" }` or

  * Code: 200 <br />
    Content: <br>
    `{ status="FAILED", reason="unauthorized access" }`


### Join Node
Join a Node

* **URL**

  /node/join

* **Method:**

  `GET`
  

* **URL Params**

    `id_token=[id_token]`<br>
    `node_name=[node_name]`<br>

* **Success Response:**

  * Code: 200 <br />
    Content: <br>
    `{ operation="JOINED", status="SUCCESS" }`

* **Error Response:**

  * Code: 200 <br />
    Content: `{ status="FAILED", operation="Join request send",reason="ALREADY_REQUESTED" }` or

  * Code: 200 <br />
    Content: `{ status="FAILED", operation="Join request send",reason="ALREADY_JOINED" }` or
    
  * Code: 200 <br />
    Content: <br>
    `{ status="FAILED"}`


### Leave Node
Leave a Node

* **URL**

  /node/leave

* **Method:**

  `GET`
  

* **URL Params**

    `id_token=[id_token]`<br>
    `node_name=[node_name]`<br>

* **Success Response:**

  * Code: 200 <br />
    Content: <br>
    `{ operation="Leave from a node", status="SUCCESS" }`

* **Error Response:**
    
  * Code: 200 <br />
    Content: <br>
    `{ status="FAILED"}`


### Leave Node
Leave a Node

* **URL**

  /node/leave

* **Method:**

  `GET`
  

* **URL Params**

    `id_token=[id_token]`<br>
    `node_name=[node_name]`<br>

* **Success Response:**

  * Code: 200 <br />
    Content: <br>
    `{ operation="Leave from a node", status="SUCCESS" }`

* **Error Response:**
    
  * Code: 200 <br />
    Content: <br>
    `{ status="FAILED"}`


### Delete All Photos
A user deletes all photos of a Node

* **URL**

  /node/deleteAllPosts

* **Method:**

  `GET`
  

* **URL Params**

    `id_token=[id_token]`<br>
    `node_name=[node_name]`<br>

* **Success Response:**

  * Code: 200 <br />
    Content: <br>
    `{ status="SUCCESS" }`

* **Error Response:**
    
  * Code: 200 <br />
    Content: <br>
    `{ status="FAILED"}` or 

  * Code: 200 <br />
    Content: <br>
    `{ status="FAILED", reason="unauthorized access"}` 


### Accept Request
Accept join request from a user

* **URL**

  /node/acceptRequest

* **Method:**

  `GET`
  

* **URL Params**

    `id_token=[id_token]`<br>
    `request_id=[request_id]`<br>
    `response=[response]`

* **Success Response:**

  * Code: 200 <br />
    Content: <br>
    `{ operation="accept user join request", status="SUCCESS" }` or 

  * Code: 200 <br />
    Content: <br>
    `{ operation="ignore join request", status="SUCCESS" }` or 


* **Error Response:**
    
  * Code: 200 <br />
    Content: <br>
    `{ status="FAILED"}` or 


### Get Node users
Get connected user details from a Node

* **URL**

  /node/getUsers

* **Method:**

  `GET`
  

* **URL Params**

    `id_token=[id_token]`<br>
    `node_name=[node_name]`<br>
    `offset=[offset]`

* **Success Response:**

  * Code: 200 <br />
    Content: <br>
    `{ connected_users=<[connected_user_details]>, status="SUCCESS" }`

* **Error Response:**
    
  * Code: 200 <br />
    Content: <br>
    `{ status="FAILED"}`



### Add Comments
Add comment for a photo

* **URL**

  /node/post/addComment

* **Method:**

  `GET`
  

* **URL Params**

    `id_token=[id_token]`<br>
    `node_name=[node_name]`<br>
    `pic_url=[pic_url]`
    `comment=[comment]`
* **Success Response:**

  * Code: 200 <br />
    Content: <br>
    `{ status="SUCCESS" }`

* **Error Response:**
    
  * Code: 200 <br />
    Content: <br>
    `{ status="FAILED"}` or 

  * Code: 200 <br />
    Content: <br>
    `{ status="FAILED", reason="unauthorized access"}`

