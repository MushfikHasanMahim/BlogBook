from flask import Flask, render_template, redirect,request, flash, url_for
import timeago, datetime
import secrets, os
from flask_sqlalchemy import SQLAlchemy
from get_time import get_time, get_time_
from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_share import Share
from PIL import Image


app = Flask(__name__)
app.config["SECRET_KEY"] = "7hdjehehu2hebeudubekeks"
app.config["SQLALCHEMY_DATABASE_URI"] ="sqlite:///site.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
share = Share(app)


login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))




class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    date_posted = db.Column(db.String(50), default=get_time())
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"),  nullable=False)
    comments = db.relationship("Comment", backref="post", passive_deletes=True)
    likes = db.relationship("Like", backref="post", passive_deletes=True)
    
    
    def __repr__(self):
        return f"Post('id -> {self.id}', title -> '{self.title}', date_posted ->'{self.date_posted}')"
        
   
class User(db.Model, UserMixin):  
    id = db.Column(db.Integer, primary_key=True)
    name =  db.Column(db.String(300), nullable=False)
    email =  db.Column(db.String(300), unique=True, nullable=False)
    profile_pic = db.Column(db.String(30), default=None)
    password =  db.Column(db.String(300), nullable=False)
    date_posted = db.Column(db.String(50), default=get_time())
    posts = db.relationship("Post", backref="user", passive_deletes=True)
    comments = db.relationship("Comment", backref="user", passive_deletes=True)
    replys = db.relationship("Reply", backref="user", passive_deletes=True)
    likes = db.relationship("Like", backref="user", passive_deletes=True)
    comment_likes = db.relationship("CommentLike", backref="user", passive_deletes=True)
    
    
    
    
    def __repr__(self):
        return f"User('{self.name}', '{self.email}', '{self.id}')"
#        
    
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime(), default=get_time_())
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"),  nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete="CASCADE"),  nullable=False)
    comment_likes = db.relationship("CommentLike", backref="comment", passive_deletes=True)
    replys = db.relationship("Reply", backref="post", passive_deletes=True)

 
class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime(), default=get_time_())
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"),  nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id', ondelete="CASCADE"),  nullable=False)
     
       
class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    counts = db.Column(db.Integer, nullable=False)
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"),  nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete="CASCADE"),  nullable=False)
    
class CommentLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    counts = db.Column(db.Integer, nullable=False)
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"),  nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id', ondelete="CASCADE"),  nullable=False)
  
  
    
# validate info function 

def validate(name, email, password, confirm_password):
    i = 4
    if User.query.filter_by(email=email).first():
        flash("This email is already taken. Please choose another one.", "danger")
        return False
        
    if len(name) < 2:
        i -= 1
        flash("Username must be atleast 2 characters.", "danger")
    if len(email) < 4:
        i -= 1
        flash("Invalid email! ", "danger")
    if len(password) < 8:
        i -= 1
        flash("Password must be atleast 8 characters.", "danger")
    if password != confirm_password:
        i -= 1
        flash("Both passwords must match! ", "danger")
    if i != 4:
        return False
    else:
        return True
    




@app.route("/")
@login_required
def index():
        # posts 
        posts = Post.query.all() 
        
        return render_template("index.html", posts=posts, User=User, user=current_user, share=share, timeago=timeago, date=datetime.datetime.now())
       
        
        
@app.route("/create-comment/<int:id>", methods=["POST"])
def create_comment(id):
    if request.method == "POST":
        print("""
        
        opps, finally it works
        
        
        """)
        
        c = request.form.get("cmt", None)
        print(c)
        if c:
            cmt = Comment(content=c, author=current_user.id, post_id=id)
            
            db.session.add(cmt)
            db.session.commit()
            return redirect("/")
        else:
            flash("Comment cant't be empty", 'info')
            return redirect("/")
    





@app.route("/login", methods=["POST", "GET"]) 
def login():
   if request.method == "POST":
       email = request.form["email"]
       password = request.form["password"]     
     
       user = User.query.filter_by(email=email).first()
     
       if user:    
           if check_password_hash(user.password, password):
               login_user(user, remember= request.form.get("remember"))
               flash(" Logged in Successfully! ", "success")
               return redirect('/')
           else:
               flash("Login Unsuccessful! ", "danger")
               return redirect("/login")
       else:
           flash("Email or Password maybe incorrect!", "warning")
           return redirect("/login")
    

       
   return render_template("login.html",user=current_user)


@app.route("/register", methods=["POST", "GET"]) 
def register():
   if request.method == "POST":
       name = request.form["name"]
       email = request.form["email"]
       password = request.form["password"]
       confirm_pass = request.form["confirm_password"]
       if validate(name, email, password, confirm_pass):
           user = User(name=name, email=email, password=generate_password_hash(password, method="sha256"))

           db.session.add(user)
           db.session.commit()
           login_user(user)
           flash(f"Account Created for {user.name}", "success")
       else:
           return redirect("/register")
       
   return render_template("register.html", user=current_user)


@app.route("/about") 
def about():
    return render_template("about.html", user=current_user)


@app.route("/update/<int:id>", methods=["POST", "GET"]) 
@login_required
def update(id):
   post = Post.query.filter_by(id=id).first()
   if request.method == "POST":    
       post.title = request.form["title"]
       post.content = request.form["content"]
       db.session.commit()
       return redirect("/")
   return render_template("update.html", post=post, user=current_user)
    


