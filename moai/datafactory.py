import datetime

import ckan.model.meta as meta
from ckan.model import Package, Resource, PackageExtra, Vocabulary
from ckanext.ceon.model import CeonPackageAuthor

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
        for row in self._sets.select(
              self._sets.c.hidden == False
            ).offset(offset).limit(batch_size).execute():
            yield {'id': row.set_id,
                   'name': row.name,
                   'description': row.description}

    def oai_earliest_datestamp(self):
#        row = sql.select([self._records.c.modified],
#                         order_by=[sql.asc(self._records.c.modified)]
#                         ).limit(1).execute().fetchone()
#        if row:
#            return row[0]
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


            
        packageList = meta.Session.query(Package).filter(Package.private == False).filter(Package.state == 'active')

        for package in packageList:
            
            resourceList = meta.Session.query(Resource).filter(Resource.package_id == package.id).filter(Resource.state == 'active')
            for resource in resourceList:
                resourceMetadata = {'title': [resource.name],
                        'identifier': [resource.url],
                        'description': [resource.description],
                        'rights': [package.license.url],
                        'type': [resource.format],
                        'relation': [package.url]
                    }

                yield {'id': resource.id,
                       'deleted': False,
                       'modified': resource.created,
                       'metadata': resourceMetadata,
                       'sets': ['public']
                    }
                
            
            packageAuthors = meta.Session.query(CeonPackageAuthor).filter(CeonPackageAuthor.package_id == package.id)
            
            creator = []
            
            for packageAuthor in packageAuthors:
                creator.append(packageAuthor.lastname + ' ' + packageAuthor.firstname)
                if packageAuthor.affiliation:
                    creator.append(packageAuthor.affiliation)
                    
            
            packageExtras = meta.Session.query(PackageExtra).filter(PackageExtra.package_id == package.id)
            
            
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
                        'identifier': [package.url],
                        'description': [package.notes],
                        'creator': creator,
                        'contributor': [],
                        'subject': [],
                        'type': [package.type],
                        'publisher': [],
                        'date': [],
                        'relation': [],
                        'subject': subjects
                    }
            if grantNumber:
                packageMetadata.get('contributor').append(grantNumber);
            if publisher:
                packageMetadata.get('publisher').append(publisher);
            if publicationYear:
                packageMetadata.get('date').append(publicationYear);
            if citation:
                packageMetadata.get('relation').append(citation);
                
            for funder in package.get_tags(Vocabulary.get('oa_funders')):
                packageMetadata.get('contributor').append(funder.name)
            for program in package.get_tags(Vocabulary.get('oa_funding_programs')):
                packageMetadata.get('contributor').append(program.name)
            for discipline in package.get_tags(Vocabulary.get('sci_disciplines')):
                packageMetadata.get('subject').append(discipline.name)
                            
            yield {'id': package.id,
                   'deleted': False,
                   'modified': package.metadata_modified,
                   'metadata': packageMetadata,
                   'sets': ['public']
                   }
