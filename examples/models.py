"""Mongo document models for Certificate documents."""
from mongoengine import Document, EmbeddedDocument
from mongoengine.fields import (
    BooleanField,
    DateTimeField,
    EmbeddedDocumentField,
    IntField,
    ListField,
    StringField,
)
from cryptography import x509
from cryptography.hazmat.backends import default_backend

from admiral.util import trim_domains


class Cert(Document):
    """Certificate mongo document model."""

    log_id = IntField(primary_key=True)
    # serial is 20 octets, see: https://tools.ietf.org/html/rfc5280#section-4.1.2.2
    serial = StringField()
    issuer = StringField()
    not_before = DateTimeField()
    not_after = DateTimeField()
    sct_or_not_before = DateTimeField()
    sct_exists = BooleanField()
    pem = StringField()
    _subjects = ListField(field=StringField(), db_field="subjects")
    _trimmed_subjects = ListField(field=StringField(), db_field="trimmed_subjects")

    meta = {
        "collection": "certs",
        "indexes": [
            "+_subjects",
            "+_trimmed_subjects",
            {"fields": ("+issuer", "+serial"), "unique": True},
        ],
    }

    @property
    def subjects(self):
        """Getter for subjects."""
        return self._subjects

    @subjects.setter
    def subjects(self, values):
        """Subjects setter.

        Normalizes inputs, and dervices trimmed_subjects
        """
        self.subjects = {i.lower() for i in values}
        self.trimmed_subjects = trim_domains(self.subjects)

    @property
    def trimmed_subjects(self):
        """Read-only property.  This is derived from the subjects."""
        return self._trimmed_subjects

    def to_x509(self):
        """Return an x509 subject for this certificate."""
        return x509.load_pem_x509_certificate(
            bytes(self.pem, "utf-8"), default_backend()
        )


class Agency(EmbeddedDocument):
    """Embedded document in a domain representing the owning agency."""

    id = StringField()
    name = StringField()


class Domain(Document):
    """Domain mongo document model."""

    domain = StringField(primary_key=True)
    agency = EmbeddedDocumentField(Agency)
    cyhy_stakeholder = BooleanField()
    scan_date = DateTimeField()

    meta = {"collection": "domains"}
