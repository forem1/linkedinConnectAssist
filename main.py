import json
import os
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By

SESSION_KEY = ""
SEARCH = "amazon recruiter"
TEXT = "I'm an experienced software and hardware engineer actively seeking a job with relocation or remote possibilities. I'm open to exploring various roles and would greatly appreciate your assistance in finding suitable positions. Your consideration of my profile would mean a lot to me."

page = 1
totalCounter = 0
today = 0

def main():
    global page, today, totalCounter
    # path to browser web driver
    driver = webdriver.Chrome()
    driver.get('http://linkedin.com')
    driver.add_cookie({"name": "li_at", "value": SESSION_KEY})

    while(True):
        print(f"Page {page}")
        driver.get(f"http://linkedin.com/search/results/people/?keywords={SEARCH}&page={page}&origin=SWITCH_SEARCH_VERTICAL")

        listOfUsers = []

        sleep(5)

        list = driver.find_element(By.CLASS_NAME, 'reusable-search__entity-result-list')
        rows = list.find_elements(By.TAG_NAME, "li")  # get all of the rows
        for row in rows:
            try:
                tempName = row.find_element(By.CSS_SELECTOR, "span[aria-hidden='true']").text.split(' ')
                if len(tempName) <= 5:
                    name = tempName[0]
                else:
                    continue
                connectButton = row.find_element(By.CLASS_NAME, "artdeco-button")
                connectButtonText = row.find_element(By.CLASS_NAME, "artdeco-button__text").text
                if connectButtonText == "Connect" and (len(name) + len(TEXT) <= 300):
                    listOfUsers.append((name, connectButton))
            except:
                pass
        print(listOfUsers)

        sleep(1)

        for user in listOfUsers:
            print(f"Write to {user[0]}")
            user[1].click()
            sleep(1)
            modal = driver.find_element(By.CLASS_NAME, "send-invite")

            try:
                modal.find_element(By.CSS_SELECTOR, "label[for='email']")
                print("Found email check")
                modal.find_element(By.CLASS_NAME, "artdeco-modal__dismiss").click()
                continue
            except:
                pass

            sleep(2)
            modal.find_element(By.CSS_SELECTOR, "button[aria-label='Add a note']").click() # Click on Add a note
            sleep(1)
            modal.find_element(By.TAG_NAME, "textarea").send_keys(f"Hello, {user[0]}.\n{TEXT}")
            sleep(2)
            modal.find_element(By.CSS_SELECTOR, "button[aria-label='Send now']").click()  # Click on Send
            totalCounter = totalCounter + 1
            today = today + 1
            print(f"Today {today}")
            sleep(1)
        page = page + 1

        print(f"Total {totalCounter}")
        f = open("log.txt", "w", encoding="utf-8")
        f.write(json.dumps({'total': totalCounter, 'currentPage': page, 'search': SEARCH}))
        f.close()


if __name__ == "__main__":
    try:
        if not os.path.exists("log.txt"):
            f = open("log.txt", "w", encoding="utf-8")
            f.write(json.dumps({'total':0, 'currentPage':1, 'search':""}))
            f.close()
        else:
            f = open('log.txt', encoding="utf-8")
            data = json.load(f)
            totalCounter = data['total']
            f.close()

        main()
    except Exception as e:
        f = open("errors.txt", "a", encoding="utf-8")
        f.write(str(e))
        f.close()

        f = open("log.txt", "w", encoding="utf-8")
        f.write(json.dumps({'total': totalCounter, 'currentPage': page, 'search': SEARCH}))
        f.close()

