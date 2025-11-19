import requests
import hashlib
import argparse

def get_password_leaks_count(response,hashed_password):
    hashes=(line.split(':') for line in response.text.splitlines())
    for hash,count in hashes:
        if hashed_password==hash:
            return count
    return 0

def get_response(password='12345')->int:
    hashed_password=hashlib.sha1(str(password).encode("utf-8")).hexdigest().upper()   
    first5_char,tail=hashed_password[:5],hashed_password[5:]
    url='https://api.pwnedpasswords.com/range/'+str(first5_char)
    res=requests.get(url)
    return int(get_password_leaks_count(res,tail))

def main():
    parser = argparse.ArgumentParser(description="check password safety")
    parser.add_argument("--password", type=str, help="password to check")
    args = parser.parse_args()
    print(get_response(args.password))
if __name__ == '__main__':
    main()
