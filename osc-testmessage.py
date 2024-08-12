import argparse
from pythonosc import udp_client

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--ip", default="127.0.0.1",
      help="The ip of the OSC server")
  parser.add_argument("--port", type=int, default=9002,
      help="The port the OSC server is listening on")
  parser.add_argument("--parameter", default="/avatar/parameters/vrphone_receiver_button",
      help="The OSC parameter to use")
  args = parser.parse_args()

  client = udp_client.SimpleUDPClient(args.ip, args.port)

  for x in range(1):
    print("Send #{} with parameter {}".format(str(x), args.parameter))
    client.send_message(args.parameter, True)
