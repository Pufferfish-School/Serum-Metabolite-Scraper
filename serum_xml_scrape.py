import lxml.etree
from typing import List, Iterable, Optional, Tuple
from dataclasses import dataclass
import re

# todo
# Do numbers
# Make experiment/predict distinction

NAMESPACE = "{http://www.hmdb.ca}"

@dataclass
class MetaboliteData:
    name: str
    abundance_in_blood: str
    melting_point: str
    boiling_point: str
    solubility: str
    logp: str
    weight: float

    def __str__(self):
        return f'"{self.name}","{self.abundance_in_blood}","{self.melting_point}","{self.boiling_point}","{self.solubility}","{self.logp}","{self.weight}"'
    
    @staticmethod
    def get_header_line():
        return '"Name","Abundance in Blood (uM)","Melting Point (°C)","Boiling Point (°C)","Solubility (mg/mL)","LogP","Monoisotopic Molecular Weight (Da)"\n'

def extract_property(metabolite_tag: lxml.etree._Element, property_group: str, property_name: str) -> str:
        try:
            result = next(filter(lambda property_tag: property_tag.find(NAMESPACE + "kind").text == property_name, metabolite_tag.find(NAMESPACE + property_group).findall(NAMESPACE + "property"))).find(NAMESPACE + "value").text
        except StopIteration:
            result = "N/A"
        return result

def scrape_metabolite_data(metabolite_tag: lxml.etree._Element) -> Optional[MetaboliteData]:
    # Get the name
    metabolite_name = metabolite_tag.find(NAMESPACE + "name").text

    try:
        blood_conc_tag = next(filter(lambda conc_tag: conc_tag.find(NAMESPACE + "biospecimen").text == "Blood" and conc_tag.find(NAMESPACE + "concentration_value").text is not None, metabolite_tag.find(NAMESPACE + "normal_concentrations").findall(NAMESPACE + "concentration")))
    except StopIteration:
        return None

    metabolite_abundance_in_blood = blood_conc_tag.find(NAMESPACE + "concentration_value").text

    if blood_conc_tag.find(NAMESPACE + "concentration_units").text != "uM":
        print(f"What the heck is this unit: {blood_conc_tag.find(NAMESPACE + 'concentration_units').text}")

    metabolite_weight = metabolite_tag.find(NAMESPACE + "monisotopic_molecular_weight").text
    if not metabolite_weight:
        metabolite_weight = "N/A"
    
    metabolite_melting_point = extract_property(metabolite_tag, "experimental_properties", "melting_point")
    metabolite_boiling_point = extract_property(metabolite_tag, "experimental_properties", "boiling_point")

    metabolite_solubility = extract_property(metabolite_tag, "experimental_properties", "water_solubility")
    if metabolite_solubility == "N/A":
        metabolite_solubility = extract_property(metabolite_tag, "predicted_properties", "solubility")
 
    metabolite_logp = extract_property(metabolite_tag, "experimental_properties", "logp")
    if metabolite_logp == "N/A":
        metabolite_logp = extract_property(metabolite_tag, "predicted_properties", "logp")

    return MetaboliteData(metabolite_name, metabolite_abundance_in_blood, metabolite_melting_point, metabolite_boiling_point, metabolite_solubility, metabolite_logp, metabolite_weight)

def main() -> None:
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
