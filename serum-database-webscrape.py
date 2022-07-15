from bs4 import BeautifulSoup
import requests
#import ben's
#todo
#1. DONE get the page for each metabolite once, and soup it once
#2. make output pretty
#2.5 WITH images
#3. DONE generalize to all pages on hsm

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
		link = get_url(link)
		link = BeautifulSoup(link.content, 'html.parser')
		links.append(link)
	return links

def get_structure_link(parsed):
	parsed_struct = parsed.find_all("td", class_="metabolite-structure")
	links = []
	for link in parsed_struct:
		link = link.find("img")
		link = link.get("src")
		link = "https://serummetabolome.ca" + link
		links.append(link)
	return links

# uncomment to get images saved
def get_structures(parsed, names):
	links = get_structure_link(parsed)
	structures_filenames = []
	for i in range(len(links)):
		webpage = requests.get(links[i])
		filename = names[i]
		# with open(filename + ".svg", 'wb') as f:
		# 	f.write(webpage.content)
		structures_filenames.append(filename)
	return structures_filenames

def find_abundances(links):
	abundances = []
	for i in range(len(links)):
		found_one = False
		abundances.append([])
		parsed_webpage = links[i].find_all("table", class_="table table-condensed table-striped concentrations")
		parsed_webpage = parsed_webpage[0].find_all("tbody")
		parsed_webpage = parsed_webpage[0].find_all("tr")
		for page in parsed_webpage:		
			page = page.find_all("td")
			found_one = True
			abundances[i].append(page[2].text)
		if not found_one:
			abundances.append("detected and quantified measurement not found")
	return abundances

def find_weights(links):
	weights = []
	for link in links:
		parsed_webpage = link.find("table", class_="content-table table table-condensed table-bordered")
		parsed_webpage = parsed_webpage.find_all("th")
		text = "Monoisotopic Molecular Weight"
		for tags in parsed_webpage:
			if tags.string == text:
				parsed_webpage = tags.find_next_siblings("td")
				for whatever in parsed_webpage:
					weights.append(whatever.text)
				break
	return weights

def find_bp_mp_sol(links):
	boilingpoint = []
	meltingpoint = []
	solubility = []
	for link in links:
		parsed_webpage = link.find("table", class_="table table-bordered")
		parsed_webpage = parsed_webpage.find("tbody")
		parsed_webpage = parsed_webpage.find_all("td")
		meltingpoint.append(parsed_webpage[1].text)
		boilingpoint.append(parsed_webpage[2].text)
		solubility.append(parsed_webpage[7].text)
	return meltingpoint, boilingpoint, solubility	

def make_data_table(names, links, structures_filenames, weights):
	listy = []
	for i in range(len(names)):
		listy.append([names[i], links[i], structures_filenames[i], weights[i], abundances[i]])
	return listy

def main():
	for i in range(1, 154):
		url_obj = get_url('https://serummetabolome.ca/metabolites?c=hmdb_id&d=up&filter=true&page=' + str(i) + '&quantified=1')
		parsed = BeautifulSoup(url_obj.content, 'html.parser')
		
		names = get_names(parsed)
		structures_filenames = get_structures(parsed, names)
		links = get_links(parsed)
		abundances = find_abundances(links)
		weights = find_weights(links)
		meltingpoint, boilingpoint, solubility = find_bp_mp_sol(links)

		# data_table = make_data_table(names, links, structures_filenames, weights, abundances)
		print("names:", len(names))
		for i in range(len(names)):
			print(names[i])
			print("abundance:", abundances[i])
			print("mw:", weights[i])
			print("meltingpoint:", meltingpoint[i])
			print("boilingpoint:", boilingpoint[i])
			print("solubility:", solubility[i])


if __name__ == '__main__':
	main()