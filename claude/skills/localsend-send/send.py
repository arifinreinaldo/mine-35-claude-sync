#!/usr/bin/env python3
"""Send files to a LocalSend device (protocol v2). Usage: send.py list | send <alias> <file>..."""
import json, mimetypes, os, socket, ssl, sys, urllib.request, uuid
from concurrent.futures import ThreadPoolExecutor

PORT = 53317
CTX = ssl._create_unverified_context()  # LocalSend uses self-signed certs
ME = {"alias": "Mac Claude", "version": "2.0", "deviceModel": "Mac", "deviceType": "desktop",
      "fingerprint": uuid.uuid4().hex, "port": PORT, "protocol": "https", "download": False}


def call(ip, path, body=None, data=None, timeout=3, **kw):
    req = urllib.request.Request(f"https://{ip}:{PORT}/api/localsend/v2/{path}", method="POST",
                                 data=data if data is not None else json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, context=CTX, timeout=timeout) as r:
        raw = r.read()
        return r.status, (json.loads(raw) if raw else None)


def probe(ip):
    try:
        return ip, call(ip, "register", ME, timeout=0.6)[1]["alias"]
    except Exception:
        return None


def devices():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))  # no packet sent; picks the LAN interface
    me = s.getsockname()[0]
    prefix = me.rsplit(".", 1)[0]  # ponytail: assumes /24, widen if the LAN is bigger
    with ThreadPoolExecutor(64) as ex:
        return [d for d in ex.map(probe, [f"{prefix}.{i}" for i in range(1, 255)]) if d and d[0] != me]


def send(alias, paths):
    found = [d for d in devices() if alias.lower() in d[1].lower()]
    if len(found) != 1:
        sys.exit(f"{len(found)} devices match '{alias}': {found}")
    ip = found[0][0]
    files = {}
    for p in paths:
        fid = uuid.uuid4().hex
        files[fid] = {"id": fid, "fileName": os.path.basename(p), "size": os.path.getsize(p),
                      "fileType": mimetypes.guess_type(p)[0] or "application/octet-stream", "_path": p}
    meta = {k: {a: b for a, b in v.items() if a != "_path"} for k, v in files.items()}
    print(f"Waiting for {found[0][1]} to accept...", flush=True)
    status, res = call(ip, "prepare-upload", {"info": ME, "files": meta}, timeout=120)
    if status == 204:
        return print("Nothing to transfer.")
    for fid, token in res["files"].items():
        with open(files[fid]["_path"], "rb") as f:
            call(ip, f"upload?sessionId={res['sessionId']}&fileId={fid}&token={token}",
                 data=f.read(), timeout=600)  # ponytail: whole file in RAM, stream if files get huge
        print("sent", files[fid]["fileName"])


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["list"]:
        for ip, alias in devices():
            print(f"{alias}\t{ip}")
    elif a[:1] == ["send"] and len(a) >= 3:
        send(a[1], a[2:])
    else:
        sys.exit(__doc__)
