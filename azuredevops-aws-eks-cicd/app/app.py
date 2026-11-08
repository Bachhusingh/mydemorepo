from flask import Flask, jsonify, request
import psycopg2
import os

app = Flask(__name__)
from prometheus_flask_exporter import PrometheusMetrics
metrics = PrometheusMetrics(app)

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )


@app.route("/")
def home():
    return jsonify({
        "message": "Azure DevOps -> ECR -> EKS -> RDS deployment successful!",
        "status": "healthy"
    })


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy"
    })


@app.route("/db-health")
def db_health():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT 1;")
        result = cur.fetchone()

        cur.close()
        conn.close()

        return jsonify({
            "database": "healthy",
            "result": result[0]
        })

    except Exception as e:
        return jsonify({
            "database": "unhealthy",
            "error": str(e)
        }), 500


@app.route("/incidents", methods=["GET"])
def get_incidents():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, title, status, created_at
            FROM incidents
            ORDER BY id DESC;
        """)

        rows = cur.fetchall()

        incidents = []

        for row in rows:
            incidents.append({
                "id": row[0],
                "title": row[1],
                "status": row[2],
                "created_at": row[3].isoformat()
            })

        cur.close()
        conn.close()

        return jsonify(incidents)

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.route("/incidents", methods=["POST"])
def create_incident():
    try:
        data = request.get_json()

        title = data.get("title")
        status = data.get("status", "OPEN")

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO incidents (title, status)
            VALUES (%s, %s)
            RETURNING id;
        """, (title, status))

        incident_id = cur.fetchone()[0]

        conn.commit()

        cur.close()
        conn.close()

        return jsonify({
            "message": "Incident created",
            "id": incident_id
        }), 201

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

    