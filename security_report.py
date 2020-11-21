#! /usr/bin/env python3

from PIL import Image
from pytesseract import image_to_string

import datetime
import os
import sys
import re

def generate_security_report(file=None):
    todays_date = str(datetime.date.today())
    recovered = None
    details = ""
    number_pattern = r'\d+.? *\d*'
    details_pattern = r'\(\d+\)'

    if file:
        file = os.path.join(os.path.expanduser("~"), "senegal_covid_reports", file)
    else:
        partial_path = os.path.join(os.path.expanduser("~"), "Downloads", "covid")
        for extension in [".png", ".jpg"]:
            full_path = partial_path + extension
            if os.path.exists(full_path):
                file = full_path
                break
        if not file:
            print("Couldn't find your covid file in your Downloads folder")
            sys.exit(1)

    data = image_to_string(Image.open(file))
    remove = ["", " ", "  "]
    lines = [line.lower() for line in data.split("\n") if line not in remove]

    for index, line in enumerate(lines):
        # print(line)
        if line.startswith("sur"):
            tested = re.findall(number_pattern, line)[0]
            todays_positive = re.findall(number_pattern, line)[1]
        elif "%" in line:
            infection_rate = ",".join(re.findall(number_pattern, line))
        elif "importé" in line:
            if "aucun" in line:
                imported = 0
            else:
                imported = re.search(number_pattern, line)[0]
        elif "contact" in line:
            if "aucun" in line:
                contacts = 0
            else:
                contacts = re.search(number_pattern, line)[0]
        elif "transmission communautaire" in line:
            community_infections = re.search(number_pattern, line)[0]
        elif "patient" in line and recovered is None:
            if "aucun" in line:
                recovered = 0
            else:
                recovered = re.search(number_pattern, line)[0]
        elif "grave" in line:
            if "aucun" in line:
                serious_cases = 0
            else:
                serious_cases = re.search(number_pattern, line)[0]
        elif line.startswith("a ce jour") or line.startswith("jour"):
            total_positive = re.findall(number_pattern, line)[0]
            total_recovered = re.findall(number_pattern, line)[1]
            try:
                deaths = re.findall(number_pattern, line)[2]
            except IndexError:
                deaths = re.findall(number_pattern, lines[index+1])[0]
        elif "sous traitement" in line:
            recovering = re.search(number_pattern, line)[0]
        elif re.search(details_pattern, line):
            details += line


    ### TEMPLATES ###

    korean_report = f"""
    [세네갈 코로나19 현황, {todays_date}]
    1. 누적 확진자 : {total_positive}명
    ㅇ 치료 중 : {recovering}명
    ㅇ 완치 : {total_recovered}명
    ㅇ 사망 : {deaths}명
    ㅇ 접촉자 : {contacts}명
    2. 금일 확진 : {todays_positive}명 ({tested}명 검사)
    ㅇ 지역사회감염 : {community_infections}명
    {details}


    3. 금일 완치자 : {recovered}명.  끝.
    """

    english_report = f"""
    Good morning dear all,
    Situation of Coronavirus outbreak in Senegal as of {todays_date}:

    Tests performed: {tested}
    Total Positive: {todays_positive}
    - Positivity Rate: {infection_rate}%
    - Contact cases: {contacts}
    - Communautary transmissions: {community_infections}

    {details}

    - Patients totally recovered: {recovered}
    - Serious cases: {serious_cases}


    Total positive cases: {total_positive}
    Totally recovered: {total_recovered}
    Deaths: {deaths}
    Patients under treatment: {recovering}
    """

    print(korean_report)
    print(english_report)


    new_path = file.replace("covid", f"covid-{todays_date}").replace("Downloads", "senegal_covid_reports")
    os.system(f"mv {file} {new_path}")
    os.system(f"open  {new_path}")

    data = {
        "todays_positive": todays_positive,
        "total_positive": total_positive,
        "total_recovered": total_recovered,
        "deaths": deaths,
    }
    for key, value in data.items():
        data[key] = int(value.strip().replace(" ", ""))
    return data


security_reports_dir = os.path.join(os.path.expanduser("~"), "senegal_covid_reports")
files = os.listdir(security_reports_dir)

info = []
for file in files:
    data = generate_security_report(file)
    date = re.search(r'\d+-\d+-\d+', file)[0]
    data["date"] = date
    info.append(data)
print(info)
