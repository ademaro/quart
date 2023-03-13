from sqlite3 import dbapi2 as sqlite3

from quart import g, Quart, redirect, request, render_template, url_for

app = Quart(__name__)

app.config.update({
    "DATABASE": app.root_path / "blog.db",
})

def _connect_db():
    engine = sqlite3.connect(app.config["DATABASE"])
    engine.row_factory = sqlite3.Row
    return engine

def _get_db():
    if not hasattr(g, "sqlite_db"):
        g.sqlite_db = _connect_db()
    return g.sqlite_db

@app.get("/")
async def posts():
    db = _get_db()
    cur = db.execute(
        """SELECT title, text
             FROM post
         ORDER BY id DESC""",
    )
    posts = cur.fetchall()
    return await render_template("posts.html", posts=posts)

@app.route("/create/", methods=["GET", "POST"])
async def create():
    if request.method != "POST":
        return await render_template("create.html")
    db = _get_db()
    form = await request.form
    db.execute(
        "INSERT INTO post (title, text) VALUES (?, ?)",
        [form["title"], form["text"]],
    )
    db.commit()
    return redirect(url_for("posts"))

def init_db():
    db = _connect_db()
    with open(app.root_path / "schema.sql", mode="r") as file_:
        db.cursor().executescript(file_.read())
    db.commit()

def run() -> None:
    app.run()
