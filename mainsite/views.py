from django.shortcuts import render, redirect, get_object_or_404
from django.dispatch import receiver
from allauth.account.signals import email_confirmed
from django.contrib.auth.models import User
from .models import *
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Count
from django.template.loader import get_template

# Create your views here.
def index(request):
	template = 'index.html'
	args = {}
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
			data1 = json.loads(data1.decode('utf-8'))['綜合標音'][0]['臺羅數字調']
			tmpL.append(data1)
			return HttpResponse(tmpL)


def video(request, id):
	template = get_template('video.html')
	song = Song.objects.get(songID=id)
	lyrics = Lyric.objects.filter(song=song)#.order_by('start_time')
	youtube_id = song.videoURL	
	viewNumbers = song.viewNumber + 1
	Song.objects.filter(songID=id).update(viewNumber=viewNumbers)
	song_id= id
	modify= False 
	this_song_comments = Comment.objects.filter(song=song)
	show_comments = this_song_comments.order_by('commentTime')[:5]
	#this_page_comments = 
	login_out = " 登出"
	user= None
	if request.user.is_authenticated():
		username = request.user.username
		user = User.objects.get(username=username)
		if song.uploader==User.objects.get(username=request.user.username):
			modify=True
		else:
			modify= False
		rating = Rating.objects.filter(user=user,song=song)
		check_user_rating =  Rating.objects.filter(user=user,song=song,good_grade=1)
		check_user_favorite = Favorite.objects.filter(user=user,song=song)
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
				message = "感謝您的評論!"
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
		isFavorite = "收藏"
	else:
		isFavorite = "取消收藏"

	html = template.render(locals())
	return HttpResponse(html)


def favorite(request, favoriteMotion, id):
	username = request.user.username
	user = User.objects.get(username=username)
	song = Song.objects.get(songID=id)
	
	if favoriteMotion=="create":
		f = Favorite.objects.create(user=user, song=song)
	elif favoriteMotion=="delete":
		f = Favorite.objects.get(user=user, song=song)
		f.delete()
	else:
		f = 87
	
	return redirect("/")

def modify(request):
	if 'id' in request.GET:
		print(type(request.GET['id']))
		template = get_template('modifymode2.html')
		song = Song.objects.get(songID=request.GET['id'])
		song_title=song.title
		song_singer=song.singer
		song_lyricist=song.lyricist
		song_composer=song.composer
		song_videoURL=song.videoURL
		song_id=song.songID
		lyrics = Lyric.objects.filter(song=song) 
		html = template.render(locals())
		return HttpResponse(html)

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
			Any = get_object_or_404(Lyric,id=Lid[i])    
			Any.delete()
			l = Lyric.objects.create(song=this_song, start_time=float(sTime[i]), end_time=float(eTime[i]), text=lyricsText[i], pinyin=ALText[i], order=order[i])
			l.save()

		return HttpResponseRedirect('/video/'+str(this_song.songID))
	else:
		return HttpResponse("error")

def follow(request, followMotion, id):
	username = request.user.username
	user1 = User.objects.get(username=username)
	user2 = User.objects.get(username=id)
	
	if followMotion=="create":
		f = Follow.objects.create(follower=user1, followee=user2)
	elif followMotion=="delete":
		f = Follow.objects.get(follower=user1, followee=user2)
		f.delete()
	else:
		f = 87
	
	return redirect("/")