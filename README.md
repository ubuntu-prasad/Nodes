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
* Save photos in Firebase storage with public read and write access, but listing is denied. 

## API

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