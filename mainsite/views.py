from django.shortcuts import render, redirect, get_object_or_404
from django.dispatch import receiver
from allauth.account.signals import email_confirmed
from django.contrib.auth.models import User
from .models import *
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db.models import Count
from django.template.loader import get_template
import http.client
from urllib import parse
import socket
import json
import os
import random
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.template.context_processors import csrf
from django.utils import timezone
import operator
from django.db.models import Q



# Create your views here.
def home(request):
	template = 'home.html'
	args = {}
	return render(request, template, args)

def index(request):
	template = 'index.html'
	args = {}
	
	if request.user.is_authenticated():
		username = request.user.username
		user = User.objects.get(username=username)
		
		if Follow.objects.filter(follower=user):
			follows = Follow.objects.filter(follower=user)
			rfollow = random.choice(follows)
			user2 = User.objects.get(username=rfollow)
			song_list_followee = Song.objects.filter(uploader=user2).order_by('-uploadTime')[:5]
			args['user2'] = user2
			args['song_list_followee'] = song_list_followee
		else:
			args['song_list_followee'] = None
		
	
	song_list_by_uploadTime = Song.objects.all().order_by('-uploadTime')[:5]
	song_list_by_viewNumber = Song.objects.all().order_by('-viewNumber')[:5]
	song_list_by_pinyinType0 = Song.objects.filter(pinyinType=0).order_by('-uploadTime')[:5]
	song_list_by_pinyinType1 = Song.objects.filter(pinyinType=1).order_by('-uploadTime')[:5]
	song_list_by_pinyinType2 = Song.objects.filter(pinyinType=2).order_by('-uploadTime')[:5]
	
	args['song_list_by_uploadTime'] = song_list_by_uploadTime
	args['song_list_by_viewNumber'] = song_list_by_viewNumber
	args['song_list_by_pinyinType0'] = song_list_by_pinyinType0
	args['song_list_by_pinyinType1'] = song_list_by_pinyinType1
	args['song_list_by_pinyinType2'] = song_list_by_pinyinType2

	return render(request, template, args)

@receiver(email_confirmed)
def createProfile(request, email_address, **kwargs):
	user = User.objects.get(email=email_address.email)
	profile = Profile.objects.create(user=user)
	profile.save()


def email_confirmation_success(request):
	template = 'email_confirmation_success.html'
	args = {}
	return render(request, template, args)

def makeNew(request):
	template = 'makeNew.html'
	args = {}
	if request.POST:
		title = request.POST['title']
		vid = request.POST['vid']
		singer = request.POST['singer']
		composer = request.POST['composer']
		lyricist = request.POST['lyricist']
		pinyinType = request.POST['pinyinType']
		productionPerformance = request.POST['productionPerformance']
		content = request.POST['SongContentI']
		tags = request.POST['tags']

		order = request.POST.getlist('order')
		lyricsText = request.POST.getlist('lyricsText')
		ALText = request.POST.getlist('ALText')
		sTime = request.POST.getlist('sText')
		eTime = request.POST.getlist('eText')
		count = len(lyricsText)

		uploader = User.objects.get(username=request.POST['producer'])

		vp = Song.objects.create(title=title, videoURL=vid, singer=singer, composer=composer, lyricist=lyricist, viewNumber=0, uploader=uploader, pinyinType=int(pinyinType), productionPerformance=float(productionPerformance), content=content)
		vp.save()

		for i in range(count):
			l = Lyric.objects.create(song=vp, start_time=float(sTime[i]), end_time=float(eTime[i]), text=lyricsText[i], pinyin=ALText[i], order=order[i])
			l.save()

		tags = tags.split('#');
		tagslength = len(tags);
		for i in range(tagslength):
			if i>0:
				T = Hashtag.objects.create(tagName=tags[i], song=vp)
				T.save()


		return HttpResponseRedirect('/video/' + str(vp.songID))
	else:
		return render(request, template, args)

def TagFounder(request):
	if request.is_ajax():
		if request.method == 'POST':
			tmp = json.loads(request.body.decode('utf-8'))
			tmpL = Hashtag.objects.filter(tagName__contains = tmp)
			s=[]
			for tagName in tmpL:
				s.append(tagName)
				s.append('/')
			
			return HttpResponse(s)

