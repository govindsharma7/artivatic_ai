import graphene

from graphene import relay, ObjectType, InputObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from django.core.exceptions import ValidationError

from artivatic_ai.home.models import UserEmail
from artivatic_ai.home.helpers import get_object, get_errors, update_create_instance


class UserCreateInput(InputObjectType):
    email = graphene.String(required=True)


class UserEmailNode(DjangoObjectType):
    class Meta:
        model = UserEmail
        # Allow for some more advanced filtering here
        filter_fields = {
            'email': ['exact', 'icontains', 'istartswith'],
        }
        interfaces = (relay.Node, )


class CreateUserEmail(relay.ClientIDMutation):

    class Input:
         user = graphene.Argument(UserCreateInput)

    new_user = graphene.Field(UserEmailNode)

    @classmethod
    def mutate_and_get_payload(cls, args, context, info):

        user_email_data = args.get('email')
        # unpack the dict item into the model instance
        new_user = UserEmail.objects.create(**user_email_data)

        return cls(new_user=new_user)


class Query(ObjectType):
    users_email = relay.Node.Field(UserEmailNode) # get user by id or by field name
    all_users_email =  DjangoFilterConnectionField(UserEmailNode) # get all users

    def resolve_users_email(self):
        return UserEmail.objects.all()


class Mutation(ObjectType):
     create_user_email = CreateUserEmail.Field()
    

schema = graphene.Schema(
    query=Query,
    mutation=Mutation,
)