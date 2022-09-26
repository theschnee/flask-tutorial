from flask import (Blueprint, flash, g, redirect, render_template, request, url_for, jsonify)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('home', __name__)

# method to automatically get the ip address of a machine's/connection's request 
# MAY NOT USE THIS RIGHT NOW 
@bp.route("/get_my_ip", methods=["GET"])
def get_my_ip():
    return jsonify({'ip': request.remote_addr}), 200

# method to show all of the posts on the blog page 
@bp.route('/')
def index():
    db = get_db()
    # TODO: Figure out why there are no commas inside the execute function
    ip_posts = db.execute(
        'SELECT p.id, ip_label, ip_addresses, created, author_id, username'
        ' FROM ip_post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('home/index.html', ip_posts=ip_posts)


# method to create post to take in an IP label and a list of addresses belonging to it 
# OPTIONAL: make sure that the user has logged in 
# TODO: Make sure that the IP addresses entered are actually IP addresses 
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():

    # if statement not currently needed, may be needed in the future
    if request.method == 'POST':
        ip_label = request.form['ip_label']
        ip_addresses = request.form['ip_addresses']
        error = None

        if not ip_label:
            error = 'IP label is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO ip_post (ip_label, ip_addresses, author_id)'
                ' VALUES (?, ?, ?)',
                (ip_label, ip_addresses, g.user['id'])
            )
            db.commit()
            return redirect(url_for('home.index'))

    return render_template('home/create.html')

