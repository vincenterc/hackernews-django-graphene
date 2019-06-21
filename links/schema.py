import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from django.db.models import Q

from users.schema import UserType
from .models import Link, Vote


class VoteType(DjangoObjectType):
    class Meta:
        model = Vote


class LinkType(DjangoObjectType):
    votes = graphene.List(VoteType)

    @graphene.resolve_only_args
    def resolve_votes(self):
        return self.votes.all()

    class Meta:
        model = Link


class FeedType(graphene.ObjectType):
    links = graphene.List(LinkType)
    count = graphene.Int()


class Query(graphene.ObjectType):
    feed = graphene.Field(
        FeedType, filter=graphene.String(), skip=graphene.Int(), first=graphene.Int()
    )
    links = graphene.List(
        LinkType, search=graphene.String(), first=graphene.Int(), skip=graphene.Int()
    )
    votes = graphene.List(VoteType)

    def resolve_feed(self, info, filter=None, skip=None, first=None, **kwargs):
        qs = Link.objects.all()

        if filter:
            q_filter = Q(description__icontans=filter) | Q(url__icontains=filter)
            qs = qs.filter(q_filter)

        if skip:
            qs = qs[skip:]

        if first:
            qs = qs[:first]

        return FeedType(links=qs, count=qs.count())

    def resolve_links(self, info, search=None, first=None, skip=None, **kwargs):
        qs = Link.objects.all()

        if search:
            filter = Q(url__icontains=search) | Q(description__icontains=search)
            qs = qs.filter(filter)

        if skip:
            qs = qs[skip:]

        if first:
            qs = qs[:first]

        return qs

    def resolve_votes(self, info, **kwargs):
        return Vote.objects.all()


class CreateLink(graphene.Mutation):
    id = graphene.Int()
    url = graphene.String()
    description = graphene.String()
    posted_by = graphene.Field(UserType)

    class Arguments:
        url = graphene.String()
        description = graphene.String()

    def mutate(self, info, url, description):
        user = info.context.user or None

        link = Link(url=url, description=description, posted_by=user)
        link.save()

        return CreateLink(
            id=link.id,
            url=link.url,
            description=link.description,
            posted_by=link.posted_by,
        )


class CreateVote(graphene.Mutation):
    user = graphene.Field(UserType)
    link = graphene.Field(LinkType)

    class Arguments:
        link_id = graphene.Int()

    def mutate(self, info, link_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You must be logged to vote!")

        link = Link.objects.filter(id=link_id).first()
        if not link:
            raise Exception("Invalid Link!")

        Vote.objects.create(user=user, link=link)

        return CreateVote(user=user, link=link)


class Post(graphene.Mutation):
    id = graphene.ID()
    created_at = graphene.DateTime()
    url = graphene.String()
    description = graphene.String()
    posted_by = graphene.Field(UserType)
    votes = graphene.List(VoteType)

    class Arguments:
        url = graphene.String()
        description = graphene.String()

    def mutate(self, info, url, description):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You must be logged to post!")

        link = Link(url=url, description=description, posted_by=user)
        link.save()

        return Post(
            id=link.id,
            created_at=link.created_at,
            url=link.url,
            description=link.description,
            posted_by=link.posted_by,
            votes=link.votes.all(),
        )


class SubmitVote(graphene.Mutation):
    id = graphene.ID()
    link = graphene.Field(LinkType)
    user = graphene.Field(UserType)

    class Arguments:
        link_id = graphene.ID()

    def mutate(self, info, link_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You must be logged to vote!")

        link = Link.objects.filter(id=link_id).first()
        if not Link:
            raise GraphQLError("Invalid Link!")

        vote = Vote.objects.create(user=user, link=link)

        return Vote(id=vote.id, link=vote.link, user=vote.user)


class Mutation(graphene.ObjectType):
    create_link = CreateLink.Field()
    create_vote = CreateVote.Field()
    post = Post.Field()
    submit_vote = SubmitVote.Field()
