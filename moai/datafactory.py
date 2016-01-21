import datetime

import ckan.model.meta as meta
from ckan.model import Package, Resource, PackageExtra, Vocabulary
from ckanext.ceon.model.metadata import CeonPackageAuthor
from ckanext.ceon.model.doi import CeonPackageDOI

from moai.utils import get_moai_log

class CKANDataFactory(object):
    """Implementation of CKAN data backend
    This implements the :ref:`IDatabase` interface, look there for
    more documentation.
    """

    def __init__(self, dburi=None):
        self.log = get_moai_log()
        
        
    def update_record(self, oai_id, modified, deleted, sets, metadata):
        # adds a record, call flush to actually store in db
        self.log.info('Update record')
            
    def get_record(self, oai_id):
        record = {'id': 'testid',
                  'deleted': 'false',
                  'modified': 'false',
                  'metadata': '',
                  'sets': 'someset'}
        return record

    def get_set(self, oai_id):
        return {'id': "testsetid",
                'name': "someset",
                'description': 'someset',
                'hidden': 'false'}

    def get_setrefs(self, oai_id, include_hidden_sets=False):
        set_ids = ['oai_dc']
        return set_ids

    def oai_sets(self, offset=0, batch_size=20):

        return [{'id': 'public',
                 'name': 'public',
                 'description': 'public'}]

    def oai_earliest_datestamp(self):
        return datetime.datetime(1970, 1, 1)
    
    def oai_query(self,
                  offset=0,
                  batch_size=20,
                  needed_sets=None,
                  disallowed_sets=None,
                  allowed_sets=None,
                  from_date=None,
                  until_date=None,
                  identifier=None):

        # make sure until date is set, and not in future
        if until_date == None or until_date > datetime.datetime.utcnow():
            until_date = datetime.datetime.utcnow()

        
        packageList = meta.Session.query(Package).filter(Package.private == False).filter(Package.state == 'active')
        packageList = packageList.filter(Package.metadata_modified  <= until_date)
        if (from_date):
            packageList = packageList.filter(Package.metadata_modified  > from_date)
        if (identifier):
            #find package or resource with specified identifier
            packageList = packageList.filter(Package.id  == identifier)
            resourceList = meta.Session.query(Resource).filter(Resource.state == 'active').filter(Resource.id == identifier)
            resourceList = resourceList.filter(Resource.created  <= until_date)
            if (from_date):
                resourceList = resourceList.filter(Resource.created  > from_date)
                
            for resource in resourceList:
                #fill package information of resource found with identifier
                packagesOfResourceList = meta.Session.query(Package).filter(Package.private == False).filter(Package.state == 'active').filter(Package.id == resource.package_id)
                licenses = []
                for packageOfResource in packagesOfResourceList:
                    doi = None
                    doiList = meta.Session.query(CeonPackageDOI).filter(CeonPackageDOI.package_id == packageOfResource.id)
                    for doiCandidate in doiList:
                        doi = doiCandidate.identifier
                    licenses.append(packageOfResource.license.url)
                        
                    resourceMetadata = {'title': [resource.name],
                                        'identifier': [resource.url],
                                        'description': [resource.description],
                                        'rights': licenses,
                                        'type': [resource.format],
                                        'relation': [],
                                        'relation.isPartOf': [],
                                        'date.available': [resource.created.strftime("%Y-%m-%d_%H:%M:%S.%f")],
                                        'date.modified': []
                    }
                    if (doi):
                        resourceMetadata.get('relation.isPartOf').append(doi);
                    if (resource.last_modified):
                        resourceMetadata.get('date.modified').append(resource.last_modified.strftime("%Y-%m-%d_%H:%M:%S.%f"))
                
                    yield {'id': resource.id,
                       'deleted': False,
                       'modified': resource.created,
                       'metadata': resourceMetadata,
                       'sets': ['public']
                    }



        for package in packageList:
            
            doi = None
            doiList = meta.Session.query(CeonPackageDOI).filter(CeonPackageDOI.package_id == package.id)
            for doiCandidate in doiList:
                doi = doiCandidate.identifier
            
            resourceList = meta.Session.query(Resource).filter(Resource.package_id == package.id).filter(Resource.state == 'active')
            resourceList = resourceList.filter(Resource.created  <= until_date)
            if (from_date):
                resourceList = resourceList.filter(Resource.created  > from_date)

            if (identifier):
                resourceList.filter(Resource.id == identifier)
            resources = []
            for resource in resourceList:
                resourceMetadata = {'title': [resource.name],
                        'identifier': [resource.url],
                        'description': [resource.description],
                        'rights': [package.license.id],
                        'rights.url': [package.license.url],
                        'type': [resource.format],
                        'relation': [],
                        'relation.isPartOf': [],
                        'date.available': [resource.created.strftime("%Y-%m-%d_%H:%M:%S.%f")],
                        'date.modified': []
                    }
                if (doi):
                    resourceMetadata.get('relation.isPartOf').append(doi);
                if (resource.last_modified):
                    resourceMetadata.get('date.modified').append(resource.last_modified.strftime("%Y-%m-%d_%H:%M:%S.%f"))
                
                resources.append(resource.url)
                yield {'id': resource.id,
                       'deleted': False,
                       'modified': resource.created,
                       'metadata': resourceMetadata,
                       'sets': ['public']
                    }
                
            
            packageAuthors = meta.Session.query(CeonPackageAuthor).filter(CeonPackageAuthor.package_id == package.id)
            
            creator = []
            creatorAffiliation = []
            
            for packageAuthor in packageAuthors:
                authorName = packageAuthor.lastname
                if (packageAuthor.firstname):
                    authorName = authorName + ' ' + packageAuthor.firstname
                creator.append(authorName)
                    
                if (packageAuthor.affiliation):
                    creatorAffiliation.append(packageAuthor.affiliation)
                else:
                    creatorAffiliation.append('none')
                    
            
            packageExtras = meta.Session.query(PackageExtra).filter(PackageExtra.package_id == package.id)
            
            grantNumber = ''
            publisher = ''
            publicationYear = ''
            citation = ''
            
            for packageExtra in packageExtras:
                if packageExtra.key == 'oa_grant_number':
                    grantNumber = packageExtra.value
                if packageExtra.key == 'publisher':
                    publisher = packageExtra.value
                if packageExtra.key == 'publication_year':
                    publicationYear = packageExtra.value
                if packageExtra.key == 'rel_citation':
                    citation = packageExtra.value
                
            subjects = []
            
            for packageTag in package.get_tags():
                subjects.append(packageTag.name)
            
            packageMetadata = {'title': [package.title],
                        'identifier': [],
                        'identifier.doi': [],
                        'identifier.url': [package.url],
                        'description': [package.notes],
                        'creator': creator,
                        'creator.affiliation': creatorAffiliation,
                        'contributor': [],
                        'contributor.funder': [],
                        'contributor.fundingProgram': [],
                        'contributor.grantNumber': [],
                        'subject': [],
                        'type': [package.type],
                        'publisher': [],
                        'date.publication': [],
                        'relation': [],
                        'relation.isReferencedBy': [],
                        'relation.hasPart': resources,
                        'subject': subjects,
                        'url':['defaultUrl']
                    }
            if grantNumber:
                packageMetadata.get('contributor.grantNumber').append(grantNumber);
            if publisher:
                packageMetadata.get('publisher').append(publisher);
            if publicationYear:
                packageMetadata.get('date.publication').append(publicationYear);
            if citation:
                packageMetadata.get('relation.isReferencedBy').append(citation);
            if (doi):
                packageMetadata.get('identifier.doi').append(doi)
                
            for funder in package.get_tags(Vocabulary.get('oa_funders')):
                packageMetadata.get('contributor.funder').append(funder.name)
            for program in package.get_tags(Vocabulary.get('oa_funding_programs')):
                packageMetadata.get('contributor.fundingProgram').append(program.name)
            for discipline in package.get_tags(Vocabulary.get('sci_disciplines')):
                packageMetadata.get('subject').append(discipline.name)
                            
            yield {'id': package.id,
                   'deleted': False,
                   'modified': package.metadata_modified,
                   'metadata': packageMetadata,
                   'sets': ['public']
                   }
