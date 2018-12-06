# -*- coding: utf-8 -*-
from typing import Any, Dict, List

from chaoslib.types import Configuration, Secrets
from kubernetes import client
from kubernetes.client.rest import ApiException
from logzero import logger
import simplejson as json

from chaosistio import create_k8s_api_client

__all__ = ["get_virtual_service"]


def get_virtual_service(virtual_service_name: str, ns: str = "default",
                        version: str = "networking.istio.io/v1alpha3",
                        configuration: Configuration = None,
                        secrets: Secrets = None) -> Dict[str, Any]:
    """
    Get a virtual service identified by `name`

    See https://istio.io/docs/reference/config/istio.networking.v1alpha3/#VirtualService
    """  # noqa: E501
    api = create_k8s_api_client(configuration, secrets)
    url = "/apis/{}/namespaces/{}/virtualservices/{}".format(
        version, ns, virtual_service_name)

    try:
        data, status, headers = api.call_api(
            url,
            "GET",
            header_params={
                "Accept": "application/json"
            },
            auth_settings=['BearerToken'],
            _preload_content=False
        )
    except ApiException as x:
        body = x.body.read(decode_content=True)
        if x.headers.get("Content-Type") == "application/json":
            body = json.loads(body)
        return {
            "status": x.status,
            "body": body,
            "headers": dict(**x.headers)
        }

    return {
        "status": status,
        "body": json.loads(data.read(decode_content=True)),
        "headers": dict(**headers)
    }
