# Mojo Perception Python API

Use Mojo Perception API as a Python module for Python applications.


## Installation

If you use `pip`, install mojo-perception-python module:
```
pip install mojoperception
```

## API Key

To use properly the API, you need an API key. Just go get one here : [https://app.mojo.ai/register](https://app.mojo.ai/register)

1. Create an account
2. Create an API Key
3. Follow the steps below to use it in your first app.

## Usage

### `import mojoperception`

```
from mojoperception.mojo_perception_api import MojoPerceptionAPI
```
Create an object MojoPerceptionAPI:
```
mojo_perception = MojoPerceptionAPI('<api_key>')
```
Expiration of MojoPerceptionAPI object is by default 360 seconds. You can set it using "expiration" parameter in constructor.
## Checkout the `Tutorials`

> 💡 &nbsp; Have a look to the tutorials section


## Troubleshooting

> 1️⃣ &nbsp; If you face a `"JsonWebTokenError"`, maybe that's because of the expiration.
> You can try to increase the user token duration to match your need. Default value of 360 seconds might be too short.

## mojo-perception-python Documentation

* [mojo-perception-python Docs & API References](https://docs.mojo.ai)
* [mojo-perception-python Tutorials](https://docs.mojo.ai/facial-expression-recognition/tutorials/create-python-app-with-facial-expression-recognition/)

