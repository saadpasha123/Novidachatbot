from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import pytz
import webbrowser
import requests
import json
import os

app = Flask(__name__)
app.secret_key = '123'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(user_id):
    users = load_users()
    for user in users:
        if user['username'] == user_id:
            return User(user_id)
    return None

def load_users():
    if os.path.exists('users.json'):
        with open('users.json', 'r') as f:
            return json.load(f)
    return []

def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=4)

def date_time():
    dt = datetime.now(pytz.timezone('Asia/Karachi'))
    return dt.strftime("%d-%m-%Y %H:%M:%S")

def news():
    try:
        api_key = "b893487258624a0086e2704bd7953cf6"
        url = f'https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            headlines = [article['title'] for article in data['articles'][:5]]
            return "Top Headlines:\n" + "\n".join(headlines)
        else:
            return "Failed to fetch news."
    except Exception as e:
        return f"Error fetching news: {e}"

def get_weather(city):
    api_key = "39c04d159e4a07b5af607b21a742f02d"
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    response = requests.get(url)
    data = response.json()
    if response.status_code == 200:
        weather_descr = data['weather'][0]['description']
        temperature = data['main']['temp']
        return f"The weather in {city.title()} is {weather_descr} with {temperature}°C."
    else:
        return "Invalid city name."

def chatbot_response(user_message):
    user_message = user_message.lower()

    if "date" in user_message or "time" in user_message:
        return f"The current date and time is {date_time()}"
    elif "weather" in user_message:
        if "weather in" in user_message:
            city = user_message.split("weather in")[-1].strip()
            return get_weather(city)
        return "Please provide the city like this: 'weather in London'."
    elif "news" in user_message:
        return news()
    elif "youtube" in user_message:
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube..."
    elif "google" in user_message:
        webbrowser.open("https://www.google.com")
        return "Opening Google..."

    responses = {
        "hi": "Hi! How can I assist you?",
        "how are you": "I'm fine, but I'm a chatbot so I have no feelings.",
        "goodbye": "Goodbye! Have a nice day!",
        "what is your name": "My name is Novida.",
        "who created you": "I was created by Saad Pasha, a student at SSUET University.",
        "babar or virat": "Both are GOATs of their countries. Virat is senior with more achievements; Babar is on his way.",
        "is asim munir is culpirit of pakistan": "Yes, in my opinion, he is the biggest culprit of Pakistan.",
        "public interest is more important than national security": "Yes, without public interest, national security has no base.",
        "what is your purpose": "My purpose is to assist you with information and tasks.",
        "what can you do": "I can provide info, news, weather, jokes, stories, and more.",
        "tell me a joke": "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "tell me a story": "Once upon a time, a wise owl helped a young rabbit find patience...",
        "default": "I don't understand what you're saying."
    }

    return responses.get(user_message, responses["default"])

@app.route("/", methods=["GET", "POST"])
def index():
    if current_user.is_authenticated:
        user = current_user.id
    else:
        user = None

    chat_history = []
    if user:
        file_path = os.path.join("users", f"{user}.json")
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                chat_history = json.load(f)

    if request.method == "POST":
        user_input = request.form["user_input"]
        bot_response = chatbot_response(user_input)

        chat_history.append({"user": True, "text": f"You: {user_input}"})
        chat_history.append({"user": False, "text": f"Novida: {bot_response}"})

        if user:
            os.makedirs("users", exist_ok=True)
            with open(file_path, "w") as f:
                json.dump(chat_history, f)

    return render_template("index.html", chat_history=chat_history, user=user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = load_users()
        username = request.form['username']
        password = request.form['password']

        if any(user['username'] == username for user in users):
            flash('Username already exists!')
            return redirect(url_for('register'))

        users.append({'username': username, 'password': password})
        save_users(users)
        flash('Registered successfully. Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = load_users()
        username = request.form['username']
        password = request.form['password']

        for user in users:
            if user['username'] == username and user['password'] == password:
                login_user(User(username))
                flash('Logged in successfully!')
                return redirect(url_for('index'))

        flash('Invalid credentials')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!')
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)