def autoAL(request):
	if request.is_ajax():
		if request.method == 'POST':
			tmp = json.loads(request.body.decode('utf-8'))
			typeofAL = tmp[0]
			hostname = socket.gethostbyname("xn--7zrr5mu7u.xn--v0qr21b.xn--kpry57d")
			uri = '/' + parse.quote("標漢字音標") + '?' + parse.quote("查詢腔口") + '=' + parse.quote("閩南語") + '&' + parse.quote("查詢語句") + '={0}'
			
			tmpL=[]
			conn = http.client.HTTPConnection("xn--lhrz38b.xn--v0qr21b.xn--kpry57d")
			conn.request(
						'GET',
						 uri.format(parse.quote(tmp))
					)

			r1 = conn.getresponse()
			data1 = r1.read()
			if typeofAL=='1':
				data1 = json.loads(data1.decode('utf-8'))['綜合標音'][0]['臺羅數字調']
			elif typeofAL=='0':
				data1 = json.loads(data1.decode('utf-8'))['綜合標音'][0]['臺羅閏號調']
			elif typeofAL=='2':
				data1 = json.loads(data1.decode('utf-8'))['綜合標音'][0]['吳守禮方音']
			else:
				data1 = json.loads(data1.decode('utf-8'))['綜合標音'][0]['通用數字調']
			
			tmpL.append(data1)
			return HttpResponse(tmpL)


def video(request, id):
	template = "video.html"
	args = {}
	args['now'] = timezone.now()
	
	song = Song.objects.get(songID=id)
	args['song'] = song;
	args['lyrics'] = Lyric.objects.filter(song=song)#.order_by('start_time')	
	viewNumbers = song.viewNumber + 1
	Song.objects.filter(songID=id).update(viewNumber=viewNumbers)
	modify = False 
	this_song_comments = Comment.objects.filter(song=song)

	# get all comment users' profile image 
	comment_profile_srch_list = []
	comment_profile_imgs = {}
	for comment in this_song_comments:
		if comment.user not in comment_profile_srch_list:
			comment_profile_srch_list.append(comment.user)
	profiles = Profile.objects.filter(user__in=comment_profile_srch_list)
	for profile in profiles:
		comment_profile_imgs[profile.user.username] = profile.profileImg
	args['comment_profile_imgs'] = comment_profile_imgs


	args['this_song_comments'] = this_song_comments
	args['show_comments'] = this_song_comments.order_by('commentTime')#[:5]
	login_out = " 登出"
	user= None
	if request.user.is_authenticated():
		username = request.user.username
		user = User.objects.get(username=username)
		args['user'] = user;
		
		if song.uploader==User.objects.get(username=request.user.username):
			modify=True
		else:
			modify= False

		#check following
		try:
			Follow.objects.get(follower=request.user, followee=song.uploader)
			isFollowing = True
		except Follow.DoesNotExist:
			isFollowing = False
		args["isFollowing"] = isFollowing


		args['modify'] = modify;
		args['check_user_rating'] =  Rating.objects.filter(user=user,song=song,good_grade=1)
		args['check_user_favorite'] = Favorite.objects.filter(user=user,song=song)
		warning = username + login_out
	else:
		username = None
		warning = "您尚未登入"
	###favorite 圖形初始畫面
	try:
		f = Favorite.objects.get(user=user, song=song)
	except Favorite.DoesNotExist:
		f = None
	
	if f == None:
		args['isFavorite'] = False
	else:
		args['isFavorite'] = True
	###like 圖形初始畫面
	try:
		r = Rating.objects.get(user=user, song=song, good_grade=1, bad_grade=0)
	except Rating.DoesNotExist:
		r = None

	if r == None:
		args['isLike'] = False
	else:
		args['isLike'] = True
	### 取得此首歌的按讚數
	this_song_good_ratings = Rating.objects.filter(song=song,good_grade=1)
	args['this_song_good_ratings'] = this_song_good_ratings

	return render(request, template, args);

def comment(request, id):
	username = request.user.username
	user = User.objects.get(username=username)
	song = Song.objects.get(songID=id)
	
	if request.method == 'POST':
		user_comment = request.POST['comment_id']

		comment = Comment.objects.create(user=user, song=song, content=user_comment)
		comment.save()
		mes = "comment saved already"
	else:
		mes = "oooooooops"

	return HttpResponse(comment)

def modify_text(request,id):
	song = Song.objects.get(songID=id)
	args = {}
	if request.user.is_authenticated():			
		if song.uploader==User.objects.get(username=request.user.username):
			if request.method =='POST':
				mdf_pinyin = request.POST['mdf_pinyin']
				mdf_text = request.POST['mdf_text']
				mdf_order = request.POST['mdf_order']
				Lyric.objects.filter(song=song,order=mdf_order).update(text=mdf_text,pinyin=mdf_pinyin)
				Data = {
					'mdf_pinyin': mdf_pinyin,
					'mdf_text': mdf_text,
					'mdf_order': mdf_order
				}
				modify_text = "編輯成功!"
			else:
				modify_text = "編輯失敗QQ"
		else:
			return false
	else:
		return false
	return JsonResponse(Data)

