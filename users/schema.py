from django.contrib.auth import get_user_model, authenticate
import graphene
from graphql import GraphQLError
from graphene_django import DjangoObjectType
from graphql_jwt.shortcuts import get_token


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()


class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)

    def mutate(self, info, username, password, email):
        user = get_user_model()(username=username, email=email)
        user.set_password(password)
        user.save()

        return CreateUser(user=user)


class SignUp(graphene.Mutation):
    token = graphene.String()
    user = graphene.Field(UserType)

    class Arguments:
        email = graphene.String()
        password = graphene.String()
        name = graphene.String()

    def mutate(self, info, email, password, name):
        user = get_user_model()(username=email, email=email)
        user.set_password(password)
        user.first_name = name
        user.save()

        token = get_token(user)

        return SignUp(token=token, user=user)


class Login(graphene.Mutation):
    token = graphene.String()
    user = graphene.Field(UserType)

    class Arguments:
        email = graphene.String()
        password = graphene.String()

    def mutate(self, info, email, password):
        user = authenticate(username=email, password=password)

        if user is None:
            raise GraphQLError("Unauthenticated User!")

        token = get_token(user)

        return Login(token=token, user=user)


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    signup = SignUp.Field()
    login = Login.Field()


class Query(graphene.ObjectType):
    users = graphene.List(UserType)
    me = graphene.Field(UserType)

    def resolve_users(self, info):
        return get_user_model().objects.all()

    def resolve_me(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Not logged in!")

        return user
