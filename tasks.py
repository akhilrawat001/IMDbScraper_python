
import requests
import bs4
import json
import os.path
import random
import time
import pprint

#Task 1
def scrape_top_list():
	url = 'https://www.imdb.com/india/top-rated-indian-movies/?ref_=nv_mv_250_in.'
	raw = requests.get(url)
	soup = bs4.BeautifulSoup(raw.text,'html.parser')
	tds = soup.find_all('td' , class_ = 'titleColumn')
	div = soup.find('div' , class_ = "article")
	tbody = div.find('tbody', class_= "lister-list")
	trs = tbody.find_all('tr')
	movies = []
	for i in range(len(tds)):
		#for links
		td = tds[i]
		link = "https://www.imdb.com" + td.find('a').get('href')
		tr = trs[i]
		#rating
		rating = float(tr.find('strong').getText())
		#name
		name = str(td.find('a').getText())
		#years
		year = int(td.find('span').getText()[1:5])
		movie_dict = {}
		movie_dict['name'] = name
		movie_dict['year'] = year
		movie_dict['position'] = i+1
		movie_dict['rating'] = rating
		movie_dict['url'] = link
		movies.append(movie_dict.copy())
	return movies

top_movies = scrape_top_list()

#Task 2
def group_by_year(movies):
	movie_dict_by_year = {movie["year"]:[]for movie in movies}
	for movie in movies:
		year = movie["year"]
		movie_dict_by_year[year].append(movie)
	return(movie_dict_by_year)
# pprint.pprint(group_by_year(top_movies))

#Task 3
def group_by_decade(movies):
	movie_by_year = group_by_year(movies)
	distinct_years = []
	for distinct_year in movie_by_year:
		distinct_years.append(distinct_year)
	start_range = str(min(distinct_years))[::-1]
	start_range = int(start_range.replace(start_range[0],'0',1)[::-1])
	end_range = str(max(distinct_years))[::-1]
	end_range = int(end_range.replace(end_range[0],'0')[::-1])
	grouped_by_decade_dict = {decade_start:[] for decade_start in range(start_range,end_range+10,10)}
	for distinct_year in movie_by_year:
		same_year_movies = movie_by_year[distinct_year]
		for decade in grouped_by_decade_dict:
			if distinct_year in range(decade,decade+10):
				grouped_by_decade_dict[decade] += same_year_movies
	return(grouped_by_decade_dict)
# pprint.pprint(group_by_decade(top_movies))
#Task 12
def scrape_movie_cast(movie_cast_url):
	m_url = movie_cast_url[:37]
	file_name = m_url[-10:-1] + '_cast' '.json'
	#checking if file exists or not
	value = os.path.exists('cast_cache/' + file_name)
	#if file exists
	if value == True:
		json_data = open('cast_cache/' + str(file_name)).read()
		data = json.loads(json_data)
		return data
	#if file dose not exists
	else:#create file
		url = movie_cast_url
		# sec = random.randint(1,3)
		raw = requests.get(url)
		soup = bs4.BeautifulSoup(raw.text, 'html.parser')
		json_data = raw.text
		# time.sleep(sec)
		#Writing data to json file
		table_data= soup.find('table' , class_ = 'cast_list')
		actors = table_data.findAll('td', class_ = "")
		cast_list = []
		for actor in actors:
			actor_dict = {}
			imdb_id = actor.find('a').get('href')[6:15]
			name = actor.getText().strip()
			actor_dict['imdb_id'] = str(imdb_id)
			actor_dict['name'] = str(name)
			cast_list.append(actor_dict.copy())
		json_data = cast_list[:]
		with open('cast_cache/' + str(file_name),'w+') as file:
			json.dump(json_data,file)
	return cast_list

