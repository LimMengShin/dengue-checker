# Imports
from flask import Flask, render_template, request
import geocoder
import requests
import json
from haversine import haversine

from questions import *


# Constants
NEA_API_URL = "https://www.nea.gov.sg/api/OneMap/GetMapData/DENGUE_CLUSTER"


# Initialise Flask
app = Flask(__name__)


# Coded by Meng Shin, Ping Jin, Ysabelle
# Calculate chance of user having dengue based on user's input in percentage
def calculate_percentage():
    total = 0  # Initialise total points of user based on their answers and the question weightages

    for question, weightage in questions.items():
        answer = request.form[question]  # User's input
        if answer == "Yes":
            total += weightage  # Add weightages to total if user answered "Yes"

    percentage = total / sum(questions.values()) * 100  # Calculate user's chance of having dengue in percentage
    return percentage


# Coded by Meng Shin
# Get location (latitude, longitude) of user using the Geocoder module
def get_location():
    g = geocoder.ip("me")
    lat_lng = g.latlng
    return lat_lng


# Coded by Meng Shin
# Make a "GET" request to the NEA API
def get_data(url):
    response = requests.get(url)
    return response


# Coded by Meng Shin
# Format response and store formatted response in a dictionary
def format_data(response):
    dengue_dict = {}  # Initialise empty dictionary to store formatted response
    results = json.loads(response.json().replace("\\", "")).get("SrchResults")[1:]  # Remove backslashes from response

    # Store formatted response in the dictionary "dengue_dict"
    for i in range(len(results)):
        cluster_raw = results[i]
        dengue_dict.update(
            {
                i: {
                    "location": cluster_raw.get("DESCRIPTION"),  # Store location of cluster (i.e. street name)
                    "case_size": int(cluster_raw.get("CASE_SIZE")),  # Store number of cases for that cluster
                    "lat_lng": [[float(i) for i in x] for x in [i.split(",") for i in cluster_raw.get("LatLng").split("|")]]  # Store location (latitude and longitude) of cluster
                }
            }
        )
    return dengue_dict


# Coded by Meng Shin
# Check for nearby clusters (less than 200 metres from user) and store them in a list
def check_nearby_clusters(dengue_dict, lat_lng):
    clusters_list = []  # Initialise empty list to store cluster info

    # Loop through each cluster in the "dengue_dict" dictionary
    for cluster in dengue_dict.values():
        for i in cluster.get("lat_lng"):
            if haversine(lat_lng, i) < 0.2:  # Using the haversine module, check if distance between cluster location and user's location is less than 200 metres
                clusters_list.append([cluster.get("location"), cluster.get("case_size")])  # Append location and case size of cluster to "clusters_list" list
                break
    return clusters_list


# Coded by Meng Shin
# Add HTML of dengue cluster(s) nearby, if any, to "clusters_html" string,
# and increase percentage depending on number of nearby clusters
def location_results(clusters_list, clusters_html, percentage):
    clusters_list_length = len(clusters_list)  # Count number of nearby clusters

    # Add HTML of dengue cluster(s) nearby, if any, to "clusters_html" string
    if clusters_list_length == 0:
        clusters_html += "<h3 class='center' >No dengue clusters nearby.</h3>"
    else:
        clusters_html += f"<h3>{clusters_list_length} dengue cluster(s) nearby:</h3>"
        clusters_html += "<ol>"
        for i in range(clusters_list_length):
            clusters_html += f"<li>{clusters_list[i][0]} | {clusters_list[i][1]} dengue cases</li>"
        clusters_html += "</ol>"

        # Increase percentage depending on number of nearby clusters
        if clusters_list_length == 1:
            percentage += 3
        else:
            percentage += 5

        # Ensure that percentage will not be more than 100%
        if percentage > 100:
            percentage = 100
    return clusters_html, percentage


# Coded by Meng Shin, Ping Jin, Ysabelle
# Add HTML of chance of having dengue percentage and advice on what to do, if applicable, to "final" string
def final_results(final, percentage):
    final += "<h2 class='center' >Chance of having dengue: <u>{:0.2f}%</u></h2>".format(percentage)  # Output percentage

    # Output advice based on percentage
    if percentage >= 80:
        final += "<h2 class='center' >Very high chance of having dengue. Please visit a doctor now.</h2>"
    elif percentage >= 50:
        final += "<h2 class='center' >High chance of having dengue. Please visit a doctor soon.</h2>"
    elif percentage >= 30:
        final += "<h2 class='center' >Medium chance of having dengue. Please visit a doctor if symptoms persist.</h2>"
    else:
        final += "<h2 class='center' >Low chance of having dengue.</h2>"
    return final


# Coded by Meng Shin
# Render page template from main.html
@app.route("/")
def main_page():
    return render_template("main.html", q=questions.keys())


# Coded by Meng Shin
# Render page template from help.html
@app.route("/help")
def help_page():
    return render_template("help.html")


# Coded by Meng Shin
# Display results page and returns results HTML
@app.route("/results", methods=["POST"])
def results_page():
    final = ""  # Initialise empty string for HTML which will be shown on results page

    percentage = calculate_percentage()

    clusters_html = ""  # Initialise empty string for HTML to show user nearby dengue clusters

    try:
        lat_lng = get_location()

        response = get_data(NEA_API_URL)

        dengue_dict = format_data(response)

        clusters_list = check_nearby_clusters(dengue_dict, lat_lng)

        clusters_html, percentage = location_results(clusters_list, clusters_html, percentage)

    except requests.ConnectionError:  # Add message to "clusters_html" string when internet connection is unavailable
        clusters_html += "<h3 class='center' >Unable to check for dengue clusters near you. Check your internet connection and try again.</h3>"

    except TypeError:  # Add message to "clusters_html" string when there is an error
        clusters_html += "<h3 class='center' >Unable to check for dengue clusters near you. There may be an error with your internet connection.<br>Try using a different internet connection.</h3>"

    final = final_results(final, percentage)

    # Top portion of HTML of results page
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

    # Bottom portion of HTML of results page
    html_bottom = "<button onclick='history.back()'>Go Back</button></body></html>"

    # Return results HTML on results page
    final = html_top + final + "<hr>" + clusters_html + html_bottom
    return final


# Run the programme
if __name__ == "__main__":
    app.run()
