from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	nickname = models.CharField(max_length=20, blank=True)
	gender = models.NullBooleanField()
	birthdate = models.DateField(null=True, blank=True)
	profileImg = models.ImageField(null=True, blank=True)
	
	def __str__(self):
		return str(self.user)

class Song(models.Model):
	songID = models.AutoField(primary_key=True)	#主鍵
	uploader = models.ForeignKey(User)	#外鍵
	singer = models.CharField(max_length=20)
	composer = models.CharField(max_length=10, blank=True)
	lyricist = models.CharField(max_length=10, blank=True)
	title = models.CharField(max_length=20)
	videoURL = models.CharField(max_length=15)
	uploadTime = models.DateTimeField(auto_now_add=True)
	viewNumber = models.IntegerField(default=0)
	pinyinType = models.IntegerField(default=0)		#0: 臺羅閏號調/1: 臺羅數字調/2: 吳守禮方音
	productionPerformance = models.DecimalField(max_digits=6, decimal_places=3, default=0)
	content = models.TextField(blank=True) 
	
	def __str__(self):
		return str(self.songID)

class Lyric(models.Model):
	start_time = models.DecimalField(max_digits=20, decimal_places=5)
	end_time = models.DecimalField(max_digits=20, decimal_places=5)
	text = models.CharField(max_length=50)
	textCH = models.CharField(max_length=50, blank=True)
	textEN  = models.CharField(max_length=50, blank=True)
	textJP = models.CharField(max_length=50, blank=True)
	pinyin = models.CharField(max_length=80, blank=True)
	song = models.ForeignKey(Song)	#外鍵
	order = models.CharField(max_length=5, blank=True)
	
	def __str__(self):
		return str(self.text)
		
class Favorite(models.Model):
	user = models.ForeignKey(User)	#外鍵
	song = models.ForeignKey(Song)	#外鍵
	
	def __str__(self):
		return str(self.song)

class Follow(models.Model):
	follower = models.ForeignKey(User, related_name="follower")#外鍵
	followee = models.ForeignKey(User, related_name="followee")#外鍵
	
	def __str__(self):
		return str(self.followee)

class Comment(models.Model):
	user = models.ForeignKey(User)	#外鍵
	song = models.ForeignKey(Song)	#外鍵
	content = models.TextField()
	commentTime = models.DateTimeField(auto_now_add=True)

	def __str__(self): 
		return str(self.content)

class Rating(models.Model):
	user = models.ForeignKey(User)	#外鍵
	song = models.ForeignKey(Song)	#外鍵
	good_grade = models.IntegerField(default=0)
	bad_grade = models.IntegerField(default=0)

class Hashtag(models.Model):
	tagName = models.CharField(max_length=20)
	song = models.ForeignKey(Song)

	def __str__(self):
		return str(self.tagName)
