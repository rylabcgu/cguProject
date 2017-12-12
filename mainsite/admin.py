from django.contrib import admin
from mainsite.models import *

# Register your models here.
class ProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'profileImg', 'nickname', 'gender', 'birthdate')
admin.site.register(Profile, ProfileAdmin)

class SongAdmin(admin.ModelAdmin):
	list_display = ('songID', 'title', 'singer', 'uploader', 'viewNumber')
admin.site.register(Song, SongAdmin)

class LyricAdmin(admin.ModelAdmin):
	list_display = ('song', 'order', 'text', 'pinyin','start_time', 'end_time')	
admin.site.register(Lyric, LyricAdmin)

class FavoriteAdmin(admin.ModelAdmin):
	list_display = ('song', 'user')
admin.site.register(Favorite, FavoriteAdmin)

class FollowAdmin(admin.ModelAdmin):
	list_display = ('follower', 'followee')
admin.site.register(Follow, FollowAdmin)

class CommentAdmin(admin.ModelAdmin):
	list_display = ('user','song','content','commentTime')
admin.site.register(Comment, CommentAdmin)

class RatingAdmin(admin.ModelAdmin):
	list_display = ('user','song','good_grade','bad_grade')
admin.site.register(Rating, RatingAdmin)

class HashtagAdmin(admin.ModelAdmin):
	list_display = ('tagName','song')
admin.site.register(Hashtag, HashtagAdmin)

class PhraseAdmin(admin.ModelAdmin):
	list_display = ('taiwanese','phonetic')
admin.site.register(Phrase, PhraseAdmin)
