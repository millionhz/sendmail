# sendmail
send email with custom headers with python

## Generating DKIM Keys

Private Key:
```bash
openssl genpkey -algorithm RSA -out private.key -pkeyopt rsa_keygen_bits:1024
```

Public Key:
```bash
openssl rsa -in private.key -pubout -out public.key
```
