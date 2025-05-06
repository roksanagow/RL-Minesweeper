# frontend/app.py

from flask import Flask, render_template
from frontend.api import api_blueprint

app = Flask(__name__, static_folder="static", template_folder="templates")
app.register_blueprint(api_blueprint, url_prefix="/api")


@app.route("/")
def index():
    return render_template("index.html")


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5000, help="Port to run the server on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host IP")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    print(f"Running on http://{args.host}:{args.port}/")
    app.run(debug=args.debug, host=args.host, port=args.port)


if __name__ == "__main__":
    app.run(debug=True)
