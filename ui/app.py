"""Flask application to manage Kubernetes clusters via Ansible."""

from __future__ import annotations

import os
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Generator, List

from flask import (
    Flask,
    Response,
    flash,
    redirect,
    render_template,
    request,
    stream_with_context,
    url_for,
)
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash, generate_password_hash
import ansible_runner
from dotenv import load_dotenv

DATABASE = Path("/data/clusters.db")
SCHEMA = Path("database/schema.sql")

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me")
auth = HTTPBasicAuth()

users = {
    os.environ.get("AUTH_USERNAME", "admin"): generate_password_hash(
        os.environ.get("AUTH_PASSWORD", "secret")
    )
}


@auth.verify_password
def verify_password(username: str, password: str) -> bool:
    """Validate a username/password pair."""
    stored = users.get(username, "")
    if username in users and check_password_hash(stored, password):
        return True
    return False


def get_db() -> sqlite3.Connection:
    db_exists = DATABASE.exists()
    conn = sqlite3.connect(DATABASE)
    if not db_exists:
        with open(SCHEMA) as f:
            conn.executescript(f.read())
        conn.commit()
    conn.row_factory = sqlite3.Row
    return conn


def cluster_list() -> List[sqlite3.Row]:
    with closing(get_db()) as db:
        cur = db.execute("SELECT * FROM clusters")
        return cur.fetchall()


@app.route("/")
@auth.login_required
def index() -> str:
    clusters = cluster_list()
    return render_template("index.html", clusters=clusters)


@app.route("/cluster/new", methods=["GET", "POST"])
@auth.login_required
def create_cluster() -> Response | str:
    if request.method == "POST":
        save_cluster(request.form)
        flash("Cluster saved", "success")
        return redirect(url_for("index"))
    return render_template("cluster_form.html", cluster=None)


@app.route("/cluster/<int:cid>", methods=["GET", "POST"])
@auth.login_required
def edit_cluster(cid: int) -> Response | str:
    if request.method == "POST":
        save_cluster(request.form, cid)
        flash("Cluster updated", "success")
        return redirect(url_for("index"))
    with closing(get_db()) as db:
        cur = db.execute("SELECT * FROM clusters WHERE id=?", (cid,))
        cluster = cur.fetchone()
    return render_template("cluster_form.html", cluster=cluster)


def save_cluster(form: dict, cid: int | None = None) -> None:
    fields = (
        form.get("name"),
        form.get("control_plane_ip"),
        form.get("worker_ips"),
        form.get("ssh_user"),
        form.get("ssh_key_path"),
        form.get("kube_version"),
        form.get("cni"),
        1 if form.get("ha") else 0,
        form.get("pod_cidr"),
    )
    with closing(get_db()) as db:
        if cid:
            db.execute(
                (
                    "UPDATE clusters SET name=?, control_plane_ip=?, "
                    "worker_ips=?, ssh_user=?, "
                    "ssh_key_path=?, kube_version=?, cni=?, ha=?, pod_cidr=? "
                    "WHERE id=?"
                ),
                (*fields, cid),
            )
        else:
            db.execute(
                (
                    "INSERT INTO clusters (name, control_plane_ip, "
                    "worker_ips, ssh_user, ssh_key_path, "
                    "kube_version, cni, ha, pod_cidr) VALUES "
                    "(?, ?, ?, ?, ?, ?, ?, ?, ?)"
                ),
                fields,
            )
        db.commit()


def generate_inventory(cluster: sqlite3.Row) -> None:
    ansible_dir = Path("ansible")
    inv_path = ansible_dir / "inventory.ini"

    inventory = (
        "[control-plane]\n"
        f"{cluster['control_plane_ip']} ansible_user={cluster['ssh_user']} "
        f"ansible_ssh_private_key_file={cluster['ssh_key_path']}\n\n"
        "[workers]\n"
    )
    for ip in cluster["worker_ips"].split(','):
        inventory += (
            f"{ip} ansible_user={cluster['ssh_user']} "
            f"ansible_ssh_private_key_file={cluster['ssh_key_path']}\n"
        )
    inv_path.write_text(inventory)

    config_path = ansible_dir / "config.yml"
    config = (
        "---\n"
        "privilege_escalation:\n"
        "  become: true\n"
        "runner_mode: 'subprocess'\n"
    )
    config_path.write_text(config)


def run_playbook(playbook: str, cluster: sqlite3.Row):
    generate_inventory(cluster)

    # thread : objet Thread (inutile ici)
    # runner : objet Runner, possède .events
    ansible_dir = Path("ansible")
    playbook_path = ansible_dir / playbook
    inventory_path = ansible_dir / "inventory.ini"

    thread, runner = ansible_runner.run_async(
<<<<<<< pwizj6-codex/corriger-les-erreurs-dans-le-code
        private_data_dir=str(ansible_dir),
        playbook=str(playbook_path),
        inventory=str(inventory_path),
=======
        private_data_dir="ansible",
        playbook=playbook,
        inventory="inventory.ini",
>>>>>>> main
        rotate_artifacts=1,
    )

    # --- boucle tant que le run n'est pas fini
    for ev in runner.events:              # itère sur la queue d'événements
        if 'stdout' in ev and ev['stdout']:
            yield f"data: {ev['stdout']}\n\n"
        if ev.get('event') == 'playbook_on_stats':
            break                         # fin du playbook

    yield "data: DONE\n\n"


@app.route("/action/<int:cid>/<op>")
@auth.login_required
def action(cid: int, op: str) -> Response:
    with closing(get_db()) as db:
        cur = db.execute("SELECT * FROM clusters WHERE id=?", (cid,))
        cluster = cur.fetchone()
    playbook = {
        "deploy": "site.yml",
        "destroy": "cleanup.yml",
        "upgrade": "upgrade.yml",
    }.get(op)
    if not playbook:
        return "Invalid operation", 400

    def generate() -> Generator[str, None, None]:
        for out in run_playbook(playbook, cluster):
            yield out
    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
    )


if __name__ == "__main__":
    app.run(debug=True)
