
from pathlib import Path
import xml.etree.ElementTree as ET

def parse_gadgetron_XML(fname_xml):
    it =ET.iterparse(fname_xml)

    for _, el in it:
        _, _, el.tag = el.tag.rpartition('}') # strip namespace
    return it.root

def get_gadget_property_from_xml(fname_xml, gadget_name, property_name):
    root = parse_gadgetron_XML(fname_xml)
    return get_gadget_property(root, gadget_name, property_name)

def get_gadget_property(root, gadget_name, property_name):
    gt = get_gadget_by_name(root, gadget_name)
    return get_property_value(gt, property_name)

def get_gadget_by_name(root,gadget_name):

    for child in root:
        if is_gadget_node(child) and get_gadget_name(child)==gadget_name:
            if child:
                return child

    raise AssertionError(f"There was no gadget of the name {gadget_name} in the XML tree of the gadgetron file you passed.  Maybe check the spelling.")

def is_gadget_node(node):
    return node.tag == 'gadget'

def get_gadget_name(gadget):
    for node in gadget.findall('./name'):
        return node.text

def get_property_value(gadget, prop_name):

    if gadget is None:
        raise AssertionError("You passed a None type object instead of a node.")
    names = gadget.findall("./property/name")
    values = gadget.findall("./property/value")

    for (n,v) in zip(names, values):
        if n.text == prop_name:
            return v.text