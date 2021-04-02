from OpenSSL import crypto
import base64

def sign(p12_b64_cert, p12_passphrase, signed_text):
    p12 = crypto.load_pkcs12(base64.b64decode(p12_b64_cert), p12_passphrase.encode())
    signcert = p12.get_certificate()
    pkey = p12.get_privatekey()

    bio_in = crypto._new_mem_buf(signed_text.encode('utf8'))
    pkcs7 = crypto._lib.PKCS7_sign(
        signcert._x509, 
        pkey._pkey,
        crypto._ffi.NULL,
        bio_in, 
        crypto._lib.PKCS7_NOATTR | crypto._lib.PKCS7_NOSMIMECAP | crypto._lib.PKCS7_PARTIAL)
    
    signer_info = crypto._lib.PKCS7_sign_add_signer(
        pkcs7,
        signcert._x509,
        pkey._pkey,
        crypto._lib.EVP_get_digestbyname(b'sha1'),
        0
    )

    crypto._lib.PKCS7_final(pkcs7, bio_in, 0)
    
    bio_out = crypto._new_mem_buf()

    #crypto._lib.PEM_write_bio_PKCS7(bio_out, pkcs7)
    #sigbytes = crypto._bio_to_string(bio_out)
    
    crypto._lib.i2d_PKCS7_bio(bio_out, pkcs7)
    sigbytes = crypto._bio_to_string(bio_out)
    signed_data = base64.b64encode(sigbytes)
    
    verified = crypto._lib.PKCS7_verify(pkcs7, crypto._ffi.NULL, crypto._ffi.NULL,
                            crypto._ffi.NULL, bio_out, crypto._lib.PKCS7_NOVERIFY)
    
    return verified, signed_data

if __name__ == "__main__":
    pass
