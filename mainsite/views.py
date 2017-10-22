from django.shortcuts import render, redirect, get_object_or_404
from django.dispatch import receiver
from allauth.account.signals import email_confirmed
from django.contrib.auth.models import User
from .models import *
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Count
from django.template.loader import get_template
import http.client
from urllib import parse
import socket
import json
import os
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.conf import settings


# Create your views here.
def index(request):
	template = 'index.html'
	args = {}
	
	song_list1 = Song.objects.all().order_by('-uploadTime')[:5]
	song_list2 = Song.objects.all().order_by('-viewNumber')[:5]
		
	args['song_list1'] = song_list1
	args['song_list2'] = song_list2

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

		order = request.POST.getlist('order')
		lyricsText = request.POST.getlist('lyricsText')
		ALText = request.POST.getlist('ALText')
		sTime = request.POST.getlist('sText')
		eTime = request.POST.getlist('eText')
		count = len(lyricsText)

		uploader = User.objects.get(username=request.POST['producer'])

		vp = Song.objects.create(title=title, videoURL=vid, singer=singer, composer=composer, lyricist=lyricist, viewNumber=0, uploader=uploader)
		vp.save()

		for i in range(count):
			l = Lyric.objects.create(song=vp, start_time=float(sTime[i]), end_time=float(eTime[i]), text=lyricsText[i], pinyin=ALText[i], order=order[i])
			l.save()
		return HttpResponseRedirect('/video/' + str(vp.songID))
	else:
		return render(request, template, args)

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
			if typeofAL=='N':
				data1 = json.loads(data1.decode('utf-8'))['綜合標音'][0]['臺羅數字調']
			elif typeofAL=='S':
				data1 = json.loads(data1.decode('utf-8'))['綜合標音'][0]['臺羅閏號調']
			else:
				data1 = json.loads(data1.decode('utf-8'))['綜合標音'][0]['吳守禮方音']
			
			tmpL.append(data1)
			return HttpResponse(tmpL)



def video(request, id):
	template = "video.html"
	args = {}
	profile_srch_list = []
	profile_imgs = {}
	song = Song.objects.get(songID=id)
	args['song'] = song;
	args['lyrics'] = Lyric.objects.filter(song=song)#.order_by('start_time')	
	viewNumbers = song.viewNumber + 1
	Song.objects.filter(songID=id).update(viewNumber=viewNumbers)
	modify = False 
	this_song_comments = Comment.objects.filter(song=song)
	for comment in this_song_comments:
		if comment.user not in profile_srch_list:
			profile_srch_list.append(comment.user)

	profiles = Profile.objects.filter(user__in=profile_srch_list)
	for profile in profiles:
		profile_imgs[profile.user.username] = profile.profileImg

	args['profile_imgs'] = profile_imgs
	args['this_song_comments'] = this_song_comments
	args['show_comments'] = this_song_comments.order_by('commentTime')[:5]
	login_out = " 登出"
	user= None
	if request.user.is_authenticated():
		username = request.user.username
		user = User.objects.get(username=username)
		if song.uploader==User.objects.get(username=request.user.username):
			modify=True
		else:
			modify= False

		args['modify'] = modify;
		rating = Rating.objects.filter(user=user,song=song)
		args['check_user_rating'] =  Rating.objects.filter(user=user,song=song,good_grade=1)
		args['check_user_favorite'] = Favorite.objects.filter(user=user,song=song)
		warning = username + login_out
		if request.method == 'POST':
			if 'goodgrade' in request.POST:
				user_goodgrade = request.POST['goodgrade']
				if(user_goodgrade):
					goodnumber = int(user_goodgrade)
					#check =  "有user_goodegrade" + user_goodgrade
					if (int(goodnumber) == 1):
						goodgrade = Rating.objects.create(user=user,song=song,good_grade=user_goodgrade,bad_grade=0)
						goodgrade.save()

					else:
						rating.delete()	
			if 'favorite' in request.POST:
				user_fav = request.POST['favorite']
				if(user_fav):
					fav_num = int(user_fav)
					if(int(fav_num) == 1):
						favorite = Favorite.objects.create(user=user,song=song)
						favorite.save()
						tellme = "save"
					else:
						favorite = Favorite.objects.filter(user=user,song=song)
						favorite.delete()
						tellme = "delete"
			if 'comment_id' in request.POST:
				user_comment = request.POST['comment_id']
				args['message'] = "感謝您的評論!"
				comment = Comment.objects.create(user=user,song=song,content=user_comment)
				comment.save()
				warning = "成功儲存!"
			else:
				comment_id = False
		else:
			user_comment = None
			message = "無留言送出!"
	else:
		username = None
		warning = "您尚未登入"

	this_song_fav = Favorite.objects.filter(song=song)
	this_song_good_ratings = Rating.objects.filter(song=song,good_grade=1)

	try:
		f = Favorite.objects.get(user=user, song=song)
	except Favorite.DoesNotExist:
		f = None
	
	if f == None:
		args['isFavorite'] = False
	else:
		args['isFavorite'] = True

	return render(request, template, args);


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

	return HttpResponse(isFavorite);

