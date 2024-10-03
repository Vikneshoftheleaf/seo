from flask import Flask, render_template, request, jsonify
from get import getInfo
import os
from dotenv import load_dotenv
from groq import Groq
load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API"),
)

"""
def getAISuggest(data):
    chat_completion = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {
                        "role":"system",
                        "content":f"you are a expert SEO AI assistant, i will give you a data of a page in a json format, you need to analyse it and give suggestion according to it, the response should not cotain any information abou the the data i provided, it must look like a person completly read that json and giving suggestions, the response should be in markdown format, the data  = {data}"
                    }
                ],
                max_tokens=1024,
            )
    return chat_completion.choices[0].message.content

"""

app = Flask(__name__)

@app.route('/api/data', methods=['POST'])
def giveDigest():
    req_data = request.json  # Parse the JSON data
    url = req_data.get("url") 
    data = getInfo(url)
    """
    dataFromAI = getAISuggest(data)
    response = {
        'status':"success",
        'content': dataFromAI
    }
    """
    return jsonify(data)

@app.route('/')
def index():
    return render_template('index.html')
 
 
@app.route('/dash')
def dash():
    return render_template('dash.html')
   


if __name__ == '__main__':
    app.run(debug=True)