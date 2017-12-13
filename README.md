# Waisse - API client with magic

Waisse is an API client that can wrap your API and create user friendly methods to interact with it.
You can describe your API in JSON (for now only JSON is supported)
After the client is initialized methods are created dinamically from the configuration.

Describe endpoints in your config, you must declare the following attributes:
  - `uri` _string_
  - `methods`_array ["string", "string", ...]_
  - `aliases` _array [{"method": "alias"}, ...]_
  - `authorization` _true|false_
  - `payload` _true|false_

### URI
The uri of the endpoint e.g. `login` (do not prepend slash)

### METHODS
An array of methods allowed for the endpoint e.g. `["post", "get"]`

### ALIASES
The general rule is to create a method called `action_uri` where action is a 1:1 map between the request method and
a defined action, for example `post` will map to `create`, `get` to read etc.

So if you declare a uri `pets` without an alias, the client will create a method called `create_pets`.

If you want to override this behaviour you can do that per method. Let's say we want a `post` to `pets` to be called
`add_new_pet` instead of `create_pets` you have to declare `"aliases": [{"post": "add_new_pet"}]`

### AUTHORIZATION
Wheter or not you must provide credentials to call an endpoint

### PAYLOAD
Wheter or not you have to pass a payload for the given method


## USAGE (DISCLAIMER: PYTHON 3 ONLY)

```Python
from waisse.client import APIClient

client = APIClient(config='path/to/your/config.json')
client.login({your_payload_here})
```