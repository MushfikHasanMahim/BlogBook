from app import db, User, Post, Comment, Like, Reply
#import timeago, datetime
#date = now = datetime.datetime.now()

#for i in Post.query.filter_by(id=6).first().likes:
#    i.author == current_user.id
#print(timeago.format(date, now))

#print(Comment.query.all())
#db.create_all()
print(Reply.query.first().content)
#c = Comment.query.first()
#print(c.date_posted)