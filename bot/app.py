from flask import Flask, Blueprint, render_template, request, redirect, url_for, send_file
from io import BytesIO
import asyncio

from .bot import upload_file as d_upload_file, get_files_list as d_get_files_list, download_file as d_download_file

routes = Blueprint("routes", "routes")

@routes.route("/")
def home():
    files_list = request.args.get("files_list")
    return render_template("home.html", files_list=files_list)

@routes.route("/upload_file", methods=["POST"])
def upload_file():
    from .bot import discord_loop as loop
    u_file = request.files.get("u-file")
    file_hex:str = u_file.stream.read().hex()

    hexes:list[str] = []
    MAX_LEN:int = 2000-len(u_file.filename)-len("\n\n")
    while len(file_hex) > MAX_LEN:
        hexes.append(
            file_hex[0:MAX_LEN]
        )
        file_hex = file_hex[MAX_LEN:]

    for i, h in enumerate(hexes):
        future = asyncio.run_coroutine_threadsafe(d_upload_file(f"{u_file.filename}:part{i+1}", h), loop)
        res = future.result(10)

    return redirect(url_for("routes.home"))

@routes.route("/get_files_list", methods=["GET"])
def get_files_list():
    from .bot import discord_loop as loop

    future = asyncio.run_coroutine_threadsafe(d_get_files_list(), loop)
    res = future.result(10)
    
    return redirect(url_for("routes.home", files_list=','.join(res)))

@routes.route("/download_file", methods=["GET"])
def download_file():
    from .bot import discord_loop as loop

    f = request.args.get("d_file").split(":")
    future = asyncio.run_coroutine_threadsafe(d_download_file(f[0], f[1]), loop)
    f_hex = future.result(30)

    #return redirect(url_for("routes.get_files_list"))
    return send_file(
        BytesIO(bytes.fromhex(f_hex)),
        mimetype="application/octet-stream",
        download_name=f[0],
        as_attachment=True
    )

def build_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = "wowsosecret"
    app.register_blueprint(routes)
    return app

def run_app(app:Flask):
    app.run('0.0.0.0', debug=True)