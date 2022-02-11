#Imports
from flask import Flask, render_template, request
import geocoder
import requests
import json
from haversine import haversine

from questions import *


NEA_API_URL = "https://www.nea.gov.sg/api/OneMap/GetMapData/DENGUE_CLUSTER"

app = Flask(__name__) # Initialise flask


def calculate_percentage():
    total = 0  # Initialising total points of user based on their answers and their question weightages

    for question, weightage in questions.items():
        answer = request.form[question]  # users input answer
        if answer == "Yes":
            total += weightage  # adding of weightages to total if they answered yes

    percentage = total / sum(questions.values()) * 100  # Calculating percentage likelihood of dengue
    return percentage


def get_location():
    g = geocoder.ip("me")  # finding latitude and longitude of user from module --> geocoder
    lat_lng = g.latlng
    return lat_lng


def get_data(url):
    response = requests.get(url)
    return response


def format_data(response):
    dengue_dict = {} #initialising of dictionary to store data from API
    results = json.loads(response.json().replace("\\", "")).get("SrchResults")[1:]  # Clean data [Chooses which data to store]
    for i in range(len(results)):  # storing data from API into dictionary
        cluster_raw = results[i]
        dengue_dict.update(
            {
                i: {
                    "location": cluster_raw.get("DESCRIPTION"),  # stores location of cluster (ie streets)
                    "case_size": int(cluster_raw.get("CASE_SIZE")),  # stores number of cases for that cluster
                    "lat_lng": [[float(i) for i in x] for x in [i.split(",") for i in cluster_raw.get("LatLng").split("|")]]
                    # stores latitude and longitude of cluster
                }
            }
        )
    return dengue_dict


def check_nearby_clusters(dengue_dict, lat_lng):
    clusters_list = []  # initialise empty list to store cluster info
    for cluster in dengue_dict.values():
        for i in cluster.get("lat_lng"):
            if haversine(lat_lng, i) < 0.2:  # if distance between cluster and user is < 200m (uses haversine formula)
                clusters_list.append([cluster.get("location"), cluster.get("case_size")])  # record location and case size into empty list
                break
    return clusters_list


def location_results(clusters_list, clusters_html, percentage):
    clusters_list_length = len(clusters_list)  # check number of clusters that is within 200m radius of user
    if clusters_list_length == 0:
        clusters_html += "<h3 class='center' >No dengue clusters nearby.</h3>"  # Varies html msg based on nearby clusters
    else:
        clusters_html += f"<h3>{clusters_list_length} dengue cluster(s) nearby:</h3>"
        clusters_html += "<ol>"
        for i in range(clusters_list_length):
            clusters_html += f"<li>{clusters_list[i][0]} | {clusters_list[i][1]} dengue cases</li>"
        clusters_html += "</ol>"

        if clusters_list_length == 1:  # Adds percentage likelihood of having dengue based on no. of nearby cluster
            percentage += 3
        else:
            percentage += 5

        if percentage > 100:  # ensures that % will not exceed 100% due to nearby clusters
            percentage = 100
    return clusters_html, percentage


def final_results(final, percentage):
    final += "<h2 class='center' >Chance of having dengue: <u>{:0.2f}%</u></h2>".format(
        percentage)  # Outputs percentage likelihood
    if percentage >= 80:  # Outputs advice based on percentage
        final += "<h2 class='center' >Very high chance of having dengue. Please visit a doctor now.</h2>"
    elif percentage >= 50:
        final += "<h2 class='center' >High chance of having dengue. Please visit a doctor soon.</h2>"
    elif percentage >= 30:
        final += "<h2 class='center' >Medium chance of having dengue. Please visit a doctor if symptoms persist.</h2>"
    else:
        final += "<h2 class='center' >Low chance of having dengue.</h2>"
    return final


#Show website design from main.html for main page & shows questions
@app.route("/")
def main_page():
    return render_template("main.html", q=questions.keys())


#Show website design from help.html for help page
@app.route("/help")
def help_page():
    return render_template("help.html")


@app.route("/results", methods=["POST"]) #Retrieves data submitted by user on main page
def results_page():
    final = "" #Initialise html which will be shown on results page

    percentage = calculate_percentage()

    clusters_html = "" #Initialise html to show user if nearby dengue clusters present

    try:
        lat_lng = get_location()

        response = get_data(NEA_API_URL)

        dengue_dict = format_data(response)

        clusters_list = check_nearby_clusters(dengue_dict, lat_lng)

        clusters_html, percentage = location_results(clusters_list, clusters_html, percentage)

    except requests.ConnectionError: #If no connection, changes cluster msg
        clusters_html += "<h3 class='center' >Unable to check for dengue clusters near you. Check your internet connection and try again.</h3>"

    except TypeError:
        clusters_html += "<h3 class='center' >Unable to check for dengue clusters near you. There may be an error with your internet connection.<br>Try using a different internet connection.</h3>"

    final = final_results(final, percentage)

    #Displays results on results page
    html_top = """
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
    <body>
    """
    html_bottom = "<button onclick='history.back()'>Go Back</button></body></html>"

    final = html_top + final + "<hr>" + clusters_html + html_bottom
    return final


if __name__ == "__main__": #Run the programme
    app.run()
