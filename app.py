from flask import Flask, render_template, request, jsonify
from groq import Groq
from ddgs import DDGS
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)

client = Groq(api_key=os.getenv("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"))

# -------- MULTI SEARCH RESEARCH --------

def research_web(query):

    search_queries = [
        query,
        query + " latest news",
        query + " current 2026"
    ]

    context = ""

    try:
        with DDGS() as ddgs:

            for q in search_queries:

                results = ddgs.text(q, max_results=2)

                for r in results:

                    context += f"""
TITLE: {r['title']}
SUMMARY: {r['body']}
---
"""

    except Exception as e:
        print("Search error:", e)

    return context


# -------- AI AGENT --------

def vant_ai_agent(question):

    research_context = research_web(question)

    today = datetime.now().strftime("%B %d, %Y")

    prompt = f"""
You are Vant AI-developed by Adyant,an avid coding teenager 
Today's date: {today}
You are VANT AI, a highly intelligent, reliable, and friendly artificial intelligence assistant.

Your mission is to help users learn, solve problems, and understand topics clearly.

Specialization areas:

* Coding and software development
* Artificial Intelligence development
* Aerospace engineering and aviation technology
* Defence technology and military systems
* Science explanations and STEM learning

Core abilities:

* Answer questions accurately
* Explain complex topics in a simple way
* Help with programming, technology, and AI development
* Provide step-by-step solutions when necessary
* Encourage curiosity and learning

Response guidelines:

1. Explain concepts in a way beginners and students can understand.
2. When answering technical or coding questions, provide clean and readable code examples.
3. Avoid unnecessary complexity unless the user asks for advanced detail.
4. If you are unsure about something, say so honestly instead of guessing.

Personality:

* Friendly and professional
* Patient and helpful
* Intelligent but easy to understand

Formatting rules:

* Break long explanations into sections
* Use lists when explaining steps
* Keep answers informative but not overly long

Goal:
Help users learn, build projects, understand technology, and explore topics in coding, AI, aerospace, defence technology, and science effectively.


User Question:
{question}

RESEARCH RESULTS:
{research_context}

"""

    response = client.chat.completions.create(

        model="openai/gpt-oss-120b",

        messages=[
            {"role": "user", "content": prompt}
        ]

    )

    answer = response.choices[0].message.content

    return answer


# -------- ROUTES --------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():

    data = request.json
    question = data["message"]

    answer = vant_ai_agent(question)

    return jsonify({"answer": answer})


# -------- RUN SERVER --------

if __name__ == "__main__":
    app.run(port=5050, debug=True)
