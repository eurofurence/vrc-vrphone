"""Small example OSC client

This program sends 10 random values between 0.0 and 1.0 to the /filter address,
waiting for 1 seconds between each value.
"""
import argparse
import random
import time

from pythonosc import udp_client


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--ip", default="127.0.0.1",
      help="The ip of the OSC server")
  parser.add_argument("--port", type=int, default=9001,
      help="The port the OSC server is listening on")
  args = parser.parse_args()

  client = udp_client.SimpleUDPClient(args.ip, args.port)

  for x in range(2):
    print("Send #{}".format(str(x)))
    client.send_message("/avatar/parameters/vrphone_receiver_button", True)
    time.sleep(.05)
    client.send_message("/avatar/parameters/vrphone_receiver_button", False)
    time.sleep(2.5)
    client.send_message("/avatar/parameters/vrphone_phonebook_entry_1_button", True)
    time.sleep(.05)
    client.send_message("/avatar/parameters/vrphone_phonebook_entry_1_button", False)
    time.sleep(2.5)
    client.send_message("/avatar/parameters/vrphone_receiver_button", True)
    time.sleep(.05)
    client.send_message("/avatar/parameters/vrphone_receiver_button", False)
    time.sleep(2.5)
    client.send_message("/avatar/parameters/vrphone_phonebook_entry_2_button", True)
    time.sleep(.05)
    client.send_message("/avatar/parameters/vrphone_phonebook_entry_2_button", False)
    time.sleep(2.5)
    client.send_message("/avatar/parameters/vrphone_receiver_button", True)
    time.sleep(.05)
    client.send_message("/avatar/parameters/vrphone_receiver_button", False)
    time.sleep(2.5)
    client.send_message("/avatar/parameters/vrphone_phonebook_entry_3_button", True)
    time.sleep(.05)
    client.send_message("/avatar/parameters/vrphone_phonebook_entry_3_button", False)
    time.sleep(2.5)
    client.send_message("/avatar/parameters/vrphone_receiver_button", True)
    time.sleep(.05)
    client.send_message("/avatar/parameters/vrphone_receiver_button", False)
    time.sleep(2.5)
    client.send_message("/avatar/parameters/vrphone_phonebook_entry_4_button", True)
    time.sleep(.05)
    client.send_message("/avatar/parameters/vrphone_phonebook_entry_4_button", False)
    time.sleep(2.5)
    client.send_message("/avatar/parameters/vrphone_receiver_button", True)
    time.sleep(.05)
    client.send_message("/avatar/parameters/vrphone_receiver_button", False)
    time.sleep(2.5)
    