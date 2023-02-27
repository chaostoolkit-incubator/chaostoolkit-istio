# -*- coding: utf-8 -*-
import json
from unittest.mock import ANY, MagicMock, patch

import pytest

from chaosistio.fault.actions import (
    add_abort_fault,
    add_delay_fault,
    remove_abort_fault,
    remove_delay_fault,
    set_fault,
    unset_fault,
)


@patch("chaosistio.fault.actions.get_virtual_service", autospec=True)
@patch("chaosistio.fault.actions.create_k8s_api_client", autospec=True)
def test_add_fault_if_route_matches(client, get_vs):
    meta = {"cluster_name": "somevalue"}

    fault = {"delay": {"fixedDelay": "5s", "percentage": {"value": 100.0}}}

    routes = [{"destination": {"host": "localhost", "subset": "v2"}}]

    get_vs.return_value = {
        "status": 200,
        "headers": {},
        "body": {
            "spec": {
                "http": [
                    {
                        "route": [
                            {
                                "destination": {
                                    "host": "localhost",
                                    "subset": "v2",
                                }
                            },
                        ]
                    },
                    {
                        "route": [
                            {
                                "destination": {
                                    "host": "localhost",
                                    "subset": "v1",
                                }
                            },
                            {
                                "destination": {
                                    "host": "otherhost",
                                    "subset": "v1",
                                }
                            },
                            {"destination": {"host": "yetotherhost"}},
                        ]
                    },
                ]
            }
        },
    }

    content = MagicMock()
    content.read.return_value = '"updated"'
    call_api = MagicMock()
    call_api.return_value = (content, 200, {})
    client.return_value.call_api = call_api

    res = set_fault(
        "mysvc",
        routes,
        fault,
        ns="default",
        version="networking.istio.io/v1beta1",
    )
    call_api.assert_called_with(
        "/apis/networking.istio.io/v1beta1/namespaces/default/virtualservices/mysvc",
        "PATCH",
        header_params={
            "Content-Type": "application/merge-patch+json",
            "Accept": "application/json",
        },
        body={
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "VirtualService",
            "metadata": {"name": "mysvc"},
            "spec": {
                "http": [
                    {
                        "route": [
                            {
                                "destination": {
                                    "host": "localhost",
                                    "subset": "v2",
                                }
                            }
                        ],
                        "fault": {
                            "delay": {
                                "fixedDelay": "5s",
                                "percentage": {"value": 100.0},
                            }
                        },
                    },
                    {
                        "route": [
                            {
                                "destination": {
                                    "host": "localhost",
                                    "subset": "v1",
                                }
                            },
                            {
                                "destination": {
                                    "host": "otherhost",
                                    "subset": "v1",
                                }
                            },
                            {"destination": {"host": "yetotherhost"}},
                        ]
                    },
                ]
            },
        },
        auth_settings=["BearerToken"],
        _preload_content=False,
    )


@patch("chaosistio.fault.actions.get_virtual_service", autospec=True)
@patch("chaosistio.fault.actions.create_k8s_api_client", autospec=True)
def test_does_not_add_fault_if_no_route_matches(client, get_vs):
    meta = {"cluster_name": "somevalue"}

    fault = {"delay": {"fixedDelay": "5s", "percentage": {"value": 100.0}}}

    routes = [{"destination": {"host": "localhost", "subset": "v3"}}]

    get_vs.return_value = {
        "status": 200,
        "headers": {},
        "body": {
            "spec": {
                "http": [
                    {
                        "route": [
                            {
                                "destination": {
                                    "host": "localhost",
                                    "subset": "v2",
                                }
                            },
                        ]
                    },
                    {
                        "route": [
                            {
                                "destination": {
                                    "host": "localhost",
                                    "subset": "v1",
                                }
                            },
                            {
                                "destination": {
                                    "host": "otherhost",
                                    "subset": "v1",
                                }
                            },
                        ]
                    },
                ]
            }
        },
    }

    content = MagicMock()
    content.read.return_value = '"updated"'
    call_api = MagicMock()
    call_api.return_value = (content, 200, {})
    client.return_value.call_api = call_api

    res = set_fault(
        "mysvc",
        routes,
        fault,
        ns="default",
        version="networking.istio.io/v1beta1",
    )
    call_api.assert_called_with(
        "/apis/networking.istio.io/v1beta1/namespaces/default/virtualservices/mysvc",
        "PATCH",
        header_params={
            "Content-Type": "application/merge-patch+json",
            "Accept": "application/json",
        },
        body={
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "VirtualService",
            "metadata": {"name": "mysvc"},
            "spec": {
                "http": [
                    {
                        "route": [
                            {
                                "destination": {
                                    "host": "localhost",
                                    "subset": "v2",
                                }
                            }
                        ]
                    },
                    {
                        "route": [
                            {
                                "destination": {
                                    "host": "localhost",
                                    "subset": "v1",
                                }
                            },
                            {
                                "destination": {
                                    "host": "otherhost",
                                    "subset": "v1",
                                }
                            },
                        ]
                    },
                ]
            },
        },
        auth_settings=["BearerToken"],
        _preload_content=False,
    )


