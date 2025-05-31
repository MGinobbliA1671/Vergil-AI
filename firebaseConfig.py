import pyrebase

firebase_config = {
   "apiKey": "AIzaSyBZUxN2z93UzFYqOkvifhWbNnP3aOY0YfE",
   "authDomain": "vergilbot-2274c.firebaseapp.com",
   "databaseURL": "https://vergilbot-2274c-default-rtdb.firebaseio.com",
   "projectId": "vergilbot-2274c",
   "storageBucket": "vergilbot-2274c.firebasestorage.app",
   "messagingSenderId": "268423869959",
   "appId": "1:268423869959:web:32ab60933ef81042c09ca2",
   "measurementId": "G-3578QXS9SK"
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