def like(request, id):
	username = request.user.username
	user = User.objects.get(username=username)
	song = Song.objects.get(songID=id)
	try:
		r = Rating.objects.get(user=user, song=song, good_grade=1, bad_grade=0)
	except Rating.DoesNotExist:
		r = None

	if r:
		r.delete()
		isLike = 0;
	else:
		r = Rating.objects.create(user=user, song=song, good_grade=1, bad_grade=0)
		r.save()
		isLike = 1;

	this_song_good_ratings = Rating.objects.filter(song=song,good_grade=1)
	count_ratings = len(this_song_good_ratings)
	Data = {
		'isLike': isLike,
		'count_ratings': count_ratings
	}

	return JsonResponse(Data)

def favorite(request, id):
	username = request.user.username
	user = User.objects.get(username=username)
	song = Song.objects.get(songID=id)

	try:
		f = Favorite.objects.get(user=user, song=song)
	except Favorite.DoesNotExist:
		f = None

	if f:
		f.delete()
		isFavorite = 0;
	else:
		f = Favorite.objects.create(user=user, song=song)
		f.save();
		isFavorite = 1;

	return HttpResponse(isFavorite)

def modify(request):
	if 'id' in request.GET:
		template = 'modifymode.html'
		args = {}
		song = Song.objects.get(songID=request.GET['id'])
		args['song'] = song
		args['lyrics'] = Lyric.objects.filter(song=song)
		args['hashtag'] = Hashtag.objects.filter(song=song)
		return render(request, template, args)

def aftermodify(request):
	if request.POST:
		delete = request.POST['IfDelete']
		title = request.POST['title']
		singer = request.POST['singer']
		composer = request.POST['composer']
		lyricist = request.POST['lyricist']
		videoURL = request.POST['videoURL']
		content = request.POST['SongContentI']
		tags = request.POST['tags']
		this_song = Song.objects.get(songID=request.POST['SongID'])
		
		if delete !='0':
			this_song.delete()
			return HttpResponseRedirect('/songlist/byuploadtime')
		else:
			Song.objects.filter(songID=request.POST['SongID']).update(singer=singer, composer=composer, lyricist=lyricist, title=title, videoURL=videoURL, content=content)
			order = request.POST.getlist('order')
			lyricsText = request.POST.getlist('lyricsText')
			ALText = request.POST.getlist('ALText')
			sTime = request.POST.getlist('sText')
			eTime = request.POST.getlist('eText')
			Lid = request.POST.getlist('id')
			count = len(lyricsText)

			deleteL = Lyric.objects.filter(song=this_song)
			deleteL.delete()

			for i in range(count):
				l = Lyric.objects.create(song=this_song, start_time=float(sTime[i]), end_time=float(eTime[i]), text=lyricsText[i], pinyin=ALText[i], order=order[i])
				l.save()

			tags = tags.split('#');
			tagslength = len(tags);
			for i in range(tagslength):
				if i>0:
					try:
					    T = Hashtag.objects.get(tagName=tags[i], song=this_song)
					except Hashtag.DoesNotExist:
					    T = Hashtag(tagName=tags[i], song=this_song)
					    T.save()

			return HttpResponseRedirect('/video/'+str(this_song.songID))
	else:
		return HttpResponse("error")

def follow(request, id):
	username = request.user.username
	user = User.objects.get(username=username)
	uploader = User.objects.get(username=id)
	action = ""

	try:
		f = Follow.objects.get(follower=user, followee=uploader)
		f.delete()
		action = "notFollow"
	except Follow.DoesNotExist:
		f = Follow.objects.create(follower=user, followee=uploader)
		f.save()
		action = "following"

	return HttpResponse(action)

