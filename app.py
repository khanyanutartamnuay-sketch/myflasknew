from flask import Flask, request, redirect, url_for, session, render_template
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
    return render_template("felt.html")

# หน้า Login
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if "username" in session:
        return redirect(url_for("profile"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in users and users[username] == password:
            session["username"] = username
            return redirect(url_for("profile"))  # redirect ไปหน้า profile
        else:
            error = "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง"

    return render_template("login.html", error=error)

# หน้า Register (สมัครสมาชิก)
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    message = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        email = request.form.get("email")

        if username in users:
            error = "มีผู้ใช้นี้แล้ว กรุณาใช้ชื่ออื่น"
        elif password != confirm:
            error = "รหัสผ่านไม่ตรงกัน"
        else:
            users[username] = {"password": password, "email": email}
            message = "สมัครสมาชิกเรียบร้อยแล้ว! สามารถเข้าสู่ระบบได้เลย"
            return redirect(url_for("login"))

    return render_template("register.html", error=error, message=message)

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
    for post in posts:
        if post["id"] == post_id:
            post["likes"] += 1
            break
    return redirect(url_for("posts_page"))

# 👉 เพิ่มคอมเมนต์
@app.route("/comment/<int:post_id>", methods=["POST"])
def comment(post_id):
    text = request.form.get("comment", "").strip()
    if text:
        for post in posts:
            if post["id"] == post_id:
                post["comments"].append(text)
                break
    return redirect(url_for("posts_page"))

# หน้าเพิ่มโพสต์ใหม่
@app.route("/new", methods=["GET", "POST"])
def new_post():
    if request.method == "POST":
        text = request.form["text"]
        if text.strip():
            new_id = max([p["id"] for p in posts]) + 1 if posts else 1
            posts.append({"id": new_id, "text": text, "likes": 0, "comments": []})
        return redirect(url_for("all_posts"))
    return render_template("new_post.html")

@app.route("/history")
def history():
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]
    user_comments = []
    for post in posts:
        for c in post["comments"]:
            if c["user"] == username:
                user_comments.append({"post_id": post["id"], "text": c["text"]})
    return render_template("history.html", username=username, comments=user_comments)


@app.route("/delete_comment/<int:post_id>/<int:comment_index>")
def delete_comment(post_id, comment_index):
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]
    for post in posts:
        if post["id"] == post_id:
            if 0 <= comment_index < len(post["comments"]):
                if post["comments"][comment_index]["user"] == username:
                    post["comments"].pop(comment_index)
            break
    return redirect(url_for("history"))

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

# หน้า Profile
@app.route("/profile")
def profile():
    if "username" not in session:
        return redirect(url_for("login"))
    username = session["username"]
    return render_template("profile.html", username=username)

@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    message = None
    if request.method == "POST":
        username = request.form.get("username")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if username not in users:
            message = "ไม่พบผู้ใช้"
        elif new_password != confirm_password:
            message = "รหัสผ่านใหม่ไม่ตรงกัน"
        else:
            users[username] = new_password
            message = "รีเซ็ตรหัสผ่านเรียบร้อย! คุณสามารถล็อกอินได้แล้ว"
            return redirect(url_for("login"))

    return render_template("reset_password.html", message=message)

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
@app.route("/posts")
def posts_page():
    return render_template("posts_page.html", posts=posts)

# หน้าเข้าสู่ระบบทั้งหมด
@app.route('/logins')
def show_logins():
    logins = [
        {"username": "user1", "time": "10:00"},
        {"username": "user2", "time": "11:00"}
    ]
    return render_template("logins_page.html", logins=logins)

if __name__ == "__main__":
     app.run(debug=True)
app.run(host="0.0.0.0")