@patch("chaosistio.fault.actions.get_virtual_service", autospec=True)
@patch("chaosistio.fault.actions.create_k8s_api_client", autospec=True)
def test_remove_fault_if_route_matches(client, get_vs):
    meta = {"cluster_name": "somevalue"}

    fault = {"delay": {"fixedDelay": "5s", "percentage": {"value": 100.0}}}

    routes = [{"destination": {"host": "localhost", "subset": "v2"}}]

    get_vs.return_value = {
        "status": 200,
        "headers": {},
        "body": {
            "spec": {
                "http": [
                    {
                        "route": [
                            {
                                "destination": {
                                    "host": "localhost",
                                    "subset": "v2",
                                }
                            },
                        ],
                        "fault": {
                            "delay": {
                                "fixedDelay": "5s",
                                "percentage": {"value": 100.0},
                            }
                        },
                    },
                    {
                        "route": [
                            {
                                "destination": {
                                    "host": "localhost",
                                    "subset": "v1",
                                }
                            },
                            {
                                "destination": {
                                    "host": "otherhost",
                                    "subset": "v1",
                                }
                            },
                        ]
                    },
                ]
            }
        },
    }

    content = MagicMock()
    content.read.return_value = '"updated"'
    call_api = MagicMock()
    call_api.return_value = (content, 200, {})
    client.return_value.call_api = call_api

    res = unset_fault(
        "mysvc", routes, ns="default", version="networking.istio.io/v1beta1"
    )
    call_api.assert_called_with(
        "/apis/networking.istio.io/v1beta1/namespaces/default/virtualservices/mysvc",
        "PATCH",
        header_params={
            "Content-Type": "application/merge-patch+json",
            "Accept": "application/json",
        },
        body={
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "VirtualService",
            "metadata": {"name": "mysvc"},
            "spec": {
                "http": [
                    {
                        "route": [
                            {
                                "destination": {
                                    "host": "localhost",
                                    "subset": "v2",
                                }
                            }
                        ]
                    },
                    {
                        "route": [
                            {
                                "destination": {
                                    "host": "localhost",
                                    "subset": "v1",
                                }
                            },
                            {
                                "destination": {
                                    "host": "otherhost",
                                    "subset": "v1",
                                }
                            },
                        ]
                    },
                ]
            },
        },
        auth_settings=["BearerToken"],
        _preload_content=False,
    )


