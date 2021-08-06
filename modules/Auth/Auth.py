import json
# import requests
# import time
# from pathlib import Path
# from sqlalchemy import exc
import webbrowser
import urllib
import requests
from splinter import Browser
from modules.Db.Helper import *
from modules.Db import Redis
import os

def is_string(input):
    try:
        text = str(input)
    except ValueError:
        return False
    return True

# This function opens a browser to authorize a new account
# and is deprecated
def authNewAccount():
    webbrowser.open(f'https://auth.tdameritrade.com/auth?response_type=code&redirect_uri=https%3A%2F%2F127.0.0.1%3A5000&client_id=A12B312C4333%40AMER.OAUTHAP', new=1, autoraise=True)

# get access token from db
def getAccessToken(accountId):
    user = Session.query(User).filter(
        User.account_number == int(accountId)
        ).first()
    Session.commit()
    access_token = Redis.r.get(f'{user.username}_access_token')

    print("inside getAccessToken function:", access_token)

    refresh_token = Redis.r.get(f'{user.username}_refresh_token')
    if(access_token):
        return access_token
    newToken = getAuth(refresh_token)
    if(newToken):
        Redis.r.set(f'{user.username}_access_token', newToken['access_token'])
        Redis.r.set(f'{user.username}_refresh_token', newToken['refresh_token'])
        Redis.r.expire(f'{user.username}_access_token', 1500)
        return newToken['access_token']
    return None

# refresh user access key
def getAuth(refresh_token):
    body = {
        # refresh_token so we can obtain access_token
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        # Offile because we're not using a server
        "access_type": "offline",
        "code": "",
        # TD Ameritrade Developer Account OAUTH
        "client_id": "A12B312C4336@AMER.OAUTHAP",
        "redirect_uri": ""
    }
    # requests.post.data = body params
    rawResponse = requests.post(
        "https://api.tdameritrade.com/v1/oauth2/token", data=body)
    if (rawResponse.content and rawResponse.status_code == 200):
        response = json.loads(rawResponse.content)
        return response
    return None



def getAccountNumber(access_token):
    header = {"Authorization": f'Bearer {access_token}'}
    body = {
        "fields": ""
    }
    response = requests.get(
        f'https://api.tdameritrade.com/v1/userprincipals',
        headers=header,
        params=body
    )
    if(response.status_code == 200):
        credentials = json.loads(response.content)
        return credentials["primaryAccountId"]
    else:
        return None


def getUserPrincipals(accountId):
    header = {"Authorization": f'Bearer {getAccessToken(accountId)}'}
    body = {
        "fields": "streamerSubscriptionKeys,streamerConnectionInfo"
    }
    response = requests.get(
        f'https://api.tdameritrade.com/v1/userprincipals',
        headers=header,
        params=body
    )
    if(response.status_code == 200):
        return json.loads(response.content)
    else:
        return None



# def get_access_token(access_code, client_key):
#
#     # THE AUTHENTICATION ENDPOINT
#
#     # define the endpoint
#     url = r"https://api.tdameritrade.com/v1/oauth2/token"
#
#     # define the headers
#     headers = {"Content-Type": "application/x-www-form-urlencoded"}
#
#     # define the payload
#     payload = {'grant_type': 'authorization_code',
#                'access_type': 'offline',
#                'code': access_code,
#                'client_id': client_key,
#                'redirect_uri': 'http://localhost'}
#
#     print("payload: ", payload)
#
#     # post the data to get the token
#     authReply = requests.post(r'https://api.tdameritrade.com/v1/oauth2/token', headers=headers, data=payload)
#
#     # convert it to a dictionary
#     decoded_content = authReply.json()
#
#     print(decoded_content)
#
#     # grab the access_token
#     access_token = decoded_content['access_token']
#
#     # store it for future use
#     os.environ['td_token'] = str(access_token)
#     return access_token

