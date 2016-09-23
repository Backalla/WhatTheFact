"""Cloud Foundry test"""
from flask import Flask, render_template, request, url_for, redirect 
from watson_developer_cloud import AlchemyLanguageV1
import cf_deployment_tracker
import os
import json
import urllib
import mechanize
import re
from bs4 import BeautifulSoup
browser = mechanize.Browser()
browser.set_handle_robots(False)
browser.addheaders=[('User-agent','chrome')]
API_KEY = '03b67c6de655fffe568886ef637742ada072763a'
# Emit Bluemix deployment event
cf_deployment_tracker.track()
alchemy_language = AlchemyLanguageV1(api_key=API_KEY)
app = Flask(__name__)

def get_concepts(text):
  try:
    response = alchemy_language.concepts(max_items=10, text=text)
    return response  
  except Exception as e:
    return "Error : " + str(e)

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


def google_search(q,num,tab=""):
  q = q.replace(" ","+")
  t=""
  if tab=="news":
    t="&tbm=nws"
  query = "http://www.google.com/search?num="+str(num)+t+"&q="+q
  # print query
  htmltext = browser.open(query).read()
  # print htmltext
  div_soup = BeautifulSoup(htmltext,"html.parser")
  results = div_soup.find_all('div',class_="g")
  # print search
  search_results = []
  for result in results:
    try:
      search_result={}
      h3_soup = BeautifulSoup(str(result),"html.parser")

      h3s = h3_soup.find_all('h3',class_="r")
      # print h3s
      link = re.search("(?P<url>https?://[^\s]+)&amp", str(h3s))
      if link is None:
        continue
      link = link.group("url")
      link = link[:link.find("&amp;")]
      # print "Link : " + link

      search_result['link']=link
      title = h3_soup.a.text.encode('ascii','ignore')
      search_result['title']=title
      # print "Title : " + title

      source = link.split(".")[1]
      search_result['source']=source.title()
      # print "Source : "+source.title()


      if len(h3_soup.find_all('img')) > 0:
        img_src = h3_soup.img['src'].encode('ascii','ignore')
        search_result['img_src']=img_src;
        # print "IMG_src : "+img_src;

      text = h3_soup.find_all(class_='st')[0].text.encode('ascii','ignore')
      search_result['text'] = text.replace("\n","")
      # print "Text : "+text

      search_results.append(search_result)
    except Exception as e:
      # print str(e)
      pass

  return search_results



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
  concepts=""
  search_results = []
  if request.method == "POST":
    text = request.form['text']
    if len(text) > 0:
      entities = get_entities(text)
      keywords = get_keywords(text)
      concepts = get_concepts(text)
      first_50_words = " ".join(text.split(" ")[:50])
      for search_result in google_search(first_50_words,2):
        search_results.append(search_result)
        print search_result

  return render_template("main.html",text=text,entities=entities,keywords=keywords,concepts=concepts,search_results=search_results)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=port)
