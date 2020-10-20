import pymysql
import os
import sys
import logging


def getConnection():
	try:
		conn = pymysql.connect(
			user=os.environ['Llama_Discord_Bot_SQL_Username'],
			password=os.environ['Llama_Discord_Bot_SQL_Password'],
			host=os.environ['Llama_Discord_Bot_SQL_Host'],
			port=3306,
			database=os.environ['Llama_Discord_Bot_SQL_Database']
		)

		return conn
	except pymysql.Error as e:
		logging.error('SQL Connection error: %s', e)
		return
