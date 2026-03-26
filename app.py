from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS fir (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        crime_type TEXT,
        location TEXT,
        description TEXT
    )
    ''')

    # Criminal Table
    c.execute('''
CREATE TABLE IF NOT EXISTS criminal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age TEXT,
    gender TEXT,
    address TEXT,
    history TEXT,
    photo TEXT
)
''')

# Case Table
    c.execute("DROP TABLE IF EXISTS cases")
    c.execute('''
CREATE TABLE cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id TEXT,
    fir_id TEXT,
    officer TEXT,
    status TEXT,
    notes TEXT
)
''')

# Victim Table
    c.execute('''
CREATE TABLE IF NOT EXISTS victim (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    contact TEXT,
    address TEXT,
    case_id TEXT
)
''')

    conn.commit()
    conn.close()

init_db()

# ---------- ROUTES ----------

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    if request.form['username'] == "admin" and request.form['password'] == "1234":
        return redirect('/dashboard')
    return "Invalid"

@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM fir")
    total = c.fetchone()[0]

    conn.close()

    return render_template('dashboard.html', total=total)

@app.route('/fir')
def fir():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("SELECT * FROM fir")
    data = c.fetchall()

    conn.close()

    return render_template('fir.html', data=data)

@app.route('/add_fir', methods=['POST'])
def add_fir():
    data = (
        request.form['crime_type'],
        request.form['location'],
        request.form['description']
    )

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO fir (crime_type, location, description) VALUES (?, ?, ?)", data)
    conn.commit()
    conn.close()

    return redirect('/dashboard')

# other pages
@app.route('/criminal', methods=['GET', 'POST'])
def criminal():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        address = request.form['address']
        history = request.form['history']

        photo = request.files['photo']
        filename = photo.filename
        photo.save(os.path.join('static/uploads', filename))

        c.execute("INSERT INTO criminal (name, age, gender, address, history, photo) VALUES (?, ?, ?, ?, ?, ?)",
                  (name, age, gender, address, history, filename))

        conn.commit()

    # 👇 FETCH DATA
    c.execute("SELECT * FROM criminal")
    data = c.fetchall()

    conn.close()

    return render_template('criminal.html', data=data)
@app.route('/delete_criminal/<int:id>')
def delete_criminal(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("DELETE FROM criminal WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/criminal')
@app.route('/edit_criminal/<int:id>', methods=['GET', 'POST'])
def edit_criminal(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        address = request.form['address']
        history = request.form['history']

        c.execute("""UPDATE criminal 
                     SET name=?, age=?, gender=?, address=?, history=? 
                     WHERE id=?""",
                  (name, age, gender, address, history, id))

        conn.commit()
        conn.close()

        return redirect('/criminal')

    c.execute("SELECT * FROM criminal WHERE id=?", (id,))
    data = c.fetchone()

    conn.close()

    return render_template('edit_criminal.html', data=data)



@app.route('/victim', methods=['GET', 'POST'])
def victim():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS victim (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        contact TEXT,
        address TEXT,
        case_id TEXT
    )
    ''')

    if request.method == 'POST':
        name = request.form['name']
        contact = request.form['contact']
        address = request.form['address']
        case_id = request.form['case_id']

        c.execute("INSERT INTO victim (name, contact, address, case_id) VALUES (?, ?, ?, ?)",
                  (name, contact, address, case_id))

        conn.commit()

    c.execute("SELECT * FROM victim")
    data = c.fetchall()

    conn.close()

    return render_template('victim.html', data=data)


@app.route('/reports', methods=['GET', 'POST'])
def reports():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    data = []
    headers = []

    if request.method == 'POST':
        report_type = request.form['type']
        print(request.form)

        if report_type == 'criminal':
            c.execute("SELECT id, name, age, gender FROM criminal")
            data = c.fetchall()
            headers = ['ID', 'Name', 'Age', 'Gender']

        elif report_type == 'case':
            c.execute("SELECT case_id, fir_id, officer, status FROM cases")
            data = c.fetchall()
            headers = ['Case ID', 'FIR ID', 'Officer', 'Status']

        elif report_type == 'fir':
            c.execute("SELECT id, crime_type, location FROM fir")
            data = c.fetchall()
            headers = ['ID', 'Crime Type', 'Location']

    conn.close()

    return render_template('reports.html', data=data, headers=headers)
@app.route('/search', methods=['GET', 'POST'])
def search():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    results = []

    if request.method == 'POST':
        keyword = request.form['keyword']

        c.execute("SELECT * FROM criminal WHERE name LIKE ?", ('%' + keyword + '%',))
        results = c.fetchall()

    conn.close()

    return render_template('search.html', results=results)
@app.route('/logout')
def logout():
    return redirect('/')

@app.route('/case', methods=['GET', 'POST'])
def case():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    if request.method == 'POST':
        case_id = request.form['case_id']
        fir_id = request.form['fir_id']
        officer = request.form['officer']
        status = request.form['status']
        notes = request.form['notes']

        c.execute("INSERT INTO cases (case_id, fir_id, officer, status, notes) VALUES (?, ?, ?, ?, ?)",
                  (case_id, fir_id, officer, status, notes))

        conn.commit()
        conn.close()

        # ✅ THIS LINE FIXES YOUR ISSUE
        return redirect('/case')

    c.execute("SELECT * FROM cases")
    data = c.fetchall()

    conn.close()

    return render_template('case.html', data=data)
conn = sqlite3.connect('database.db')
c = conn.cursor()

c.execute("PRAGMA table_info(cases)")
print(c.fetchall())

conn.close()


if __name__ == "__main__":
    init_db()
    import os

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)