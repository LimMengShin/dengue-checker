import geocoder #Import all modules used
import requests
import json
from haversine import haversine

print("Disclaimer: This test cannot be used to substitute professional medical advice nor consulatation. Please seek medical help if you feel unwell.\n") #disclaimer

questions = [
    "Have you been bitten by a mosquito in the last 4 - 10 days?",
    "Have you experienced high fever (above 40ºC) in the last 4 - 10 days?",
    "Have you experienced headaches in the last 4 - 10 days?",
    "Have you experienced muscle, bone or joint pains in the last 4 - 10 days",
    "Have you experienced nausea or vomiting in the last 4 - 10 days?",
    "Have you experienced swollen glands in the last 4 - 10 days?",
    "Have you experienced rashes in the last 4 - 10 days?",
    "Have you experienced severe stomach pain in the last 4 - 10 days?",
    "Have you experienced bleeding in your gums and nose in the last 4 - 10 days?",
    "Have you observed blood in your urine, stools or vomit in the last 4 - 10 days?",
    "Have you observed any bruises on your skin in the last 4 - 10 days?",
    "Have you experienced difficult or rapid breathing in the last 4 - 10 days?",
    "Have you experienced fatigue in the last 4 - 10 days?",
    "Have you felt more irritable or restless in the last 4 - 10 days?",
] #Questions to ask user
weightages = [20, 15, 10, 10, 10, 10, 10, 5, 5, 5, 5, 5, 5, 5] #Weightages of each question
answers = [] #Empty list to record answers of users

for i in range(len(questions)):
    print(f"{i + 1}. {questions[i]}")

    while True: #Forever loop for input validation
        answer = input("Enter answer [y/n]: ") #users input answer 
        print()
        if answer.lower() == "y" or answer.lower() == "n": #input validation check
            answers.append(answer)
            break #Break after input is validated
        else:
            print("Your answer is invalid.\nRe-", end="") #Error message

total = 0 #initialising total points of user based on their answers and their question weightages 

for i in range(len(answers)):
    if answers[i] == "y":
        total += weightages[i] #adding of weightages to total if they answered yes

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

    clusters_list = [] #initialise empty list to 
    for cluster in dengue_dict.values():
        for i in cluster.get("lat_lng"):
            if haversine(lat_lng, i) < 0.2: #if distance between latitude and longitude of cluster and user is < 200m (uses haversine formula)
                clusters_list.append([cluster.get("location"), cluster.get("case_size")]) #record location and case size into empty list
                break

    clusters_list_length = len(clusters_list) #check number of clusters that is within 200m radius of user
    if clusters_list_length == 0: #Output 
        print("You are not near any dengue clusters.")
    elif clusters_list_length == 1:
        print(f"You are near 1 dengue cluster:\n{clusters_list[0][0]} | {clusters_list[0][1]} dengue cases")
    else:
        print(f"You are near {clusters_list_length} dengue clusters:")
        for i in range(clusters_list_length):
            print(f"{i+1}. {clusters_list[i][0]} | {clusters_list[i][1]} dengue cases")
except TypeError:
    print("Unable to check for dengue clusters near you. Check your internet connection and try again.")

percentage = total / 120 * 100
print("\nChance of having dengue: {:0.2f}%".format(percentage))
if percentage >= 80:
    print("Very high chance of having dengue. Please visit a doctor now.")
elif percentage >= 50:
    print("High chance of having dengue. Please visit a doctor soon.")
elif percentage >= 30:
    print("Medium chance of having dengue. Please visit a doctor if symptoms persist.")
else:
    print("Low chance of having dengue.")
