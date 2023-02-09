import longhorn
import os
import requests
from kubernetes import client, config
from kubernetes.client import Configuration
from kubernetes.client.api import core_v1_api
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream


config.load_incluster_config() # change this to load_incluster_config()
v1 = client.CoreV1Api()
try:
    c = Configuration().get_default_copy()
except AttributeError:
    c = Configuration()
    c.assert_hostname = False
Configuration.set_default(c)
core_v1 = core_v1_api.CoreV1Api()

longhorn_url = os.getenv("longhorn_url", "http://longhorn-frontend.longhorn-system.svc.cluster.local/v1")
longhorn_ns = os.getenv("longhorn_namespace", "longhorn-system")

lh_client = longhorn.Client(url=longhorn_url)

def pod_exec(name, namespace, command, api_client):
    resp = stream(api_client.connect_get_namespaced_pod_exec, name, namespace, command=command, stderr=True, stdout=True, tty=False, stdin=False)

    print(resp)

def trim_fs_api(volume_name):
    print(f"Trimming {volume_name}")
    requests.post(longhorn_url+f"/volumes/{volume_name}?action=trimFilesystem")

def trim_fs_rwx(volume_name):
    manager = f"share-manager-{volume_name}"
    path = f"/export/{volume_name}"
    print(f"Trimming {volume_name}")
    pod_exec(manager, longhorn_ns, ["fstrim", path], core_v1)

if __name__ == "__main__":
    volumes = lh_client.list_volume()
    for volume in volumes:
        if volume.state != "attached":
            continue
        if volume.accessMode == 'rwo':
            trim_fs_api(volume.name)
        else:
            trim_fs_rwx(volume.name)

