# -*- coding: utf-8 -*-
from copy import deepcopy
from typing import Any, Dict, List

from chaoslib.exceptions import ActivityFailed
from chaoslib.types import Configuration, Secrets
from kubernetes.client.rest import ApiException
import simplejson as json

from chaosistio import create_k8s_api_client
from chaosistio.fault.probes import get_virtual_service

__all__ = ["set_fault", "add_delay_fault", "add_abort_fault",
           "unset_fault", "remove_delay_fault", "remove_abort_fault"]


def set_fault(virtual_service_name: str, routes: List[Dict[str, str]],  # noqa: C901
              fault: Dict[str, Any], ns: str = "default",
              version: str = "networking.istio.io/v1alpha3",
              configuration: Configuration = None,
              secrets: Secrets = None) -> Dict[str, Any]:
    """
    Setfault injection on the virtual service identified by `name`

    The `fault` argument must be the object passed as the `spec` property
    of a virtual service resource.

    If a fault already exists, it is updated with the new specification.

    See https://istio.io/docs/reference/config/istio.networking.v1alpha3/#HTTPFaultInjection
    """  # noqa: E501
    result = get_virtual_service(
        virtual_service_name, ns=ns, version=version,
        configuration=configuration, secrets=secrets)
    if result["status"] != 200:
        raise ActivityFailed("Virtual Service '{}' does not exist: {}".format(
            virtual_service_name, str(result["body"])))

    # which destinations to we target?
    expected_destinations = set()
    for route in routes:
        if "destination" in route:
            destination = route["destination"]
            expected_destinations.add(
                (destination["host"], destination.get("subset")))

    # inject a fault block into the targets
    spec = deepcopy(result["body"]["spec"]["http"])
    for i in spec:
        if "route" in i:
            for route in i["route"]:
                if "destination" in route:
                    destination = route["destination"]
                    # not mandatory in response
                    # https://istio.io/latest/docs/reference/config/networking/virtual-service/#Destination  # noqa: E501
                    target = (destination["host"], destination.get("subset"))
                    if target in expected_destinations:
                        i["fault"] = fault
                        break

    api = create_k8s_api_client(configuration, secrets)

    url = "/apis/{}/namespaces/{}/virtualservices/{}".format(
        version, ns, virtual_service_name)
    payload = {
        "apiVersion": version,
        "kind": "VirtualService",
        "metadata": {
            "name": virtual_service_name
        },
        "spec": {"http": spec}
    }

    try:
        data, status, headers = api.call_api(
            url,
            "PATCH",
            header_params={
                "Content-Type": "application/merge-patch+json",
                "Accept": "application/json"
            },
            body=payload,
            auth_settings=['BearerToken'],
            _preload_content=False
        )
    except ApiException as x:
        body = x.body
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


def unset_fault(virtual_service_name: str, routes: List[Dict[str, str]],  # noqa: C901
                ns: str = "default",
                version: str = "networking.istio.io/v1alpha3",
                configuration: Configuration = None,
                secrets: Secrets = None) -> Dict[str, Any]:
    """
    Unset fault injection from the virtual service identified by `name`

    The `fault` argument must be the object passed as the `spec` property
    of a virtual service resource.

    See https://istio.io/docs/reference/config/istio.networking.v1alpha3/#HTTPFaultInjection
    """  # noqa: E501
    result = get_virtual_service(
        virtual_service_name, ns=ns, version=version,
        configuration=configuration, secrets=secrets)
    if result["status"] != 200:
        raise ActivityFailed("Virtual Service '{}' does not exist: {}".format(
            virtual_service_name, str(result["body"])))

    # which destinations to we target?
    expected_destinations = set()
    for route in routes:
        if "destination" in route:
            destination = route["destination"]
            expected_destinations.add(
                (destination["host"], destination.get("subset")))

    # remove fault block from the targets
    spec = deepcopy(result["body"]["spec"]["http"])
    for i in spec:
        if "route" in i:
            for route in i["route"]:
                if "destination" in route:
                    destination = route["destination"]
                    target = (destination["host"], destination.get("subset"))
                    if target in expected_destinations:
                        i.pop("fault", None)

    api = create_k8s_api_client(configuration, secrets)

    url = "/apis/{}/namespaces/{}/virtualservices/{}".format(
        version, ns, virtual_service_name)
    payload = {
        "apiVersion": version,
        "kind": "VirtualService",
        "metadata": {
            "name": virtual_service_name
        },
        "spec": {"http": spec}
    }

    try:
        data, status, headers = api.call_api(
            url,
            "PATCH",
            header_params={
                "Content-Type": "application/merge-patch+json",
                "Accept": "application/json"
            },
            body=payload,
            auth_settings=['BearerToken'],
            _preload_content=False
        )
    except ApiException as x:
        body = x.body
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


