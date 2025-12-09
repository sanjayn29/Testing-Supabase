from flask import Flask, request, jsonify
from dotenv import load_dotenv
import psycopg2
import os

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

app = Flask(__name__)

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

@app.route("/")
def index():
    # Serve a simple HTML UI with a form
    return """
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8" />
      <title>Save Data to Supabase</title>
    </head>
    <body>
      <h1>Save Data to Supabase via Python</h1>

      <form id="data-form">
        <input type="text" id="username" placeholder="Username" required />
        <input type="text" id="info" placeholder="Some info" required />
        <button type="submit">Save</button>
      </form>

      <p id="message"></p>

      <script>
        const form = document.getElementById("data-form");
        const msg = document.getElementById("message");

        form.addEventListener("submit", async (e) => {
          e.preventDefault();

          const username = document.getElementById("username").value;
          const info = document.getElementById("info").value;

          try {
            const res = await fetch("/save-data", {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({ username, info }),
            });

            const data = await res.json();
            if (res.ok) {
              msg.textContent = "Saved! New row id: " + data.id;
              form.reset();
            } else {
              msg.textContent = "Error: " + data.error;
            }
          } catch (err) {
            console.error(err);
            msg.textContent = "Network error";
          }
        });
      </script>
    </body>
    </html>
    """

@app.route("/save-data", methods=["POST"])
def save_data():
    try:
        payload = request.get_json()
        username = payload.get("username")
        info = payload.get("info")

        if not username or not info:
            return jsonify({"error": "username and info are required"}), 400

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO app_data (username, info) VALUES (%s, %s) RETURNING id;",
            (username, info)
        )
        new_id = cur.fetchone()[0]

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"id": new_id}), 201

    except Exception as e:
        print("Error inserting data:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
