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

                results = ddgs.text(q, max_results=5)

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
You are VANT AI, a research assistant.

Today's date: {today}

You MUST answer using ONLY the research results below.

Rules:
- Do not rely on your training knowledge.
- Use only the research results provided.
- If the research does not contain the answer, say you could not find it.
- Never mention knowledge cutoff.

Formatting rules:
• Clear paragraphs
• Headings where helpful
• Bullet points if useful
• Use emojis appropriately

User Question:
{question}

RESEARCH RESULTS:
{research_context}

Using only the research results above, answer the question.
"""

    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

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