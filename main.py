from bs4 import BeautifulSoup
import requests
import json
import re
import csv

headers = {
    "accept": "*/*",
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.160 Mobile Safari/537.36"
}
req = requests.get(url="https://orel.hh.ru/",headers=headers)
src = req.text

with open("index.html","w",encoding="utf-8") as file:
    file.write(src)
with open("index.html","r",encoding="utf-8") as file:
    src = file.read()
soup = BeautifulSoup(src,"lxml")

names = soup.find_all(class_="bloko-link bloko-link_kind-tertiary")
names = names[1:]
resultdict = {}

#Записываем все разделы и ссылки на них в json файл

for items in names:
    if ("https://orel.hh.ru" + items.get("href") not in resultdict.values()) and not("Работа" in items.text) and not (items.text == "Новости") and not (items.text == "Статьи"):
        resultdict[re.sub(r"\d+",r"",items.text)] = "https://orel.hh.ru" + items.get("href")
with open("all_categories.json", "w", encoding="utf-8") as file:
    json.dump(resultdict, file, indent=4, ensure_ascii=False)

keys=[]
values=[]

for i,j in resultdict.items():
    keys.append(i)
    values.append(j)

for jh in range(len(keys)):
    t=0
    maxt=[]
    with open("all_categories.json","r",encoding="utf-8")as file: #Загружаем из файла разделы и ссылки
        resultdict = json.load(file)

    req = requests.get(url=values[jh]+f"?page=0",headers=headers)
    src = req.text

    soup = BeautifulSoup(src,"lxml")

    y = soup.find(class_="pager")
    if y != None:
        resq = y.text.replace("дальше","")
        y = None
    else:
        resq=0

    #Находим максимальное количество страничек у раздела

    if (resq != 0) and ("." in resq):
        for i in range(len(resq)-1,0,-1):
            if resq[i] == ".":
                break
            else:
                maxt.append(resq[i])
    elif resq == 0:
        maxt = 0
    else:
        maxt = resq[-1]

    if maxt != 0:
        maxt = ''.join(reversed(maxt))

    #Проходим в цикле по всем страничкам

    while t<=int(maxt):
        req = requests.get(url=values[jh]+f"?page={t}",headers=headers)
        src = req.text

        soup = BeautifulSoup(src,"lxml")

        vacancy = soup.find_all("h3")
        vacanciesdict = {}

        #Создаем csv файл и попарно записываем информацию о вакансии и заработной плате(также удаляем ненужные символы чтобы избежать проблем в будущем)

        with open(f"data/result_{keys[jh]}.csv", "a", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(("Вакансия","ЗП"))

            for items in vacancy:
                prom = items.find_parent().find("span", class_="bloko-header-section-3")

                if prom != None:
                    vacanciesdict[items.text] = prom.text.replace("\u202f"," ")
                    writer.writerow((items.text,prom.text.replace("\u202f"," ")))
                    prom=None
                elif "\xa0" in items.text:
                    continue
                else:
                    writer.writerow((items.text,"Договорная"))

        if maxt==0:
            print(f"Единственная страничка раздела {keys[jh]} записана")
        elif int(int(maxt)-t-1)>0:
            print(f"{t+1} Страничка готова....\nОсталось {int(maxt)-t-1}")
        else:
            print(f"Запись окончена переходим к следуещему разделу...")
        t+=1
