import os
import geocoder
import requests
from dotenv import load_dotenv

load_dotenv()

print("Disclaimer: This test cannot be used to substitute professional medical advice nor consulatation. Please seek medical help if you feel unwell.\n")

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
]
weightages = [20, 15, 10, 10, 10, 10, 10, 5, 5, 5, 5, 5, 5, 5]
answers = []

for i in range(len(questions)):
    print(f"{i + 1}. {questions[i]}")

    while True:
        answer = input("Enter answer [y/n]: ")
        print()
        if answer.lower() == "y" or answer.lower() == "n":
            answers.append(answer)
            break
        else:
            print("Your answer is invalid.\nRe-", end="")

total = 0

for i in range(len(answers)):
    if answers[i] == "y":
        total += weightages[i]

g = geocoder.ip("me")
lat = g.latlng[0]
long = g.latlng[1]

ONEMAP_API_TOKEN = os.getenv("ONEMAP_API_TOKEN")

onemap_api_url = f"https://developers.onemap.sg/privateapi/themesvc/retrieveTheme?queryName=dengue_cluster&token={ONEMAP_API_TOKEN}"
response = requests.get(onemap_api_url)

try:
    dengue_dict = {}
    results = response.json().get("SrchResults")[1:]
    for i in range(len(results)):
        cluster = results[i]
        dengue_dict.update({i: {"location": cluster.get("DESCRIPTION"), "case_size": int(cluster.get("CASE_SIZE")), "alert_level": cluster.get("SYMBOLCOLOR"), "lat_lng": cluster.get("LatLng").split("|")}})
except TypeError:
    print("Unable to check for dengue clusters near you. Please check that your OneMap API Token is valid and replace it with a valid one if not.")

percentage = total / 120 * 100
print("Chance of having dengue: {:0.2f}%".format(percentage))
if percentage >= 80:
    print("Very high chance of having dengue. Please visit a doctor now.")
elif percentage >= 50:
    print("High chance of having dengue. Please visit a doctor soon.")
elif percentage >= 30:
    print("Medium chance of having dengue. Please visit a doctor if symptoms persist.")
else:
    print("Low chance of having dengue.")
