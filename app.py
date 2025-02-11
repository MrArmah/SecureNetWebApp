from flask import Flask, render_template, redirect, request, jsonify, json, session
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime
import requests
import openai
import os
from dotenv import load_dotenv




## APP setup
app = Flask(__name__, static_folder='static', template_folder='templates')



#URLs for APIs


#SECURE_NETWORKS_NEWS = hSECURE_NETWORKS_NEWS = "ttps://otx.alienvault.com/api/v1/indicators/IPv4/8.8.8.8"

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NEWS_API_URL = f"https://newsapi.org/v2/everything?q=secure+networks&apiKey={NEWS_API_KEY}"
NEWS_API_URL_2 = f"https://newsapi.org/v2/everything?q=cyber+security&apiKey={NEWS_API_KEY}"



#Route for AI assistant
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_API_URL = os.getenv("MISTRAL_API_URL")
app.secret_key = os.getenv("APP_SECRET_KEY") 



@app.route("/chat", methods=["GET", "POST"])
def Chat():
    if "chat_history" not in session:
        session["chat_history"] = []  # Initialize chat history

    if request.method == "POST":
        user_input = request.form.get("message", "")

        if user_input:
            # Store user message
            session["chat_history"].append({"role": "user", "content": user_input})
            session.modified = True  # Ensure session is updated

            headers = {
                "Authorization": f"Bearer {MISTRAL_API_KEY}",
                "Content-Type": "application/json",
            }

            data = {
                "model": "mistral-small",
                "messages": [{"role": "system", "content": "You are an expert in secure networks."},
                             {"role": "user", "content": user_input}],
                "temperature": 0.5,
                "max_tokens": 500
            }

            response = requests.post(MISTRAL_API_URL, headers=headers, json=data)

            if response.status_code == 200:
                ai_response = response.json().get("choices", [{}])[0].get("message", {}).get("content", "Error getting response")

                # Store AI response
                session["chat_history"].append({"role": "ai", "content": ai_response})
                session.modified = True

    return render_template("Ai_page.html", chat_history=session["chat_history"])





def fetch_news():
    articles = []
    
   
    try:
        response = requests.get(NEWS_API_URL_2)
        if response.status_code == 200:
            articles += response.json().get("results", [])[:32] 
    except Exception as e:
        print(f"Error fetching news for cyber security : {e}")
    
  
    try:
        response = requests.get(NEWS_API_URL)
        if response.status_code == 200:
            needed_articles = 65 - len(articles)
            articles += response.json().get('articles', [])[:needed_articles] 
    except Exception as e:
        print(f"Error fetching news for secure networks : {e}")
    
    return articles


Scss(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)


@app.route("/", methods=["POST", "GET"])
def Home():
    return render_template('Home.html')
   

@app.route("/tools", methods=["GET"])
def Tools():
        db.session.expire_all()  # Refresh session
        query = request.args.get("search")
    
        if query:
            items = My_Tools.query.filter(
                (My_Tools.Name.ilike(f"%{query}%")) |
                (My_Tools.Application.ilike(f"%{query}%")) |
                (My_Tools.Description.ilike(f"%{query}%"))
            ).all()
        else:
            items = My_Tools.query.all()
    
        return render_template("Tools.html", items=items, search_query=query)

@app.route("/news", methods=["GET", "POST"])
def News():
    news_articles = fetch_news()
    return render_template('Newses.html', news=news_articles)



@app.route("/security", methods=["GET","POST"])
def Security():
    return render_template('Security.html')






#Data Class ~ Row of Data
class My_Tools(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name= db.Column(db.String(100), nullable=False)
    Description = db.Column(db.String(1056), nullable=False)
    Image = db.Column(db.String(1056), nullable = False)
    Application = db.Column(db.String(1056), nullable = False)
    Download = db.Column(db.String(1056), nullable = False)
    Visit_site = db.Column(db.String(1056), nullable = False)



    def __repr__(self) -> str:
        return f"Task {self.id}"
    



if __name__ in "__main__":
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 6005))
    app.run(host='0.0.0.0', port=port, debug=True)






















# @app.route("/chat", methods=["GET", "POST"])
# def Chat():
#     if "chat_history" not in session:
#         session["chat_history"] = []  # Initialize chat history

#     if request.method == "POST":
#         user_input = request.form.get("message", "")

#         if user_input:
#             # Send user input to the AI model
#             headers = {
#                 "Authorization": f"Bearer {MISTRAL_API_KEY}",
#                 "Content-Type": "application/json",
#             }

#             data = {
#                 "model": "mistral-small",
#                 "messages": [{"role": "system", "content": "You are an expert in secure networks."},
#                              {"role": "user", "content": user_input}],
#                 "temperature": 0.5,
#                 "max_tokens": 500
#             }

#             response = requests.post(MISTRAL_API_URL, headers=headers, json=data)

#             if response.status_code == 200:
#                 ai_response = response.json().get("choices", [{}])[0].get("message", {}).get("content", "Error getting response")
#                 session["chat_history"].append({"role": "assistant", "content": ai_response})  # Add AI response to history
#             else:
#                 ai_response = "Error: AI model is not responding."

#             # Store chat history in session
#             # session["chat_history"].append({"user": user_input, "ai": ai_response})
#             session.modified = True  # Save session changes
#             return render_template("Ai_page.html", chat_history=session["chat_history"])

#     return render_template("Ai_page.html", chat_history=session["chat_history"])

























