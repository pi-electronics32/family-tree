
from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3, os

app = Flask(__name__)
DB = os.path.join(os.path.dirname(__file__), "family.db")

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = db()
    con.execute("""CREATE TABLE IF NOT EXISTS people (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        gender TEXT DEFAULT '',
        notes TEXT DEFAULT ''
    )""")
    con.execute("""CREATE TABLE IF NOT EXISTS relationships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        person1 INTEGER NOT NULL,
        person2 INTEGER NOT NULL,
        relation TEXT NOT NULL
    )""")
    con.commit()
    con.close()

def person_id(con, name):
    row = con.execute("SELECT id FROM people WHERE name=?", (name,)).fetchone()
    return row["id"] if row else None

def add_person(con, name, gender="", notes=""):
    pid = person_id(con, name)
    if pid:
        return pid
    cur = con.execute("INSERT INTO people(name,gender,notes) VALUES(?,?,?)",
                      (name, gender, notes))
    return cur.lastrowid

def rel(con, a, b, relation):
    aid, bid = person_id(con, a), person_id(con, b)
    if not aid or not bid:
        return
    exists = con.execute(
        "SELECT id FROM relationships WHERE person1=? AND person2=? AND relation=?",
        (aid, bid, relation)
    ).fetchone()
    if not exists:
        con.execute(
            "INSERT INTO relationships(person1,person2,relation) VALUES(?,?,?)",
            (aid,bid,relation)
        )

