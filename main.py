import json
import logging
import logging.config as logging_conf
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
import os
from dotenv import load_dotenv

load_dotenv()

SESSION_KEY = os.getenv('SESSION_KEY')
SEARCH = os.getenv('SEARCH')
TEXT = os.getenv('TEXT')

logging_conf.fileConfig('logger.conf')

def create_driver():
    driver = webdriver.Chrome()
    driver.get('http://linkedin.com')
    driver.add_cookie({"name": "li_at", "value": SESSION_KEY})
    return driver


def get_users_from_search(driver, page):
    driver.get(
        f"http://linkedin.com/search/results/people/?keywords={SEARCH}&page={page}&origin=SWITCH_SEARCH_VERTICAL")

    users = []

    sleep(5)

    list_tag = driver.find_element(By.CLASS_NAME, 'reusable-search__entity-result-list')
    rows = list_tag.find_elements(By.TAG_NAME, "li")  # get all of the rows
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
                users.append((name, connectButton))
        except:
            pass

    return users


def send_invitations_from_search(users, driver, page, totalCounter, file):
    logger = logging.getLogger('send_invitations_from_search')
    for user in users:
        logger.info(f"Write to {user[0]}")
        user[1].click()
        sleep(1)
        modal = driver.find_element(By.CLASS_NAME, "send-invite")

        try:
            modal.find_element(By.CSS_SELECTOR, "label[for='email']")
            logger.info("Found email check")
            modal.find_element(By.CLASS_NAME, "artdeco-modal__dismiss").click()
            continue
        except:
            pass

        sleep(2)
        modal.find_element(By.CSS_SELECTOR, "button[aria-label='Add a note']").click()  # Click on Add a note
        sleep(1)
        modal.find_element(By.TAG_NAME, "textarea").send_keys(f"Hello, {user[0]}.\n{TEXT}")
        sleep(2)
        modal.find_element(By.CSS_SELECTOR, "button[aria-label='Send now']").click()  # Click on Send
        sleep(1)
        totalCounter += 1
        logger.info(f"Done. Total {totalCounter}")

    file.write(json.dumps({'total': totalCounter, 'currentPage': page, 'search': SEARCH}))


def send_invitations(fileName):
    logger = logging.getLogger('send_invitations')
    page = 1
    totalCounter = 0
    invitationLogFile = open(fileName, "w", encoding="utf-8")
    driver = create_driver()

    try:
        if not os.path.exists(fileName):
            f = open(fileName, "w", encoding="utf-8")
            f.write(json.dumps({'total': 0, 'currentPage': 1, 'search': ""}))
            f.close()
        else:
            f = open(fileName, encoding="utf-8")
            data = json.load(f)
            totalCounter = data['total']
            f.close()

        while True:
            logger.info(f"Page {page}")
            sleep(1)
            users = get_users_from_search(driver, page)
            sleep(1)
            send_invitations(users, driver, page, totalCounter, invitationLogFile)
            page += 1
    except:
        invitationLogFile.close()


def get_users_from_contacts(driver):
    logger = logging.getLogger('get_users_from_contacts')
    users = []

    driver.get(f"https://www.linkedin.com/mynetwork/invite-connect/connections/")

    sleep(5)

    list = driver.find_element(By.CLASS_NAME, 'scaffold-finite-scroll')

    try:
        while (True):
            moreButton = list.find_element(By.CLASS_NAME, "scaffold-finite-scroll__load-button")
            logger.info("Loaded more users")
            moreButton.click()
            sleep(5)
    except:
        pass

    rows = list.find_element(By.TAG_NAME, "ul").find_elements(By.TAG_NAME, "li")  # get all connections of the rows
    for row in rows:
        try:
            name = row.find_element(By.CLASS_NAME, "mn-connection-card__name").text
            link = row.find_element(By.TAG_NAME, "a").get_attribute("href")
            users.append([name, link])
        except:
            pass

    logger.info(f"Total contacts: {len(users)}")

    return users


def get_email_from_user(driver, user):
    logger = logging.getLogger('get_email_from_user')
    logger.info(f"Work with {user[0]}")
    driver.get(user[1] + "overlay/contact-info/")

    sleep(5)

    try:
        email = \
        driver.find_element(By.CLASS_NAME, "ci-email").find_element(By.TAG_NAME, "a").get_attribute("href").split(':')[
            1]
        logger.info(email)
        return email
    except:
        logger.warning(f"{user[0]}'s email not found")
        return False


def contacts_email_collector(fileName):
    emails = []
    driver = create_driver()
    users = get_users_from_contacts(driver)

    for user in users:
        email = get_email_from_user(driver, user)
        if email != False:
            emails.append([email, user[0], user[1]])

    f = open(fileName, "w", encoding="utf-8")
    f.write(json.dumps(emails))
    f.close()


if __name__ == "__main__":
    # send_invitations("invitationLog.txt")
    contacts_email_collector("userEmails.txt")

