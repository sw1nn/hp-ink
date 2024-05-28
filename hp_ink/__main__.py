import requests
from xml.etree import ElementTree

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ns = {'ccdyn': 'http://www.hp.com/schemas/imaging/con/ledm/consumableconfigdyn/2007/11/19',
      'dd': 'http://www.hp.com/schemas/imaging/con/dictionaries/1.0/',
      'prdcfgdyn': 'http://www.hp.com/schemas/imaging/con/ledm/productconfigdyn/2007/11/05',
      'prdcfgdyn2': 'http://www.hp.com/schemas/imaging/con/ledm/productconfigdyn/2009/03/16',
      }
def print_printer_info(hostname):

    response = requests.get(f"https://{hostname}/DevMgmt/ProductConfigDyn.xml", verify=False)
    response.raw.decode_content = True

    root = ElementTree.fromstring(response.content)
    make_and_model = root.find('.//prdcfgdyn:ProductInformation/dd:MakeAndModel',ns)
    serial_number = root.find('.//prdcfgdyn:ProductInformation/dd:SerialNumber',ns)

    header_line = f"{make_and_model.text} ({serial_number.text})"
    print(f'\033[4m{header_line}\033[0m')
    

def print_consumable_info(hostname):
    response = requests.get(f"https://{hostname}/DevMgmt/ConsumableConfigDyn.xml", verify=False)
    response.raw.decode_content = True

    root = ElementTree.fromstring(response.content)
    
    for n in root.findall(".//ccdyn:ConsumableInfo",ns):
        code = n.find ('dd:ConsumableLabelCode',ns)
        level = n.find('dd:ConsumablePercentageLevelRemaining', ns)
        descriptor = n.find('dd:ConsumableKeyingDescriptor',ns)
        if not (code is None or level is None):
            print(f"{code.text:<4} {level.text:>2}% {descriptor.text}")


if __name__ == "__main__":
    print_printer_info("hp3b6bda")
    print_consumable_info("hp3b6bda")
