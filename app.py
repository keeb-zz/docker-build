from flask import Flask
from flask import request
from flask import jsonify
from flask import abort

import json

from git import Git

from docker import client

from subprocess import Popen

import shlex

app = Flask(__name__)
app.debug = True

docker_client = client.Client()


SAVE_DIR_BASE = "dest"
GIT_REPO = "git://github.com/keeb/blog"


@app.route('/', methods=["POST"])
def index():
    info = json.loads(request.data)
    rep_id = info["commits"][0]["id"][0:5]
    save_dir = "%s/%s" % (SAVE_DIR_BASE, rep_id)
    tag = 'keeb/blog-snapshot-%s' % rep_id
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
        clone(GIT_REPO, save_dir)
        build(save_dir, tag)
        if not check(tag): abort(400)
        run(tag)

    else: abort(400)

    
    return jsonify(id=rep_id)


def clone(repo, into):
    Git().clone(repo, into)

def build(f, tag):
    #since docker_client doesn't support add, we need to do this manually for now.
    it = shlex.split("docker build -t %s %s" % (tag, f))
    proc = Popen(it)
    proc.wait()


def check(tag):
    if docker_client.images(name=tag):
        return True
    return False

def run(tag):
    #docker_client also doesn't support run, so we have to do that manually as well.
    it = shlex.split("docker run -d %s" %  tag)
    proc = Popen(it)
    proc.wait()



if __name__ == '__main__':
    import sys, os
    app.run(host="0.0.0.0")