def modify(request):
	if 'id' in request.GET:
		template = 'modifymode.html'
		args = {}
		song = Song.objects.get(songID=request.GET['id'])
		args['song'] = song
		args['lyrics'] = Lyric.objects.filter(song=song) 
		return render(request, template, args)

def aftermodify(request):
	if request.POST:
		title = request.POST['title']
		singer = request.POST['singer']
		composer = request.POST['composer']
		lyricist = request.POST['lyricist']
		this_song = Song.objects.get(songID=request.POST['SongID'])

		order = request.POST.getlist('order')
		lyricsText = request.POST.getlist('lyricsText')
		ALText = request.POST.getlist('ALText')
		sTime = request.POST.getlist('sText')
		eTime = request.POST.getlist('eText')
		Lid = request.POST.getlist('id')
		count = len(lyricsText)

		for i in range(count):
			if Lid[i] !='-1':
				Any = get_object_or_404(Lyric,id=Lid[i])    
				Any.delete()
			l = Lyric.objects.create(song=this_song, start_time=float(sTime[i]), end_time=float(eTime[i]), text=lyricsText[i], pinyin=ALText[i], order=order[i])
			l.save()

		return HttpResponseRedirect('/video/'+str(this_song.songID))
	else:
		return HttpResponse("error")

def follow(request, followMotion, id):
	username = request.user.username
	user = User.objects.get(username=username)
	user2 = User.objects.get(username=id)
	
	if followMotion=="create":
		f = Follow.objects.create(follower=user, followee=user2)
	elif followMotion=="delete":
		f = Follow.objects.get(follower=user, followee=user2)
		f.delete()
	else:
		f = 87
	
	return redirect("/")

@login_required(login_url='/accounts/login/')
def userinfo(request, id):
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
	uploadSongs = Song.objects.filter(uploader=user2)
	follows = Follow.objects.filter(follower=user)
	
	try:
		f = Follow.objects.get(follower=user, followee=user2)
	except Follow.DoesNotExist:
		f = None
	
	if f == None:
		isFollowing = "追蹤"
	else:
		isFollowing = "取消追蹤"
	
	args['user2'] = user2
	args['userinfo'] = userinfo
	args['favorites'] = favorites
	args['uploadSongs'] = uploadSongs
	args['follows'] = follows
	args['isFollowing'] = isFollowing
	args['id'] = id
	
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
	
	if id == "1":
		song_list = Song.objects.all().order_by('-uploadTime')
	elif id == "2":
		song_list = Song.objects.all().order_by('-viewNumber')
	else:
		song_list = 87
	
	paginator = Paginator(song_list, 5)
	page = request.GET.get('page')
	try:
		songs = paginator.page(page)
	except PageNotAnInteger:
		songs = paginator.page(1)
	except EmptyPage:
		songs = paginator.page(paginator.num_pages)
	
	args['songs'] = songs
	
	return render(request, template, args)

def uploadImage(request):
	if request.method == "POST":
		profile = Profile.objects.get(user=request.user)
		if profile.profileImg:
			os.remove(os.path.join(settings.MEDIA_ROOT, profile.profileImg.name))
			
		profile.profileImg = request.FILES['imgFile']
		profile.save()
	
	return HttpResponseRedirect("/userinfo/" + request.user.username)

def deleteImage(request):
	profile = Profile.objects.get(user=request.user)
	if profile.profileImg: 
			os.remove(os.path.join(settings.MEDIA_ROOT, profile.profileImg.name))
			profile.profileImg.delete()
	profile.save()
	return HttpResponseRedirect("/userinfo/" + request.user.username)

