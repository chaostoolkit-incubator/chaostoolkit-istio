# -*- coding: utf-8 -*-
import json
from unittest.mock import ANY, MagicMock, patch

import pytest

from chaosistio.fault.probes import get_virtual_service


@patch("chaosistio.fault.probes.get_virtual_service", autospec=True)
@patch("chaosistio.fault.probes.create_k8s_api_client", autospec=True)
def test_get_virtual_service(client, get_vs):
    content = MagicMock()
    content.read.return_value = '"vs"'
    call_api = MagicMock()
    call_api.return_value = (content, 200, {})
    client.return_value.call_api = call_api

    res = get_virtual_service("mysvc")
    call_api.assert_called_with(
        "/apis/networking.istio.io/v1alpha3/namespaces/default/virtualservices/mysvc",
        "GET",
        header_params={"Accept": "application/json"},
        auth_settings=["BearerToken"],
        _preload_content=False,
    )
