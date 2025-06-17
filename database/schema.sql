CREATE TABLE IF NOT EXISTS clusters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    control_plane_ip TEXT NOT NULL,
    worker_ips TEXT NOT NULL,
    ssh_user TEXT NOT NULL,
    ssh_key_path TEXT NOT NULL,
    kube_version TEXT,
    cni TEXT,
    ha INTEGER DEFAULT 0,
    pod_cidr TEXT
);
