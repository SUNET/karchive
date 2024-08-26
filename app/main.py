import gzip
import os
from logging.config import dictConfig

from flask import Flask, request
from git import Repo

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)

app = Flask(__name__)
GIT_REPO = "/repo"


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
    try:
        filedata = gzip.decompress(request.data)
    except Exception as e:
        app.logger.error(f"Error: {e}")
        return "Error", 400

    app.logger.info(f"Received file: {filename}")

    filename = filename.replace(".gz", "")

    try:
        repo = git_check_repo(GIT_REPO)
        app.logger.info(f"Repository checked: {GIT_REPO}")

        git_commit_repo(repo, GIT_REPO, filename, filedata)
        app.logger.info(f"File committed: {filename}")
    except GitError as e:
        app.logger.error(f"Error: {e}")
        return "Error", 400

    return "OK", 200


if __name__ == "__main__":
    app.run(debug=True)
