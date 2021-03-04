from __besafe__ import app


@app.route("/")
def go_home():
    """Renders the besafe homepage. (Tested)"""
    return render_template("../templates/homepage.html")