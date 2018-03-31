from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from cfd.models import chats,users
import json
from keras.models import load_model
import h5py
import pandas as pd
from keras.preprocessing import sequence
import re
import numpy as np
from keras import backend as K
import pusher
import cntk as c
max_length = 35
embedding_vector_length = 100


emoji_map={}
emoji_map['eoji1f384']=':christmas_tree:'
emoji_map['eoji1f495']=':revolving_hearts:'
emoji_map['eoji1f4af']=':100:'
emoji_map['eoji1f525']=':fire:'
emoji_map['eoji1f602']=':joy:'
emoji_map['eoji1f60a']=':blush:'
emoji_map['eoji1f60d']=':heart_eyes:'
emoji_map['eoji1f618']=':kissing_heart:'
emoji_map['eoji1f64c']=':open_hands:'
emoji_map['eoji2764']=':heart:'
emoji_map['eoji1f389']=':tada:'
emoji_map['eoji1f44c']=':ok_hand:'
emoji_map['eoji1f48b']=':kiss:'
emoji_map['eoji1f499']=':blue_heart:'
emoji_map['eoji1f4aa']=':muscle:'
emoji_map['eoji1f60e']=':sunglasses:'
emoji_map['eoji1f62d']=':sob:'
emoji_map['eoji1f64f']=':pray:'
emoji_map['eoji2728']=':sparkles:'
emoji_map['eoji2744']=':snowflake:'

label_map={}
label_map['0']='eoji1f384'
label_map['1']='eoji1f389'
label_map['2']='eoji1f44c'
label_map['3']='eoji1f48b'
label_map['4']='eoji1f495'
label_map['5']='eoji1f499'
label_map['6']='eoji1f4aa'
label_map['7']='eoji1f4af'
label_map['8']='eoji1f525'
label_map['9']='eoji1f602'
label_map['10']='eoji1f60a'
label_map['11']='eoji1f60d'
label_map['12']='eoji1f60e'
label_map['13']='eoji1f618'
label_map['14']='eoji1f62d'
label_map['15']='eoji1f64c'
label_map['16']='eoji1f64f'
label_map['17']='eoji2728'
label_map['18']='eoji2744'
label_map['19']='eoji2764'

pusher_client = pusher.Pusher(
  app_id='497553',
  key='00f94d2692aca226deee',
  secret='c32ee5679e33c89bf962',
  cluster='ap2',
  ssl=True
)


word_dict={}
with open('cfd/word_dict.json','r') as fp:
	word_dict=json.load(fp)

model=load_model('cfd/rnn.h5')

def index(request):
	if request.session.get("user_id"):
		return HttpResponseRedirect('/chating')
	return render_to_response('login.html')
@csrf_exempt
def signup(request):
	if request.method=='GET':
		return render_to_response('signup.html')
	else:
		name=request.POST.get("name")
		username=request.POST.get("username")
		password=request.POST.get("password")
		user=users(name=name,username=username,password=password)
		user.save()
		request.session['user_id']=None
		return render_to_response('login.html')
@csrf_exempt
def forgot(request):
	if request.method=="POST":
		username =request.POST.get("username")
		password=request.POST.get("password")
		user=users.objects.get(username=username)
		user.password=password
		user.save()
		request.session['user_id']=None
		return render_to_response('login.html')	
	return render_to_response('forgot.html')

@csrf_exempt
def logout(request):
	request.session['user_id']=''
	return HttpResponseRedirect('/index')

@csrf_exempt
def login(request):
	if request.method == "POST":
		username =request.POST.get("username")
		password=request.POST.get("password")
		user=users.objects.filter(username=username,password=password)
		if len(user)==0:
			return HttpResponse(json.dumps({'login':-1}),content_type='application/json')
		else:
			user_id=int(users.objects.get(username=username,password=password).id)
			request.session['user_id']=user_id 
			return HttpResponse(json.dumps({'login':1,'user_id':user_id}),content_type="application/json")

def chat(request):
	return render_to_response('chat.html')

@csrf_exempt
def sendMessage(request):
	result={}
	result['msg']=-1
	if request.method == "POST":
		dataObj = json.loads(request.body)
		message =dataObj["message"]
		msg_from =request.session.get('user_id')
		msg_to =int(dataObj["msg_to"])
		chat=chats(msg=message,msg_to=msg_to,msg_from=msg_from)
		chat.save()
		result['message']=message
		result['to']=msg_to
		result['from']=msg_from
		result['emoji'],result['unicode']=run(message)
		pusher_client.trigger('chatterJi', 'newMsg', result)
		print result['emoji'],result['unicode']
		return HttpResponse(json.dumps(result),content_type="application/json")
	else : return HttpResponse(json.dumps(result),content_type="application/json")

