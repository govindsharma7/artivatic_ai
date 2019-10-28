from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import DocType, Index
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

client = Elasticsearch()

my_search = Search(using=client)

from artivatic_ai.home.models import UserEmail

# Create a connection to ElasticSearch
connections.create_connection()

user_email = Index('user_email')

user_email.settings(
    number_of_shards=1,
    number_of_replicas=0
)


@user_email.doc_type
class UserEmailDocument(DocType):

    class Meta:
        model = UserEmail
        fields = ['email', 'created_at', 'updated_at']


# define simple search here
# Simple search function
def search(email):
    query = my_search.query("match", email=email)
    response = query.execute()
    return response
