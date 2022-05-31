from pprint import pprint

from kubernetes import client, config, watch

GROUP = "test.group"
VERSION = "v1"
PLURAL = "samples"
NAMESPACE = "default"

config.load_kube_config()
crds = client.CustomObjectsApi()
resource_version = ""

while True:
    print("initializing stream")
    stream = watch.Watch().stream(crds.list_cluster_custom_object,
                                  GROUP, VERSION, PLURAL,
                                  resource_version=resource_version)

    for event in stream:

        a = crds.list_namespaced_custom_object(GROUP, VERSION, NAMESPACE, PLURAL)

        event_type = event["type"]
        if event_type == "ADDED" or event_type == "MODIFIED":
            event_object = event["object"]
            event_metadata = event_object['metadata']
            event_name = event_metadata["name"]
            event_spec = event_object['spec']

            print("-------------------------------------")
            print("type:", event_type)
            print("-------------------------------------")
            print("object:")
            pprint(event_object)
            print("-------------------------------------")

            # Configure where to resume streaming.

            if event_metadata['resourceVersion'] is not None:
                resource_version = event_metadata['resourceVersion']
                print("resource_version:", resource_version)
                print("-------------------------------------")

            event_object['status']['progressStatus'] = "DONE"
            print("-------------------------------------")
            print(event_object)
            print("-------------------------------------")
            print(event_name)
            print("-------------------------------------")

            update_result = crds.patch_namespaced_custom_object(GROUP, VERSION, NAMESPACE,  PLURAL, event_name, event_object)
            print(update_result)