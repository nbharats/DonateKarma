from itsdangerous import URLSafeTimedSerializer

salt=b'st?"\xfb\x0e\xee\n'

def encrypt(data):
    serializer=URLSafeTimedSerializer('donatekarma')
    serializer.dumps(data,salt=salt)

def decrypt(data):
    serializer=URLSafeTimedSerializer('donatekarma')
    serializer.loads(data,salt=salt)