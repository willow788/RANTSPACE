from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your-secret-key-change-this"

DB = "rants.db"
admin_password= "GIVEYOUROWNPASSWORDTHISISNOTTHEPASSWORDOFMINE"

def init_db():
    connect = sqlite3.connect(DB)
    c = connect.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS rants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            title TEXT,
            body TEXT,
            tags TEXT,
            likes INTEGER DEFAULT 0,
            approved INTEGER DEFAULT 0,
            created TEXT
        )
    """)
    connect.commit()
    connect.close()

@app.route("/")
def index():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("SELECT id, username, title, body, tags, likes, created FROM rants WHERE approved=1 ORDER BY created DESC") 
    rants = c.fetchall()

    conn.close()
    return render_template("index.html", rants=rants)


@app.route("/rant/<int:rant_id>")
def rant(rant_id):
    connect = sqlite3.connect(DB)
    c= connect.cursor()

    c.execute("SELECT id, username, title, body, tags, likes, created FROM rants WHERE id=? AND approved=1", (rant_id,))
    rant = c.fetchone()

    connect.close()
    return render_template("rant.html", rant=rant)

#now likes
@app.route("/like/<int:rant_id>", methods=["POST"])
def like(rant_id):
    connect = sqlite3.connect(DB)
    c = connect.cursor()

    c.execute("update rants set likes = likes + 2 where id=?", (rant_id,))
    connect.commit()
    connect.close()
    return redirect(url_for("rant", rant_id= rant_id))
#my app my fucknig rules
# whenever you like a rant you give me 2 likes
#fuck you if you dont like it
#my app my rules!


#now writing the rant:

@app.route("/write", methods= ["GET", "POST"])

def write_your_fucking_rant():
    if request.method == "POST":
        username = request.form.get("username") or("I'M PEPPA PIG, I'LL SNORT YOUR ASS!")
        what = request.form.get("title")
        body= request.form.get("body")
        tags= request.form.get("tags") or ""
        created = datetime.now().isoformat()

        if not what or not body:
            return "Title and body are required. What you're happy or something?, no rage?", 400
        

        connect = sqlite3.connect(DB)
        c= connect.cursor()

        c.execute("INSERT INTO rants (username, title, body, tags, created) VALUES (?, ?, ?, ?, ?)", (username, what, body, tags, created))

        connect.commit()
        connect.close()

        return redirect(url_for("index"))
    
    return render_template("write.html")



@app.route("/admin", methods= ["GET", "POST"])
def admin_allowance():
    if request.method == "POST":
        # If not logged in yet, treat POST as a login attempt.
        if not session.get('admin_logged_in'):
            pw = request.form.get("password")
            if not pw or pw != admin_password:
                return "access denied"
            session['admin_logged_in'] = True
            return redirect(url_for("admin_allowance"))

        # Logged in: process moderation actions.
        rant_id = request.form.get("rant_id")
        action = request.form.get("action")

        if rant_id and action:
            connect = sqlite3.connect(DB)
            c = connect.cursor()

            if action == "approve":
                c.execute("UPDATE rants SET approved=1 WHERE id=?", (rant_id,))
            elif action == "delete":
                c.execute("DELETE FROM rants WHERE id=?", (rant_id,))

            connect.commit()
            connect.close()
    
    if not session.get('admin_logged_in'):
        return render_template("admin_login.html")
    
    connect = sqlite3.connect(DB)
    c = connect.cursor()
    c.execute("SELECT id, username, title, body, tags, likes, created FROM rants WHERE approved=0 ORDER BY created DESC")
    pending_rants = c.fetchall()
    connect.close()

    return render_template("admin.html", pending_rants=pending_rants)


@app.route("/admin/logout")
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for("admin_allowance"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)



        

