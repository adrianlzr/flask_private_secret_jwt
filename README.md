# flask_private_secret_jwt
Flask Server for issuing a JWT which can be used as a Bearer Token for Okta's APIs
--------------------------

This Flask server was specifically created to be used by Okta employees / customers. It **should** be considered as a POC, but can be forked and customized / enhanced to satisfy the business needs of any individual. This is **not** an official Okta product, nor is it supported by Okta.


## Getting started

```
pip install -r requirements.txt

python private_secret_jwt.py
```

The server runs by default on port *5000*. To change the port:

```
python private_secret_jwt.py port_number
```
**Note**: The port number must be a integer.

--------------------------

## Usage guide

The server only accepts **POST** HTTP requests. The body must be a valid JSON. 

Attribute | Required | Default value
----------|----------|--------------
client_id | Yes | None
audience | Yes | None
kid | No | str(uuid4())
valid_for | No | 600 seconds (10 minutes)

###  Request Sample:
```
curl --location --request POST 'http://localhost:5000' \
--header 'Content-Type: application/json' \
--data-raw '{
	"client_id":"{{your_client_id}}",
	"audience":"{{base_okta_url}}/oauth2/v1/token"
}'
```

### Response Sample
```
{
    "jwk": {
        "kid": "25c27275-6d6c-42b3-9960-414f1ffaff02",
        "e": "AQAB",
        "n": "wCk23IDTPSiJJQpIKGb46s3Zghm-SW1GWIt2BSvOn8LYw_ZEbaDEbG1A1Y_0CFkZAN_7J0hkJO4MtY6Pc0bbvMCgkzOdJUQblxdfPcr9BRXQ8svmqlbIh11Y2uozUvJdlzSj3OvK0UGTrbxDXRRGCuvk61-3ktZi5s2Ks5HEhB1MynV6tHRD3Z_NqAfYDXC2Ve4aQBvdL4AhUs_ez5qz4s90bfPnWVTHtXFKOXTOPu8P4J02aGSeoG_g8Y_Ama1Eg40SeUPDWiN-Fd6wauDlJiHfZ9B-WsejRzpMRwEHXm58d8fEkHOGLcuUvorPdJaScU2r-_pOimKqYec7zDGjbw"
    },
    "jwt": "eyJ0eXAiOiAiSldUIiwgImFsZyI6ICJSUzI1NiIsICJ1c2UiOiAic2lnIiwgImtpZCI6ICIyNWMyNzI3NS02ZDZjLTQyYjMtOTk2MC00MTRmMWZmYWZmMDIifQ.eyJhdWQiOiAiaHR0cHM6Ly9hZHJpYW4ub2t0YXByZXZpZXcuY29tL29hdXRoMi92MS90b2tlbiIsICJqdGkiOiAiMTM2MmQzZjYtZTliMy00NGFjLWEwZDktYWI4NzA1MTFlNTQ3IiwgImlhdCI6IDE1Nzk3NzU5NTQsICJleHAiOiAxNTc5Nzc2NTU0LCAiaXNzIjogIjBvYXBkOTl4cmZGQ21hRHVWMGg3IiwgInN1YiI6ICIwb2FwZDk5eHJmRkNtYUR1VjBoNyJ9.li7QMEwj6OtmAPPVoitBDNje-_xUGdWvI3cGUQTlYrdQY0FsIqwr-ovBPK-1mSFQGX5lJXcBQIA2WRY-bBOVRuaEeWN8_3exjZl8w6q6xyJBvCvuXHt7EusJ2-16GsqzjsEqwMuovcRhYjxl5TpBkXn79SltepE1mP3Y73JNr19em58Uzxr4Q3Z_qAQ_AFAQ7wvI48pI-wGcFHU5jCBjpJXnM6-0LD5Bnb1BK1WeGJdcNV22Vvrh90n01q3uGMqFuBRD7sHdcb8Su83A6jmbeu4ljv7aeWpdzqChaz3UQyy1Mx4aSAOVV2vgRlOoBPN9l8-dQUs5jXu2_qR8W50Sjg",
    "private_key_changed": true
}
```

