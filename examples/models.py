from cryptography import x509
from cryptography.hazmat.backends import default_backend

from pymodm import MongoModel, EmbeddedMongoModel, fields
from pymongo.write_concern import WriteConcern
from pymongo.operations import IndexModel
from pymongo import ASCENDING

# https://tools.ietf.org/html/rfc5280#section-4.1.2.2

class Cert(MongoModel):
    log_id = fields.IntegerField(primary_key=True)
    serial = fields.CharField()  # 20 octets
    issuer = fields.CharField()
    not_before = fields.DateTimeField()
    not_after = fields.DateTimeField()
    sct_or_not_before = fields.DateTimeField()
    sct_exists = fields.BooleanField()
    pem = fields.CharField()
    subjects = fields.ListField(fields.CharField())
    trimmed_subjects = fields.ListField(fields.CharField())

    def x509(self):
        return x509.load_pem_x509_certificate(bytes(self.pem, 'utf-8'), default_backend())

    class Meta:
        indexes = [IndexModel(keys=[
            ('issuer', ASCENDING),
            ('serial', ASCENDING)], unique=True),
            IndexModel(keys=[('subjects', ASCENDING)]),
            IndexModel(keys=[('trimmed_subjects', ASCENDING)])]
        write_concern = WriteConcern(j=True)
        connection_alias = 'local'
        collection_name = 'certs'
        final = True


class Agency(EmbeddedMongoModel):
    id = fields.CharField()
    name = fields.CharField()

    class Meta:
        final = True


class Domain(MongoModel):
    domain = fields.CharField(primary_key=True)
    agency = fields.EmbeddedDocumentField(Agency) # deprecated soon: EmbeddedMongoModelField
    cyhy_stakeholder = fields.BooleanField()
    scan_date = fields.DateTimeField()

    class Meta:
        write_concern = WriteConcern(j=True)
        connection_alias = 'production'
        collection_name = 'domains'
        final = True
