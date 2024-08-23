import gzip
import os

from flask import Flask, request
from git import Repo

app = Flask(__name__)
GIT_REPO = "./repo"


class GitError(Exception):
    pass


def git_check_repo(repopath):
    repo = None

    if not os.path.exists(repopath):
        raise GitError("Repository does not exist")

    try:
        repo = Repo(repopath)

        if repo.is_dirty():
            raise GitError("Repository is dirty")
    except Exception as e:
        raise GitError(str(e))

    return repo


def git_commit_repo(repo, repopath, filename, filedata):
    if isinstance(filedata, bytes):
        filedata = filedata.decode("utf-8")

    with open(repopath + "/" + filename, "w") as f:
        f.write(filedata)

    repo.index.add([filename])
    repo.index.commit(f"{filename}")

    return True


@app.route("/commit/<filename>", methods=["PUT"])
def put(filename):
    if not request.headers["Content-Type"] == "application/gzip":
        return "Unsupported Media Type", 415

    reqdata = request.data

    try:
        filedata = gzip.decompress(reqdata)
    except Exception as e:
        return str(e), 400

    print(f"Received file: {filename}")

    filename = filename.replace(".gz", "")

    try:
        repo = git_check_repo(GIT_REPO)
        git_commit_repo(repo, GIT_REPO, filename, filedata)
    except GitError as e:
        print(f"Error: {e}")
        return str(e), 400

    return "OK", 200


if __name__ == "__main__":
    app.run(debug=True)
