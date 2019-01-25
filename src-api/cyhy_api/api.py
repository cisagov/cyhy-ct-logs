from flask import Flask
from flask_rest_jsonapi import Api, ResourceDetail, ResourceList, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound
from flask_rest_jsonapi.data_layers.base import BaseDataLayer
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
import dateutil.parser as parser


TEST_DATA = {'issuer_id': 1482,
 'issuer': 'C=US, O="thawte, Inc.", CN=thawte SHA256 SSL CA',
 'subject': 'dhs.gov',
 'id': 12766419,
 'min_entry_timestamp': parser.parse('2016-02-10T06:40:01.099'),
 'not_before': parser.parse('2016-02-10T00:00:00'),
 'not_after': parser.parse('2019-02-09T23:59:59')
 }


app = Flask(__name__)
app.config['DEBUG'] = True

class DictDataLayer(BaseDataLayer):
    def get_collection(self, qs, view_kwargs):
        """Retrieve a collection of objects
        :param QueryStringManager qs: a querystring manager to retrieve information from url
        :param dict view_kwargs: kwargs from the resource view
        :return tuple: the number of object and the list of objects
        """
        print(f'qs={qs} view_kwargs={view_kwargs}')
        return 1, [TEST_DATA]

    def get_object(self, view_kwargs, qs=None):
        """Retrieve an object
        :params dict view_kwargs: kwargs from the resource view
        :return DeclarativeMeta: an object
        """
        return TEST_DATA


class CertificateSchema(Schema):
    class Meta:
        type_ = 'certificate'
        self_view = 'certificate_detail'
        self_view_kwargs = {'id':'<id>'}
        self_view_many = 'certificate_list'

    id = fields.Integer(as_string=True, dump_only=True)
    subject = fields.Str(required=True, load_only=False)
    issuer = fields.Str(required=True, load_only=False)
    issuer_id = fields.Integer(as_string=True, dump_only=True)
    not_before = fields.Date()
    not_after = fields.Date()


class CertificateList(ResourceList):
    schema = CertificateSchema
    data_layer = {'class': DictDataLayer}


class CertificateDetail(ResourceDetail):
    schema = CertificateSchema
    data_layer = {'class': DictDataLayer}


api = Api(app)
api.route(CertificateList, 'certificate_list', '/certs')
api.route(CertificateDetail, 'certificate_detail', '/certs/<int:id>')

@app.route('/')
def hello():
    return 'Hello, World!'

def main():
    app.run(debug=True, host='0.0.0.0')

if __name__ == '__main__':
    main()