**Keep in mind**: 
* If the *kid* (JWT signing key identifier) attribute is not present in the request payload, it will be different for each jwt generated. Only the first request should not include the *kid* so it can be used when creating the Oauth2 application in Okta. Subsequent requests should use the *kid* that was initially generated so it will not be necessary to update the application before each request for a access_token.
* The *valid_for* attribute must be a integer and **must** not be higher than 3600 seconds(1 hour). Okta only accepts a JWT which is valid for maximum 1 hour.
* *"private_key_changed"* will be **true** only when there was no private_key.pem in the root folder, **or** the key was **rotated**. This means that the private_key.pem file was generated and saved on the disk. On subsequent requests, it will be read and used to sign the JWT. 

--------------------------

## Key Rotation

To rotate the key (generate a new private key) that is used to sign the JWT, simply append ?rotate=true to the URL. Once the the key was rotated, make sure to update the Oauth2 application in Okta with the new public exponent *n* and *kid* if it was not present in the request.

###  Request Sample:
```
curl --location --request POST 'http://localhost:5000?rotate=true' \
--header 'Content-Type: application/json' \
--data-raw '{
	"client_id":"{{your_client_id}}",
	"audience":"{{base_okta_url}}/oauth2/v1/token",
	"kid": "25c27275-6d6c-42b3-9960-414f1ffaff02",
	"valid_for":3600
}'
```

### Response Sample:
```
{
    "jwk": {
        "kid": "25c27275-6d6c-42b3-9960-414f1ffaff02",
        "e": "AQAB",
        "n": "28nb32WtjxBIIQVtN-AXYBH6muWIBM6n7pBErsbq5OmWrC4fY0YgQiAgT3AmE72FvuIVa2XIXM-OP0m4pM377Uu_MFxpS--5a8TVx7Wjj-1k-NrVgrB7QXK76STNlg3GmSeHgwmNqc2xzL72lys1J6FQMS2xhUlcCm54F572e1HXpDPeuGtS8V7aSfdp1MUsyvjuMvJU3WG8R6k5qd0XF_dKKp0PObn5WwwWwYzEoHYSS2aUeWMbAUitVVb57JQShwJXdCo7HsTN823n0_9xp6V6Kb1r4aR-lmNBEYYSN_cCWRrCNhDCKk73gJvd3_xVviuPzw0MheUdLTVA5Ws8VQ"
    },
    "jwt": "eyJ0eXAiOiAiSldUIiwgImFsZyI6ICJSUzI1NiIsICJ1c2UiOiAic2lnIiwgImtpZCI6ICIyNWMyNzI3NS02ZDZjLTQyYjMtOTk2MC00MTRmMWZmYWZmMDIifQ.eyJhdWQiOiAiaHR0cHM6Ly9hZHJpYW4ub2t0YXByZXZpZXcuY29tL29hdXRoMi92MS90b2tlbiIsICJqdGkiOiAiNDg5NGY2OWEtMjdkMi00ZTJjLWFjMWQtNjMwNjAwM2EzMGY0IiwgImlhdCI6IDE1Nzk3Nzg2NTQsICJleHAiOiAxNTc5NzgyMjU0LCAiaXNzIjogIjBvYXBkOTl4cmZGQ21hRHVWMGg3IiwgInN1YiI6ICIwb2FwZDk5eHJmRkNtYUR1VjBoNyJ9.sbCwhGe60qpcvRaFqI_boYUzHc0Z_AMRJ4s0V9pp6or_xPQ_bRG9zcQiMT3a5y_IrS4iAXiA-XdRJ-_bJTKCXXx4tsqk7FcKiaUcdvoQG0v05_9WejbV_9mKTzzpgDDIn2gfBCsOqYmYeG63b3zOjU24AMwfZs7UO4awg79YwbNd6vIceTPCGT7b3JJvu9aS7qW5G5lTjLT0hQdYnjYFE4fU12t6jres1rRaVbZ-WQFBzUhsJURCd_iz0Wsdl1bkGX8nsWI0rify7IS4HuEkJAXggkp9posukTZSNWymz10QOBdgaMz9S2gzaRIkrLEdLa9qIQfotkeagZ339YZXWQ",
    "private_key_changed": true
}
```

----------------
## SUGGESTIONS?
Please feel free to email me at adrian.lazar95@outlook.com or lzr.adrian95@gmail.com. I am opened to improvement / suggestions and critics. 