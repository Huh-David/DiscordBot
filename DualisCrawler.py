# Most of this code is from https://github.com/KarelZe/dualis
# We adjusted it to work with the current version of dualis

import itertools
from concurrent import futures

import requests
from bs4 import BeautifulSoup
from werkzeug.exceptions import abort
import json
import os
import asyncio

BASE_URL = "https://dualis.dhbw.de"
units = []


async def get_grades(user, password):
	# create a session
	url = BASE_URL + "/scripts/mgrqispi.dll"
	cookie_request = requests.post(url)

	data = {"usrname": user, "pass": password,
			"APPNAME": "CampusNet",
			"PRGNAME": "LOGINCHECK",
			"ARGUMENTS": "clino,usrname,pass,menuno,menu_type, browser,platform",
			"clino": "000000000000001",
			"menuno": "000324",
			"menu_type": "classic",
			"browser": "",
			"platform": ""
			}
	# return dualis response code, if response code is not 200
	login_response = requests.post(url, data=data, headers=None, verify=True, cookies=cookie_request.cookies)
	arguments = login_response.headers['REFRESH']
	if not login_response.ok:
		abort(login_response.status_code)

	# redirecting to course results...
	url_content = BASE_URL + "/scripts/mgrqispi.dll?APPNAME=CampusNet&PRGNAME=COURSERESULTS&ARGUMENTS=" + arguments[84:]
	# url_content = url_content.replace("STARTPAGE_DISPATCH", "COURSERESULTS")
	semester_ids_response = requests.get(url_content, cookies=login_response.cookies)
	if not semester_ids_response.ok:
		abort(semester_ids_response.status_code)

	# get ids of all semester, replaces -N ...
	soup = BeautifulSoup(semester_ids_response.content, 'html.parser')
	options = soup.find_all('option')
	semester_ids = [option['value'] for option in options]
	semester_urls = [url_content[:-15] + semester_id for semester_id in semester_ids]

	# search for all unit_urls in parallel
	with futures.ThreadPoolExecutor(8) as semester_pool:
		tmp = semester_pool.map(parse_semester, semester_urls, [login_response.cookies] * len(semester_urls))
	unit_urls = list(itertools.chain.from_iterable(tmp))

	# query all unit_urls to obtain grades in parallel
	with futures.ThreadPoolExecutor(8) as detail_pool:
		semester = detail_pool.map(parse_unit, unit_urls, [login_response.cookies] * len(unit_urls))
	units.extend(semester)

	# Create valid json
	jsonString = str(units).replace('\'', '"').replace('\\xa0', '').replace('True', 'true').replace('False', 'false')

	# find logout url in html source code and logout
	logout_url = BASE_URL + soup.find('a', {'id': 'logoutButton'})['href']
	logout(logout_url, cookie_request.cookies)
	# return dict containing units and exams as valid json

	# Change json format from object to key-value with key = Module name and value = [exams]
	resDict = json.loads(jsonString)
	dict2 = {}

	for obj in resDict:
		dict2[obj["name"]] = obj["exams"]

	# Do the same formatting shit again because python is crap
	return json.loads(str(dict2).replace('\'', '"').replace('True', 'true').replace('False', 'false'))


def parse_student_results(url, cookies):
	"""
	This function calls the dualis web page of a given semester to query for all modules, that have been finished.
	:param url: url of STUDENT_RESULT page
	:param cookies: cookie of current session
	:return: list of urls for units
	"""
	response = requests.get(url=url, cookies=cookies)
	student_result_soup = BeautifulSoup(response.content, "html.parser")
	table = student_result_soup.find("table", {"class": "students_results"})
	return [a['href'] for a in table.find_all("a", href=True)]


def parse_semester(url, cookies):
	"""
	function calls the dualis web page of a given a semester to extract the urls of all units within the semester.
	It's searching for script-tags containing the urls and crops away the surrounding javascript.
	:param url: url of the semester page
	:param cookies: cookie for the semester page
	:return: list with urls of all units in semester
	"""
	semester_response = requests.get(url, cookies=cookies)
	semester_soup = BeautifulSoup(semester_response.content, 'html.parser')
	table = semester_soup.find("table", {"class": "list"})
	# get unit details from javascript
	returnStuff = [str(script).strip()[398:514] for script in table.find_all("script")]
	return returnStuff


def parse_unit(url, cookies):
	"""
	function calls the dualis webpage of a given module to extract the grades
	:param url: url for unit page
	:param cookies: cookie for unit page
	:return: unit with information about name and exams incl. grades
	"""
	response = requests.get(url=BASE_URL + url, cookies=cookies)
	detail_soup = BeautifulSoup(response.content, "html.parser")
	h1 = detail_soup.find("h1").text.strip()
	table = detail_soup.find("table", {"class": "tb"})
	td = [td.text.strip() for td in table.find_all("td")]
	unit = {'name': h1.replace("\n", " ").replace("\r", ""), 'exams': []}
	# units have non uniform structure. Try to map based on total size.
	if len(td) <= 24:
		exam = {'name': td[13], 'date': td[14], 'grade': td[15], 'externally accepted': False}
		unit['exams'].append(exam)
	elif len(td) <= 29:
		exam = {'name': td[19], 'date': td[14], 'grade': td[21], 'externally accepted': False}
		unit['exams'].append(exam)
	elif len(td) == 30:
		for idx in range(13, len(td) - 5, 6):
			exam = {'name': td[idx], 'date': td[idx + 1], 'grade': td[idx + 2], 'externally accepted': False}
			unit['exams'].append(exam)
	elif len(td) <= 31:
		for idx in range(11, len(td) - 7, 7):
			exam = {'name': td[idx], 'date': td[idx + 3], 'grade': td[idx + 4], 'externally accepted': False}
			unit['exams'].append(exam)
	else:
		for idx in range(19, len(td) - 5, 6):
			exam = {'name': td[idx], 'date': td[14], 'grade': td[idx + 2], 'externally accepted': False}
			unit['exams'].append(exam)
	return unit


def logout(url, cookies):
	"""
	Function to perform logout in dualis.dhbw.de
	:param url: url to perform logout
	:param cookies: cookie with session information
	:return: boolean whether logging out was successful
	"""
	return requests.get(url=url, cookies=cookies).ok


async def grade_available(module):
	grades = await get_grades(os.environ['PADDY_DHBW_USER'], os.environ['PADDY_DHBW_PASSWORD'])
	#print(grades)
	for grade in grades:
		if module in grade:
			return "Grade available! Log in at https://dualis.dhbw.de now!" if grades[grade][0]['grade'] != 'noch nicht gesetzt' else "Grade not available yet :/"
	return "I don't know this module. Please check if the module name is correct. You can provide the ID (e.g. T3INF1000) or the name (e.g. Programmieren)."


if __name__ == '__main__':
	print(asyncio.run(grade_available('Programmieren')))
