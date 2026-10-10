#!/bin/bash
# Migrate the Docker data-root to a loop-mounted xfs (pquota) filesystem.
#
# Why: PG and TiDB scenario containers enforce disk quota via
# `docker run --storage-opt size=...` (directly or through compose
# `storage_opt`), and Docker only supports that on overlay2 over an xfs
# filesystem mounted with pquota. On ext4 every container start fails with:
#   "Error response from daemon: --storage-opt is supported only for overlay
#    over xfs with 'pquota' mount option"
#
# What it does:
#   1. create a sparse image file and format it xfs
#   2. loop-mount it with pquota
#   3. stop docker, rsync /var/lib/docker into the new root
#   4. set data-root in /etc/docker/daemon.json and restart docker
#   5. verify quota enforcement, restart previously running containers
#
# Run as: sudo bash scripts/setup_docker_xfs_dataroot.sh
# Overridables (env): IMG, MNT, SIZE   e.g. SIZE=100G bash scripts/...
# After success, add the printed fstab line — the loop mount is runtime state
# and disappears on reboot, leaving docker with an empty data-root directory.
set -euo pipefail

IMG="${IMG:-/srv/docker-xfs.img}"
MNT="${MNT:-/srv/docker-xfs}"
SIZE="${SIZE:-200G}"   # sparse: real usage grows only as docker fills it

[ "$(id -u)" -eq 0 ] || { echo "must run as root (sudo)"; exit 1; }
[ -e "$IMG" ] && { echo "$IMG already exists, aborting"; exit 1; }
mountpoint -q "$MNT" && { echo "$MNT already mounted, aborting"; exit 1; }

echo "== 1/6 create sparse image $IMG ($SIZE) =="
truncate -s "$SIZE" "$IMG"

echo "== 2/6 mkfs.xfs =="
mkfs.xfs -f "$IMG"

echo "== 3/6 mount with pquota =="
mkdir -p "$MNT"
mount -o loop,pquota "$IMG" "$MNT"
xfs_quota -x -c 'report -h' "$MNT"   # sanity: quota accounting works

echo "== 4/6 stop docker, migrate data =="
RUNNING="$(docker ps -q)"
systemctl stop docker docker.socket
rsync -aHAX --info=progress2 /var/lib/docker/ "$MNT"/
mv /var/lib/docker /var/lib/docker.ext4.bak

echo "== 5/6 set data-root, start docker =="
# Only data-root is touched here; registry mirrors (if your network needs
# them) are a separate daemon.json setting you maintain yourself.
python3 - "$MNT" <<'EOF'
import json, sys
p = "/etc/docker/daemon.json"
cfg = json.load(open(p))
cfg["data-root"] = sys.argv[1]
json.dump(cfg, open(p, "w"), indent=2)
print(open(p).read())
EOF
systemctl start docker

echo "== 6/6 verify =="
docker info | grep -E "Docker Root|Storage Driver"
docker run --rm --storage-opt size=1g hello-world >/dev/null 2>&1 \
  || docker run --rm --storage-opt size=1g postgres:16 df -h / | tail -1
echo "quota test passed if the df line above shows ~1G instead of host size"

echo "== restart previously running containers =="
[ -n "$RUNNING" ] && docker start $RUNNING
docker ps --format '{{.Names}} {{.Status}}'

echo "== fstab entry for reboot persistence =="
echo "$IMG $MNT xfs loop,pquota 0 0"
echo "Append the line above to /etc/fstab, otherwise the mount is lost on reboot."
echo "Rollback: systemctl stop docker docker.socket; rm -rf $MNT; mv /var/lib/docker.ext4.bak /var/lib/docker; remove data-root from daemon.json; systemctl start docker"
