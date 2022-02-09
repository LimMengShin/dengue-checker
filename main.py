#Imports
from flask import Flask, render_template, request
import geocoder
import requests
import json
from haversine import haversine

app = Flask(__name__) # Initialise flask

questions = {
    "Have you been bitten by a mosquito in the last 4 - 10 days?": 20,
    "Have you experienced high fever (above 40ºC) in the last 4 - 10 days?": 15,
    "Have you experienced headaches in the last 4 - 10 days?": 10,
    "Have you experienced muscle, bone or joint pains in the last 4 - 10 days": 10,
    "Have you experienced nausea or vomiting in the last 4 - 10 days?": 10,
    "Have you experienced swollen glands in the last 4 - 10 days?": 10,
    "Have you experienced rashes in the last 4 - 10 days?": 10,
    "Have you experienced severe stomach pain in the last 4 - 10 days?": 5,
    "Have you experienced bleeding in your gums and nose in the last 4 - 10 days?": 5,
    "Have you observed blood in your urine, stools or vomit in the last 4 - 10 days?": 5,
    "Have you observed any bruises on your skin in the last 4 - 10 days?": 5,
    "Have you experienced difficult or rapid breathing in the last 4 - 10 days?": 5,
    "Have you experienced fatigue in the last 4 - 10 days?": 5,
    "Have you felt more irritable or restless in the last 4 - 10 days?": 5,
} #Questions (with weightages) to ask user


#Show website design from main.html for main page & shows questions
@app.route("/")
def dengue_checker():
    return render_template("main.html", q=questions.keys())

#Show website design from help.html for help page
@app.route("/help")
def help_page():
    return render_template("help.html")


@app.route("/results", methods=["POST"]) #Retrieves data submitted by user on main page
def results():
    final = "" #Initialise html which will be shown on results page

    total = 0 #Initialising total points of user based on their answers and their question weightages

    for question, weightage in questions.items():
        answer = request.form[question] #users input answer
        if answer == "Yes":
            total += weightage #adding of weightages to total if they answered yes

    percentage = total / sum(questions.values()) * 100 #Calculating percentage likelihood of dengue

    clusters_html = "" #Initialise html to show user if nearby dengue clusters present

    try:
        g = geocoder.ip("me") #finding latitude and longitude of user from module --> geocoder
        lat_lng = g.latlng

        nea_api_url = "https://www.nea.gov.sg/api/OneMap/GetMapData/DENGUE_CLUSTER" #use of API to find location of dengue clusters in SG
        response = requests.get(nea_api_url) #Retrieve data from API

        dengue_dict = {} #initialising of dictionary to store data from API
        results = json.loads(response.json().replace("\\", "")).get("SrchResults")[1:] #Clean data [Chooses which data to store]
        for i in range(len(results)): #storing data from API into dictionary
            cluster_raw = results[i]
            dengue_dict.update(
                {
                    i: {
                        "location": cluster_raw.get("DESCRIPTION"), #stores location of cluster (ie streets)
                        "case_size": int(cluster_raw.get("CASE_SIZE")), #stores number of cases for that cluster
                        "lat_lng": [[float(i) for i in x] for x in [i.split(",") for i in cluster_raw.get("LatLng").split("|")]] #stores latitude and longitude of cluster
                    }
                }
            )

        clusters_list = [] #initialise empty list to store cluster info
        for cluster in dengue_dict.values():
            for i in cluster.get("lat_lng"):
                if haversine(lat_lng, i) < 0.2: #if distance between cluster and user is < 200m (uses haversine formula)
                    clusters_list.append([cluster.get("location"), cluster.get("case_size")]) #record location and case size into empty list
                    break

        clusters_list_length = len(clusters_list) #check number of clusters that is within 200m radius of user
        if clusters_list_length == 0:
            clusters_html += "<h3 class='center' >No dengue clusters nearby.</h3>" #Varies html msg based on nearby clusters
        else:
            clusters_html += f"<h3>{clusters_list_length} dengue cluster(s) nearby:</h3>"
            clusters_html += "<ol>"
            for i in range(clusters_list_length):
                clusters_html += f"<li>{clusters_list[i][0]} | {clusters_list[i][1]} dengue cases</li>"
            clusters_html += "</ol>"

            if clusters_list_length == 1: #Adds percentage likelihood of having dengue based on no. of nearby cluster
                percentage += 3
            else:
                percentage += 5

            if percentage > 100: #ensures that % will not exceed 100% due to nearby clusters
                percentage = 100
    except requests.ConnectionError: #If no connection, changes cluster msg
        clusters_html += "<h3 class='center' >Unable to check for dengue clusters near you. Check your internet connection and try again.</h3>"

    final += "<h2 class='center' >Chance of having dengue: <u>{:0.2f}%</u></h2>".format(percentage) #Outputs percentage likelihood
    if percentage >= 80: #Outputs advice based on percentage
        final += "<h2 class='center' >Very high chance of having dengue. Please visit a doctor now.</h2>"
    elif percentage >= 50:
        final += "<h2 class='center' >High chance of having dengue. Please visit a doctor soon.</h2>"
    elif percentage >= 30:
        final += "<h2 class='center' >Medium chance of having dengue. Please visit a doctor if symptoms persist.</h2>"
    else:
        final += "<h2 class='center' >Low chance of having dengue.</h2>"

    #Displays results on results page
    final = """
    <!DOCTYPE html>
    <html lang='en'>
    <head>
        <meta charset='UTF-8'>
        <title>Results</title>
        <style>
            body {
                font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
            } 
            .center {
                text-align: center
            }
            ol {
                list-style: none;
                counter-reset: counter;
            }
            li {
                counter-increment: counter;
                margin: 0.5rem;
            }
            li::before {
                content: counter(counter);
                background: #8b0000;
                width: 1.5rem;
                height: 1.5rem;
                border-radius: 20%;
                display: inline-block;
                line-height: 1.5rem;
                color: white;
                text-align: center;
                margin-right: 0.5rem;
            }
        </style>
    </head>
    <body>""" + final + "<hr>" + clusters_html + "<button onclick='history.back()'>Go Back</button></body></html>"
    return final


if __name__ == "__main__": #Run the programme
    app.run(debug=True)
