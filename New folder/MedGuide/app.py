import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, abort

# ──────────────────────────────────────────────────────────────────────────────
# Flask app — template & static folders resolved relative to this file
# so the app works both locally and on Vercel
# ──────────────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)

# ──────────────────────────────────────────────────────────────────────────────
# Database path
# Vercel serverless → /tmp  (writable; ephemeral between cold-starts)
# Local dev         → project directory
# ──────────────────────────────────────────────────────────────────────────────
DATABASE = (
    "/tmp/medguide.db"
    if os.environ.get("VERCEL") or not os.access(BASE_DIR, os.W_OK)
    else os.path.join(BASE_DIR, "database.db")
)


# ──────────────────────────────────────────────────────────────────────────────
# DB helpers
# ──────────────────────────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_database():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS medicines (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            medicine_name TEXT NOT NULL,
            category      TEXT NOT NULL,
            composition   TEXT,
            uses          TEXT,
            purpose       TEXT,
            precautions   TEXT,
            side_effects  TEXT,
            warnings      TEXT
        )
    """)

    cur.execute("SELECT COUNT(*) FROM medicines")
    if cur.fetchone()[0] == 0:
        seed = [
            ("Paracetamol", "Tablet",
             "Paracetamol 500mg",
             "Commonly used for temporary relief of mild to moderate pain and fever.",
             "Pain and fever relief.",
             "Follow the product label or healthcare professional's advice. Avoid alcohol.",
             "Possible nausea, stomach discomfort, or allergic reactions in rare cases.",
             "Do not exceed the recommended amount. Overdose can cause serious liver damage."),

            ("Cetirizine", "Tablet",
             "Cetirizine Hydrochloride 10mg",
             "Relieves symptoms of hay fever, hives, and other allergic conditions.",
             "Allergy symptom relief (sneezing, runny nose, watery eyes).",
             "Follow the product label or your doctor's advice.",
             "May cause drowsiness or dry mouth.",
             "Avoid driving or operating machinery if drowsy."),

            ("Ibuprofen", "Tablet",
             "Ibuprofen 400mg",
             "Used for pain relief, reducing fever, and relieving inflammation.",
             "Anti-inflammatory, analgesic, and antipyretic.",
             "Take with food or milk to reduce stomach upset.",
             "May cause stomach pain, nausea, or headache.",
             "Avoid in people with stomach ulcers or kidney problems."),

            ("Amoxicillin", "Capsule",
             "Amoxicillin Trihydrate 500mg",
             "Treats a wide variety of bacterial infections including ear, throat, skin, and urinary tract.",
             "Antibiotic — treatment of bacterial infections.",
             "Complete the full prescribed course. Do not skip doses.",
             "May cause diarrhoea, rash, or allergic reactions.",
             "Inform your doctor if allergic to penicillin. Requires a prescription."),

            ("Omeprazole", "Capsule",
             "Omeprazole 20mg",
             "Reduces stomach acid for conditions like acid reflux, GERD, and stomach ulcers.",
             "Proton-pump inhibitor — stomach acid reducer.",
             "Take 30–60 minutes before meals. Follow prescribed duration.",
             "Headache, diarrhoea, stomach pain, or nausea may occur.",
             "Long-term use may affect magnesium levels. Consult your doctor."),

            ("Paracetamol Syrup", "Syrup",
             "Paracetamol 125mg / 5ml",
             "Temporary relief of mild to moderate pain and fever in children.",
             "Paediatric pain and fever relief.",
             "Use the measuring device supplied. Follow the label instructions.",
             "Possible nausea or allergic reactions in rare cases.",
             "Do not exceed the recommended dose. Keep out of reach of children."),

            ("Ibuprofen Syrup", "Syrup",
             "Ibuprofen 100mg / 5ml",
             "Pain relief, fever reduction, and anti-inflammation for children.",
             "Paediatric anti-inflammatory and antipyretic.",
             "Give with food or milk. Dose by child's weight.",
             "May cause stomach upset, nausea, or allergic reactions.",
             "Not for children under 3 months. Consult a doctor first."),

            ("Chlorpheniramine Syrup", "Syrup",
             "Chlorpheniramine Maleate 2mg / 5ml",
             "Relieves allergy symptoms, hay fever, and common cold symptoms.",
             "Antihistamine for allergy and cold relief.",
             "Use exactly as directed. Avoid alcohol.",
             "Drowsiness, dry mouth, or blurred vision may occur.",
             "Do not drive or operate machinery. Keep out of reach of children."),

            ("Mupirocin", "Ointment",
             "Mupirocin 2% w/w",
             "Used for certain bacterial skin infections such as impetigo when prescribed.",
             "Topical antibiotic for bacterial skin infections.",
             "Use only as directed. Clean skin before applying.",
             "Skin irritation, burning, or itching at application site.",
             "For external use only. Avoid contact with eyes. Requires a prescription."),

            ("Clotrimazole", "Ointment",
             "Clotrimazole 1% w/w",
             "Treats fungal skin infections such as ringworm, athlete's foot, and thrush.",
             "Antifungal treatment for skin infections.",
             "Apply thinly to affected area. Continue for the full recommended period.",
             "Mild burning, stinging, or skin irritation may occur.",
             "For external use only. Avoid eyes and mucous membranes."),

            ("Betamethasone Cream", "Ointment",
             "Betamethasone Valerate 0.1% w/w",
             "Reduces inflammation and itching caused by skin conditions like eczema and psoriasis.",
             "Topical corticosteroid for inflammatory skin conditions.",
             "Apply a thin layer. Do not use for longer than directed.",
             "Skin thinning, stretch marks, or discolouration with prolonged use.",
             "For external use only. Avoid face, eyes, and open wounds."),

            ("Azithromycin", "Tablet",
             "Azithromycin 500mg",
             "Treats bacterial infections of the lungs, throat, sinuses, skin, and ears.",
             "Macrolide antibiotic — broad-spectrum bacterial infection treatment.",
             "Take on an empty stomach. Complete the full course.",
             "Stomach upset, diarrhoea, nausea, or abdominal pain may occur.",
             "May interact with other medicines. Requires a prescription."),

            ("Metformin", "Tablet",
             "Metformin Hydrochloride 500mg",
             "Helps control blood sugar levels in type 2 diabetes.",
             "Oral antidiabetic — blood glucose management.",
             "Take with meals to reduce stomach upset. Monitor blood glucose.",
             "Nausea, vomiting, diarrhoea, or loss of appetite may occur.",
             "Do not use in kidney disease. Requires a prescription."),

            ("Vitamin C", "Tablet",
             "Ascorbic Acid 500mg",
             "Dietary supplement to support immune health and prevent vitamin C deficiency.",
             "Vitamin C supplementation.",
             "Do not exceed the recommended amount.",
             "High doses may cause digestive discomfort.",
             "Consult a doctor before use during pregnancy or if on other medicines."),

            ("Loratadine", "Syrup",
             "Loratadine 5mg / 5ml",
             "Relieves allergy symptoms including runny nose, sneezing, and itching.",
             "Non-drowsy antihistamine for allergy relief.",
             "Use as directed on the label.",
             "Headache or stomach upset in some individuals.",
             "Generally non-drowsy but avoid alcohol."),
        ]

        cur.executemany("""
            INSERT INTO medicines
                (medicine_name, category, composition, uses, purpose,
                 precautions, side_effects, warnings)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, seed)

    conn.commit()
    conn.close()


