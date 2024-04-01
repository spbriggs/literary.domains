import os
import re
import csv
from pathlib import Path
import pandas
from flask import Blueprint, request, jsonify
import sqlite3
from sqlite3 import Error

search_gutenberg_blueprint = Blueprint('search_gutenberg_blueprint', __name__)
gutenberg_db_file = f'data/gutenberg.sqlite'


def init_gutenberg_search():
    conn = None
    try:
        conn = sqlite3.connect(gutenberg_db_file)
        df = pandas.read_csv('data/pg_catalog.csv')
        df.to_sql('gutenberg', conn, if_exists='append', index=False)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


@search_gutenberg_blueprint.route('/search-gutenberg')
def search_gutenberg():
    if not os.path.isfile(gutenberg_db_file):
        init_gutenberg_search()
    # TODO: Check if the existing pg_catalog.csv file is older than one day and if so,
    # download it again from https://www.gutenberg.org/cache/epub/feeds/pg_catalog.csv

    query = request.args.get('query').lower()
    result_ids = []
    results = []

    conn = None
    try:
        conn = sqlite3.connect(gutenberg_db_file)
        cur = conn.cursor()
        results = cur.execute('select title, authors from gutenberg where title like ? or authors like ?',
                              ('%' + query + '%', '%' + query + '%'))
        stuff=results.fetchall()
        mappedstuff = list(map(lambda x: {'title': x[0], 'authors': x[1].split(';')}, stuff))
        return jsonify(results=mappedstuff)

    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()