def initAccessCode(client_id, username, password):
    executable_path = {'executable_path': r'/usr/local/bin/chromedriver'}

    # Create a new instance of the browser, make sure we can see it (Headless = False)
    browser = Browser('chrome', **executable_path, headless=False)

    # define the components to build a URL
    method = 'GET'
    url = 'https://auth.tdameritrade.com/auth?'
    client_code = client_id + '@AMER.OAUTHAP'
    redirect_uri = 'https://hooks.zapier.com/hooks/catch/7385471/oroh4je/'
    # redirect_uri = "https://bidasktrader.com/register"
    payload = {'response_type': 'code', 'redirect_uri': redirect_uri, 'client_id': client_code}
    # 885084780

    # Needs to look like the following
    # https://auth.tdameritrade.com/auth?response_type=code&redirect_uri=https%3A%2F%2Fhooks.zapier.com%2Fhooks%2Fcatch%2F7385471%2Foroh4je%2F%3Fcode%3D123&client_id=OSP8IKN8RIL91USENMD0SMOLEXRSQ6BP%40AMER.OAUTHAP

    # build the URL and store it in a new variable
    p = requests.Request(method, url, params=payload).prepare()
    myurl = p.url

    # go to the URL
    browser.visit(myurl)

    # # define items to fillout form
    payload = {'username': username, 'password': password}

    # # fill out each part of the form and click submit
    username = browser.find_by_id("username").first.fill(payload['username'])
    password = browser.find_by_id("password").first.fill(payload['password'])
    submit_login = browser.find_by_id("accept").first.click()

    # nature of scraping this process might take a few iterations to rerun
    secret_question_option = False
    while not secret_question_option:
        try:
            secret_question_option = browser.find_by_text("Can't get the text message?").first.click()
            secret_question_init = browser.find_by_id("stepup_0_secretquestion").first.click()
            secret_question_option = True
        except:
            pass


    secret_question_answer = False
    while not secret_question_answer:
        try:
            question_element = browser.find_by_css('div[class="row description"]').last.text

            text_filter = "Question: "
            question_filtered = question_element.split(text_filter, 1)[1]

            # security questions will be moved to another layer
            if "school" in question_filtered:
                answer = browser.find_by_id("secretquestion").first.fill("washington dc")

            if "born" in question_filtered:
                answer = browser.find_by_id("secretquestion").first.fill("moscow")

            if "mascot" in question_filtered:
                answer = browser.find_by_id("secretquestion").first.fill("frog")

            if "spouse" in question_filtered:
                answer = browser.find_by_id("secretquestion").first.fill("balboa")

            # this needs work to remember device - can't find textbox and can't interact with it
            browser.find_by_css('div[class="row user_settings"]').last.click

            submit_security_question = browser.find_by_id("accept").first.click()
            submit_authorization = browser.find_by_id("accept").first.click()

            # grab the part we need, and decode it.
            redirect_uri_response = browser.url
            # print(redirect_uri_response.split('code='))
            decoded_token = urllib.parse.unquote(redirect_uri_response.split('code=')[1])
            secret_question_answer = True

        except:
            pass

    # close the browser
    browser.quit()
    os.environ['td_token'] = str(decoded_token)

    return decoded_token



def initAccessToken(client_id, access_code):
    body = {
        # refresh_token so we can obtain access_token
        "grant_type": "authorization_code",
        # Offile because we're not using a server
        "access_type": "offline",
        "code": access_code,
        # TD Ameritrade Developer Account OAUTH
        "client_id": client_id + "@AMER.OAUTHAP",
        "redirect_uri": "https://hooks.zapier.com/hooks/catch/7385471/oroh4je/"
    }

    # method = 'GET'
    # url = 'https://auth.tdameritrade.com/auth?'
    # client_code = client_id + '@AMER.OAUTHAP'
    # redirect_uri = 'https://hooks.zapier.com/hooks/catch/7385471/oroh4je/'

    # requests.post.data = body params
    rawResponse = requests.post(
        "https://api.tdameritrade.com/v1/oauth2/token", data=body)

    print(rawResponse)
    print(rawResponse.status_code)
    print(access_code)

    if(rawResponse.status_code == 200 or rawResponse.status_code == 201):
        response = json.loads(rawResponse.content)
        return response
    return False




# get auth for the first time when creating an account
def getAuthNewUser(auth_key):
    body = {
        # refresh_token so we can obtain access_token
        "grant_type": "authorization_code",
        # Offile because we're not using a server
        "access_type": "offline",
        "code": auth_key,
        # TD Ameritrade Developer Account OAUTH
        "client_id": "A12B312C4336@AMER.OAUTHAP",
        "redirect_uri": "https://bidasktrader.com/register"
    }
    # requests.post.data = body params
    rawResponse = requests.post(
        "https://api.tdameritrade.com/v1/oauth2/token", data=body)
    print(rawResponse)
    print(rawResponse.status_code)
    print(auth_key)
    if(rawResponse.status_code == 200 or rawResponse.status_code == 201):
        response = json.loads(rawResponse.content)
        return response
    return False
