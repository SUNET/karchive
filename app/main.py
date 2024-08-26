import re
import gzip
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

try:
    repo = Repo(GIT_REPO)
except Exception as e:
    app.logger.error(f"Error: {e}")
    exit(1)


class GitError(Exception):
    pass


def git_commit_repo(repo, repopath, filename, filedata):
    if isinstance(filedata, bytes):
        filedata = filedata.decode("utf-8")

    with open(repopath + "/" + filename, "w") as f:
        f.write(filedata)

    repo.index.add([filename])
    app.logger.info(f"File added to index: {filename} in repo {repopath}")

    repo.index.commit(f"{filename}")
    app.logger.info(f"File committed: {filename} in repo {repopath}")

    return True


@app.route("/commit/<filename>", methods=["PUT"])
def put(filename):
    re_strip = re.compile(r"_\.*\d{8}_\d{6}")

    try:
        filedata = gzip.decompress(request.data)
    except Exception as e:
        app.logger.error(f"Error: {e}")
        return "Error", 400

    app.logger.info(f"Received file: {filename}")

    filename = filename.replace(".gz", "")
    filename = filename.replace("-re0", "")
    filename = filename.replace("-re1", "")
    filename = filename.replace("_juniper", "")
    filename = re.sub(re_strip, "", filename)

    try:
        git_commit_repo(repo, GIT_REPO, filename, filedata)
    except GitError as e:
        app.logger.error(f"Error: {e}")
        return "Error", 400

    return "OK", 200


if __name__ == "__main__":
    app.run(debug=True)
