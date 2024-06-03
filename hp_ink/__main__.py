import requests
from xml.etree import ElementTree

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from zeroconf import ServiceBrowser, ServiceListener, Zeroconf, IPVersion
import socket
import time
from termcolor import colored,cprint

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
    cprint(header_line, attrs=['bold','underline'])


def print_consumable_info(hostname):
    response = requests.get(f"https://{hostname}/DevMgmt/ConsumableConfigDyn.xml", verify=False)
    response.raw.decode_content = True

    root = ElementTree.fromstring(response.content)

    for n in root.findall(".//ccdyn:ConsumableInfo",ns):
        code = n.find ('dd:ConsumableLabelCode',ns)
        level = n.find('dd:ConsumablePercentageLevelRemaining', ns)
        descriptor = n.find('dd:ConsumableKeyingDescriptor',ns)
        if not (code is None or level is None):
            status_line = f"{code.text:<4} {level.text:>2}% {descriptor.text}".replace("CMY",f"{colored('C','cyan')}{colored('M','magenta')}{colored('Y', 'yellow')}").replace("K", colored('K','black'))
            print(status_line)


class PrinterListener(ServiceListener):
    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        pass

    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        pass

    def add_service(self, zc: Zeroconf, type: str, name: str) -> None:
        info = zc.get_service_info(type, name)
        address=socket.inet_ntoa(info.addresses[0])
        print_printer_info(address)
        print_consumable_info(address)


if __name__ == "__main__":
    zeroconf = Zeroconf()
    listener = PrinterListener()
    browser = ServiceBrowser(zeroconf, "_ipp._tcp.local.", listener)
    try:
        time.sleep(5)
    finally:
        zeroconf.close()
