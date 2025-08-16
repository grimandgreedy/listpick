#!/bin/python
# -*- coding: utf-8 -*-
"""
Get a wikipedia table and display it in a Picker.

Author: GrimAndGreedy
License: MIT
"""

import requests
from bs4 import BeautifulSoup
import pickle
from listpick.listpick_app import Picker, start_curses, close_curses


def fetch_and_parse_webpage(url: str) -> list:
    """ Get list of tables from webpage at url. """
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        tables = soup.find_all('table')
        return [parse_table(table) for table in tables]
    else:
        raise Exception(f"Failed to fetch webpage: {response.status_code}")

def parse_table(table) -> list[list[str]]:
    """ Convert a bs4 table to a list of lists. """
    headers = [header.text.strip() for header in table.find('tr').find_all('th')]
    rows = []
    for row in table.find_all('tr')[1:]:
        cells = [cell.text.strip() for cell in row.find_all(['td', 'th'])]
        rows.append(cells)
    return [headers] + rows

def save_data(data, filename: str) -> None:
    """ Pickle data. """
    with open(filename, 'wb') as file:
        pickle.dump(data, file)

def load_data(filename: str, url: str) -> list:
    """ 
    Load tables from wikipedia page. Data is saved to `filename`. 
    If the tables have already been cached then we load the data and nothing is downloaded.
    """
    try:
        with open(filename, 'rb') as file:
            data = pickle.load(file)
        return data
    except FileNotFoundError:
        print(f"File not found. Fetching data from the web.")
        data = fetch_and_parse_webpage(url)
        save_data(data, filename)
        return data

if __name__ == "__main__":
    url = 'https://en.wikipedia.org/wiki/2024-25_Premier_League'

    # Filename for pickled data
    # pickle_filename = './auxiallary_files/premier_league_tables_2024.pkl'
    pickle_filename = f'./auxiallary_files/{url.split("/")[-1]}.pkl'
    try:
        tables = load_data(pickle_filename, url)
        league_table_number = 4
        items = tables[league_table_number][1:]
        header = tables[league_table_number][0]
        stdscr = start_curses()
        app = Picker(
            stdscr, 
            items=items, 
            header=header,
            title="Premier League Table 2024-25",
            colour_theme_number=3,
        )
        app.run()

        close_curses(stdscr)
    except:
        pass
