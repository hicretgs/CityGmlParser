import io
from xml.etree import ElementTree
import re

ns = {
    'core': 'http://www.opengis.net/citygml/2.0',
    'gml': 'http://www.opengis.net/gml',
    'bldg': 'http://www.opengis.net/citygml/building/2.0',
    'gen': 'http://www.opengis.net/citygml/generics/2.0',
    'grp': 'http://www.opengis.net/citygml/cityobjectgroup/2.0',
    'app': 'http://www.opengis.net/citygml/appearance/2.0',
    'xlink': 'http://www.w3.org/1999/xlink',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
}


def clear_namespace(str):
    m = re.match('\{.*\}', str)
    return str.replace(m.group(0), '') if m else str


def get_ns_name(str):
    m = re.match('\{.*\}', str)
    g = m.group(0).replace('{', '').replace('}', '')
    t = ''
    for n in ns:
        if ns[n] == g:
            t = n
    return t


def get_clear_name(str):
    return get_ns_name(str) + ':' + clear_namespace(str)


def ParseGmlFile(gmlFile):
    tree = ElementTree.parse(gmlFile)
    root = tree.getroot()
    print(clear_namespace(root.tag))
    r_boundedBy = root[0]
    print(get_clear_name(r_boundedBy.tag))
    envelope = r_boundedBy[0]
    # print(' ' + get_clear_name(envelope.tag) + ' srsDimension: ' + envelope.attrib['srsDimension'] + ' srsName: ' + envelope.attrib['srsName'])
    # print('  ' + get_clear_name(envelope[0].tag) + ': ' + envelope[0].text)
    # print('  ' + get_clear_name(envelope[1].tag) + ': ' + envelope[1].text)
    print('---------------------------------------------')

    CONTENT = ''
    for cityObjectMember in root.findall('core:cityObjectMember', ns):
        if clear_namespace(cityObjectMember[0].tag) == 'Building':
            Building = cityObjectMember[0]
            _cityObjectMember_gml_id = Building.attrib['{' + ns['gml'] + '}id'].lstrip('#')
            print('Building  ->' + 'gml:id: ' + _cityObjectMember_gml_id)
            for outerBuildingInstallatione in Building.findall('bldg:outerBuildingInstallation', ns):
                buildingInstallation = outerBuildingInstallatione.find('bldg:BuildingInstallation', ns)
                _buildingInstallation_gml_id = buildingInstallation.attrib['{' + ns['gml'] + '}id'].lstrip('#')
                _name = buildingInstallation.find('gml:name', ns).text
                _independentSectionObjectReference = \
                buildingInstallation.find('gen:stringAttribute[@name=\'independentSectionObjectReference\']', ns)[
                    0].text  # [1][0].text
                _geometrySuitability = buildingInstallation.find('gen:intAttribute[@name=\'geometrySuitability\']', ns)[
                    0].text
                _additionalNote = buildingInstallation.find('gen:stringAttribute[@name=\'additionalNote\']', ns)[0].text
                _planArea = buildingInstallation.find('gen:doubleAttribute[@name=\'planArea\']', ns)[0].text
                _calculatedArea = buildingInstallation.find('gen:doubleAttribute[@name=\'calculatedArea\']', ns)[0].text
                _class = buildingInstallation.find('bldg:class', ns).text
                CONTENT += '\r\nINSERT INTO deneme."BuildingInstallation" (gml_id, parent_gml_id, "name", "independentSectionObjectReference", "geometrySuitability", "additionalNote", "planArea", "calculatedArea", "class") ' \
                           'VALUES(\'' + _buildingInstallation_gml_id + '\', \'' + _cityObjectMember_gml_id + '\', \'' + _name + '\', \'' + _independentSectionObjectReference + '\', \'' + _geometrySuitability + '\', \'' + _additionalNote + '\', \'' + _planArea + '\', \'' + _calculatedArea + '\', \'' + _class + '\');'
                for boundedBy in buildingInstallation.findall('bldg:boundedBy', ns):
                    _boundedBy = clear_namespace(boundedBy[0].tag)
                    _srsName = boundedBy[0][0][0].attrib['srsName']
                    for surfaceMember in boundedBy[0][0][0].findall('gml:surfaceMember', ns):
                        polygon = surfaceMember[0]
                        _polygon_gml_id = polygon.attrib['{' + ns['gml'] + '}id'].lstrip('#')
                        _geom = 'POLYGON(('
                        for pos in polygon[0][0].findall('gml:pos', ns):
                            _geom = _geom + pos.text + ','
                        _geom = _geom.rstrip(',') + '))'
                        CONTENT += '\r\nINSERT INTO deneme."Geometry" (gml_id, parent_gml_id, "srsName", geom, "boundedBy") ' \
                                   'VALUES(\'' + _polygon_gml_id + '\', \'' + _buildingInstallation_gml_id + '\', \'' + _srsName + '\', \'' + _geom + '\', \'' + _boundedBy + '\');'
            for boundedBy in Building.findall('bldg:boundedBy', ns):
                _boundedBy = clear_namespace(boundedBy[0].tag)
                lod2MultiSurface = boundedBy[0].find('bldg:lod2MultiSurface', ns)
                _srsName = lod2MultiSurface[0].attrib['srsName']
                for surfaceMember in lod2MultiSurface[0].findall('gml:surfaceMember', ns):
                    polygon = surfaceMember[0]
                    _polygon_gml_id = polygon.attrib['{' + ns['gml'] + '}id'].lstrip('#')
                    _geom = 'POLYGON(('
                    for pos in polygon[0][0].findall('gml:pos', ns):
                        _geom = _geom + pos.text + ','
                    _geom = _geom.rstrip(',') + '))'
                    CONTENT += '\r\nINSERT INTO deneme."Geometry" (gml_id, parent_gml_id, "srsName", geom, "boundedBy") ' \
                               'VALUES(\'' + _polygon_gml_id + '\', \'' + _cityObjectMember_gml_id + '\', \'' + _srsName + '\', \'' + _geom + '\', \'' + _boundedBy + '\');'
            for interiorRoom in Building.findall('bldg:interiorRoom', ns):
                for room in interiorRoom.findall('bldg:Room', ns):
                    _room_gml_id = room.attrib['{' + ns['gml'] + '}id'].lstrip('#')
                    _name = room.find('gml:name', ns).text
                    if _room_gml_id.startswith('OA_'):
                        _storeyObjectReference = room.find('gen:stringAttribute[@name=\'storeyObjectReference\']', ns)[
                            0].text
                        _commonAreaUsage = room.find('gen:intAttribute[@name=\'commonAreaUsage\']', ns)[0].text
                        _independentSectionObjectReference = ''
                        _partUsage = ''
                        _geometrySuitability = ''
                        _additionalNote = ''
                        _planArea = ''
                        _volume = ''
                    elif _room_gml_id.startswith('BBK_'):
                        _independentSectionObjectReference = \
                        room.find('gen:stringAttribute[@name=\'independentSectionObjectReference\']', ns)[0].text
                        _partUsage = room.find('gen:intAttribute[@name=\'partUsage\']', ns)[0].text
                        _storeyObjectReference = ''
                        _commonAreaUsage = ''
                        _geometrySuitability = room.find('gen:intAttribute[@name=\'geometrySuitability\']', ns)[0].text
                        _additionalNote = room.find('gen:stringAttribute[@name=\'additionalNote\']', ns)[0].text
                        _planArea = room.find('gen:doubleAttribute[@name=\'planArea\']', ns)[0].text
                        _volume = room.find('gen:doubleAttribute[@name=\'volume\']', ns)[0].text
                    else:
                        print('KURAL TANIMSIZ - interiorRoom : {0}'.format(_room_gml_id))
                    _calculatedArea = room.find('gen:doubleAttribute[@name=\'calculatedArea\']', ns)[0].text
                    _class = room.find('bldg:class', ns).text
                    CONTENT += '\r\nINSERT INTO deneme."InteriorRoom"(gml_id, parent_gml_id, "name", "independentSectionObjectReference", "partUsage", "storeyObjectReference", "commonAreaUsage", "geometrySuitability", "additionalNote", "planArea", "calculatedArea", volume, "class") ' \
                               'VALUES(\'' + _room_gml_id + '\', \'' + _cityObjectMember_gml_id + '\', \'' + _name + '\', \'' + _independentSectionObjectReference + '\', \'' + _partUsage + '\', \'' + _storeyObjectReference + '\', \'' + _commonAreaUsage + '\', \'' + _geometrySuitability + '\', \'' + _additionalNote + '\', \'' + _planArea + '\', \'' + _calculatedArea + '\', \'' + _volume + '\', \'' + _class + '\');'
                    for boundedBy in room.findall('bldg:boundedBy', ns):
                        _boundedBy = clear_namespace(boundedBy[0].tag)
                        _srsName = boundedBy[0][0][0].attrib['srsName']
                        for surfaceMember in boundedBy[0][0][0].findall('gml:surfaceMember', ns):
                            polygon = surfaceMember[0]
                            _polygon_gml_id = polygon.attrib['{' + ns['gml'] + '}id'].lstrip('#')
                            _geom = 'POLYGON(('
                            for pos in polygon[0][0].findall('gml:pos', ns):
                                _geom = _geom + pos.text + ','
                            _geom = _geom.rstrip(',') + '))'
                            CONTENT += '\r\nINSERT INTO deneme."Geometry" (gml_id, parent_gml_id, "srsName", geom, "boundedBy") ' \
                                       'VALUES(\'' + _polygon_gml_id + '\', \'' + _room_gml_id + '\', \'' + _srsName + '\', \'' + _geom + '\', \'' + _boundedBy + '\');'
        if clear_namespace(cityObjectMember[0].tag) == 'CityObjectGroup':
            CityObjectGroup = cityObjectMember[0]
            _cityObjectGroup_gml_id = CityObjectGroup.attrib['{' + ns['gml'] + '}id'].lstrip('#')
            _name = CityObjectGroup.find('gml:name', ns).text
            if _cityObjectGroup_gml_id.startswith('K_'):
                _parent_gml_id = CityObjectGroup.find('grp:parent', ns).attrib['{' + ns['xlink'] + '}href'].lstrip('#')
                _storeyNumber = CityObjectGroup.find('gen:stringAttribute[@name=\'storeyNumber\']', ns)[0].text
                _storeyUsage = CityObjectGroup.find('gen:intAttribute[@name=\'storeyUsage\']', ns)[0].text
                _independentSectionCount = \
                CityObjectGroup.find('gen:intAttribute[@name=\'independentSectionCount\']', ns)[0].text
                _class = CityObjectGroup.find('grp:class', ns).text
                CONTENT += '\r\nINSERT INTO deneme."Storey"(gml_id, parent_gml_id, "name", "storeyNumber", "storeyUsage", "independentSectionCount", "class") ' \
                           'VALUES(\'' + _cityObjectGroup_gml_id + '\', \'' + _parent_gml_id + '\', \'' + _name + '\', \'' + _storeyNumber + '\', \'' + _storeyUsage + '\', \'' + _independentSectionCount + '\', \'' + _class + '\');'
                for gMember in CityObjectGroup.findall('grp:groupMember', ns):
                    _independent_gml_id = gMember.attrib['{' + ns['xlink'] + '}href'].lstrip('#')
                    CONTENT += '\r\nINSERT INTO deneme."StoreyGroupMember"(gml_id, independent_gml_id) VALUES(\'' + _cityObjectGroup_gml_id + '\', \'' + _independent_gml_id + '\');'
                geometry = CityObjectGroup.find('grp:geometry', ns)
                for surfaceMember in geometry[0].findall('gml:surfaceMember', ns):
                    polygon = surfaceMember[0]
                    _polygon_gml_id = polygon.attrib['{' + ns['gml'] + '}id'].lstrip('#')
                    _srsName = ''
                    _boundedBy = ''
                    _geom = 'POLYGON(('
                    for pos in polygon[0][0].findall('gml:pos', ns):
                        _geom = _geom + pos.text + ','
                    _geom = _geom.rstrip(',') + '))'
                    CONTENT += '\r\nINSERT INTO deneme."Geometry" (gml_id, parent_gml_id, "srsName", geom, "boundedBy") ' \
                               'VALUES(\'' + _polygon_gml_id + '\', \'' + _cityObjectGroup_gml_id + '\', \'' + _srsName + '\', \'' + _geom + '\', \'' + _boundedBy + '\');'
            elif _cityObjectGroup_gml_id.startswith('MBG_'):
                _class = CityObjectGroup.find('grp:class', ns).text
                for gMember in CityObjectGroup.findall('grp:groupMember', ns):
                    _groupMember_gml_id = gMember.attrib['{' + ns['xlink'] + '}href'].lstrip('#')
                    CONTENT += '\r\nINSERT INTO deneme."CityObjectGroup"(gml_id, "name", "class", "groupMember_gml_id") ' \
                               'VALUES(\'' + _cityObjectGroup_gml_id + '\', \'' + _name + '\', \'' + _class + '\', \'' + _groupMember_gml_id + '\');'
            else:
                print('KURAL TANIMSIZ - CityObjectGroup : {0}'.format(_cityObjectGroup_gml_id))
        if clear_namespace(cityObjectMember[0].tag) == 'GenericCityObject':
            GenericCityObject = cityObjectMember[0]
            _genericCityObject_gml_id = GenericCityObject.attrib['{' + ns['gml'] + '}id'].lstrip('#')
            _name = GenericCityObject.find('gml:name', ns).text
            if _genericCityObject_gml_id.startswith('BB_'):
                _class = GenericCityObject.find('gen:class', ns).text
                _geometrySuitability = GenericCityObject.find('gen:intAttribute[@name=\'geometrySuitability\']', ns)[
                    0].text
                _integrationState = GenericCityObject.find('gen:intAttribute[@name=\'integrationState\']', ns)[0].text
                _independentSectionNumber = \
                GenericCityObject.find('gen:stringAttribute[@name=\'independentSectionNumber\']', ns)[0].text
                _takbisPropertyIdentityNumber = \
                GenericCityObject.find('gen:intAttribute[@name=\'takbisPropertyIdentityNumber\']', ns)[0].text
                _additionalNote = GenericCityObject.find('gen:stringAttribute[@name=\'additionalNote\']', ns)[0].text
                _independentSectionCardinalDirection = '{'
                for independentSectionCardinalDirection in GenericCityObject.findall(
                        'gen:intAttribute[@name=\'independentSectionCardinalDirection\']', ns):
                    _independentSectionCardinalDirection += independentSectionCardinalDirection[0].text + ','
                _independentSectionCardinalDirection = _independentSectionCardinalDirection.rstrip(',') + '}'
                _independentSectionUsage = \
                GenericCityObject.find('gen:intAttribute[@name=\'independentSectionUsage\']', ns)[0].text
                _partCount = GenericCityObject.find('gen:intAttribute[@name=\'partCount\']', ns)[0].text
                _independentSectionNetArea = \
                GenericCityObject.find('gen:doubleAttribute[@name=\'independentSectionNetArea\']', ns)[0].text
                _independentSectionGrossArea = \
                GenericCityObject.find('gen:doubleAttribute[@name=\'independentSectionGrossArea\']', ns)[0].text
                CONTENT += '\r\nINSERT INTO deneme."IndependentSection"(gml_id, parent_gml_id, "name", "geometrySuitability", "integrationState", "independentSectionNumber", "takbisPropertyIdentityNumber", "additionalNote", "independentSectionCardinalDirection", "independentSectionUsage", "partCount", "independentSectionNetArea", "independentSectionGrossArea", "class") ' \
                           'VALUES(\'' + _genericCityObject_gml_id + '\', \'\', \'' + _name + '\', \'' + _geometrySuitability + '\', \'' + _integrationState + '\', \'' \
                           + _independentSectionNumber + '\', \'' + _takbisPropertyIdentityNumber + '\', \'' + _additionalNote + '\', \'' + _independentSectionCardinalDirection + '\', \'' + _independentSectionUsage + \
                           '\', \'' + _partCount + '\', \'' + _independentSectionNetArea + '\', \'' + _independentSectionGrossArea + '\', \'' + _class + '\');'
                _lod2Geometry = GenericCityObject.find('gen:lod2Geometry', ns)
                _boundedBy = clear_namespace(_lod2Geometry[0].tag)
                _srsName = _lod2Geometry[0].attrib['srsName']
                for surfaceMember in _lod2Geometry[0].findall('gml:surfaceMember', ns):
                    polygon = surfaceMember[0]
                    _polygon_gml_id = polygon.attrib['{' + ns['gml'] + '}id'].lstrip('#')
                    _geom = 'POLYGON(('
                    for pos in polygon[0][0].findall('gml:pos', ns):
                        _geom = _geom + pos.text + ','
                    _geom = _geom.rstrip(',') + '))'
                    CONTENT += '\r\nINSERT INTO deneme."Geometry" (gml_id, parent_gml_id, "srsName", geom, "boundedBy") ' \
                               'VALUES(\'' + _polygon_gml_id + '\', \'\', \'' + _srsName + '\', \'' + _geom + '\', \'' + _boundedBy + '\');'
            else:
                print('KURAL TANIMSIZ: {0}'.format(_cityObjectGroup_gml_id))

    fileName = gmlFile.split('\\')[-1].replace('.gml', '.txt')
    with io.open(r"D:\GITPROJECTS\Python Projects\CityGMLParser\INSERT-" + fileName, "w", encoding="utf-8") as f:
        f.write(CONTENT)


ParseGmlFile(r'D:\temp\GML\M-3013675-A.gml')
ParseGmlFile(r'D:\temp\GML\M-3016815-A.gml')
ParseGmlFile(r'D:\temp\GML\M-3018678-A.gml')
ParseGmlFile(r'D:\temp\GML\M-3018679-A.gml')
ParseGmlFile(r'D:\temp\GML\M-3101736-A.gml')
ParseGmlFile(r'D:\temp\GML\M-3107551-A.gml')
ParseGmlFile(r'D:\temp\GML\M-3134952-A.gml')
ParseGmlFile(r'D:\temp\GML\M-3157372-A.gml')