@login_required(login_url='/accounts/login/')
def userinfo(request, id, view):
	template = 'userinfo.html'
	args = {}

	username = request.user.username
	user = User.objects.get(username=username)
	user2 = User.objects.get(username=id)
	userinfo = Profile.objects.get(user=user2)
	
	if request.POST.get('nickname') is not None:
		userinfo.nickname = request.POST.get('nickname')
		userinfo.save()
	if request.POST.get('gender') is not None:	
		userinfo.gender = request.POST.get('gender')
		userinfo.save()
	if request.POST.get('birthdate') is not None:
		userinfo.birthdate = request.POST.get('birthdate')
		userinfo.save()
	
	favorites = Favorite.objects.filter(user=user2)
	uploadSongs = Song.objects.filter(uploader=user2).order_by("-uploadTime")
	follows = Follow.objects.filter(follower=user2)

	
	try:
		f = Follow.objects.get(follower=user, followee=user2)
	except Follow.DoesNotExist:
		f = None
	
	if f == None:
		isFollowing = "追蹤"
	else:
		isFollowing = "已追蹤"
	
	# get all following users' profile image 
	follow_profile_srch_list = []
	follow_profile_imgs = {}
	for follow in follows:
		follow_profile_srch_list.append(follow.followee)
	profiles = Profile.objects.filter(user__in=follow_profile_srch_list)
	for profile in profiles:
		follow_profile_imgs[profile.user.username] = profile.profileImg
	args['follow_profile_imgs'] = follow_profile_imgs

	args['user2'] = user2
	args['userinfo'] = userinfo
	args['favorites'] = favorites
	args['uploadSongs'] = uploadSongs
	args['follows'] = follows
	args['isFollowing'] = isFollowing
	args['id'] = id
	args['view'] = view
	
	return render(request, template, args)
	
def userinfoEdit(request):
	template = 'userinfoedit.html'
	args = {}
	
	username = request.user.username
	user = User.objects.get(username=username)
	userinfo = Profile.objects.get(user=user)
	
	args['user'] = user
	args['userinfo'] = userinfo
	
	return render(request, template, args)

def songlist(request, id):
	template = 'songlist.html'
	args = {}
	
	if id == "byuploadtime":
		song_list = Song.objects.all().order_by('-uploadTime')
	elif id == "byviewnumber":
		song_list = Song.objects.all().order_by('-viewNumber')	
	elif id == "bypinyin0":
		song_list = Song.objects.filter(pinyinType=0)
	elif id == "bypinyin1":
		song_list = Song.objects.filter(pinyinType=1)
	elif id == "bypinyin2":
		song_list = Song.objects.filter(pinyinType=2)
	else:
		song_list = 87
	
	paginator = Paginator(song_list, 10)
	page = request.GET.get('page')
	try:
		songs = paginator.page(page)
	except PageNotAnInteger:
		songs = paginator.page(1)
	except EmptyPage:
		songs = paginator.page(paginator.num_pages)
	
	if (songs.number-3) < 1:
		theFirstPreviousPage=1
	else:
		theFirstPreviousPage=songs.number-3
		
	if (songs.number+3) > paginator.num_pages:
		theLastNextPage=paginator.num_pages
	else:
		theLastNextPage=songs.number+4
	
	songsRange=[]
	for i in range(theFirstPreviousPage, theLastNextPage):
		songsRange.append(i)
	
	theFirstPage=1
	theLastPage=paginator.num_pages
	
	args['songs'] = songs
	args['songsRange'] = songsRange
	args['theFirstPage'] = theFirstPage
	args['theLastPage'] = theLastPage
	
	return render(request, template, args)

def uploadImage(request):
	if request.method == "POST":
		profile = Profile.objects.get(user=request.user)
		if profile.profileImg:
			os.remove(os.path.join(settings.MEDIA_ROOT, profile.profileImg.name))
			
		profile.profileImg = request.FILES['imgFile']
		profile.save()
	
	return HttpResponseRedirect("/userinfo/" + request.user.username + "/videos")

def deleteImage(request):
	profile = Profile.objects.get(user=request.user)
	if profile.profileImg: 
			os.remove(os.path.join(settings.MEDIA_ROOT, profile.profileImg.name))
			profile.profileImg.delete()
	profile.save()
	return HttpResponseRedirect("/userinfo/" + request.user.username + "/videos")

def reduce(func, items):
	result = items.pop()
	for item in items:
		result = func(result, item)

	return result

def songSearch(request):
	template = "search_result.html"
	args = {}

	keywords = request.GET["keywords"]
	keyword_list = keywords.split(" ")
	
	songs = Song.objects.filter(reduce(operator.or_, [Q(title__contains=keyword) for keyword in keyword_list]) | 
								reduce(operator.or_, [Q(singer__contains=keyword) for keyword in keyword_list]) |
								reduce(operator.or_, [Q(content__contains=keyword) for keyword in keyword_list]) |
								reduce(operator.or_, [Q(videoURL__contains=keyword) for keyword in keyword_list]))


	args = {
		'songs': songs
	}
	return render(request, template, args)