def add_delay_fault(virtual_service_name: str, fixed_delay: str,
                    routes: List[Dict[str, str]],
                    percentage: float = None, ns: str = "default",
                    version: str = "networking.istio.io/v1alpha3",
                    configuration: Configuration = None,
                    secrets: Secrets = None) -> Dict[str, Any]:
    """
    Add delay to the virtual service identified by `name`

    See https://istio.io/docs/reference/config/istio.networking.v1alpha3/#HTTPFaultInjection-Delay
    """  # noqa: E501
    fault = {
        "delay": {
            "fixedDelay": fixed_delay
        }
    }
    if percentage is not None:
        fault["delay"]["percentage"] = {}
        fault["delay"]["percentage"]["value"] = percentage

    return set_fault(
        virtual_service_name, fault=fault, ns=ns, configuration=configuration,
        secrets=secrets, routes=routes, version=version
    )


def add_abort_fault(virtual_service_name: str, http_status: int,
                    routes: List[Dict[str, str]],
                    percentage: float = None, ns: str = "default",
                    version: str = "networking.istio.io/v1alpha3",
                    configuration: Configuration = None,
                    secrets: Secrets = None) -> Dict[str, Any]:
    """
    Abort requests early by the virtual service identified by `name`

    See https://istio.io/docs/reference/config/istio.networking.v1alpha3/#HTTPFaultInjection-Abort
    """  # noqa: E501
    fault = {
        "abort": {
            "httpStatus": http_status
        }
    }
    if percentage is not None:
        fault["abort"]["percentage"] = {}
        fault["abort"]["percentage"]["value"] = percentage

    return set_fault(
        virtual_service_name, fault=fault, ns=ns, configuration=configuration,
        secrets=secrets, routes=routes, version=version
    )


def remove_delay_fault(virtual_service_name: str,
                       routes: List[Dict[str, str]],
                       ns: str = "default",
                       version: str = "networking.istio.io/v1alpha3",
                       configuration: Configuration = None,
                       secrets: Secrets = None) -> Dict[str, Any]:
    """
    Remove delay from the virtual service identified by `name`

    See https://istio.io/docs/reference/config/istio.networking.v1alpha3/#HTTPFaultInjection-Delay
    """  # noqa: E501
    return unset_fault(
        virtual_service_name, ns=ns, configuration=configuration,
        secrets=secrets, routes=routes, version=version
    )


def remove_abort_fault(virtual_service_name: str,
                       routes: List[Dict[str, str]], ns: str = "default",
                       version: str = "networking.istio.io/v1alpha3",
                       configuration: Configuration = None,
                       secrets: Secrets = None) -> Dict[str, Any]:
    """
    Remove abort request faults from the virtual service identified by `name`

    See https://istio.io/docs/reference/config/istio.networking.v1alpha3/#HTTPFaultInjection-Abort
    """  # noqa: E501
    return unset_fault(
        virtual_service_name, ns=ns, configuration=configuration,
        secrets=secrets, routes=routes, version=version
    )
