# import time
import urllib
import requests
from splinter import Browser

# from flask import Flask, make_response, request, current_app, jsonify, send_file
# import json
# import subprocess
# import getopt
# import sys

# define the location of the Chrome Driver - CHANGE THIS!!!!!
# if chromedriver is not install run the following on a mac:
# >brew cask install chromedriver
# if you forget type: which chromedriver




def initAccessToken(client_id, username, password):
    executable_path = {'executable_path': r'/usr/local/bin/chromedriver'}

    # Create a new instance of the browser, make sure we can see it (Headless = False)
    browser = Browser('chrome', **executable_path, headless=False)

    # define the components to build a URL
    method = 'GET'
    url = 'https://auth.tdameritrade.com/auth?'
    client_code = client_id + '@AMER.OAUTHAP'
    redirect_uri = 'https://hooks.zapier.com/hooks/catch/7385471/oroh4je/'
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

    secret_question_answer = False
    while not secret_question_answer:
        try:
            # grab the part we need, and decode it.
            redirect_uri_response = browser.url
            print(redirect_uri_response.split('code='))
            decoded_token = urllib.parse.unquote(redirect_uri_response.split('code=')[1])
            secret_question_answer = True
        except:
            pass

    # close the browser
    browser.quit()

    return decoded_token


client_id = 'OSP8IKN8RIL91USENMD0SMOLEXRSQ6BP'
username = 'fkolyadin'
password = 'Ots0sik@'

initAccessToken(client_id, username, password)c