def seed():
    con = db()
    if con.execute("SELECT COUNT(*) FROM people").fetchone()[0] > 0:
        con.close()
        return

    people = [
        ("Karan Singh","M","Family origin"),
        ("Raja Singh","M","Son of Karan Singh"),
        ("Indradev Singh","M","Unmarried"),
        ("Matki Singh","M","Unmarried"),
        ("RamPrit Singh","M","Son of Raja Singh"),
        ("Jeera Devi","F","Daughter of RamPrit Singh"),
        ("Ram Bricch Singh","M","Son of Raja Singh; no children recorded"),
        ("Bhagwan Singh","M","Son of Raja Singh; no children recorded"),
        ("Ganesh Singh","M","Son of Raja Singh"),
        ("Jaglal Singh","M","Married to Rajkali Devi"),
        ("Rajkali Devi","F","Wife of Jaglal Singh"),
        ("Jairam Singh","M","Child of Ganesh Singh"),
        ("Phulahi Devi","F","Child of Ganesh Singh"),
        ("Lalpati Devi","F","Child of Ganesh Singh"),
        ("Shushil Singh","M","Married to Late Dr. Sunita Singh"),
        ("Late Dr. Sunita Singh","F","Late; wife of Shushil Singh"),
        ("Vikash Kumar","M","Married to Ishita Raghuvanshi"),
        ("Ishita Raghuvanshi","F","Wife of Vikash Kumar"),
        ("Ishivka Kumar","F","Child of Vikash Kumar and Ishita Raghuvanshi"),
        ("Pooja Singh","F","Married to Ankit"),
        ("Ankit","M","Husband of Pooja Singh"),
        ("Siddhart","M","Child of Pooja Singh and Ankit"),
        ("Samridhhi","F","Child of Pooja Singh and Ankit"),
        ("Vakil Singh","M","Married to Sumitra Devi"),
        ("Sumitra Devi","F","Wife of Vakil Singh"),
        ("Preeti Singh","F","Married to Manoranjan Kumar"),
        ("Manoranjan Kumar","M","Husband of Preeti Singh"),
        ("Ishan Singh","M","Child of Preeti Singh and Manoranjan Kumar"),
        ("Aditi","F","Child of Preeti Singh and Manoranjan Kumar"),
        ("Manish Singh","M","Married to Riya Kumari"),
        ("Riya Kumari","F","Wife of Manish Singh"),
        ("Kartik","M","Child of Manish Singh and Riya Kumari"),
        ("Khusbu Singh","F","Child of Vakil Singh and Sumitra Devi"),
        ("Kedarnath Singh","M","Married to Anita Devi"),
        ("Anita Devi","F","Wife of Kedarnath Singh"),
        ("Akash","M","Child of Kedarnath Singh and Anita Devi"),
        ("Kajal","F","Child of Kedarnath Singh and Anita Devi"),
        ("Bijendra Singh","M","Married to Poonam Devi"),
        ("Poonam Devi","F","Wife of Bijendra Singh"),
        ("Priyanshu Singh","M","Child of Bijendra Singh and Poonam Devi"),
        ("Palak","F","Child of Bijendra Singh and Poonam Devi"),
        ("Biresh Singh","M","Married to Lovely Devi"),
        ("Lovely Devi","F","Wife of Biresh Singh"),
        ("Simran","F","Child of Biresh Singh and Lovely Devi"),
        ("Aditya","M","Child of Biresh Singh and Lovely Devi"),
        ("Arushi","F","Child of Biresh Singh and Lovely Devi"),
        ("Poornima Devi","F","Married to Sanjeet Singh"),
        ("Sanjeet Singh","M","Husband of Poornima Devi"),
        ("Rohiit","M","Child of Poornima Devi and Sanjeet Singh"),
        ("Ankit","M","Already recorded as Pooja Singh's husband"),
        ("Chandani Devi","F","Child of Jaglal Singh and Rajkali Devi"),
    ]
    # Remove duplicate Ankit while retaining first entry.
    seen=set()
    for p in people:
        if p[0] not in seen:
            add_person(con,*p)
            seen.add(p[0])

    parent_child = [
        ("Karan Singh","Raja Singh"),("Karan Singh","Indradev Singh"),("Karan Singh","Matki Singh"),
        ("Raja Singh","RamPrit Singh"),("Raja Singh","Ram Bricch Singh"),
        ("Raja Singh","Bhagwan Singh"),("Raja Singh","Ganesh Singh"),
        ("RamPrit Singh","Jeera Devi"),
        ("Ganesh Singh","Jaglal Singh"),("Ganesh Singh","Jairam Singh"),
        ("Ganesh Singh","Phulahi Devi"),("Ganesh Singh","Lalpati Devi"),
        ("Jaglal Singh","Shushil Singh"),("Jaglal Singh","Vakil Singh"),
        ("Jaglal Singh","Kedarnath Singh"),("Jaglal Singh","Bijendra Singh"),
        ("Jaglal Singh","Biresh Singh"),("Jaglal Singh","Poornima Devi"),
        ("Jaglal Singh","Chandani Devi"),
        ("Shushil Singh","Vikash Kumar"),("Shushil Singh","Pooja Singh"),
        ("Vikash Kumar","Ishivka Kumar"),("Pooja Singh","Siddhart"),("Pooja Singh","Samridhhi"),
        ("Vakil Singh","Preeti Singh"),("Vakil Singh","Manish Singh"),("Vakil Singh","Khusbu Singh"),
        ("Preeti Singh","Ishan Singh"),("Preeti Singh","Aditi"),("Manish Singh","Kartik"),
        ("Kedarnath Singh","Akash"),("Kedarnath Singh","Kajal"),
        ("Bijendra Singh","Priyanshu Singh"),("Bijendra Singh","Palak"),
        ("Biresh Singh","Simran"),("Biresh Singh","Aditya"),("Biresh Singh","Arushi"),
        ("Poornima Devi","Rohiit"),("Poornima Devi","Ankit")
    ]
    spouses = [
        ("Jaglal Singh","Rajkali Devi"),("Shushil Singh","Late Dr. Sunita Singh"),
        ("Vikash Kumar","Ishita Raghuvanshi"),("Pooja Singh","Ankit"),
        ("Vakil Singh","Sumitra Devi"),("Preeti Singh","Manoranjan Kumar"),
        ("Manish Singh","Riya Kumari"),("Kedarnath Singh","Anita Devi"),
        ("Bijendra Singh","Poonam Devi"),("Biresh Singh","Lovely Devi"),
        ("Poornima Devi","Sanjeet Singh")
    ]
    for a,b in parent_child: rel(con,a,b,"parent")
    for a,b in spouses: rel(con,a,b,"spouse")
    con.commit()
    con.close()

@app.route("/")
def index():
    con=db()
    people=[dict(x) for x in con.execute("SELECT * FROM people ORDER BY name").fetchall()]
    relationships=[dict(x) for x in con.execute("SELECT * FROM relationships").fetchall()]
    con.close()
    return render_template("index.html", people=people, relationships=relationships)

@app.route("/add", methods=["POST"])
def add():
    name=request.form.get("name","").strip()
    gender=request.form.get("gender","").strip()
    notes=request.form.get("notes","").strip()
    if name:
        con=db(); add_person(con,name,gender,notes)
        parent=request.form.get("parent","").strip()
        spouse=request.form.get("spouse","").strip()
        if parent:
            add_person(con,parent)
            rel(con,parent,name,"parent")
        if spouse:
            add_person(con,spouse)
            rel(con,name,spouse,"spouse")
        con.commit(); con.close()
    return redirect(url_for("index"))

@app.route("/api/tree")
def api_tree():
    con=db()
    people=[dict(x) for x in con.execute("SELECT * FROM people").fetchall()]
    relationships=[dict(x) for x in con.execute("SELECT * FROM relationships").fetchall()]
    con.close()
    return jsonify({"people":people,"relationships":relationships})

if __name__=="__main__":
    init_db()
    seed()
    app.run(debug=True)
