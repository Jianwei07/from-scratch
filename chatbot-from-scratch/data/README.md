# Harness data

`chat_cases.json` is the shared black-box contract for `POST /chat`.

Each case contains:

- `name`: stable test identifier;
- `request`: JSON body sent to the endpoint;
- `expected_status_code`: required HTTP status;
- `expected_body`: optional response fields that must match.

The harness deliberately checks only stable response fields. It does not compare
the fake model’s full reply text, so wording can change without breaking the API
contract.
