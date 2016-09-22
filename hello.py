"""Cloud Foundry test"""
from flask import Flask, render_template, request, url_for, redirect 
from watson_developer_cloud import AlchemyLanguageV1
import cf_deployment_tracker
import os
import json


API_KEY = '03b67c6de655fffe568886ef637742ada072763a'
# Emit Bluemix deployment event
cf_deployment_tracker.track()
alchemy_language = AlchemyLanguageV1(api_key=API_KEY)
app = Flask(__name__)

def get_entities(text):
  try:
    response = alchemy_language.entities(text=text)
    return response  
  except Exception as e:
    return "Error : " + str(e)


def get_keywords(text):
  try:
    response = alchemy_language.keywords(max_items=10, text=text)
    return response  
  except Exception as e:
    return "Error : " + str(e)


# try:
#   alchemy_language.targeted_sentiment(text='I would love to have burger. I dont like banana',targets=['burger', 'banana'], language='english')
# except Exception as e:
#   print str(e)
# On Bluemix, get the port number from the environment variable VCAP_APP_PORT
# When running this app on the local machine, default the port to 8080
port = int(os.getenv('VCAP_APP_PORT', 8080))

@app.context_processor
def utility_processor():
    def app_float(num):
        return float(num)
    return dict(app_float=app_float)


@app.route('/',methods=["GET","POST"])
def main():
  text=""
  entities=""
  keywords=""
  if request.method == "POST":
    text = request.form['text']
    if len(text) > 0:
      entities = get_entities(text)
      keywords = get_keywords(text)
  return render_template("main.html",text=text,entities=entities,keywords=keywords)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=port)
