import os
import pandas 
from requests import get
from bs4 import BeautifulSoup
from contextlib import closing
from requests.exceptions import RequestException

def good_respons(e):  
	# Returns True if the response seems to be HTML, False otherwise.
    content_type = e.headers['Content-Type'].lower()
    return (e.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)

def basically_a_con(dom, stream=False):  
	# Attempts to get the content at `url` (dom) by making an HTTP GET request.
    try:
        if stream:
            with closing(get(dom, stream=stream)) as e:
				# If the content-type of response is some kind of HTML/XML
                if good_respons(e):  
					# return the text content
                    return e.content  
        else:
            with closing(get(dom, stream=True)) as e:
                if good_respons(e):  # If the content-type of response is some kind of HTML/XML
                    return e.content  # return the text content
    except RequestException as e:  # otherwise return None
        raise Exception(f'Error during requests to {dom} : {e}')

def pull_group_details(base_url):
	'''
	inputs:
	> base_url (str)
		>> url to group of interest

	outputs: 
	> many_datas (list)
		>> group name
		>> location 
		>> base_url
		>> and members 
		'''
	# pull the url
	response = basically_a_con(base_url)
	# url accessibility check
	if response is not None:  
		html = BeautifulSoup(response, 'html.parser')
		many_datas = []
		# pull group name
		pull_name = "a.groupHomeHeader-groupNameLink"
		# pull group locatino 
		pull_location = '.groupHomeHeaderInfo-cityLink span'
		# pull group members
		pull_members = '.groupHomeHeaderInfo-memberLink span'
		# go through all datapoints to pull
		for info_bit in [pull_name, pull_location, base_url, pull_members]:
			if info_bit == base_url:
				many_datas.append(base_url)
			else:
				# focus data point
				for ul in html.select(info_bit):  
					# in case there's multiple
					for info in ul.text.split('\n'):
						# make sure something is here
						if len(info) > 0:
							# is this the members?
							if info_bit != pull_members:
								# clean it up and add it to set
								many_datas.append(info.strip())
							# this is the members
							else:
								# clean it up and add it to set
								many_datas.append(int(info.strip().split(' ')[0].replace(',', '')))
		# output group info
		return many_datas
    # we failed to get any data from the url
	raise Exception(f'Error retrieving new_listings_on_base_page_to_scrape at {base_url}')

if __name__=='__main__':
	def run(city_groups, city_name):
		# collect multiple group's info
		output = []
		# go through groups
		for group in city_groups:
			# pull group info 
			run = pull_group_details(group)
			# add group info to final output
			output.append(run)
		# make dataframe from groups
		df = pandas.DataFrame(output, columns=['Meetup Name', 'Location', 'Link', 'Members'])
		# record groups to data dir
		df.to_csv(f'data/{city_name}_groups.csv', index=False)
	# import city lists
	from city_lists import atl_groups, austin_groups, boston_groups, dallas_groups, denver_groups, houston_groups, lax_groups, miami_groups, san_antonio_groups, san_diego_groups, sfo_groups
	# collect cities & names/aliases
	cities = [atl_groups, austin_groups, boston_groups, dallas_groups, denver_groups, houston_groups, 
			  lax_groups, miami_groups, san_antonio_groups, san_diego_groups, sfo_groups]
	names = ['atlanta', 'austin', 'boston', 'dallas', 'denver', 'houston', 
			 'los_angeles', 'miami', 'san_antonio', 'san_diego', 'sfo']
	# go through the lists
	for i in range(len(cities)):
		# and run each city
		run(cities[i], names[i])
