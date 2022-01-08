print("Disclaimer: This test cannot be used to substitute professional medical advice nor consulatation. Please seek medical help if you feel unwell.\n")

questions = [
    "Have you been bitten by a mosquito in the last 4 - 10 days?",
    "Did you experience high fever (above 40ºC) in the last 4 - 10 days?",
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

percentage = total / 120 * 100
print("Chance of having dengue: {:0.2f}%".format(percentage))
