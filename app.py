from flask import Flask, render_template
import sqlite3
import base64

app = Flask(__name__)

@app.route("/")
def index():
    conn = sqlite3.connect(r"C:\Users\Asus\OneDrive\Desktop\python-workspace\ppe_web\violationss2.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, frame_number, people_count, timestamp, violations,  violation_count, violation_image, area
        FROM violations ORDER BY id DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()

    violations = []
    for row in rows:
        image_data = base64.b64encode(row[6]).decode('utf-8') if row[6] else None
        violations.append({
            "id": row[0],
            "frame_number": row[1], 
            "people_count": row[2], 
            "timestamp": row[3], 
            "violations": row[4], 
            "violation_count": row[5], 
            "image_data": image_data, 
            "area": row[7] if len(row) > 7 else "Unknown"
        })

    return render_template("index.html", violations=violations)

if __name__ == "__main__":
    app.run(debug=True)


#cd C:\Users\Asus\OneDrive\Desktop\python-workspace\ppe_web
#python app.py