from django.contrib import admin

from .models import Link, Vote


# Register your models here.
@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ("id", "url", "created_at")


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("id", "username")

    def username(self, obj):
        return obj.user.username
