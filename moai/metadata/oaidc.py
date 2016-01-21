
from lxml import etree
from lxml.builder import ElementMaker

XSI_NS = 'http://www.w3.org/2001/XMLSchema-instance'
  
class OAIDC(object):
    """The standard OAI Dublin Core metadata format.
    
    Every OAI feed should at least provide this format.

    It is registered under the name 'oai_dc'
    """
    
    def __init__(self, prefix, config, db):
        self.prefix = prefix
        self.config = config
        self.db = db

        self.ns = {'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
                   'dc':'http://purl.org/dc/elements/1.1/',
                   'dcterms':'http://purl.org/dc/terms/'}
        self.schemas = {
            'oai_dc': 'http://www.openarchives.org/OAI/2.0/oai_dc.xsd'}
        
    def get_namespace(self):
        return self.ns[self.prefix]

    def get_schema_location(self):
        return self.schemas[self.prefix]
    
    def __call__(self, element, metadata):

        etree.register_namespace('dcterms','http://purl.org/dc/terms/')
        
        data = metadata.record
        
        OAI_DC =  ElementMaker(namespace=self.ns['oai_dc'],
                               nsmap =self.ns)
        DC = ElementMaker(namespace=self.ns['dc'])
        DCTERMS = ElementMaker(namespace=self.ns['dcterms'])

        oai_dc = OAI_DC.dc()
        oai_dc.attrib['{%s}schemaLocation' % XSI_NS] = '%s %s' % (
            self.ns['oai_dc'],
            self.schemas['oai_dc'])
        
        #oai_dc.attrib['dcterms'] = 'http://purl.org/dc/terms/'

        for field in ['title', 'creator', 'subject', 'description',
                      'publisher', 'contributor', 'type', 'format',
                      'identifier', 'source', 'language', 'date',
                      'relation', 'coverage', 'rights']:
            el = getattr(DC, field)
            if field == 'identifier' and data['metadata'].get('identifier.url'):
                value = data['metadata']['identifier.url'][0]
                if value:
                    element2 = el(value)
                    element2.set('{http://www.w3.org/2001/XMLSchema-instance}'+'type', etree.QName('{http://purl.org/dc/terms/}URI'))
                    oai_dc.append(element2)
            elif field == 'identifier' and data['metadata'].get('identifier.doi'):
                value = data['metadata']['identifier.url'][0]
                element2 = el(value)
                oai_dc.append(element2)
            elif field == 'rights' and data['metadata'].get('rights.uri'):
                value = data['metadata']['rights.uri'][0]
                element2 = el(value)
                element2.set('{http://www.w3.org/2001/XMLSchema-instance}'+'type', etree.QName('{http://purl.org/dc/terms/}URI'))
                oai_dc.append(element2)
            elif field == 'relation' and data['metadata'].get('relation.hasPart'):
                for value in data['metadata']['relation.hasPart']:
                    el2 = getattr(DCTERMS, 'hasPart')
                    oai_dc.append(el2(value))
            elif field == 'relation' and data['metadata'].get('relation.isReferencedBy'):
                for value in data['metadata']['relation.isReferencedBy']:
                    el2 = getattr(DCTERMS, 'isReferencedBy')
                    oai_dc.append(el2(value))
            elif field == 'relation' and data['metadata'].get('relation.isPartOf'):
                for value in data['metadata']['relation.isPartOf']:
                    el2 = getattr(DCTERMS, 'isPartOf')
                    oai_dc.append(el2(value))
            elif field == 'date' and data['metadata'].get('date.available'):
                for value in data['metadata']['date.available']:
                    el2 = getattr(DCTERMS, 'available')
                    oai_dc.append(el2(value))
            elif field == 'date' and data['metadata'].get('date.publication'):
                for value in data['metadata']['date.publication']:
                    el2 = getattr(DCTERMS, 'available')
                    oai_dc.append(el2(value))
            elif field == 'date' and data['metadata'].get('date.modified'):
                for value in data['metadata']['date.modified']:
                    el2 = getattr(DCTERMS, 'modified')
                    oai_dc.append(el2(value))
            elif field == 'contributor' and data['metadata'].get('contributor.funder'):
                for value in data['metadata']['contributor.funder']:
                    oai_dc.append(el(value))
            elif field == 'contributor' and data['metadata'].get('contributor.fundingProgram'):
                for value in data['metadata']['contributor.fundingProgram']:
                    oai_dc.append(el(value))
            elif field == 'contributor' and data['metadata'].get('contributor.grantNumber'):
                for value in data['metadata']['contributor.grantNumber']:
                    oai_dc.append(el(value))
            else:
                for value in data['metadata'].get(field, []):
                    if value:
                        oai_dc.append(el(value))
        
        
        
        element.append(oai_dc)
