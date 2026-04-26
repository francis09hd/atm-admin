import uiautomator2 as u2
import re

def find_price_buttons(d=None, device_ip="127.0.0.1:62001"):
    if d is None:
        d = u2.connect(device_ip)
    d.dump_hierarchy()
    nodes = d.xpath('//*[@clickable="true"]').all()
    result = []
    for node in nodes:
        text = node.attrib.get('text', '')
        if re.search(r'(RD\$|\$)\s*\d+', text):
            bounds = node.attrib.get('bounds', '')
            result.append({'text': text, 'bounds': bounds})
    return result

if __name__ == "__main__":
    botones = find_price_buttons()
    for btn in botones:
        print(btn)
