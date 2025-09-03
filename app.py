from flask import Flask, request, redirect, url_for, session, render_template,SQLAlchemy
from datetime import datetime
from bs4 import BeautifulSoup
import sys
import os


app = Flask(__name__)
app.secret_key = "mysecretkey"
app.secret_key = "your_secret_key"
app.secret_key = "my_secret_key"
app.secret_key = "secret"
app.secret_key = "YOUR_SECRET_KEY" 
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    likes = db.Column(db.Integer, default=0)
    comments = db.relationship("Comment", backref="post", cascade="all, delete")

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
   
   
with app.app_context():
    db.create_all()
                         
messages_list = []
posts = [
    {"id": 1, "text": "โพสต์แรก", "likes": 3, "comments": [{"user": "Aom", "text": "ดีมาก!"}]},
    {"id": 2, "text": "โพสต์สอง", "likes": 1, "comments": []}
]


# เก็บโพสต์เป็น list ของ dict
posts = [
    {"title": "โพสต์ 1", "content": "เนื้อหาของโพสต์ 1", "likes": 0, "comments": []},
    {"title": "โพสต์ 2", "content": "เนื้อหาของโพสต์ 2", "likes": 0, "comments": []},
    {"title": "โพสต์ 3", "content": "เนื้อหาของโพสต์ 3", "likes": 0, "comments": []},
]


users = {
    "user1": "1234",
    "user2": "abcd"
}

user_posts = {}

posts = []

@app.route("/", methods=["GET", "POST"])
def index():
        return render_template("index.html")

@app.route('/song')
def music():
    return render_template("music.html")

@app.route("/felt", methods=["GET", "POST"])
def felt():
    if request.method == "POST":
        text = request.form.get("message", "").strip()
        if text:
            posts.append({
                "id": len(posts),   # id ของโพสต์
                "text": text,       # เนื้อหาของโพสต์
                "likes": 0,         # จำนวนไลค์
                "comments": []      # คอมเมนต์
            })
            return redirect(url_for("posts_page"))
        return redirect(url_for("new_post"))
    return render_template("felt.html")

# หน้า Dashboard
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        username = session['username']
        return render_template('dashboard.html', username=username)
    else:
        return redirect(url_for('login'))



# 👉 กดไลค์
@app.route("/like/<int:post_id>")
def like(post_id):
    post = Post.query.get_or_404(post_id)
    post.likes += 1
    db.session.commit()
    return redirect(url_for("all_posts"))


# 👉 เพิ่มคอมเมนต์
@app.route("/comment/<int:post_id>", methods=["POST"])
def comment(post_id):
    post = Post.query.get_or_404(post_id)
    text = request.form.get("comment")
    if text:
        new_comment = Comment(text=text, post=post)
        db.session.add(new_comment)
        db.session.commit()
    return redirect(url_for("all_posts"))


# หน้าเพิ่มโพสต์ใหม่
@app.route("/new_post", methods=["GET", "POST"])
def new_post():
    if request.method == "POST":
        text = request.form.get("text")
        if text:
            post = Post(text=text)
            db.session.add(post)
            db.session.commit()
        return redirect(url_for("all_posts"))
    return render_template("new_post.html")


# เพิ่มข้อความ (สำหรับทดสอบ)
@app.route("/add_post", methods=["POST"])
def add_post():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    text = request.form.get("text")
    if not text:
        return redirect(url_for("profile"))

    try:
        with open("posts.html", "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
    except FileNotFoundError:
        soup = BeautifulSoup("<ul id='post-list'></ul>", "html.parser")

    ul = soup.find("ul", {"id": "post-list"})
    li = soup.new_tag("li")
    li.string = f"{username}: {text}"
    ul.insert(0, li)

    with open("posts.html", "w", encoding="utf-8") as f:
        f.write(str(soup))

    return redirect(url_for("profile"))

# แสดงข้อความทั้งหมด
@app.route("/all_posts")
def all_posts():
    posts = Post.query.all()
    return render_template("all_posts.html", posts=posts)


if __name__ == "__main__":
     app.run(debug=True)
app.run(host="0.0.0.0")
