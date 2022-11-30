import lxml.etree
from typing import List, Iterable, Optional
from dataclasses import dataclass

# todo
# Make output pretty

NAMESPACE = "{http://www.hmdb.ca}"

@dataclass
class MetaboliteData:
    name: str
    abundance_in_blood: str
    melting_point: str
    boiling_point: str
    solubility: str
    logp: str
    weight: str

    def __str__(self):
        return f'"{self.name}", "{self.abundance_in_blood}", "{self.melting_point}", "{self.boiling_point}", "{self.solubility}", "{self.logp}", "{self.weight}"'
    
    @staticmethod
    def get_header_line():
        return "Name,Abundance in Blood,Melting Point,Boiling Point,Solubility,LogP,Weight\n"

def scrape_metabolite_data(metabolite_tag: lxml.etree._Element) -> Optional[MetaboliteData]:
    # Get the name
    metabolite_name = metabolite_tag.find(NAMESPACE + "name").text

    try:
        blood_conc_tag = next(filter(lambda conc_tag: conc_tag.find(NAMESPACE + "biospecimen").text == "Blood" and conc_tag.find(NAMESPACE + "concentration_value").text is not None, metabolite_tag.find(NAMESPACE + "normal_concentrations").findall(NAMESPACE + "concentration")))
    except:
        return None
    metabolite_abundance_in_blood = blood_conc_tag.find(NAMESPACE + "concentration_value").text + " " + blood_conc_tag.find(NAMESPACE + "concentration_units").text
    
    metabolite_weight = metabolite_tag.find(NAMESPACE + "average_molecular_weight").text
    try:
        metabolite_melting_point = next(filter(lambda property_tag: property_tag.find(NAMESPACE + "kind").text == "melting_point", metabolite_tag.find(NAMESPACE + "experimental_properties").findall(NAMESPACE + "property"))).find(NAMESPACE + "value").text
    except:
        metabolite_melting_point = "N/A"

    try:
        metabolite_boiling_point = next(filter(lambda property_tag: property_tag.find(NAMESPACE + "kind").text == "boiling_point", metabolite_tag.find(NAMESPACE + "experimental_properties").findall(NAMESPACE + "property"))).find(NAMESPACE + "value").text
    except:
        metabolite_boiling_point = "N/A"

    try:
        metabolite_solubility = next(filter(lambda property_tag: property_tag.find(NAMESPACE + "kind").text == "water_solubility", metabolite_tag.find(NAMESPACE + "experimental_properties").findall(NAMESPACE + "property"))).find(NAMESPACE + "value").text
    except:
        # TODO: not that this is predicted
        try:
            metabolite_solubility = next(filter(lambda property_tag: property_tag.find(NAMESPACE + "kind").text == "solubility", metabolite_tag.find(NAMESPACE + "predicted_properties").findall(NAMESPACE + "property"))).find(NAMESPACE + "value").text
        except:
            metabolite_solubility = "N/A"

    try:
        metabolite_logp = next(filter(lambda property_tag: property_tag.find(NAMESPACE + "kind").text == "logp", metabolite_tag.find(NAMESPACE + "experimental_properties").findall(NAMESPACE + "property"))).find(NAMESPACE + "value").text
    except:
        # TODO: not that this is predicted
        try:
            metabolite_logp = next(filter(lambda property_tag: property_tag.find(NAMESPACE + "kind").text == "logp", metabolite_tag.find(NAMESPACE + "predicted_properties").findall(NAMESPACE + "property"))).find(NAMESPACE + "value").text
        except:
            metabolite_logp = "N/A"

    return MetaboliteData(metabolite_name, metabolite_abundance_in_blood, metabolite_melting_point, metabolite_boiling_point, metabolite_solubility, metabolite_logp, metabolite_weight)

def main():
    data_table: List[MetaboliteData] = []
    for metabolite_tag in lxml.etree.parse("./serum_metabolites.xml").getroot().getchildren():
        metabolite_data: Optional[MetaboliteData] = scrape_metabolite_data(metabolite_tag)
        if metabolite_data is not None:
            data_table.append(metabolite_data)

    with open("out.csv", "w") as f:
        f.write(MetaboliteData.get_header_line())
        f.write("\n".join(str(metabolite_data) for metabolite_data in data_table))

if __name__ == "__main__":
    main()
