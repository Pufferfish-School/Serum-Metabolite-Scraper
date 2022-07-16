from bs4 import BeautifulSoup
import requests
import collections
import multiprocessing

# import ben's

# todo
# 1. DONE get the page for each metabolite once, and soup it once
# 2. make output pretty
# 2.5 WITH images
# 3. DONE generalize to all pages on hsm

URL = "https://serummetabolome.ca/metabolites"
PAGE_MAX = 154


def get_metabolite_names(outer_webpage, data_table):
    """Grabs the metabolite names from the outer webpage and sticks them in the data table."""
    for name_tag in outer_webpage.find_all("td", class_="metabolite-name"):
        data_table[name_tag.get_text().strip()] = {}


def get_structure_image_links(outer_webpage, data_table):
    """Grabs the metabolite image links from the outer webpage and sticks them in the data table."""
    structure_tags = outer_webpage.find_all("td", class_="metabolite-structure")
    for name, structure_tag in zip(data_table.keys(), structure_tags):
        img = structure_tag.find("img")
        src = img.get("src")
        data_table[name]["structure_image_link"] = "https://serummetabolome.ca" + src


def get_metabolite_webpages(outer_webpage):
    """Get the metabolite webpages. It's gross, but we do this with a genexpr
    to avoid having all the webpages in memory at once."""
    return (
        BeautifulSoup(
            requests.get(link_tag.find("a").get("href")).content, "html.parser"
        )
        for link_tag in outer_webpage.find_all("td", class_="metabolite-link")
    )


def get_abundances(metabolite_webpage, data_table_row):
    """Get the abundances for one metabolite."""

    # The page has 2 tables; one for normal concentrations, and another for abnormal concentrations.
    # We want normal concentrations.
    conc_tables = metabolite_webpage.find_all(
        "table", class_="table table-condensed table-striped concentrations"
    )

    if not 1 <= len(conc_tables) <= 2:
        return

    data_table_row["abundances"] = []

    normal_conc_table = conc_tables[0]
    conc_table_rows = normal_conc_table.find("tbody").find_all("tr")
    for conc_table_row in conc_table_rows:
        conc_row_entries = conc_table_row.find_all("td")
        assert len(conc_row_entries) == 8

        # A concentration table row looks like this:
        # Biospecimen | Status | Value | Age | Sex | Condition | Reference | Details
        data_table_row["abundances"].append(
            {
                "biospecimen": conc_row_entries[0].text,
                "status": conc_row_entries[1].text,
                "value": conc_row_entries[2].text,
                "age": conc_row_entries[3].text,
                "sex": conc_row_entries[4].text,
                "condition": conc_row_entries[5].text,
            }
        )


def get_weight(metabolite_webpage, data_table_row):
    """Get the weight of one metabolite."""

    property_table = metabolite_webpage.find(
        "table", class_="content-table table table-condensed table-bordered"
    )
    if property_table is None:
        return

    property_table_headers = property_table.find_all("th")
    if property_table_headers is None:
        return

    weight_headers = list(
        filter(
            lambda h: h.string == "Monoisotopic Molecular Weight",
            property_table_headers,
        )
    )
    assert len(weight_headers) == 1

    weight_header = weight_headers[0]
    weights = weight_header.find_next_siblings("td")
    assert len(weights[0]) == 1

    data_table_row["weight"] = weights[0].text


def get_metabolite_data(metabolite_webpage, data_table_row):
    """Get MP, BP, solubility, and logp for one metabolite."""

    # Should be 4 properties, each with a title, value, and source, so 12 entries in total
    property_table = metabolite_webpage.find("table", class_="table table-bordered")
    if property_table is None:
        return

    property_table_body = property_table.find("tbody")
    if property_table_body is None:
        return

    property_table_entries = property_table_body.find_all("td")

    assert len(property_table_entries) == 12

    data_table_row["melting point"] = property_table_entries[1].text
    data_table_row["boiling point"] = property_table_entries[4].text
    data_table_row["solubility"] = property_table_entries[7].text
    data_table_row["logp"] = property_table_entries[10].text


def get_data_from_outer_page(page_number):
    """Process one outer webpage."""

    data_table = collections.OrderedDict()
    http_response = requests.get(f"{URL}?quantified=1&page={page_number}")
    outer_webpage = BeautifulSoup(http_response.content, "html.parser")

    get_metabolite_names(outer_webpage, data_table)
    get_structure_image_links(outer_webpage, data_table)

    for name, metabolite_webpage in zip(
        data_table.keys(), get_metabolite_webpages(outer_webpage)
    ):
        get_metabolite_data(metabolite_webpage, data_table[name])
        get_abundances(metabolite_webpage, data_table[name])
        get_weight(metabolite_webpage, data_table[name])

    print(f"Done with page {page_number}")
    return data_table


def main():
    full_data_table = {}
    with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
        page_data_tables = pool.map(get_data_from_outer_page, range(1, PAGE_MAX + 1))

    for page_data_table in page_data_tables:
        full_data_table.update(page_data_table)

    with open("out.py", "w") as f:
        f.write("data=")
        f.write(str(full_data_table))


if __name__ == "__main__":
    main()
