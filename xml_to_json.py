import xmltodict
import json
import yaml

input  = print("dsa")

with open("../src/PointzAggregator-AirlinesData.xml", "r", encoding="utf-8") as xml_file:
    xml_data = xml_file.read()

data_dict = xmltodict.parse(xml_data)

json_data = json.dumps(data_dict, indent=4)

with open("PointzAggregator-AirlinesData.json", "w", encoding="utf-8") as json_file:
    json_file.write(json_data)

print("XML has been successfully converted to JSON!")
