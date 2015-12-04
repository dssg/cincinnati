#!/usr/bin/env python

import tax_defs


"""
Generate a SQL query to fix the case sensitive column names
"""

tax_table = 'taxes_2015'
column_list = tax_defs.field_names_2015

for i in range(len(column_list)):
	print 'ALTER TABLE public.' + tax_table
	print 'RENAME COLUMN \"' + column_list[i] + '\" to ' + column_list[i] + ';'