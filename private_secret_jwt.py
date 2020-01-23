from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding, utils
from json import dumps, loads, JSONDecodeError
from flask import Flask, request
from uuid import uuid4 
from time import time
import codecs
import sys

def int_to_hex_to_b64_url_safe(integer):

    hex_string = hex(integer)
    if len(hex_string) % 2 != 0:
        hex_string = hex_string[2:len(hex_string)]
        hex_string = "0"+hex_string
    else:
        hex_string = hex_string[2:len(hex_string)]
    return codecs.encode(codecs.decode(hex_string, 'hex'), 'base64').decode().replace("+", "-").replace("/", "_").replace("=", "").replace("\n", "")

def generate_private_key():

    prv_k = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )   

    pub_k = prv_k.public_key()  

    private_key = prv_k.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ).decode()  

    with open("private_key.pem", "w") as f:
        f.write(private_key)
    
    return prv_k

def load_private_key():

    with open("private_key.pem", "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    return private_key



def generate_jwk_and_jwt(client_id, audience, kid, valid_for, rotate):

    private_key_changed = False
    if rotate is True:
        print(rotate)
        private_key = generate_private_key()
        private_key_changed = True
    else:
        try:
            private_key = load_private_key()
        except FileNotFoundError:
            private_key_changed = True
            private_key = generate_private_key()

    numbers = private_key.private_numbers()

    e = numbers.public_numbers.e
    n = numbers.public_numbers.n

    url_safe_e = int_to_hex_to_b64_url_safe(e)
    url_safe_n = int_to_hex_to_b64_url_safe(n)

    kid = kid
    client_id = client_id
    audience = audience
    jti = str(uuid4())
    iat = int(time())
    exp = iat + int(valid_for) # By default, it is valid for 5 minutes (300 seconds).
    kid = kid

    header = {
        "typ":"JWT",
        "alg":"RS256",
        "use": "sig",
        "kid": kid
    }

    payload = {
        "aud":audience,
        "jti":jti,
        "iat":iat,
        "exp":exp,
        "iss":client_id,
        "sub":client_id
    }

    b64_header = codecs.encode(bytes(dumps(header).encode()), 'base64').decode().replace("+", "-").replace("/", "_").replace("=", "").replace("\n", "")
    b64_payload = codecs.encode(bytes(dumps(payload).encode()), 'base64').decode().replace("+", "-").replace("/", "_").replace("=", "").replace("\n", "")
    message = f"{b64_header}.{b64_payload}"

    chosen_hash = hashes.SHA256()
    hasher = hashes.Hash(chosen_hash, default_backend())
    hasher.update(bytes(message.encode()))
    digest = hasher.finalize()
    signature = private_key.sign(
        digest,
        padding.PKCS1v15(),
        utils.Prehashed(chosen_hash)
    )

    signature = codecs.encode(signature, 'base64').decode().replace("+", "-").replace("/", "_").replace("=", "").replace("\n", "")
    jwt = f"{message}.{signature}"

    response = {
        "jwk": {
            "kid": kid,
            "e": url_safe_e,
            "n": url_safe_n
        },
        "jwt": jwt,
        "private_key_changed":private_key_changed
        
    }

    return dumps(response)


def validate_payload(client_id, audience, valid_for):

    if audience is None and client_id is None:
        return dumps({"Error":"audience and client_id are mandatory!"})

    if client_id is None:
        return dumps({"Error":"client_id is mandatory!"})

    if audience is None:
        return dumps({"Error":"audience is mandatory!"})
   
    if not isinstance(valid_for, int):
        return dumps({"Error":"valid_for must be a integer!"})
    if valid_for > 3600:
        return dumps({"Error":"valid_for must not be higher than 3600 seconds (1 hour)!"})

    return "Valid"

app = Flask(__name__)

@app.route("/", methods=["POST"])
def jwk_and_jwt():

    try:
        payload = loads(request.data)
    except JSONDecodeError:
        return app.response_class(
            response = dumps({"Error":"Invalid JSON request body. Check the integrity of the data."}),
            status = 400,
            mimetype = "application/json"
        )
    is_rotate = str(request.args.get("rotate")).lower()
    rotate = ((lambda: False, lambda: True)[is_rotate == "true"]()) ## if is_rotate is set to True, a new private key will be generated

    client_id = payload.get("client_id")
    audience = payload.get("audience")
    kid = payload.get("kid") or str(uuid4())
    valid_for = payload.get("valid_for") or 600 ## default value of 600 seconds ( 10 minutes ).

    is_payload_valid = validate_payload(client_id, audience, valid_for)
    if "Error" in is_payload_valid:
        return app.response_class(
            response = is_payload_valid,
            status = 400,
            mimetype = "application/json"
        )

    response = generate_jwk_and_jwt(client_id, audience, kid, valid_for, rotate)
    return app.response_class(
        response = response,
        status = 200,
        mimetype = "application/json"
    )

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            raise Exception("Port must be a integer!")
    else:
        port=5000
    app.run(debug=True, port=port)