@csrf_exempt
def suggestEmoji(request):
	if request.method=="POST":
		msg=json.loads(request.body)["message"]
		result={}
		result['emoji'],result['unicode']=run(msg)
		return HttpResponse(json.dumps(result),content_type="application/json")
def tokenize(tweet):
    tokens = re.sub('[!\.#\'\",:?(){}<>;\@/|=$%^*]', '', tweet)
    tokens = re.sub('[_-]', ' ', tokens)
    tokens = re.sub('user', ' <user> ', tokens)
    tokens = re.sub('&+', 'and', tokens)
    tokens = re.sub('\d+', ' <num> ', tokens)
    tokens = tokens.split()
    return tokens

def indexify(tweet):
    indexes = list()
    for word in tweet:
        try:
            indexes.append(word_dict[word])
        except KeyError:
            indexes.append(0)
    return indexes

def create_indexed_tweets(df):
  df['indexed_tweets'] = df['Tweet'].apply(lambda x:tokenize(x))
  df['indexed_tweets'] = df['indexed_tweets'].apply(lambda x:indexify(x))

def run(msg):
	# my_test={'Tweet':['This food is delicious', 'I would like to have a chat with you','This is better than i thought','you totally rock','This is cool bro','The weather is awesome','I miss you','This is not possible',"You're cool bro"]}
	my_test={}
	my_test['Tweet']=[msg]
	my_df=pd.DataFrame(data=my_test)
	create_indexed_tweets(my_df)
	my_set= sequence.pad_sequences(my_df.indexed_tweets.values,maxlen=max_length)
	pred=[]
	for i in xrange(20):
		pred.append([model.predict(my_set)[0][i],i])
	# pred = np.argmax(model.predict(my_set), axis=1)
	pred=sorted(pred,key=lambda x: x[0])
	pred_list=[]
	pred_list1=[]
	for i in pred[-3:]:
	  	pred_list.append(label_map[str(i[1])])
	  	pred_list1.append(emoji_map[label_map[str(i[1])]])
	print pred_list1
	return pred_list1[::-1],pred_list[::-1]

def interface(request):
	user_id=request.session.get('user_id')
	if not user_id:
		return HttpResponseRedirect('/index')
	uname=users.objects.get(id=user_id).name
	print uname
	return render_to_response('chats.html', {"name": uname,'user_id':user_id})

def getUsers(request):
	all_users={}
	all_users["online"]=[]
	user_id=request.session.get("user_id")
	for user in users.objects.all():
		if user.id != user_id:
			user_dict={}
			user_dict['name']=user.name
			user_dict['id']=user.id
			all_users["online"].append(user_dict)
	return HttpResponse(json.dumps(all_users),content_type="application/json")

def data(request):
	messages={}
	messages['messages']=[]
	true,false =True,False 
	toid= int(request.GET.get("id"))
	user_id=request.session.get('user_id')
	print user_id,toid
	for chat in chats.objects.all():
		msg_dict={}
		if (chat.msg_from==toid or chat.msg_to==toid) and (chat.msg_from==user_id or chat.msg_to==user_id): 
			msg_dict={}
			msg_dict["message"]=chat.msg
			if chat.msg_from==user_id: 
				msg_dict['me']=true
			else: 
				msg_dict['me']=false
			messages['messages'].append(msg_dict)
	return HttpResponse(json.dumps(messages),content_type="application/json")
def emoji(request):
	emoji={}
	emoji['data']=[
		        {"name": ":christmas_tree:","emoji": ""},
        		{"name": ":revolving_hearts:","emoji": ""},
        		{"name": ":100:","emoji": ""},
        		{"name": ":fire:","emoji": ""},
        		{"name": ":joy:","emoji": ""},
        		{"name": ":blush:","emoji": ""},
     			{"name": ":heart_eyes:","emoji": ""},
				{"name": ":kissing_heart:","emoji": ""},
        		{"name": ":open_hands:","emoji": ""},
				{"name": ":heart:","emoji": ""},
        		{"name": ":tada:","emoji": ""},
        		{"name": ":kiss:","emoji": ""},
        		{"name": ":blue_heart:", "emoji": ""},
        		{"name": ":muscle:", "emoji": ""},
        		{"name": ":sunglasses:", "emoji": ""},
        		{"name": ":sob:", "emoji": ""},
        		{"name": ":pray:", "emoji": ""},
        		{"name": ":sparkles:", "emoji": ""},
        		{"name": ":ok_hand:", "emoji": ""},
        		{"name": ":snowflake:", "emoji": ""},]

	return HttpResponse(json.dumps(emoji),content_type="application/json")