#Task 4 and Task 8 and Task 9 and Task 13
def scrape_movie_details(movie_url):
	m_url = movie_url[:37]
	file_name = m_url[-10:-1] + '.json'
	#checking if file exists or not
	value = os.path.exists('movies_cache/' + file_name)
	#if file exists
	if value == True:
		json_data = open('movies_cache/' + str(file_name)).read()
		data = json.loads(json_data)
		return data
	#if file dose not exists
	else:#create file
		url = movie_url
		# sec = random.randint(1,3)
		raw = requests.get(url)
		# time.sleep(sec)
		soup = bs4.BeautifulSoup(raw.text, 'html.parser')
	movie_details_dict = {}
	#name
	name = soup.find('h1').getText()[:-8]
	movie_details_dict['name'] = name
	#bio
	bio = soup.find('div' ,class_= 'summary_text').getText().strip()
	bio_director = soup.find('div' ,class_= 'plot_summary').getText().split('\n')
	bio = bio_director[2].strip()
	movie_details_dict['bio'] = bio
	#directors
	directors = bio_director[6]
	if ',' in directors:
	    directors = bio_director[6].split(',')
	    for d in range(len(directors)):
	    	if '|' in directors[d]:
	    		directors[d] = directors[d].strip("|").strip()
	else:
	    directors =[directors]
	for director in range(len(directors)):
		directors[director] = directors[director].strip()
	movie_details_dict['director'] = directors[:]

	#genre
	divs = soup.findAll('div', class_="see-more inline canwrap")
	for div in divs:
		if 'Genre' in div.getText():
			a_tags = div.findAll('a')
			movie_details_dict['genre'] = [a.getText().strip() for a in a_tags]
	#poster image url
	img_div = soup.find_all('div',class_ = 'poster')
	img_tag = img_div[0].find('img')
	poster_link = img_tag['src']
	movie_details_dict['poster_image_url'] = poster_link
	#runtime
	runtimes = soup.findAll("time")
	runtime = runtimes[-1].getText().strip()
	if 'h' not in runtime:
		movie_details_dict['runtime'] = runtime[:3]
	elif 'h'in runtime  and 'min'in runtime:
		movie_details_dict['runtime'] = int(runtime[0])*60 + int(runtime[3:-3])
	elif 'h'in runtime:
		movie_details_dict['runtime'] = int(runtime[0])*60

	divs =  soup.findAll('div', {'id': 'titleDetails'})
	for div in divs:
		s_div = div.find_all('div', class_='txt-block')
	#langague
	movie_details_dict['language'] = []
	for div in s_div:
		if 'Language' in div.getText():
			a_tags = (div.findAll('a'))
	for a in a_tags:
		movie_details_dict['language'].append(a.getText().strip())
	#country
	for div in s_div:
		if 'Country' in div.getText():
			a_tags = (div.findAll('a'))
	for a in a_tags:
		movie_details_dict['country'] = a.getText().strip()
	#cast
	movie_url = movie_url[:37] + 'fullcredits?ref_=tt_cl_sm#cast'
	cast = scrape_movie_cast(movie_url)
	movie_details_dict['cast'] = cast
	json_data = movie_details_dict.copy()
	with open('movies_cache/' + str(file_name),'w+') as file:
		json.dump(json_data,file)
	return movie_details_dict

#Task 5
def get_movie_list_details(movie_list):
	movie_d_list = []
	# t = 1
	for movie_dict in movie_list:
		url = movie_dict['url']
		details = scrape_movie_details(url)
		movie_d_list.append(details)
		# print(t)
		# t = t + 1
	return movie_d_list
movies_detail_list = get_movie_list_details(top_movies[:])
# pprint.pprint(movies_detail_list)

#Task 6
def analyse_movies_language(movies_list):
	language_list = []
	for movie in movies_list:
		for language in movie['language']:
			if language not in language_list:
				language_list.append(language)
	language_dict = {language : 0 for language in language_list}
	for language in language_list:
		for movie in movies_list:
			if language in movie['language']:
				language_dict[language] += 1
	return(language_dict)
# language_analysis = analyse_movies_language(movies_detail_list)
# print(language_analysis)

