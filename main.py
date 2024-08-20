import os
from urllib.parse import unquote

from flask import Flask, request
from git import Repo

app = Flask(__name__)
GIT_REPO = "./repo"


def git_check_repo(repo_path):
    errstr = []

    if not os.path.exists(repo_path):
        errstr.append("Repository does not exist")
        return errstr

    try:
        repo = Repo(repo_path)

        if repo.is_dirty():
            errstr.append("Repository is dirty")
    except Exception as e:
        errstr.append(str(e))
        return errstr

    return errstr


@app.route("/commit", methods=["POST"])
def post_text():
    errstr = []

    content = request.data.decode("utf-8")
    content = unquote(content)

    fileheader = content.split("\n")[0].replace("#", "")
    filename = fileheader.split(":")[0]
    fileuser = fileheader.split(":")[1]
    filepath = os.path.join(GIT_REPO, filename)
    filedata = content

    try:
        errstr = git_check_repo(GIT_REPO)

        if errstr:
            return "\n".join(errstr), 500

        with open(filepath, "w") as f:
            f.write(filedata)

        repo = Repo(GIT_REPO)
        repo.index.add([filename])
        repo.index.commit(f"{fileuser}")

    except Exception as e:
        errstr.append(str(e))

    if errstr:
        return "\n".join(errstr), 500

    return "OK", 200


if __name__ == "__main__":
    app.run(debug=True)
