import bs4
import requests

movie_url = 'https://www.imdb.com/title/tt0066763/?pf_rd_m=A2FGELUUNOQJNL&pf_rd_p=690bec67-3bd7-45a1-9ab4-4f274a72e602&pf_rd_r=QZ5DCNGC09S0Z9J9HBES&pf_rd_s=center-4&pf_rd_t=60601&pf_rd_i=india.top-rated-indian-movies&ref_=fea_india_ss_toprated_tt_1'
def get_cast(url):
	raw = requests.get(url)
	soup = bs4.BeautifulSoup(raw.text, 'html.parser')
	table_data= soup.find('table' , class_ = 'cast_list').getText().split("\n")
	cast_data = []
	for i in range(len(table_data)):
		table_data[i] = table_data[i].strip() 
	for i in table_data:
		if i in ['',' ',"..."]:
			continue
		elif i[0] == "(":
			continue
		elif i == 'Rest of cast listed alphabetically:':
			continue
		else:
			cast_data.append(i)
	cast = {}
	for i in range(0,len(cast_data),2):
		if i !=len(cast_data)-1:
			cast[cast_data[i]] = cast_data[i+1]
	print(cast)
	# return cast

def get_cast_url(movie_url):
	movie_url = movie_url[:37] + 'fullcredits?ref_=tt_cl_sm#cast'
	return movie_url
url = get_cast_url(movie_url)
cast = get_cast(url)
for i in cast:
	print(i + ' : '+ cast[i])