#Task 7
def analyse_movies_directors(movies_list):
	director_list = []
	for movie in movies_list:
		for director in movie['director']:
			if director not in director_list:
				director_list.append(director)
	director_dict = {director : 0 for director in director_list}
	for director in director_list:
		for movie in movies_list:
			if director in movie['director']:
				director_dict[director] += 1
	return(director_dict)
# director_analysis = analyse_movies_directors(movies_detail_list)
# pprint.pprint(director_analysis)

#Task 10
def analyse_language_and_directors(movies_list):
	directors_dict = analyse_movies_directors(movies_list)
	directors_lang = {director:{} for director in directors_dict}
	for i in range(len(movies_list)):
		for director in directors_lang:
			if director in movies_list[i]['director']:
				for language in movies_list[i]['language']:
					directors_lang[director][language] = 0
	for i in range(len(movies_list)):
		for director in directors_lang:
			if director in movies_list[i]['director']:
				for language in movies_list[i]['language']:
					directors_lang[director][language] += 1
	return directors_lang
# director_language = analyse_language_and_directors(movies_detail_list)
# pprint.pprint(director_language)

#Task 11
def analyse_movies_genre(movies_list):
	genre_list = []
	for movie in movies_list:
		for genre in movie['genre']:
			if genre not in genre_list:
				genre_list.append(genre)
	genre_dict = {genre : 0 for genre in genre_list}
	for genre in genre_list:
		for movie in movies_list:
			if genre in movie['genre']:
				genre_dict[genre] += 1
	return(genre_dict)
# genre_analysis = analyse_movies_genre(movies_detail_list)
# pprint.pprint(genre_analysis)

#Task 14
def analyse_co_actors(movies_list):
	main_actors = []
	for movies in movies_list:
		main_actors.append(movies['cast'][0])
	# pprint.pprint(main_actors)
	co_actors_dict = {actor['imdb_id'] : {'name' : actor['name'],'frequent_co_actors':[]} for actor in main_actors}
	# pprint.pprint(co_actors_dict)
	all_actors = []
	co_actors = []
	for movie in movies_list:
		temp_actors = []
		for actor in movie['cast'][:5]:
			actor['num_movies'] = 1
			temp_actors.append(actor)
		all_actors.append(temp_actors)
	# pprint.pprint(all_actors)
	for main_actor_dict in main_actors:
		for actors_list in all_actors:
			if main_actor_dict in actors_list:
				main_id = main_actor_dict['imdb_id']
				co_actor_list = co_actors_dict[main_id]['frequent_co_actors']
				for actor in actors_list[1:]:
					if actor not in co_actor_list:
						co_actor_list.append(actor)
					else:
						co_actor_list[co_actor_list.index(actor)]['num_movies'] += 1

	for actor_id in co_actors_dict:
		for actor in co_actors_dict[actor_id]['frequent_co_actors']:
			if actor_id == actor['imdb_id']:
				co_actors_dict[actor_id]['frequent_co_actors'].pop(co_actors_dict[actor_id]['frequent_co_actors'].index(actor))
	return co_actors_dict
# pprint.pprint(analyse_co_actors(movies_detail_list))

#Task 15
def analyse_actors(movies_list):
	all_actors = []
	for movie in movies_list:
		cast_list = movie['cast']
		for actor in cast_list:
			all_actors.append(actor)
	all_actors_dict = {actor['imdb_id'] : {'name': actor['name'],'num_movies':0} for actor in all_actors}

	for actor in all_actors_dict:
		for actors in all_actors:
			if actors['imdb_id'] == actor:
				all_actors_dict[actor]['num_movies'] += 1
	actors_dict = {}
	for actor in all_actors_dict:
		if all_actors_dict[actor]['num_movies'] > 1:
			actors_dict[actor] = all_actors_dict[actor]
	return actors_dict

pprint.pprint(analyse_actors(movies_detail_list))
