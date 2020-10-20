import pymysql
import os
import sys
import logging

def getConnection():
	try:
		conn = pymysql.connect(
			user=os.environ['Llama-Discord-Bot-SQL-Username'],
			password=os.environ['Llama-Discord-Bot-SQL-Password'],
			host=os.environ['Llama-Discord-Bot-SQL-Host'],
			port=3306,
			database=os.environ['Llama-Discord-Bot-SQL-Database']
		)

		return conn
	except pymysql.Error as e:
		logging.error('SQL Connection error: %s', e)
		return