# ──────────────────────────────────────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/")
@app.route("/api/index")
def home():
    create_database()
    conn = get_db()
    medicines = conn.execute(
        "SELECT * FROM medicines ORDER BY medicine_name"
    ).fetchall()
    conn.close()
    return render_template("index.html", medicines=medicines)


@app.route("/search")
def search():
    create_database()
    q = request.args.get("medicine", "").strip()
    conn = get_db()
    medicines = conn.execute("""
        SELECT * FROM medicines
        WHERE medicine_name LIKE ?
           OR category      LIKE ?
           OR composition   LIKE ?
        ORDER BY medicine_name
    """, (f"%{q}%", f"%{q}%", f"%{q}%")).fetchall()
    conn.close()
    return render_template("index.html", medicines=medicines, search_text=q)


@app.route("/category/<cat>")
def category(cat):
    create_database()
    conn = get_db()
    medicines = conn.execute("""
        SELECT * FROM medicines WHERE category = ? ORDER BY medicine_name
    """, (cat,)).fetchall()
    conn.close()
    return render_template("index.html", medicines=medicines, active_cat=cat)


@app.route("/medicine/<int:mid>")
def medicine_details(mid):
    create_database()
    conn = get_db()
    medicine = conn.execute(
        "SELECT * FROM medicines WHERE id = ?", (mid,)
    ).fetchone()
    conn.close()
    if medicine is None:
        abort(404)
    return render_template("medicine.html", medicine=medicine)


@app.route("/admin")
def admin():
    create_database()
    conn = get_db()
    medicines = conn.execute(
        "SELECT * FROM medicines ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return render_template("admin.html", medicines=medicines)


@app.route("/add", methods=["POST"])
def add_medicine():
    create_database()
    fields = [
        request.form.get("medicine_name", "").strip(),
        request.form.get("category", "").strip(),
        request.form.get("composition", "").strip(),
        request.form.get("uses", "").strip(),
        request.form.get("purpose", "").strip(),
        request.form.get("precautions", "").strip(),
        request.form.get("side_effects", "").strip(),
        request.form.get("warnings", "").strip(),
    ]
    if fields[0] and fields[1]:          # name + category required
        conn = get_db()
        conn.execute("""
            INSERT INTO medicines
                (medicine_name, category, composition, uses, purpose,
                 precautions, side_effects, warnings)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, fields)
        conn.commit()
        conn.close()
    return redirect(url_for("admin"))


@app.route("/delete/<int:mid>", methods=["POST"])
def delete_medicine(mid):
    create_database()
    conn = get_db()
    conn.execute("DELETE FROM medicines WHERE id = ?", (mid,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin"))


# ──────────────────────────────────────────────────────────────────────────────
# Local dev only
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    create_database()
    app.run(debug=True)
