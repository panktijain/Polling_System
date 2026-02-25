from django.contrib import admin

from .models import Option, Poll, Vote


class OptionInline(admin.TabularInline):
    model = Option
    extra = 3
    min_num = 1


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ('question', 'created_by', 'created_at', 'is_active', 'total_votes')
    list_filter = ('is_active',)
    inlines = [OptionInline]


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'poll', 'option', 'voted_at')
    list_filter = ('poll',)
    raw_id_fields = ('user', 'poll', 'option')
