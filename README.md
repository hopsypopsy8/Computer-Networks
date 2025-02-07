# Computer-Networks

This project implements a multi-threaded chat system using Python 3.9 and sockets. The system supports multiple users communicating over a server and is divided into two scenarios:

## Scenarios

Single-Channel Chat Server: A server that allows multiple users to communicate in a single shared channel.

Multi-Channel Chat Server: An extension of Single Channel, but introduces multiple channels where users can join different chat rooms.

Both scenarios use the same server and client implementation, but they have different configuration files.

## Project Details
Uses Python’s socket and threading libraries.
Implements essential chat functionalities such as message broadcasting, user management, and multi-channel support.

# HOW TO USE:

## Scenario 1
for server:
$ python3 mchatserver.py <configfile_01.txt>

for client:
$ python3 mchatclient.py <port> <username>

Note: Port and number of connections is determined by the config file

## Scenario 2
for server:
$ python3 mchatserver.py <configfile_02.txt>

for client:
$ python3 mchatclient.py <port> <username>

## Client-Side Commands
Clients can enter special commands:
/list – Displays all available channels with their capacity and queue status.
/whisper <username> <message> – Sends a private message to a specific user. If the user is not in the channel, an error is displayed.
/switch <channel_name> – Moves the client to a different channel. If the channel is full, they are queued. If the username already exists in the new channel, the switch fails.

## Server-Side Commands
The server can use the following commands:

/mute <channel_name> <username> <time> – Mutes a user in a channel for a specified duration. Muted users cannot send messages but can still use commands.
/empty <channel_name> – Disconnects all users in the specified channel.





