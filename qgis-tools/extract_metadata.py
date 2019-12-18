from os import path
from sys import argv
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

from osgeo import ogr
from qgis.core import QgsApplication, QgsVectorLayer


def extract_abstract(xml_root, target_directory, layer_name):
    abstract_element = xml_root.find("./dataIdInfo/idAbs")

    if abstract_element is None:
        print("No abstract element for {} in {}".format(layer_name, fgdb_path))
        return

    abstract_html = abstract_element.text
    abstract_text = BeautifulSoup(abstract_html, "lxml").text.strip()

    if not abstract_text:
        print("No abstract text for {} in {}".format(layer_name, fgdb_path))
        return

    abstract_path = path.join(target_directory, "{}.abstract.txt".format(layer_name))
    with open(abstract_path, "w+") as abstract_file:
        abstract_file.write(abstract_text)


def extract_title(xml_root, target_directory, layer_name):
    title_element = xml_root.find("./dataIdInfo/idCitation/resTitle")

    if title_element is None:
        print("No title element for {} in {}".format(layer_name, fgdb_path))
        return

    title_text = title_element.text

    if not title_text:
        print("No title text for {} in {}".format(layer_name, fgdb_path))
        return

    title_path = path.join(target_directory, "{}.title.txt".format(layer_name))
    with open(title_path, "w+") as title_file:
        title_file.write(title_text)


def extract_revision_date(xml_root, target_directory, layer_name):
    revision_date_element = xml_root.find("./dataIdInfo/idCitation/date/reviseDate")

    if revision_date_element is None:
        print("No revision date element for {} in {}".format(layer_name, fgdb_path))
        return

    revision_date_text = revision_date_element.text

    if not revision_date_text:
        print("No revision date text for {} in {}".format(layer_name, fgdb_path))
        return

    revision_date_text = revision_date_text.split("T")[0]

    revision_date_path = path.join(target_directory, "{}.revision_date.txt".format(layer_name))
    with open(revision_date_path, "w+") as revision_date_file:
        revision_date_file.write(revision_date_text)


def extract_metadata_for_fgdb_layer(fgdb, fgdb_path, layer_name):
    parent_dir = path.abspath(path.join(fgdb_path, '..'))

    metadata_layer = fgdb.ExecuteSQL("GetLayerMetadata {}".format(layer_name))
    metadata_string = metadata_layer.GetFeature(0).GetFieldAsString(0)
    if not metadata_string:
        print("No metadata found for {} in {}".format(layer_name, fgdb_path))
        return

    metadata_path = path.join(parent_dir, "{}.xml".format(layer_name))
    with open(metadata_path, "w+") as metadata_file:
        metadata_file.write(metadata_string)

    root = ET.fromstring(metadata_string)

    extract_abstract(root, parent_dir, layer_name)
    extract_title(root, parent_dir, layer_name)
    extract_revision_date(root, parent_dir, layer_name)

    print("Complete: {}".format(layer_name))


def extract_metadata_for_fgdb_layers(fgdb_path):
    if not path.isdir(fgdb_path):
        print("Error: FGDB not found at {}".format(fgdb_path))
        return

    driver = ogr.GetDriverByName("OpenFileGDB")
    fgdb = driver.Open(fgdb_path, 0)
    layer_names = [l.GetName() for l in fgdb]

    for layer_name in layer_names:
        extract_metadata_for_fgdb_layer(fgdb, fgdb_path, layer_name)


def main():
    QgsApplication.setPrefixPath("/usr", True)
    qgis = QgsApplication([], False)
    qgis.initQgis()

    params = argv[1:]
    if len(params) > 0:
        for param in params:
            extract_metadata_for_fgdb_layers(param)
    else:
        print("Usage: extract_metadata.py fgdb_path [fgdb_path2 ...]")

    qgis.exitQgis()


if __name__ == "__main__":
    main()
