#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
import csv
import os
range = xrange # make this more py3 like
text = str # this line allows us to use schema as the type in python. clever!

DATA = '/Users/kurt/Dropbox/foodquery/data/'
SQLITE_DB = 'food.db'

try:
    os.remove(SQLITE_DB)
except OSError:
    pass

# TODO
#make units 4 unicode chars
#make tagname 16 chars.
#make desc 64 chars.
NUTR_DEF_SCHEMA = ('NUTR_DEF', list(range(6)), [
        ('nutr_no', 'int', 'primary key'),
        ('units', 'text'),
        ('tagname', 'text'),
        ('desc', 'text'),
        ('num_dec', 'int'), # number of decimal places
        ('sr_order', 'int'), # int for sorting of sr fields..?
        ])

NUT_DATA_SCHEMA = ('NUT_DATA', list(range(3)), [
        ('ndb_no', 'int', 'not null'),
        ('nutr_no', 'int', 'not null'),
        ('nutr_val', 'float', 'not null'), # amount per 100 g
        ])

# TODO
# make long_desc 200 char
# make short_desc 60 char
FOOD_DESC_SCHEMA = ('FOOD_DES', [0, 1, 2, 3, 10, 11, 12, 13], [
        ('ndb_no', 'int', 'primary key'),
        ('food_group_code', 'int'),
        ('long_desc', 'text'),
        ('short_desc', 'text'),
        #('common_names', 'text'),
        ('nitrogen_factor', 'float'), # Factor for converting nitrogen to protein (see p. 11).
        ('protein_factor', 'float'), # Factor for calculating calories from protein (see p. 12).
        ('fat_factor', 'float'), # Factor for calculating calories from fat (see p. 12).
        ('carb_factor', 'float'), # Factor for calculating calories from carbohydrate (see p. 12).
        ])

# WARNING: These methods DON'T do escaping
def sqlstr_create_table(table_name, schema):
    s = ('CREATE TABLE ' + table_name + ' (' + ', '.join(' '.join(x) for x in schema) + ')')
    return s

def sqlstr_insert(table_name, num_values):
    s = ('INSERT INTO ' + table_name + ' values (' + ', '.join('?' * num_values) + ')')
    return s

conn = sqlite3.connect('food.db')
conn.text_factory = str
c = conn.cursor()

for full_schema in (NUTR_DEF_SCHEMA, NUT_DATA_SCHEMA, FOOD_DESC_SCHEMA):
    c.execute(sqlstr_create_table(full_schema[0],full_schema[2]))

    # NEED TO FIX 2nd PART UP
    with open(os.path.join(DATA, full_schema[0]+'.txt')) as f:
        reader = csv.reader(f, delimiter='^', quotechar='~')
        indexes = full_schema[1]

        row_converter = [(i, s[1]) for i, s in zip(indexes, full_schema[2])]
        rows = []
        for r in reader:
            # WARNING we've got an eval here. This should be 
            # converting schema types into python types. if it's not we're in trouble!
            row = tuple(None if not r[i] else eval(typeclass)(r[i]) for i, typeclass in row_converter)
            rows.append(row)

        #c.execute(sqlstr_insert(full_schema[0], len(full_schema[2])), rows[0])
        c.executemany(sqlstr_insert(full_schema[0], len(full_schema[2])), rows)

c.close()
