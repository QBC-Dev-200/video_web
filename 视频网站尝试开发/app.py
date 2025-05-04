from flask import Flask, render_template,jsonify,session,request,redirect,url_for,send_file
from werkzeug.security import generate_password_hash,check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_,and_
from functools import wraps
from datetime import datetime, timedelta
import os
import random
import uuid

app = Flask(__name__)
VIDEO_PATH=os.path.join(os.path.abspath(os.path.dirname(__file__)),'static','video')
USER_IMG_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'user_img')
MUSEIES_PATH=os.path.join(os.path.abspath(os.path.dirname(__file__)),'static','music')
MUSIC_IMG_PATH=os.path.join(os.path.abspath(os.path.dirname(__file__)),'static','music_img')
app.config['SECRET_KEY']='none'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.db'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # session 保持 7 天
app.config['SESSION_TYPE'] = 'filesystem'

db=SQLAlchemy(app)

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(100),unique=True,nullable=False)
    password_hash=db.Column(db.String(100),nullable=False)
    intor=db.Column(db.String(100),nullable=False,default='这个人很懒，什么都没有留下')
    img=db.Column(db.String(100),nullable=False,default='None')

    def set_password(self,password):
        self.password_hash=generate_password_hash(password)
    
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

class Video(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(100),nullable=False)
    intor=db.Column(db.String(100),nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    video_name=db.Column(db.String(100),nullable=False)
    time=db.Column(db.String(100),nullable=False)

class Museies(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(100),nullable=False)
    img=db.Column(db.String(100),nullable=False,default='默认')
    music=db.Column(db.String(100),nullable=False)
    time=db.Column(db.String(100),nullable=False)

class Like(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,nullable=False)
    video_id=db.Column(db.Integer,nullable=False)

class Comment(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,nullable=False)
    video_id=db.Column(db.Integer,nullable=False)
    content=db.Column(db.String(100),nullable=False)
    time=db.Column(db.String(100),nullable=False)

class Collection(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,nullable=False)
    video_id=db.Column(db.Integer,nullable=False)

class Focus(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,nullable=False)
    focus_id=db.Column(db.Integer,nullable=False)

class Message(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,nullable=False)
    receive_id=db.Column(db.Integer,nullable=False)
    content=db.Column(db.String(100),nullable=False)
    time=db.Column(db.String(100),nullable=False)

class Comment_reply(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,nullable=False)
    comment_id=db.Column(db.Integer,nullable=False)
    content=db.Column(db.String(100),nullable=False)
    time=db.Column(db.String(100),nullable=False)

class Barrage(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,nullable=False)
    content=db.Column(db.String(100),nullable=False)
    time=db.Column(db.String(100),nullable=False)
    progress=db.Column(db.String(100),nullable=False)
    video_id=db.Column(db.Integer,nullable=False)

class Historical_record(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,nullable=False)
    video_id=db.Column(db.Integer,nullable=False)

with app.app_context():
    db.create_all()

if not os.path.exists(USER_IMG_PATH):
    os.makedirs(USER_IMG_PATH)
elif not os.path.exists(VIDEO_PATH):
    os.makedirs(VIDEO_PATH)
elif not os.path.exists(MUSEIES_PATH):
    os.makedirs(MUSEIES_PATH)
elif  not os.path.exists(MUSIC_IMG_PATH):
    os.makedirs(MUSIC_IMG_PATH)

def login_required(f):
    @wraps(f)
    def wrapper(*args,**kwargs):
        if 'user_id' not in session or 'username' not in session:
            return redirect(url_for('login'))
        return f(*args,**kwargs)
    return wrapper

def request_required(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        request_messages=request.headers.get('User-Agent').lower()
        if not request_messages or 'request' in request_messages or 'curl' in request_messages:
            return jsonify({'error':'非法请求'}),403
        return f(*args,**kwargs)
    return decorated_function

@app.route('/')
@login_required
@request_required
def index():
    return render_template('index.html')

@app.route('/userhome',methods=['GET'])
@login_required
@request_required
def userhome():
    user=User.query.get(session['user_id'])
    user_msg={'username':user.username,'img':user.img,'intor':user.intor,'id':user.id}
    return render_template('userhome.html',user_msg=user_msg)

@app.route('/other_userhome/<user_id>',methods=['GET'])
@login_required
@request_required
def other_userhome(user_id):
    user=User.query.get(int(user_id))
    user_msg={'username':user.username,'img':user.img,'intor':user.intor,'id':user.id}
    return render_template('other_userhome.html',user_msg=user_msg)

@app.route('/get_user_videos',methods=['POST'])
@request_required
@login_required
def get_user_videos():
    try:
        user_id=request.get_json().get('user_id')
        videos=Video.query.filter_by(user_id=user_id).order_by(Video.time.desc()).all()
        return jsonify({'videos':[{'id':v.id,'title':v.title,'time':v.time,'video':v.video_name} for v in videos]})
    except Exception as e:
        return jsonify({'error':str(e)}),500

@app.route('/video_index/<video_id>',methods=['GET'])
@login_required
@request_required
def video_index(video_id):
    return render_template('video_index.html',video_id=video_id)

@app.route('/meiove_pwd',methods=['GET'])
@login_required
@request_required
def meiove_pwd():
    try:
        json=request.get_json()
        old_pwd=json.get('old_pwd')
        new_pwd=json.get('new_pwd')
        user=User.query.get(session['user_id'])
        if user.check_password(old_pwd):
            user.set_password(new_pwd)
            db.session.commit()
            return jsonify({'message':'修改成功'}),200
        return jsonify({'error':'旧密码错误'}),400
    except Exception as e:
        return jsonify({'error':str(e)}),500

@app.route('/get_one_video',methods=['POST'])
@login_required
@request_required
def get_one_video():
    try:
        video_id=request.get_json().get('video_id')
        video=Video.query.get(int(video_id))
        likes_count=Like.query.filter_by(video_id=int(video_id)).count()
        comment_count=Comment.query.filter_by(video_id=int(video_id)).count()
        collection_count=Collection.query.filter_by(video_id=int(video_id)).count()
        like_zt='已点赞' if Like.query.filter_by(user_id=int(session['user_id']),video_id=int(video_id)).first() else '未点赞'
        collection_zt='已搜藏' if Collection.query.filter_by(user_id=int(session['user_id']),video_id=int(video_id)).first() else '未搜藏'
        return jsonify({'video_msg':{'id':video.id,'video':video.video_name,'title':video.title,'intor':video.intor,'time':video.time,'likes_count':likes_count,'comment_count':comment_count,'collection_count':collection_count,'user_id':video.user_id,'user_img':User.query.get(video.user_id).img,'user_name':User.query.get(video.user_id).username},'zt':{'like_zt':like_zt,'collection_zt':collection_zt}})
    except Exception as e:
        return jsonify({'msg':str(e)})

@app.route('/login',methods=['GET','POST'])
@request_required
def login():
    try:
        if request.method =='POST':
            username=request.form.get('username')
            password=request.form.get('password')
            user=User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                session.permanent = True  # 设置 session 为永久性
                session['user_id']=user.id
                session['username']=user.username
                session['last_videos']=[]
                session['future_videos']=[]
                return jsonify({'message':'登录成功','redirect':'/'})
            else:
                return jsonify({'error':'用户名或密码错误'}),401
        return render_template('login.html')
    except Exception as e:
        return jsonify({'error':str(e)}),500

@app.route('/logout',methods=['GET'])
@request_required
@login_required
def logout():
    try:
        session.clear()
        return redirect(url_for('login'))
    except Exception as e:
        return jsonify({'error':str(e)}),500

@app.route('/clear_last_videos',methods=['GET'])
@request_required
@login_required
def clear_last_videos():
    try:
        session.pop('last_videos',None)
        session.pop('future_videos',None)
        return jsonify({'message':'清除成功'}),200
    except Exception as e:
        return jsonify({'error':str(e)}),500

@app.route('/register',methods=['GET','POST'])
@request_required
def register():
    try:
        if request.method =='POST':
            username=request.form.get('username')
            password=request.form.get('password')
            user_check=User.query.filter_by(username=username).first()
            if user_check:
                return jsonify({'error':'用户名已存在'}),400
            
            if len(password)<6:
                return jsonify({'error':'密码长度不能小于6位'}),400
            
            if username[0].isdigit():
                return jsonify({'error':'用户名不能以数字开头'}),400
            
            user=User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return jsonify({'message':'注册成功'}),200

        return render_template('register.html')
    except Exception as e:
        return jsonify({'error':str(e)}),500

@app.route('/upload_user_img',methods=['POST'])
@login_required
@request_required
def upload_user_img():
    try:
        img=request.files.get('img')
        if not img:
            return jsonify({'error':'请上传图片'}),400
        if not img.filename:
            return jsonify({'error':'请选择图片文件'}),400
        if img.filename.split('.')[-1] not in ['jpg','png','jpeg']:
            return jsonify({'error':'请上传正确的图片格式'}),400
        img_name=f"{uuid.uuid4()}.{img.filename.split('.')[-1]}"
        img.save(os.path.join(USER_IMG_PATH,img_name))
        user=User.query.get(session['user_id'])
        user.img=img_name
        db.session.commit()
        return jsonify({'message':'上传成功'}),200
    except Exception as e:
        return jsonify({'error':str(e)}),500

@app.route('/upload',methods=['GET','POST'])
@login_required
@request_required
def upload():
    try:
        if request.method =='POST':
            into=request.form.get('tags')
            title=request.form.get('title')
            time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            video=request.files.get('video')
            if not video:
                return jsonify({'error':'请上传视频'}),400
            if not video.filename:
                return jsonify({'error':'请选择视频文件'}),400
            if video.filename.split('.')[-1] not in ['mp4','avi','mov','wmv','flv','mpeg','mpg','m4v','webm']:
                return jsonify({'error':'请上传正确的视频格式'}),400
            
            video_name=f'{uuid.uuid4()}.{video.filename.split(".")[-1]}'
            video.save(os.path.join(VIDEO_PATH,video_name))
            video_message=Video(title=title,intor=into,user_id=session['user_id'],video_name=video_name,time=time)
            db.session.add(video_message)
            db.session.commit()
            return jsonify({'message':'上传成功','redirect':url_for('index')})
        return render_template('upload.html')
    except Exception as e:
        return jsonify({'error':str(e)}),500
            
@app.route('/get_video',methods=['GET'])
@request_required
@login_required
def get_video():
    try:
        if 'future_videos' not in session and 'last_videos' not in session:
            session['future_videos']=[]
            session['last_videos']=[]
        elif 'future_videos' not in session:
            session['future_videos']=[]
        elif 'last_videos' not in session:
            session['last_videos']=[]

        if session['future_videos']:
            video=Video.query.get(session['future_videos'][-1])
            if not video:
                return jsonify({'error':'视频不存在'}),404
            likes=Like.query.filter_by(video_id=video.id).count()
            comments=Comment.query.filter_by(video_id=video.id).count()
            collections=Collection.query.filter_by(video_id=video.id).count()
            session['last_videos'].append(session['future_videos'][-1])
            session.modified=True
            session['future_videos'].pop()
            session.modified=True
            #print('session',session['future_videos'],session['last_videos'])
            historical_record=Historical_record(user_id=session['user_id'],video_id=video.id)
            db.session.add(historical_record)
            db.session.commit()
            return jsonify({'video_msg':{
                'id': video.id,
                'video':video.video_name,
                'title':video.title,
                'intor':video.intor,
                'time':video.time,
                'user_id':video.user_id,
                'user_img':User.query.get(video.user_id).img,
                'user_name':User.query.get(video.user_id).username,
                'likes_count':likes,
                'comments_count':comments,
                'collections_count':collections
            }})

        videos=Video.query.all()
        video=random.choice(videos)
        likes=Like.query.filter_by(video_id=video.id).count()
        comments=Comment.query.filter_by(video_id=video.id).count()
        collections=Collection.query.filter_by(video_id=video.id).count()

        session['last_videos'].append(video.id)
        session.modified = True  
        if Historical_record.query.filter_by(user_id=session['user_id'],video_id=video.id).first():
            return jsonify({'video_msg':{
                'id': video.id,
                'video':video.video_name,
                'title':video.title,
                'intor':video.intor,
                'time':video.time,
                'user_id':video.user_id,
                'user_img':User.query.get(video.user_id).img,
                'user_name':User.query.get(video.user_id).username,
                'likes_count':likes,
                'comments_count':comments,
                'collections_count':collections
            }})

        historical_record=Historical_record(user_id=session['user_id'],video_id=video.id)
        db.session.add(historical_record)
        db.session.commit()

        return jsonify({'video_msg':{
            'id': video.id,
            'video':video.video_name,
            'title':video.title,
            'intor':video.intor,
            'time':video.time,
            'user_id':video.user_id,
            'user_img':User.query.get(video.user_id).img,
            'user_name':User.query.get(video.user_id).username,
            'likes_count':likes,
            'comments_count':comments,
            'collections_count':collections
        }})
    except Exception as e:
        return jsonify({'error':str(e)}),500

@app.route('/get_focus_videos',methods=['POST'])
@login_required
@request_required
def get_focus_videos():
    try:
        if 'future_videos' not in session and 'last_videos' not in session:
            session['future_videos']=[]
            session['last_videos']=[]
        elif 'future_videos' not in session:
            session['future_videos']=[]
        elif 'last_videos' not in session:
            session['last_videos']=[]

        if session['future_videos']:
            video=Video.query.get(session['future_videos'][-1])
            likes=Like.query.filter_by(video_id=video.id).count()
            comments=Comment.query.filter_by(video_id=video.id).count()
            collections=Collection.query.filter_by(video_id=video.id).count()
            session['last_videos'].append(session['future_videos'][-1])
            session.modified=True
            session['future_videos'].pop()
            session.modified=True
            print('session',session['future_videos'],session['last_videos'])
            
            historical_record=Historical_record(user_id=session['user_id'],video_id=video.id)
            db.session.add(historical_record)
            db.session.commit()
            return jsonify({'video_msg':{
                'id': video.id,
                'video':video.video_name,
                'title':video.title,
                'intor':video.intor,
                'time':video.time,
                'user_id':video.user_id,
                'user_img':User.query.get(video.user_id).img,
                'user_name':User.query.get(video.user_id).username,
                'likes_count':likes,
                'comments_count':comments,
                'collections_count':collections
            }})
            
        focus_user=Focus.query.filter_by(user_id=int(session['user_id'])).all()
        focus_videos=[Video.query.filter_by(user_id=u.focus_id).all() for u in focus_user]
        focus_videos=[v for f in focus_videos for v in f]
        focus_videos.sort(key=lambda x:x.time,reverse=True)
        video=random.choice(focus_videos)
        likes=Like.query.filter_by(video_id=video.id).count()
        comments=Comment.query.filter_by(video_id=video.id).count()
        collections=Collection.query.filter_by(video_id=video.id).count()
        session['last_videos'].append(video.id)
        session.modified=True
        if Historical_record.query.filter_by(user_id=session['user_id'],video_id=video.id).first():
            return jsonify({'video_msg':{
                'id':video.id,
                'video':video.video_name,
                'title':video.title,
                'intor':video.intor,
                'time':video.time,
                'user_id':video.user_id,
                'user_img':User.query.get(video.user_id).img,
                'user_name':User.query.get(video.user_id).username,
                'likes_count':likes,
                'comments_count':comments,
                'collections_count':collections
            }})
        historical_record=Historical_record(user_id=session['user_id'],video_id=video.id)
        db.session.add(historical_record)
        db.session.commit()
        #$print('session',session['future_videos'],session['last_videos'])
        return jsonify({'video_msg':{
            'id':video.id,
            'video':video.video_name,
            'title':video.title,
            'intor':video.intor,
            'time':video.time,
            'user_id':video.user_id,
            'user_img':User.query.get(video.user_id).img,
            'user_name':User.query.get(video.user_id).username,
            'likes_count':likes,
            'comments_count':comments,
            'collections_count':collections
        }})
    except Exception as e:
        return jsonify({'error':str(e)}),500

@app.route('/video/<filename>',methods=['GET'])
@request_required
def video(filename):
    path=os.path.abspath(os.path.join(VIDEO_PATH,filename))
    if not os.path.exists(path):
        return jsonify({'error':'视频不存在'}),404
    return send_file(path,as_attachment=True)

@app.route('/get_user_img/<filename>')
@request_required
def get_user_img(filename):
    try:

        if filename == 'None':
            default_path = os.path.join(USER_IMG_PATH, '默认', 'default.png')
            if not os.path.exists(default_path):
                return jsonify({'error': '默认头像不存在'}), 404
            return send_file(default_path)

        file_path=os.path.join(USER_IMG_PATH,filename)
        if not os.path.exists(file_path):
            default_path = os.path.join(USER_IMG_PATH, '默认', 'default.png')
            if not os.path.exists(default_path):
                return jsonify({'error': '默认头像不存在'}), 404
            return send_file(default_path)
        
        return send_file(file_path)
    except Exception as e:
        print(f"获取用户头像错误: {str(e)}") 
        return jsonify({'error': str(e)}), 500

@app.route('/get_last_videos',methods=['POST'])
@request_required
@login_required
def get_last_videos():
    try: 
        if len(session['last_videos'])<=1:
            return jsonify({'msg':'没有更多视频了'}),400
        session['future_videos'].append(session['last_videos'][-1])
        #print('session',session['future_videos'],session['last_videos'])
        session.modified=True
        
        last_video = session['last_videos'][-2]
        video = Video.query.get(last_video)
        likes = Like.query.filter_by(video_id=video.id).count()
        comments = Comment.query.filter_by(video_id=video.id).count()
        collections = Collection.query.filter_by(video_id=video.id).count()
        #print('last_video', last_video, 'current_id', vide_id)
        session['last_videos'].pop()
        session.modified = True
        historical_record=Historical_record.query.filter_by(user_id=session['user_id'],video_id=video.id).first()

        if historical_record:
            db.session.delete(historical_record)
            db.session.commit()

        return jsonify({'video_msg':{
            'id': video.id,
            'video': video.video_name,
            'title': video.title,
            'intor': video.intor,
            'time': video.time,
            'user_id': video.user_id,
            'user_img': User.query.get(video.user_id).img,
            'user_name': User.query.get(video.user_id).username,
            'likes_count': likes,
            'comments_count': comments,
            'collections_count': collections
        }})
        
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search',methods=['GET'])
@request_required
@login_required
def search():
    try:
        return render_template('search.html')
    except Exception as e:
        return jsonify({'error':str(e)}),500

@app.route('/search_result',methods=['POST'])
@request_required
@login_required
def search_result():
    try:
        search_content=request.form.get('search_content')
        video=Video.query.filter(Video.title.like(f'%{search_content}%')).all()
        return jsonify({'videos':[{'id':v.id,'title':v.title,'time':v.time,'video':v.video_name,'user_id':v.user_id,'user_img':User.query.get(v.user_id).img,'user_name':User.query.get(v.user_id).username} for v in video]})
    except Exception as e:
        return jsonify({'error':str(e)}),500

@app.route('/like_video',methods=['POST'])
@request_required
@login_required
def like():
    try:
        video_id=request.get_json().get('video_id')
        like=Like(user_id=session['user_id'],video_id=video_id)
        db.session.add(like)
        db.session.commit()
        return jsonify({'message':'点赞成功'}),200
    except Exception as e:
        return jsonify({'error':str(e)}),500

@app.route('/unlike',methods=['POST'])
@request_required
@login_required
def unlike():
    try:
        video_id=request.get_json().get('video_id')
        like=Like.query.filter_by(user_id=session['user_id'],video_id=video_id).first()
        db.session.delete(like)
        db.session.commit()
        return jsonify({'message':'取消点赞成功'}),200
    except Exception as e:
        return jsonify({'error':str(e)}),500

@app.route('/collection_video',methods=['POST'])
@request_required
@login_required
def collection():
    try:
        video_id=request.get_json().get('video_id')
        collection=Collection(user_id=session['user_id'],video_id=video_id)
        db.session.add(collection)
        db.session.commit()
        return jsonify({'message':'收藏成功'}),200
    except Exception as e:
        return jsonify({'error':str(e)}),500

@app.route('/uncollection',methods=['POST'])
@request_required
@login_required
def uncollection():
    try:
        video_id=request.get_json().get('video_id')
        collection=Collection.query.filter_by(user_id=session['user_id'],video_id=video_id).first()
        db.session.delete(collection)
        db.session.commit()
        return jsonify({'message':'取消搜藏成功'}),200
    except Exception as e:
        return jsonify({'error':str(e)}),500
    
@app.route('/comment_video',methods=['POST'])
@request_required
@login_required
def comment():
    try:
        json=request.get_json()
        video_id=json.get('video_id')
        content=json.get('content')
        time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        comment=Comment(user_id=session['user_id'],video_id=video_id,content=content,time=time)
        db.session.add(comment)
        db.session.commit()
        return jsonify({'message':'评论成功'}),200
    except Exception as e:
        return jsonify({'error':str(e)}),500

@app.route('/reply_comment',methods=['POST'])
@request_required
@login_required
def reply_comment():
    try:
        json=request.get_json()
        comment_id=json.get('comment_id')
        content=json.get('content')
        time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        reply=Comment_reply(user_id=int(session['user_id']),comment_id=int(comment_id),content=content,time=time)
        db.session.add(reply)
        db.session.commit()
        return jsonify({'message':'回复成功'}),200
    except Exception as e:
        return jsonify({'error':str(e)}),500

@app.route('/get_comment_reply',methods=['POST'])
@login_required
@request_required
def get_comment_reply():
    try:
        json=request.get_json()
        comment_id=json.get('comment_id')
        reply=Comment_reply.query.filter_by(comment_id=comment_id).all()
        return jsonify({'reply':[{'user_id':r.user_id,'content':r.content,'time':r.time,'user_img':User.query.get(r.user_id).img,'user_name':User.query.get(r.user_id).username,'obj_username':User.query.get(Comment.query.get(r.comment_id).user_id).username} for r in reply]})
    except Exception as e:
        return jsonify({'error':str(e)}),500

@app.route('/send_barrage',methods=['POST'])
@request_required
@login_required
def send_barrage():
    try:
        json=request.get_json()
        content=json.get('content')
        progress=json.get('progress')
        video_id=json.get('video_id')
        time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        barrage=Barrage(user_id=session['user_id'],content=content,time=time,progress=progress,video_id=video_id)
        db.session.add(barrage)
        db.session.commit()
        return jsonify({'message':'发送成功'}),200
    except Exception as e:
        return jsonify({'error':str(e)}),500

@app.route('/get_barrage',methods=['POST'])
@request_required
@login_required
def get_barrage():
    try:
        barrages=Barrage.query.filter_by(video_id=request.get_json().get('video_id')).all()
        return jsonify({'barrages':[{'user_id':b.user_id,'content':b.content,'time':b.time,'progress':b.progress,'user_img':User.query.get(b.user_id).img,'user_name':User.query.get(b.user_id).username} for b in barrages]})
    except Exception as e:
        return jsonify({'error':str(e)}),500
    
@app.route('/focus',methods=['POST'])
@request_required
@login_required
def focus():
    try:
        focus_id=request.get_json().get('focus_id')
        focus=Focus(user_id=session['user_id'],focus_id=focus_id)
        db.session.add(focus)
        db.session.commit()
        return jsonify({'message':'关注成功'}),200
    except Exception as e:
        return jsonify({'error':str(e)}),500

@app.route('/unfocus',methods=['POST'])
@request_required
@login_required
def unfocus():
    try:
        unfocus_id=request.get_json().get('unfocus_id')
        focus=Focus.query.filter_by(user_id=session['user_id'],focus_id=unfocus_id).first()
        db.session.delete(focus)
        db.session.commit()
        return jsonify({'msg':'取消关注成功'}),200
    except Exception as e:
        return jsonify({'error':str(e)}),500

@app.route('/get_comments',methods=['POST'])
@request_required
@login_required
def get_comments():
    try:
        video_id=request.get_json().get('video_id')
        comments=Comment.query.filter_by(video_id=video_id).all()
        return jsonify([{'user_id':c.user_id,'content':c.content,'time':c.time,'user_img':User.query.get(c.user_id).img,'user_name':User.query.get(c.user_id).username} for c in comments])
    except Exception as e:
        return jsonify({'error':str(e)}),500

@app.route('/get_friends',methods=['POST'])
@request_required
@login_required
def get_friends():
    try:
        focus=Focus.query.filter_by(user_id=int(session['user_id'])).all()
        friends=[i.focus_id for i in focus if Focus.query.filter_by(user_id=i.focus_id,focus_id=int(session['user_id'])).first()]
        return jsonify({'friends':[{'user_id':i,'user_img':User.query.get(i).img,'user_name':User.query.get(i).username} for i in friends]})
    except Exception as e:
        return jsonify({'error':str(e)}),500

@app.route('/send_message',methods=['POST'])
@request_required
@login_required
def send_message():
    try:
        json=request.get_json()
        receive_id=json.get('receive_id')
        content=json.get('content')
        time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message=Message(user_id=int(session['user_id']),receive_id=int(receive_id),content=content,time=time)
        db.session.add(message)
        db.session.commit()
        return jsonify({'message':'发送成功'}),200
    except Exception as e:
        return jsonify({'error':str(e)}),500
    
@app.route('/get_user_messages',methods=['POST'])
@request_required
@login_required
def get_user_messages():
    try:
        user_id=request.get_json().get('user_id')
        my_id=int(session['user_id'])
        message=Message.query.filter(
            or_(
                and_(Message.user_id==user_id,Message.receive_id==my_id),
                and_(Message.user_id==my_id,Message.receive_id==user_id)
            )
        ).order_by(Message.time.desc()).all()

        return jsonify(
            [
                {
                    'send_user_id':m.user_id,
                    'username':User.query.get(m.user_id).username,
                    'user_img':User.query.get(m.user_id).img,
                    'content':m.content,
                    'time':m.time
                }
                for m in message]
        )

    except Exception as e:
        return jsonify({'error':str(e)}),500

@app.route('/get_new_messages',methods=['POST'])
@request_required
@login_required
def get_new_messages():
    try:
        user_id=request.get_json().get('user_id')
        last_time=request.get_json().get('last_time')
        my_id=int(session['user_id'])
        messages=Message.query.filter(
            and_(
                or_(
                    and_(Message.user_id==user_id,Message.receive_id==my_id),
                    and_(Message.user_id==my_id,Message.receive_id==user_id)
                ),
                Message.time>last_time
            )
        ).order_by(Message.time.asc()).all()
        if not messages:
            return jsonify({'msg':'没有新消息'}),200
        return jsonify([
            {
                'send_user_id':m.user_id,
                'username':User.query.get(m.user_id).username,
                'user_img':User.query.get(m.user_id).img,
                'content':m.content,
                'time':m.time
            }
            for m in messages
        ])
    except Exception as e:
        return jsonify({'error':str(e)}),500

@app.route('/delete_video',methods=['POST'])
@request_required
@login_required
def delete_video():
    try:
        video_id=request.get_json().get('video_id')
        video=Video.query.get(int(video_id))
        video_file=os.path.join(VIDEO_PATH,video.video_name)
        if os.path.exists(video_file):
            os.remove(video_file)
        else:
            return jsonify({'error':'视频不存在'}),400
        db.session.delete(video)
        db.session.commit()
        return jsonify({'message':'删除成功'}),200
    except Exception as e:
        return jsonify({'error':str(e)}),500

@app.route('/upload_museies',methods=['GET','POST'])
@request_required
@login_required
def upload_museies():
    try:
        if request.method=='POST':
            title=request.form.get('title')
            img=request.files.get('img')
            music=request.files.get('music')
            img_name=None
            music_name=None
            if img and music:
                img_name=img.filename
                music_name=uuid.uuid4().hex+music.filename
                img.save(os.path.join(MUSIC_IMG_PATH,img_name))
                music.save(os.path.join(MUSEIES_PATH,music_name))
            elif not music:
                return jsonify({'error':'请上传音频'})

            time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            museies=Museies(title=title,img=img_name,music=music_name,time=time)
            db.session.add(museies)
            db.session.commit()
            return jsonify({'message':'上传成功'}),200
        return render_template('upload_museies.html')
    except Exception as e:
        return jsonify({'error':str(e)}),500

@app.route('/get_page_museies',methods=['POST'])
@request_required
@login_required
def get_page_museies():
    try:
        museies=Museies.query.order_by(Museies.time.random()).all() if Museies.query.count() <20 else Museies.query.order_by(Museies.time.random()).all()[:20]
        return jsonify({'museies':[{'title':m.title,'img':m.img,'music':m.music,'time':m.time} for m in museies]})
    except Exception as e:
        return jsonify({'error':str(e)}),500

@app.route('/get_music',methods=['POST','GET'])
@request_required
@login_required
def get_music():
    try:
        if request.method=='POST':
            json=request.get_json()
            music_id=json.get('music_id')
            music=Museies.query.get(int(music_id))
            return jsonify({'music':{'title':music.title,'img':music.img,'music':music.music,'time':music.time,'id':music_id}})
        music_id=request.args.get('music_id')
        return render_template('get_museies.html',music_id=music_id)
    except Exception as e:
        return jsonify({'error':str(e)}),500

@app.route('/get_music_aideo/<music_name>',methods=['GET'])
@request_required
@login_required
def get_music_aideo(music_name):
    try:
        return send_file(os.path.join(MUSEIES_PATH,music_name),as_attachment=True)
    except Exception as e:
        return jsonify({'error':str(e)}),500

@app.route('/get_aideo_img/<img_name>',methods=['GET'])
@request_required
@login_required
def get_aideo_img(img_name):
    try:
        return send_file(os.path.join(MUSIC_IMG_PATH,img_name),as_attachment=True)
    except Exception as e:
        return jsonify({'error':str(e)}),500

'''
def recognize_lyrics(audio_path):
    mole=whisper.load_model('base')
    result = mole.transcribe(audio_path, language='zh')
    return result['text']

@app.route('/get_music_words',methods=['POST'])
@request_required
@login_required
def get_music_words():
    try:
       json=request.get_json()
       music_name=json.get('music_name')
       music_path=os.path.join(MUSEIES_PATH,music_name)
       if not os.path.exists(music_path):
           return jsonify({'error':'音乐不存在'}),400
       words=recognize_lyrics(music_path)
       if words:
           return jsonify({'words':words,'zt':True})
       else:
           return jsonify({'error':'无歌词','zt':False}),500
       
    except Exception as e:
        return jsonify({'error':str(e)}),500
'''

@app.route('/get_historical_record',methods=['POST'])
@request_required
@login_required
def get_historical_record():
    try:
        historical_record=Historical_record.query.filter_by(user_id=session['user_id']).all()
        return jsonify([{'video_id':h.video_id,'video_name':Video.query.get(h.video_id).video_name,'video_img':Video.query.get(h.video_id).img,'video_title':Video.query.get(h.video_id).title} for h in historical_record])
    except Exception as e:
        return jsonify({'error':str(e)}),500

@app.route('/delete_historical_record',methods=['POST'])
@request_required
@login_required
def delete_historical_record():
    try:
        historical_record=Historical_record.query.filter_by(user_id=session['user_id']).delete()
        return jsonify({'message':'删除成功','count':historical_record}),200
    except Exception as e:
        return jsonify({'error':str(e)}),500

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)
