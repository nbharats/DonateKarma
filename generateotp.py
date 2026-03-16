import random
import string

def generateotp():
    uc=string.ascii_uppercase
    lc=string.ascii_lowercase
    numbers=random.randrange(0,10)
    otp=[]
    for i in range(2):
        otp.append(random.choice(uc))
        otp.append(str(random.randrange(0,10)))
        otp.append(random.choice(lc))
    random.shuffle(otp)
    return ''.join(otp)
<<<<<<< HEAD


=======
>>>>>>> 0a453d5fefa3863992b61d2817e0c5a995ca7fdb
