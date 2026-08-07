import html
import os
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

import psycopg2


def get_db_connection():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "postgres"),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )


def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            username VARCHAR(50) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS weather_logs (
            log_id SERIAL PRIMARY KEY,
            user_id INT REFERENCES users(user_id),
            region VARCHAR(50) NOT NULL,
            memo TEXT,
            log_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    cur.execute("SELECT COUNT(*) FROM users;")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO users (username) VALUES (%s), (%s);",
            ("portfolio_user", "cloud_engineer"),
        )
        cur.execute(
            """
            INSERT INTO weather_logs (user_id, region, memo)
            VALUES (%s, %s, %s), (%s, %s, %s);
            """,
            (
                1,
                "Seoul",
                "3-Tier architecture deployment completed.",
                2,
                "Busan",
                "RDS-backed weather log service is running.",
            ),
        )

    conn.commit()
    cur.close()
    conn.close()


class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed_path.query)

        if parsed_path.path == "/add" and "region" in query and "memo" in query:
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO weather_logs (user_id, region, memo)
                    VALUES (%s, %s, %s);
                    """,
                    (1, query["region"][0], query["memo"][0]),
                )
                conn.commit()
                cur.close()
                conn.close()
                self.send_response(303)
                self.send_header("Location", "/")
                self.end_headers()
                return
            except Exception as exc:
                print(f"Insert Error: {exc}")

        db_rows = []
        error_msg = ""
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT u.username, w.region, w.memo, w.log_time
                FROM weather_logs w
                JOIN users u ON w.user_id = u.user_id
                ORDER BY w.log_time DESC;
                """
            )
            db_rows = cur.fetchall()
            cur.close()
            conn.close()
        except Exception as exc:
            error_msg = f"DB Error: {exc}"

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()

        rows_html = ""
        for username, region, memo, log_time in db_rows:
            rows_html += f"""
            <tr>
                <td>{html.escape(str(username))}</td>
                <td><strong>{html.escape(str(region))}</strong></td>
                <td>{html.escape(str(memo))}</td>
                <td>{html.escape(str(log_time))}</td>
            </tr>
            """

        response_html = f"""
        <!doctype html>
        <html lang="ko">
        <head>
            <meta charset="utf-8">
            <title>AWS 3-Tier Weather Board</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f7f7f7; }}
                main {{ max-width: 900px; margin: auto; background: white; padding: 30px; border-radius: 8px; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 10px; border-bottom: 1px solid #ddd; text-align: center; }}
                form {{ margin: 24px 0; }}
                input {{ padding: 6px; margin-right: 8px; }}
                button {{ padding: 7px 14px; cursor: pointer; }}
                .status {{ color: #2e7d32; }}
                .error {{ color: #c62828; }}
            </style>
        </head>
        <body>
            <main>
                <h2>AWS Cloud Weather Board</h2>
                <p class="status"><strong>3-Tier Distributed DB CRUD Active</strong></p>

                <form action="/add" method="get">
                    <input type="text" name="region" placeholder="Region" required>
                    <input type="text" name="memo" placeholder="Weather memo" required>
                    <button type="submit">Save to DB</button>
                </form>

                <p class="error">{html.escape(error_msg)}</p>
                <table>
                    <thead>
                        <tr>
                            <th>User</th>
                            <th>Region</th>
                            <th>Memo</th>
                            <th>Created At</th>
                        </tr>
                    </thead>
                    <tbody>{rows_html}</tbody>
                </table>
            </main>
        </body>
        </html>
        """

        self.wfile.write(response_html.encode("utf-8"))


if __name__ == "__main__":
    init_db()
    server = HTTPServer(("0.0.0.0", 5000), MyHandler)
    print("WAS Server started on 0.0.0.0:5000")
    server.serve_forever()
