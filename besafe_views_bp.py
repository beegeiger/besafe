from flask import (Flask, render_template, redirect, request, flash,
                   session, jsonify, Blueprint)

views_bp = Blueprint('views_bp', __name__,
    template_folder='templates',
    static_folder='static', static_url_path='assets')


@app.route("/")
def go_home():
    """Renders the besafe homepage. (Tested)"""
    return render_template("homepage.html")