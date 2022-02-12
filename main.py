from TinyURL import TinyURL
import sys

if __name__ == '__main__':
    tiny_url = None
    len_argv = len(sys.argv)
    if len_argv==1:
        tiny_url = TinyURL()
    elif len_argv==3:
        if sys.argv[2].isdigit():
            tiny_url = TinyURL(host=sys.argv[1],port=int(sys.argv[2]))
    
    if not tiny_url:
        print("\n-----------------------------------------------------------------------")
        print("------------------------------| TinyURL |------------------------------")
        print("-----------------------------------------------------------------------")
        print("python ./main.py [host] [port]")
        print("[host](optional): the host for redis server, (default: localhost)")
        print("[port](optional): the port for redis server, (default: 6379)")
        print("-----------------------------------------------------------------------\n")
