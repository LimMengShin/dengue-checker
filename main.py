import geocoder #Import all modules used
import requests
import json
from haversine import haversine

print("Disclaimer: This test cannot be used to substitute professional medical advice nor consulatation. Please seek medical help if you feel unwell.\n") #disclaimer

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
total = 0 #initialising total points of user based on their answers and their question weightages

qn_num = 1
for question, weightage in questions.items():
    print(f"{qn_num}. {question}")
    qn_num += 1

    while True: #Forever loop for input validation
        answer = input("Enter answer [y/n]: ") #users input answer 
        print()
        if answer.lower() == "y": #input validation check
            total += weightage #adding of weightages to total if they answered yes
            break #Break after input is validated
        elif answer.lower() == "n":
            break
        else:
            print("Your answer is invalid.\nRe-", end="") #Error message

percentage = total / sum(questions.values()) * 100

try:
    g = geocoder.ip("me") #finding latitude and longitude of user from module --> geocoder
    lat_lng = g.latlng

    nea_api_url = "https://www.nea.gov.sg/api/OneMap/GetMapData/DENGUE_CLUSTER" #use of API to find location of dengue clusters in SG
    response = requests.get(nea_api_url)

    dengue_dict = {} #initialising of dictionary to store data from API
    results = json.loads(response.json().replace("\\", "")).get("SrchResults")[1:]
    for i in range(len(results)): #storing data from API into dictionary
        cluster = results[i]
        dengue_dict.update(
            {
                i: {
                    "location": cluster.get("DESCRIPTION"), #stores location of cluster (ie streets)
                    "case_size": int(cluster.get("CASE_SIZE")), #stores number of cases for that cluster
                    "lat_lng": [[float(i) for i in x] for x in [i.split(",") for i in cluster.get("LatLng").split("|")]] #stores latitude and longitude of cluster
                }
            }
        )

    clusters_list = [] #initialise empty list to store cluster info
    for cluster in dengue_dict.values():
        for i in cluster.get("lat_lng"):
            if haversine(lat_lng, i) < 0.2: #if distance between latitude and longitude of cluster and user is < 200m (uses haversine formula)
                clusters_list.append([cluster.get("location"), cluster.get("case_size")]) #record location and case size into empty list
                break

    clusters_list_length = len(clusters_list) #check number of clusters that is within 200m radius of user
    if clusters_list_length == 0: #Output
        print("You are not near any dengue clusters.")
    elif clusters_list_length == 1:
        if percentage <= 97:
            percentage += 3
        print(f"You are near 1 dengue cluster:\n{clusters_list[0][0]} | {clusters_list[0][1]} dengue cases")
    else:
        if percentage <= 95:
            percentage += 5
        print(f"You are near {clusters_list_length} dengue clusters:")
        for i in range(clusters_list_length):
            print(f"{i+1}. {clusters_list[i][0]} | {clusters_list[i][1]} dengue cases")
except TypeError:
    print("Unable to check for dengue clusters near you. Check your internet connection and try again.")

print("\nChance of having dengue: {:0.2f}%".format(percentage))
if percentage >= 80:
    print("Very high chance of having dengue. Please visit a doctor now.")
elif percentage >= 50:
    print("High chance of having dengue. Please visit a doctor soon.")
elif percentage >= 30:
    print("Medium chance of having dengue. Please visit a doctor if symptoms persist.")
else:
    print("Low chance of having dengue.")