@patch("chaosistio.fault.actions.get_virtual_service", autospec=True)
@patch("chaosistio.fault.actions.create_k8s_api_client", autospec=True)
def test_add_delay_fault(client, get_vs):
    meta = {"cluster_name": "somevalue"}

    routes = [{"destination": {"host": "localhost", "subset": "v2"}}]

    get_vs.return_value = {
        "status": 200,
        "headers": {},
        "body": {
            "spec": {
                "http": [
                    {
                        "route": [
                            {
                                "destination": {
                                    "host": "localhost",
                                    "subset": "v2",
                                }
                            },
                        ]
                    },
                    {
                        "route": [
                            {
                                "destination": {
                                    "host": "localhost",
                                    "subset": "v1",
                                }
                            },
                            {
                                "destination": {
                                    "host": "otherhost",
                                    "subset": "v1",
                                }
                            },
                        ]
                    },
                ]
            }
        },
    }

    content = MagicMock()
    content.read.return_value = '"updated"'
    call_api = MagicMock()
    call_api.return_value = (content, 200, {})
    client.return_value.call_api = call_api

    res = add_delay_fault(
        "mysvc",
        "5s",
        routes,
        percentage=100.0,
        ns="default",
        version="networking.istio.io/v1beta1",
    )
    call_api.assert_called_with(
        "/apis/networking.istio.io/v1beta1/namespaces/default/virtualservices/mysvc",
        "PATCH",
        header_params={
            "Content-Type": "application/merge-patch+json",
            "Accept": "application/json",
        },
        body={
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "VirtualService",
            "metadata": {"name": "mysvc"},
            "spec": {
                "http": [
                    {
                        "route": [
                            {
                                "destination": {
                                    "host": "localhost",
                                    "subset": "v2",
                                }
                            }
                        ],
                        "fault": {
                            "delay": {
                                "fixedDelay": "5s",
                                "percentage": {"value": 100.0},
                            }
                        },
                    },
                    {
                        "route": [
                            {
                                "destination": {
                                    "host": "localhost",
                                    "subset": "v1",
                                }
                            },
                            {
                                "destination": {
                                    "host": "otherhost",
                                    "subset": "v1",
                                }
                            },
                        ]
                    },
                ]
            },
        },
        auth_settings=["BearerToken"],
        _preload_content=False,
    )


@patch("chaosistio.fault.actions.get_virtual_service", autospec=True)
@patch("chaosistio.fault.actions.create_k8s_api_client", autospec=True)
def test_add_abort_fault(client, get_vs):
    meta = {"cluster_name": "somevalue"}

    routes = [{"destination": {"host": "localhost", "subset": "v2"}}]

    get_vs.return_value = {
        "status": 200,
        "headers": {},
        "body": {
            "spec": {
                "http": [
                    {
                        "route": [
                            {
                                "destination": {
                                    "host": "localhost",
                                    "subset": "v2",
                                }
                            },
                        ]
                    },
                    {
                        "route": [
                            {
                                "destination": {
                                    "host": "localhost",
                                    "subset": "v1",
                                }
                            },
                            {
                                "destination": {
                                    "host": "otherhost",
                                    "subset": "v1",
                                }
                            },
                        ]
                    },
                ]
            }
        },
    }

    content = MagicMock()
    content.read.return_value = '"updated"'
    call_api = MagicMock()
    call_api.return_value = (content, 200, {})
    client.return_value.call_api = call_api

    res = add_abort_fault(
        "mysvc",
        404,
        routes,
        percentage=100.0,
        ns="default",
        version="networking.istio.io/v1beta1",
    )
    call_api.assert_called_with(
        "/apis/networking.istio.io/v1beta1/namespaces/default/virtualservices/mysvc",
        "PATCH",
        header_params={
            "Content-Type": "application/merge-patch+json",
            "Accept": "application/json",
        },
        body={
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "VirtualService",
            "metadata": {"name": "mysvc"},
            "spec": {
                "http": [
                    {
                        "route": [
                            {
                                "destination": {
                                    "host": "localhost",
                                    "subset": "v2",
                                }
                            }
                        ],
                        "fault": {
                            "abort": {
                                "httpStatus": 404,
                                "percentage": {"value": 100.0},
                            }
                        },
                    },
                    {
                        "route": [
                            {
                                "destination": {
                                    "host": "localhost",
                                    "subset": "v1",
                                }
                            },
                            {
                                "destination": {
                                    "host": "otherhost",
                                    "subset": "v1",
                                }
                            },
                        ]
                    },
                ]
            },
        },
        auth_settings=["BearerToken"],
        _preload_content=False,
    )
