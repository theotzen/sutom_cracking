import utils as ut
import pandas as pd


from bs4 import BeautifulSoup as bs
import numpy as np
import pandas as pd
from selenium import webdriver
import time
import pyperclip as pc

from selenium.webdriver.firefox.options import Options

options = Options()
options.add_argument('--headless')


def lemme_ver(row):
    if row['4_cgram'] == 'VER':
        return row['3_lemme']
    else:
        return row['1_ortho']


lexique = pd.read_excel(
    './Lexique383.xlsb')
lexique['1_ortho'] = lexique.apply(lemme_ver, axis=1)
# lexique = lexique[(lexique['4_cgram'] != 'VER') &
# (lexique['4_cgram'] != 'ADJ')]
lexique = lexique[lexique['4_cgram'] == 'NOM']

lexique = lexique[['1_ortho', '8_freqlemlivres']].rename(
    columns={'1_ortho': 'mot', '8_freqlemlivres': 'freq'})

lexique.dropna(axis=0, inplace=True)
lexique.drop_duplicates(inplace=True)


browser = webdriver.Firefox()
browser.set_window_size(1200, 900)
already_seen = []

for i in range(6):
    browser.get('https://sutom.nocle.fr/')
    time.sleep(1)
    html = browser.execute_script('return document.documentElement.outerHTML')
    all_html = bs(html, 'lxml')
    rules = browser.find_element_by_xpath(
        f"//a[@id='panel-fenetre-bouton-fermeture']")
    try:
        rules.click()
    except:
        pass

    grille_scd = ut.extract_grille(all_html)
    if grille_scd[i].lower() == '':
        print('break')
        break
    print(grille_scd[i].lower())
    forbidden_scd = ut.get_forbidden_letters_from_html(all_html)
    forbidden_scd = [ut.remove_accents(letter.lower())
                     for letter in forbidden_scd]
    print(forbidden_scd)
    yellow_scd = ut.get_yellow_letters_from_html(all_html)
    yellow_scd = [ut.remove_accents(letter.lower()) for letter in yellow_scd]
    print(yellow_scd)

    to_try = ut.get_first_word(ut.filter_results(ut.get_most_freq_res(ut.get_results(lexique, ut.create_total_query(
        yellow_scd, forbidden_scd, grille_scd[i].lower()))).to_frame(), already_seen))
    print(to_try)

    ut.write_word(ut.remove_accents(to_try).upper(), browser)
    already_seen.append(to_try)

time.sleep(1)
browser.find_element_by_xpath(
    f"//a[@id='configuration-stats-bouton']").click()
time.sleep(1)
browser.find_element_by_xpath(
    f"//a[@id='fin-de-partie-panel-resume-bouton']").click()
print(pc.paste())
