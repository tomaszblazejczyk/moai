
from lxml import etree
from lxml.builder import ElementMaker

XSI_NS = 'http://www.w3.org/2001/XMLSchema-instance'
  
class OAIDATACITE(object):
    """The OAI Data Cite metadata format.
    

    It is registered under the name 'oai_datacite'
    """
    
    def __init__(self, prefix, config, db):
        self.prefix = prefix
        self.config = config
        self.db = db

        self.ns = {'oai_datacite': 'http://schema.datacite.org/oai/oai-1.0/',
                   'datacite':'http://datacite.org/schema/kernel-3'}
        self.schemas = {
            'oai_datacite': 'http://schema.datacite.org/oai/oai-1.0/oai_datacite.xsd',
            'datacite': 'http://schema.datacite.org/meta/kernel-3/metadata.xsd'}
        
    def get_namespace(self):
        return self.ns[self.prefix]

    def get_schema_location(self):
        return self.schemas[self.prefix]
    
    def __call__(self, element, metadata):

        data = metadata.record
        
        OAI_DATACITE =  ElementMaker(namespace=self.ns['oai_datacite'],
                               nsmap =self.ns)
        DATACITE = ElementMaker(namespace=self.ns['datacite'])

        oai_datacite = OAI_DATACITE.oai_datacite()
        oai_datacite.attrib['{%s}schemaLocation' % XSI_NS] = '%s %s' % (
            self.ns['oai_datacite'],
            self.schemas['oai_datacite'])
        el = getattr(OAI_DATACITE, "isReferenceQuality")
        isReferenceQuality = el('true');
        oai_datacite.append(isReferenceQuality)
        
        el = getattr(OAI_DATACITE, "schemaVersion")
        schemaVersion = el('3');
        oai_datacite.append(schemaVersion)
        
        el = getattr(OAI_DATACITE, "datacentreSymbol")
        datacentreSymbol = el('RepOD');
        oai_datacite.append(datacentreSymbol)

        payload = OAI_DATACITE.payload()
        oai_datacite.append(payload)

        resource = DATACITE.resource()
        resource.attrib['{%s}schemaLocation' % XSI_NS] = '%s %s' % (
            self.ns['datacite'],
            self.schemas['datacite'])
        payload.append(resource)
        
        if (data['metadata'].get('identifier.doi')):
            el = getattr(OAI_DATACITE, "identifier")
            identifier = el(data['metadata'].get('identifier.doi')[0])
            identifier.set('identifierType', 'DOI')
            resource.append(identifier)
        
        if (data['metadata'].get('creator')):
            creators = DATACITE.creators()
            resource.append(creators)
            for creator, affiliation in zip(data['metadata'].get('creator'), data['metadata'].get('creator.affiliation')):
                creatorElement = DATACITE.creator()
                creators.append(creatorElement)
                el = getattr(DATACITE, "creatorName")
                creatorNameElement = el(creator)
                creatorElement.append(creatorNameElement)
                el = getattr(DATACITE, "affiliation")
                affiliationElement = el(affiliation)
                creatorElement.append(affiliationElement)
                
                
        if (data['metadata'].get('title')):
            titles = DATACITE.titles()
            resource.append(titles)
            for title in data['metadata'].get('title'):
                el = getattr(DATACITE, "title")
                titleElement = el(title)
                titles.append(titleElement)

        if (data['metadata'].get('publisher')):
            for publisher in data['metadata'].get('publisher'):
                el = getattr(DATACITE, "publisher")
                publisherElement = el(publisher)
                resource.append(publisherElement)

        if (data['metadata'].get('date.publication')):
            for dateAvailable in data['metadata'].get('date.publication'):
                el = getattr(DATACITE, "publicationYear")
                publicationYear = el(dateAvailable)
                resource.append(publicationYear)

        if (data['metadata'].get('subject')):
            subjects = DATACITE.subjects()
            resource.append(subjects)
            for subject in data['metadata'].get('subject'):
                el = getattr(DATACITE, "subject")
                subjectElement = el(subject)
                subjects.append(subjectElement)
                
        contributors = DATACITE.contributors()
        if (data['metadata'].get('contributor.funder')):
            funderElement = DATACITE.contributor()
            funderElement.set('contributorType', 'Funder')
            el = getattr(DATACITE, "contributorName")
            funderName = el(data['metadata'].get('contributor.funder')[0])
            contributors.append(funderElement)
            funderElement.append(funderName)
            if (data['metadata'].get('contributor.fundingProgram') and data['metadata'].get('contributor.grantNumber')):
                el = getattr(DATACITE, "nameIdentifier")
                funderId = 'info:eu-repo/grantAgreement/' + \
                    data['metadata'].get('contributor.funder')[0]+ '/' + \
                    data['metadata'].get('contributor.fundingProgram')[0] + '/' + \
                    data['metadata'].get('contributor.grantNumber')[0]
                funderIdElement = el(funderId)
                funderIdElement.set('nameIdentifierScheme', 'info')
                funderElement.append(funderIdElement)
        resource.append(contributors)

        if (data['metadata'].get('description')):
            descriptions = DATACITE.descriptions()
            resource.append(descriptions)
            for description in data['metadata'].get('description'):
                el = getattr(DATACITE, "description")
                if description:
                    descriptionElement = el(description)
                    descriptions.append(descriptionElement)

        if (data['metadata'].get('relation.hasPart')):
            relatedIdentifiers = DATACITE.relatedIdentifiers()
            resource.append(relatedIdentifiers)
            for relatedIdentifier in data['metadata'].get('relation.hasPart'):
                el = getattr(DATACITE, "relatedIdentifier")
                relatedIdentifierElement = el(relatedIdentifier)
                relatedIdentifierElement.set('relatedIdentifierType', 'DOI')
                relatedIdentifierElement.set('relationType', 'HasPart')
                relatedIdentifiers.append(relatedIdentifierElement)

        if (data['metadata'].get('relation.isPartOf')):
            relatedIdentifiers = DATACITE.relatedIdentifiers()
            resource.append(relatedIdentifiers)
            for relatedIdentifier in data['metadata'].get('relation.isPartOf'):
                el = getattr(DATACITE, "relatedIdentifier")
                relatedIdentifierElement = el(relatedIdentifier)
                relatedIdentifierElement.set('relatedIdentifierType', 'DOI')
                relatedIdentifierElement.set('relationType', 'IsPartOf')
                relatedIdentifiers.append(relatedIdentifierElement)

        if (data['metadata'].get('type')):
            formats = DATACITE.formats()
            resource.append(formats)
            for format in data['metadata'].get('type'):
                el = getattr(DATACITE, "format")
                formatElement = el(format)
                formats.append(formatElement)
        
        if (data['metadata'].get('date.available') or data['metadata'].get('date.modified')):
            datesElement = DATACITE.dates()
            resource.append(datesElement)
        
            if (data['metadata'].get('date.available')):
                for dateAvailable in data['metadata'].get('date.available'):
                    el = getattr(DATACITE, "date")
                    dateAvailableElement = el(dateAvailable)
                    dateAvailableElement.set('dateType', 'available')
                    datesElement.append(dateAvailableElement)
            
            if (data['metadata'].get('date.modified')):
                for dateModified in data['metadata'].get('date.modified'):
                    el = getattr(DATACITE, 'date')
                    dateAvailableElement = el(dateModified)
                    dateAvailableElement.set('dateType', 'modified')
                    datesElement.append(dateAvailableElement)
            
        if (data['metadata'].get('rights')):
            rightsListElement = DATACITE.rightsList()
            resource.append(rightsListElement)
            el = getattr(DATACITE, 'rights')
            rightElement = el(data['metadata'].get('rights')[0])
            if (data['metadata'].get('rights.uri')):
                rightElement.set('rightsURI', data['metadata'].get('rights.uri')[0])
            rightsListElement.append(rightElement)
            
        element.append(oai_datacite)
