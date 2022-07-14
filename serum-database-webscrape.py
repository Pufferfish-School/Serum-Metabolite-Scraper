from bs4 import BeautifulSoup
import requests
#import ben's

def get_url(link):
	return requests.get(link)

def get_names(parsed):
	parsed_names = parsed.find_all("td", class_="metabolite-name")
	names = []
	for name in parsed_names:
		names.append(name.get_text().strip())
	return names

def get_links(parsed):
	parsed_links = parsed.find_all("td", class_="metabolite-link")
	links = []
	for link in parsed_links:
		link = link.find("a")
		link = link.get("href")
		links.append(link)
	return links

#this does not separate out abundance by which compound it is.  most compounds have many abundances.  still need to construct a list within 'abundances' per molecule
def find_abundances(links):
	abundances = []
	for i in range(len(links)):
		link = get_url(links[i])
		found_one = False
		abundances.append([])
		parsed_webpage = BeautifulSoup(link.content, 'html.parser')
		parsed_webpage = parsed_webpage.find_all("table", class_="table table-condensed table-striped concentrations")
		parsed_webpage = parsed_webpage[0].find_all("tbody")
		parsed_webpage = parsed_webpage[0].find_all("tr")
		for page in parsed_webpage:		
			page = page.find_all("td")
			found_one = True
			abundances[i].append(page[2].text)
		if not found_one:
			abundances.append("detected and quantified measurement not found")
	return abundances

def get_structure_link(parsed):
	parsed_struct = parsed.find_all("td", class_="metabolite-structure")
	links = []
	for link in parsed_struct:
		link = link.find("img")
		link = link.get("src")
		link = "https://serummetabolome.ca" + link
		links.append(link)
	return links

def get_structures(parsed, names):
	links = get_structure_link(parsed)
	# print(links)
	structures_filenames = []
	for i in range(len(links)):
		webpage = requests.get(links[i])
		filename = names[i]
		with open(filename, 'wb') as f:
			f.write(webpage.content)
		structures_filenames.append(filename)
	return structures_filenames

def find_weights(links):
	weights = []
	for link in links:
		link = get_url(link)
		parsed_webpage = BeautifulSoup(link.content, 'html.parser')
		parsed_webpage = parsed_webpage.find("table", class_="content-table table table-condensed table-bordered")
		parsed_webpage = parsed_webpage.find_all("th")
		text = "Monoisotopic Molecular Weight"
		for tags in parsed_webpage:
			print(tags)
			if tags.string == text:
				parsed_webpage = tags.find_next_siblings("td")
				for whatever in parsed_webpage:
					weights.append(whatever.text)
				break
	return weights

def find_boilingpoint(links):
	boilingpoints = []
	for link in links:
		link = get_url(link)
		parsed_webpage = BeautifulSoup(link.content, 'html.parser')
		parsed_webpage = parsed_webpage.find("table", class_="content-table table table-condensed table-bordered")
		parsed_webpage = parsed_webpage.find_all("th")
	return boilingpoints

def make_data_table(names, links, structures_filenames, weights):
	listy = []
	for i in range(len(names)):
		listy.append([names[i], links[i], structures_filenames[i], weights[i], abundances[i]])
	return listy

def main():
	url_obj = get_url('https://serummetabolome.ca/metabolites?utf8=%E2%9C%93&c=hmdb_id&d=up&quantified=1&filter=true')
	parsed = BeautifulSoup(url_obj.content, 'html.parser')
	
	names = get_names(parsed)
	# structures_filenames = get_structures(parsed, names)
	links = get_links(parsed)
	# abundances = find_abundances(links)
	# weights = find_weights(links)
	boilingpoints = find_boilingpoint(links)

	# data_table = make_data_table(names, links, structures_filenames, weights, abundances)
	print("names:", len(names))
	print("abundances", len(abundances))
	for i in range(len(names)):
		print(names[i], ":", boilingpoints[i])


if __name__ == '__main__':
	main()