@app.route("/account", methods=["POST", "GET"]) 
def account():
   return render_template("account.html") 


@app.route("/create-post", methods=["POST", "GET"]) 
@login_required
def create_post():
   if request.method == "POST":
       title = request.form.get("title", None)
       content = request.form.get("content", None)
       user = current_user
       
       if title and content:
           post = Post(title=title, content=content, author=user.id)
           db.session.add(post)
           db.session.commit()
           return redirect("/")
       else:
           flash(" Title and description can't be empty.", "danger")
           return redirect("/create-post")
    
   else:
       return render_template("create_post.html", user=current_user)


@app.route("/delete/<int:id>", methods=["POST", "GET"]) 
@login_required
def delete(id):
   post = Post.query.filter_by(id=id).first() 
   for c in post.comments:
       for r in c.replys:
           db.session.delete(r)
           db.session.commit()
       for like in c.comment_likes:
           db.session.delete(like)
           db.session.commit()
       db.session.delete(c)
       db.session.commit()
   for like in post.likes:
       db.session.delete(like) 
       db.session.commit() 
   db.session.delete(post)
   db.session.commit()
   flash("Post deleted successfully", "success")
   
   return redirect('/')

@app.route("/logout")
@login_required
def logout():
   logout_user()
   flash("Logged out successfully!", "success")
   return redirect("/")      



def save_profile_pic(pic):
    random_hex = secrets.token_hex(8)
    f, e = os.path.splitext(pic.filename)
    p_f = random_hex + e
    picture_path = os.path.join(app.root_path, "static/Profile_pic", p_f)
    img = Image.open(pic)
    img = img.resize((500, 500))
    
    img = img.rotate(90)
    img.save(picture_path)
    return p_f

    
    
@login_required
@app.route("/profile", methods=["POST", "GET"])   
def profile():
      if request.method == "POST":
          if request.files["pic"].filename:
              
              image = save_profile_pic(request.files["pic"])
              import os
              from PIL import Image
              path = os.path.join(app.root_path, "static/Profile_pic", current_user.profile_pic)
              print(f""""
              
              
              {path} 
              
              
              """)
              
              
              if os.path.exists(path):
                 os.remove(path)
              else:
                 print("The file does not exist")
              current_user.profile_pic = image              
              db.session.commit()
              return redirect('/profile')
          else:
              return redirect('/profile')
      else:
          if url_for("static", filename=f"Profile_pic/{ current_user.profile_pic }")[-4:] != 'None':
              print(type(url_for("static", filename=f"Profile_pic/{ current_user.profile_pic }")[-5:]))
              image = url_for("static", filename=f"Profile_pic/{ current_user.profile_pic }")
          else:
              image = None
          
          return render_template('profile.html', user=current_user, profile_pic=image)
   

@app.route("/delete-comment/<int:id>")
@login_required
def delete_comment(id):
      cmt = Comment.query.filter_by(id=id).first()
      for r in cmt.replys:
          db.session.delete(r)
          db.session.commit()
      for l in cmt.comment_likes:
          db.session.delete(l)
          db.session.commit()
      db.session.delete(cmt)
      db.session.commit()
      
      return redirect("/")


@app.route("/like/<int:id>")
def add_or_delete_like(id):
      post = Post.query.filter_by(id=id).first() 
      for like in post.likes:
          if like.author == current_user.id:
              db.session.delete(like)
              db.session.commit()
              return redirect("/")
      else:
          like = Like(counts=1, author=current_user.id, post_id=id)
          db.session.add(like)
          db.session.commit()
          return redirect("/")

@app.route("/like-comment/<int:id>")      
def like_comment(id):
    comment = Comment.query.filter_by(id=id).first() 
    for like in comment.comment_likes:
          if like.author == current_user.id:
              db.session.delete(like)
              db.session.commit()
              return redirect("/")
    else:
          like = CommentLike(counts=1, author=current_user.id, comment_id=id)
          db.session.add(like)
          db.session.commit()
          return redirect("/")          
      
      
@app.route("/reply/<int:id>", methods=["GET", "POST"]) 
def reply(id):
    if request.method == "POST":
        reply = request.form.get("reply", None)
        print(reply)
        if reply:
            reply = Reply(content=reply, author=current_user.id, comment_id=id)
            
            db.session.add(reply)
            db.session.commit()
            return redirect("/")
        else:
            flash("Reply cant't be empty", 'info')
            return redirect("/")      
            

@login_required
@app.route("/update_profile/<string:name>", methods=["POST", "GET"])  
def update_profile(name):
    if url_for("static", filename=f"Profile_pic/{ current_user.profile_pic }")[-4:] != 'None':
       image = url_for("static", filename=f"Profile_pic/{ current_user.profile_pic }")
    else:
       image = None
    return render_template("update_profile.html", user=current_user, profile_pic=image)        
                                 
@app.route("/delete-reply/<int:id>")
@login_required
def delete_reply(id):
    reply = Reply.query.filter_by(id=id).first()
    db.session.delete(reply)
    db.session.commit()    
    return redirect("/")                    

@app.route("/control_panel", methods=["GET", "POST"])
def control_panel():
    return render_template("control_panel.html", User=User, Comment=Comment, Post=Post, user=current_user)
                
                                        
if __name__ == "__main__":
    app.run(debug=True)