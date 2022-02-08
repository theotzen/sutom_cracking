import unicodedata
import pandas as pd
import re

from bs4 import BeautifulSoup as bs
import numpy as np
import requests
import pandas as pd
import webbrowser
import urllib.request
import csv
from selenium import webdriver
import time

from selenium.webdriver.firefox.options import Options

options = Options()
options.add_argument('--headless')


def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])


def create_query(current_word):
    query = ""
    for idx, char in enumerate(current_word):
        if char == '.':
            pass
        else:
            query += f"mot.str[{idx}] == '{char}' and "
    return query + "mot.str.len() == " + str(len(current_word))


def get_results(lex, query):
    return lex.query(query, engine="python").sort_values(by='freq', ascending=False)


def get_most_freq_res(t):
    return t.reset_index(drop=True).loc[0:5, 'mot']


def create_query_letters(list_of_letters):
    query = ""
    for idx, letter in enumerate(list_of_letters):
        if idx < len(list_of_letters) - 1:
            query += f"mot.str.contains('{letter}', na=False) and "
        else:
            query += f"mot.str.contains('{letter}', na=False)"

    return query


def create_query_forbidden_letters(list_of_forbidden_letters):
    query = ""
    for idx, letter in enumerate(list_of_forbidden_letters):
        if idx < len(list_of_forbidden_letters) - 1:
            query += f"~mot.str.contains('{letter}', na=False) and "
        else:
            query += f"~mot.str.contains('{letter}', na=False)"

    return query


def create_total_query(list_of_letters, list_of_forbidden_letters, current_word):
    if list_of_letters and list_of_forbidden_letters:
        return create_query_letters(list_of_letters) + " and " + create_query_forbidden_letters(list_of_forbidden_letters) + " and " + create_query(current_word)
    elif list_of_letters and not list_of_forbidden_letters:
        return create_query_letters(list_of_letters) + " and " + create_query(current_word)
    elif not list_of_letters and list_of_forbidden_letters:
        return create_query_forbidden_letters(list_of_forbidden_letters) + " and " + create_query(current_word)
    else:
        return create_query(current_word)


def filter_results(res, already_seen: list):
    tampon = res[(~res.mot.isin(already_seen))]
    return tampon[(~tampon.mot.str.contains(' ', na=False)) & (~tampon.mot.str.contains('-', na=False))]


def get_first_word(filtered_results):
    print(filtered_results)

    return filtered_results.iloc[0, 0]


def extract_words(l: list) -> list:
    words = []
    for to_clean in l:
        if len(to_clean) > 2:
            words.append(re.sub('<td>|</td>', '', to_clean))

    return words


def extract_grille(html_page):
    root = html_page.findAll('div', {'id': "grille"})
    root_content = re.split('<tr>|</tr>', str(root[0]))[1:-1]
    return extract_words(root_content)


def get_forbidden_letters_from_html(all_html):
    forbid = []
    l = list(all_html.findAll(
        'div', {'class': "input-lettre lettre-non-trouve"}))
    if l:
        for elem in l:
            forbid.append(str(elem)[-7])
    else:
        return []
    return forbid


def get_yellow_letters_from_html(all_html):
    yellow = []
    l = list(all_html.findAll(
        'div', {'class': "input-lettre lettre-mal-place"}))
    if l:
        for elem in l:
            yellow.append(str(elem)[-7])
    else:
        return []
    return yellow


def write_word(word, browser):
    # browser.get('https://sutom.nocle.fr/')
    time.sleep(0.5)
    for char in word:
        element = browser.find_element_by_xpath(
            f"//div[@data-lettre='{char}']")
        element.click()
    browser.find_element_by_xpath(f"//div[@data-lettre='_entree']").click()
