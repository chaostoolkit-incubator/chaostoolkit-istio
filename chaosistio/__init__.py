# -*- coding: utf-8 -*-
import os
import os.path
from typing import List

from chaoslib.discovery.discover import discover_actions, discover_probes, \
    initialize_discovery_result
from chaoslib.types import Configuration, Discovery, DiscoveredActivities, \
    Secrets
from kubernetes import client, config
from logzero import logger


__all__ = ["create_k8s_api_client", "discover", "__version__"]
__version__ = '0.1.5'


def has_local_config_file():
    config_path = os.path.expanduser(
        os.environ.get('KUBECONFIG', '~/.kube/config'))
    return os.path.exists(config_path)


def create_k8s_api_client(configuration: Configuration,
                          secrets: Secrets = None) -> client.ApiClient:
    """
    Create a Kubernetes client from:

    1. From a local configuration file if it exists (`~/.kube/config`). You
       can specify which context you want to use as well through the
       `KUBERNETES_CONTEXT` key in the environment or in the `secrets` object.
    2. From the cluster configuration if executed from a Kubernetes pod and
       the CHAOSTOOLKIT_IN_POD is set to `"true"`.
    3. From a mix of the following environment keys:

        * KUBERNETES_HOST: Kubernetes API address

        You can authenticate with a token via:
        * KUBERNETES_API_KEY: the API key to authenticate with
        * KUBERNETES_API_KEY_PREFIX: the key kind, if not set, defaults to
          "Bearer"

        Or via a username/password:
        * KUBERNETES_USERNAME
        * KUBERNETES_PASSWORD

        Or via SSL:
        * KUBERNETES_CERT_FILE
        * KUBERNETES_KEY_FILE

        Finally, you may disable SSL verification against HTTPS endpoints:
        * KUBERNETES_VERIFY_SSL: should we verify the SSL (unset means no)
        * KUBERNETES_CA_CERT_FILE: path the CA certificate when verification is
          expected

        You may pass a secrets dictionary, in which case, values will be looked
        there before the environ.
    """
    env = os.environ
    secrets = secrets or {}

    def lookup(k: str, d: str = None) -> str:
        return secrets.get(k, env.get(k, d))

    if has_local_config_file():
        context = lookup("KUBERNETES_CONTEXT")
        logger.debug("Using Kubernetes context: {}".format(
            context or "default"))
        return config.new_client_from_config(context=context)

    elif env.get("CHAOSTOOLKIT_IN_POD") == "true":
        config.load_incluster_config()
        return client.ApiClient()

    else:
        cfg = client.Configuration()
        cfg.debug = True
        cfg.host = lookup("KUBERNETES_HOST", "http://localhost")
        cfg.verify_ssl = lookup(
            "KUBERNETES_VERIFY_SSL", False) is not False
        cfg.cert_file = lookup("KUBERNETES_CA_CERT_FILE")

        if "KUBERNETES_API_KEY" in env or "KUBERNETES_API_KEY" in secrets:
            cfg.api_key['authorization'] = lookup(
                "KUBERNETES_API_KEY")
            cfg.api_key_prefix['authorization'] = lookup(
                "KUBERNETES_API_KEY_PREFIX", "Bearer")
        elif "KUBERNETES_CERT_FILE" in env or \
                "KUBERNETES_CERT_FILE" in secrets:
            cfg.cert_file = lookup("KUBERNETES_CERT_FILE")
            cfg.key_file = lookup("KUBERNETES_KEY_FILE")
        elif "KUBERNETES_USERNAME" in env or "KUBERNETES_USERNAME" in secrets:
            cfg.username = lookup("KUBERNETES_USERNAME")
            cfg.password = lookup("KUBERNETES_PASSWORD", "")

    return client.ApiClient(cfg)


def discover(discover_system: bool = True) -> Discovery:
    """
    Discover Istio capabilities offered by this extension.
    """
    logger.info("Discovering capabilities from chaostoolkit-istio")

    discovery = initialize_discovery_result(
        "chaostoolkit-istio", __version__, "istio")
    discovery["activities"].extend(load_exported_activities())
    return discovery


###############################################################################
# Private functions
###############################################################################
def load_exported_activities() -> List[DiscoveredActivities]:
    """
    Extract metadata from actions and probes exposed by this extension.
    """
    activities = []
    activities.extend(discover_actions("chaosistio.fault.actions"))
    activities.extend(discover_probes("chaosistio.fault.probes"))
    return activities
