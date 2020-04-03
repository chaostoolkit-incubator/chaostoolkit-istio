 # Chaos Toolkit Extension for Istio Fault Injection

[![Python versions](https://img.shields.io/pypi/pyversions/chaostoolkit-istio.svg)](https://www.python.org/)


This project is a collection of [actions][] and [probes][], gathered as an
extension to the [Chaos Toolkit][chaostoolkit].

[actions]: http://chaostoolkit.org/reference/api/experiment/#action
[probes]: http://chaostoolkit.org/reference/api/experiment/#probe
[chaostoolkit]: http://chaostoolkit.org

## Install

This package requires Python 3.5+

To be used from your experiment, this package must be installed in the Python
environment where [chaostoolkit][] already lives.

```
$ pip install -U chaostoolkit-istio
```

## Usage

Below is an example of using this extension to inject a delay of 5 seconds to
a specific user.

Note this example can be applied against the
[bookinfo Istio sample application](https://istio.io/docs/examples/bookinfo/).

To run it, simple set the `KUBERNETES_CONTEXT` environment variable to the
target cluster and ensure your local kubeconfig is properly populated for that
context. Set also the `PRODUCT_PAGE_SERVICE_BASE_URL` to the address of the
Istio gateway.

For instance:

```
$ export PRODUCT_PAGE_SERVICE_BASE_URL=$(kubectl get po -l istio=ingressgateway -n istio-system -o 'jsonpath={.items[0].status.hostIP}'):$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.spec.ports[?(@.name=="http2")].nodePort}')
```

```json
{
    "title": "Network latency does not impact our users",
    "description": "Using Istio fault injection capability, let's explore how latency impacts a single user",
    "configuration": {
        "product_page_url": {
            "type": "env",
            "key": "PRODUCT_PAGE_SERVICE_BASE_URL"
        }
    },
    "secrets": {
        "istio": {
            "KUBERNETES_CONTEXT": {
                "type": "env",
                "key": "KUBERNETES_CONTEXT"
            }
        }
    },
    "steady-state-hypothesis": {
        "title": "Our service should respond under 1 second",
        "probes": [
            {
                "type": "probe",
                "name": "sign-in-as-jason",
                "tolerance": 0,
                "provider": {
                    "type": "process",
                    "path": "curl",
                    "arguments": "-v -X POST -d 'username=jason&passwd=' -c /tmp/cookie.txt --silent ${product_page_url}/login"
                }
            },
            {
                "type": "probe",
                "name": "fetch-productpage-for-jason-in-due-time",
                "tolerance": 0,
                "provider": {
                    "type": "process",
                    "path": "curl",
                    "arguments": "-v --connect-timeout 1 --max-time 1 -b /tmp/cookie.txt --silent ${product_page_url}/productpage"
                }
            }
        ]
    },
    "method": [
        {
            "type": "action",
            "name": "inject-fault-for-jason-only",
            "provider": {
                "type": "python",
                "module": "chaosistio.fault.actions",
                "func": "add_delay_fault",
                "secrets": ["istio"],
                "arguments": {
                    "virtual_service_name": "reviews",
                    "fixed_delay": "5s",
                    "percentage": {
                        "value":  100.0
                    },
                    "routes": [
                        {
                            "destination": {
                                "host": "reviews",
                                "subset": "v2"
                            }
                        }
                    ]
                }
            },
            "pauses": {
                "after": 2
            }
        }
    ],
    "rollbacks": [
        {
            "type": "action",
            "name": "remove-fault-for-jason-only",
            "provider": {
                "type": "python",
                "module": "chaosistio.fault.actions",
                "func": "remove_delay_fault",
                "secrets": ["istio"],
                "arguments": {
                    "virtual_service_name": "reviews",
                    "routes": [
                        {
                            "destination": {
                                "host": "reviews",
                                "subset": "v2"
                            }
                        }
                    ]
                }
            }
        }
    ]
}
```

That's it!

Please explore the code to see existing probes and actions.

## Configuration

This extension needs you specify how to connect to the Kubernetes cluster. This
can be done by setting the `KUBERNETES_CONTEXT` in the `secrets` payload.


## Contribute

If you wish to contribute more functions to this package, you are more than
welcome to do so. Please, fork this project, make your changes following the
usual [PEP 8][pep8] code style, sprinkling with tests and submit a PR for
review.

[pep8]: https://pycodestyle.readthedocs.io/en/latest/

The Chaos Toolkit projects require all contributors must sign a
[Developer Certificate of Origin][dco] on each commit they would like to merge
into the master branch of the repository. Please, make sure you can abide by
the rules of the DCO before submitting a PR.

[dco]: https://github.com/probot/dco#how-it-works

### Develop

If you wish to develop on this project, make sure to install the development
dependencies. But first, [create a virtual environment][venv] and then install
those dependencies.

[venv]: http://chaostoolkit.org/reference/usage/install/#create-a-virtual-environment

```console
$ pip install -r requirements-dev.txt -r requirements.txt
```

Then, point your environment to this directory:

```console
$ python setup.py develop
```

Now, you can edit the files and they will be automatically be seen by your
environment, even when running from the `chaos` command locally.

### Test

To run the tests for the project execute the following:

```
$ pytest
```
