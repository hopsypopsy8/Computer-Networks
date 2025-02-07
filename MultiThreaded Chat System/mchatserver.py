import socket
import threading
import sys
import time
import queue
import os


class Client:
    def __init__(self, username, connection, address):
        self.username = username
        self.connection = connection
        self.address = address
        self.kicked = False
        self.in_queue = True
        self.remaining_time = 100 # remaining time before AFK
        self.muted = False
        self.mute_duration = 0


class Channel:
    def __init__(self, name, port, capacity):
        self.name = name
        self.port = port
        self.capacity = capacity
        self.queue = queue.Queue()
        self.clients = []

def all_client_msg(channel, msg):
    for client in channel.clients:
        client.connection.send(msg.encode())


def parse_config(config_file: str) -> list:
    """
    Parses lines from a given configuration file and VALIDATE the format of each line. The 
    function validates each part and if valid returns a list of tuples where each tuple contains
    (channel_name, channel_port, channel_capacity). The function also ensures that there are no 
    duplicate channel names or ports. if not valid, exit with status code 1.
    Status: TODO
    Args:
        config_file (str): The path to the configuration file (e.g, config_01.txt).
    Returns:
        list: A list of tuples where each tuple contains:
        (channel_name, channel_port, and channel_capacity)
    Raises:
        SystemExit: If there is an error in the configuration file format.
    """
    # Write your code here... still no done
    ports = {}
    name = {}
    f = open(config_file, "r")
    #list of all lines with \n on it!
    content = f.readlines()
    #checks for at least 1 or 3+ channels to satisfy both conditions
    if len(content) < 1 or len(content) == 2:
        raise(SystemExit)
    #list send with channels
    final_list = []
    #check each line in channel list
    for line in content:
        #split the line at the space somehow the \n was removed idk
        values = line.split()
        #check len of values to make sure correct amount of args provided
        if len(values) != 4:
            raise(SystemExit)
        
        temp = []

        #checks for no numbers or special characters
        if values[1].isalpha() == False:
            raise(SystemExit)

        #check for name
        #O(1) lookup in if it exists lolz
        if values[1] == name.get(values[1]):
            raise(SystemExit)
        name[values[1]] = values[1]
        temp.append(values[1])

        #checks for valid port
        if int(values[2]) < 1 or int(values[2]) > 49151: 
            raise(SystemExit)
        
        #O(1) lookup in if it exists lolz
        if values[2] == ports.get(values[2]):
            raise(SystemExit)
        ports[values[2]] = values[2]
        temp.append(int(values[2]))

        #valid length of channel capacity
        if int(values[3]) > 5 or int(values[3]) < 1:            
            #print("exit3")
            raise(SystemExit)
        temp.append(int(values[3]))
        tup = tuple(temp)
        final_list.append(tup)

    return final_list
    

def get_channels_dictionary(parsed_lines) -> dict:
    """
    Creates a dictionary of Channel objects from parsed lines.
    Status: Given
    Args:
        parsed_lines (list): A list of tuples where each tuple contains:
        (channel_name, channel_port, and channel_capacity)
    Returns:
        dict: A dictionary of Channel objects where the key is the channel name.
    """
    channels = {}

    for channel_name, channel_port, channel_capacity in parsed_lines:
        channels[channel_name] = Channel(channel_name, channel_port, channel_capacity)

    return channels

def quit_client(client, channel) -> None:
    """
    Implement client quitting function
    Status: TODO
    """
    # if client is in queue
    if client.in_queue:
        # Write your code here...
        # remove, close connection, and print quit message in the server.
        temp_queue = channel.queue
        while not channel.queue.empty():
            qclient = channel.queue.get()
            if qclient != client:
                temp_queue.put(qclient)
        channel.queue = temp_queue

        client.connection.close()
        print(f"[Server message ({time.strftime('%H:%M:%S')})] {client.username} has left the channel.")
        # broadcast queue update message to all the clients in the queue.
        for x in range(len(channel.queue)):
            queuecast = f"[Server message ({time.strftime('%H:%M:%S')})] You are in the waiting queue and there are {x} user(s) ahead of you."
            channel.queue[x].connection.send(queuecast.encode()) 
    # if client is in channel
    else:
        if client in channel.clients:
            channel.clients.remove(client)
            client.connection.close()
        # Write your code here...
        # remove client from the channel, close connection, and broadcast quit message to all clients.
        msg = f"[Server message ({time.strftime('%H:%M:%S')})] {client.username} has left the channel."
        print(msg)
        for clients in channel.clients:
            clients.connection.send(msg.encode())
      

def send_client(client, channel, msg) -> None:
    """
    Implement file sending function, if args for /send are valid.
    Else print appropriate message and return.
    Status: TODO
    """
    # Write your code here...
    # if in queue, do nothing
    if client.in_queue:
        return
    else:
        # if muted, send mute message to the client
        if client.muted:
            mute_msg = f"[Server message ({time.strftime('%H:%M:%S')})] You are still muted for {client.mute_duration} seconds"
            client.connection.send(mute_msg.encode())

        # if not muted, process the file sending
        else:
            # validate the command structure
            msg_parts = msg.split()
            target = msg_parts[1]
            filepath = msg_parts[2]
            # check for target existance
            target_client = None
            for clients in channel.clients:
                if target == clients.username:
                    target_client = clients
            
            if target_client is None:
                msg = f"[Server message ({time.strftime('%H:%M:%S')})] {target} is not here."
                client.connection.send(msg.encode())
            # check for file existence
            if not os.path.isfile(filepath):
                msg = f"[Server message ({time.strftime('%H:%M:%S')})] {filepath} does not exist."
                client.connection.send(msg.encode())
            # check if receiver is in the channel, and send the file
            if target_client in channel.clients:
                file_msg = f"[Server message ({time.strftime('%H:%M:%S')})] {client.username} sent {filepath} to {target}."
                sender_msg = f"[Server message ({time.strftime('%H:%M:%S')})] You sent {filepath} to {target}."
                print(file_msg)
                #send stuff to client
                client.connection.send(sender_msg.encode())
                target_client.connection.send(f"/FILE: {filepath}".encode())
                file = open(filepath, 'r')
                target_client.connection.send(file.read().encode())
                file.close()

def list_clients(client, channels) -> None:
    """
    List all channels and their capacity
    Status: TODO
    """
    # Write your code here...
    for channel_name, channel in channels.items():
        msg = f"[Channel] {channel_name} {channel.port} Capacity: {len(channel.clients)}/ {channel.capacity}, Queue: {channel.queue.qsize()}."
        client.connection.send(msg.encode())

def whisper_client(client, channel, msg) -> None:
    """
    Implement whisper function, if args for /whisper are valid.
    Else print appropriate message and return.
    Status: TODO
    """
    # Write your code here...
    # if in queue, do nothing
    if client.in_queue:
        return
    else:
        # if muted, send mute message to the client
        if client.muted:
            pass
        else:
            # validate the command structure
            msg_parts = msg.split(' ', 2)
            #print(msg_parts)
            username = msg_parts[1]
            usermsg = msg_parts[2]

            # validate if the target user is in the channel
            sendclient = None
            for checkclient in channel.clients:
                # if target user is in the channel, send the whisper message
                if checkclient.username == username:
                    sendclient = checkclient
                    #print(sendclient.username)
            
            if sendclient:
                msg = f"[{client.username} whispers to you: ({time.strftime('%H:%M:%S')})] {usermsg}"
                sendclient.connection.send(msg.encode())
                # print whisper server message
                print(f"[{client.username} whispers to {sendclient.username}: ({time.strftime('%H:%M:%S')})] {usermsg}", flush=True)
            else:
                msg = f"[Server message ({time.strftime('%H:%M:%S')})] {sendclient.username} is not here."
                client.connection.send(msg.encode())

def switch_channel(client, channel, msg, channels) -> bool:
    """
    Implement channel switching function, if args for /switch are valid.
    Else print appropriate message and return.

    Returns: bool
    Status: TODO
    """
    # Write your code here...
    # validate the command structure
    msg_parts = msg.split()
    target_channel_name = msg_parts[1]        
    # check if the new channel exists
    target_channel = None
    for _,c in channels.items():
        if c.name == target_channel_name:
            target_channel = c

    if target_channel == None:
        msg = f"[Server message ({time.strftime('%H:%M:%S')})] {target_channel_name} does not exist."
        client.connection.send(msg.encode())
        return
    # check if there is a client with the same username in the new channel
    for x in target_channel.clients:
        if x.username == client.username:
            msg = f"[Server message ({time.strftime('%H:%M:%S')})] {target_channel_name} already has a user with username {channel.username}."
            client.connection.send(msg.encode())
            return
    
    # if all checks are correct, and client in queue
    if client.in_queue:
        # remove client from current channel queue
        channel.queue = remove_item(client)
        # broadcast queue update message to all clients in the current channel
        process_queue(channel)
        # tell client to connect to new channel and close connection
        client.connection.send(f"/SWITCH: {channels[target_channel_name].port}".encode())
        client.connection.close()
        #only queue case
        print(f"[Server message ({time.strftime('%H:%M:%S')})] {client.username} has left the channel.")


    # if all checks are correct, and client in channel
    else:
        # remove client from current channel
        channel.clients.remove(client)
        # tell client to connect to new channel and close connection
        client.connection.send(f"/SWITCH: {channels[target_channel_name].port}".encode())
        client.connection.close()
        msg = f"[Server message ({time.strftime('%H:%M:%S')})] {client.username} has left the channel."
        print(msg)
        for x in channel.clients:
            x.connection.send(msg.encode())


def broadcast_in_channel(client, channel, msg) -> None:
    """
    Broadcast a message to all clients in the channel.
    Status: TODO
    """
    # Write your code here...
    # if in queue, do nothing
    if client.in_queue:
        return
    # if muted, send mute message to the client
    if client.muted:
        msg = f"[ Server message ({time.strftime('%H:%M:%S')})] You are still muted for {client.mute_duration} seconds."
        client.connection.send(msg.encode)
        return
    # broadcast message to all clients in the channel
    final_msg = f"[{client.username} ({time.strftime('%H:%M:%S')})] {msg}"
    for clients in channel.clients:
        #if client != clients:
        clients.connection.send(final_msg.encode())
    print(final_msg)

def client_handler(client, channel, channels) -> None:
    """
    Handles incoming messages from a client in a channel. Supports commands to quit, send, switch, whisper, and list channels. 
    Manages client's mute status and remaining time. Handles client disconnection and exceptions during message processing.
    Status: TODO (check the "# Write your code here..." block in Exception)
    Args:
        client (Client): The client to handle.
        channel (Channel): The channel in which the client is.
        channels (dict): A dictionary of all channels.
    """
    while True:
        if client.kicked:
            break
        try:
            msg = client.connection.recv(1024).decode()

            # check message for client commands
            if msg.startswith("/quit"):
                quit_client(client, channel)
                break
            elif msg.startswith("/send"):
                send_client(client, channel, msg)
            elif msg.startswith("/list"):
                list_clients(client, channels)
            elif msg.startswith("/whisper"):
                whisper_client(client, channel, msg)
            elif msg.startswith("/switch"):
                is_valid = switch_channel(client, channel, msg, channels)
                if is_valid:
                    break
                else:
                    continue

            # if not a command, broadcast message to all clients in the channel
            else:
                broadcast_in_channel(client, channel, msg)

            # reset remaining time before AFK
            if not client.muted:
                client.remaining_time = 100
        except EOFError:
            continue
        except OSError:
            break
        except Exception as e:
            print(f"Error in client handler: {e}")
            # remove client from the channel, close connection
            # Write your code here...
            if client in channel.clients:
                #mb wrong atm
                client.connection.close()
                channel.clients.remove(client)
                #leave_msg = f"[Server message ({time.strftime('%H:%M:%S')})] {client.username} has left the channel."
                client.connection.close()
            break

def check_duplicate_username(username, channel, conn) -> bool:
    """
    Check if a username is already in a channel or its queue.
    Status: TODO
    """
    # Write your code here...
    for x in channel.clients:
        if x.username == username:
            conn.close()
            return False
    #allows for the queue to be iterated over since channel.queue does not (its a queue duh)
    queue_list = list(channel.queue.queue)
    for client in queue_list:
        if client.username == username:
            conn.close()
            return False
    return True

def position_client(channel, conn, username, new_client) -> None:
    """
    Place a client in a channel or queue based on the channel's capacity.
    Status: TODO
    """
    # Write your code here...
    if len(channel.clients) < channel.capacity and channel.queue.empty():
        # put client in channel and reset remaining time before AFK
        channel.clients.append(new_client)
        new_client.remaining_time=100
        new_client.in_queue = False
        #send message to all client with self made function
        msg = f"[Server message ({time.strftime('%H:%M:%S')})] {new_client.username} has joined the channel."
        all_client_msg(channel, msg)
        #print to server as required
        print(f"[Server message ({time.strftime('%H:%M:%S')})] {new_client.username} has joined the {channel.name} channel.")
    else:
        # put client in queue
        channel.queue.put(new_client)
        #for client in queue
        wait_msg = f"[Server message ({time.strftime('%H:%M:%S')})] Welcome to the {channel.name} waiting room, {username}."
        new_client.connection.send(wait_msg.encode())

def channel_handler(channel, channels) -> None:
    """
    Starts a chat server, manage channels, respective queues, and incoming clients.
    This initiates different threads for chanel queue processing and client handling.
    Status: Given
    Args:
        channel (Channel): The channel for which to start the server.
    Raises:
        EOFError: If there is an error in the client-server communication.
    """
    # Initialize server socket, bind, and listen
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("localhost", channel.port))
    server_socket.listen(channel.capacity)

    # launch a thread to process client queue
    queue_thread = threading.Thread(target=process_queue, args=(channel,))
    queue_thread.start()

    while True:
        try:
            # accept a client connection
            conn, addr = server_socket.accept()
            username = conn.recv(1024).decode()

            # check duplicate username in channel and channel's queue
            is_valid = check_duplicate_username(username, channel, conn)
            if not is_valid: continue

            welcome_msg = f"[Server message ({time.strftime('%H:%M:%S')})] Welcome to the {channel.name} channel, {username}."
            conn.send(welcome_msg.encode())
            time.sleep(0.1)
            new_client = Client(username, conn, addr)

            # position client in channel or queue
            position_client(channel, conn, username, new_client)

            # Create a client thread for each connected client, whether they are in the channel or queue
            client_thread = threading.Thread(target=client_handler, args=(new_client, channel, channels))
            client_thread.start()
        except EOFError:
            continue

def remove_item(q, item_to_remove) -> queue.Queue:
    """
    Remove item from queue
    Status: Given
    Args:
        q (queue.Queue): The queue to remove the item from.
        item_to_remove (Client): The item to remove from the queue.
    Returns:
        queue.Queue: The queue with the item removed.
    """
    new_q = queue.Queue()
    while not q.empty():
        current_item = q.get()
        if current_item != item_to_remove:
            new_q.put(current_item)

    return new_q

def process_queue(channel) -> None:
    """
    Processes the queue of clients for a channel in an infinite loop. If the channel is not full, 
    it dequeues a client, adds them to the channel, and updates their status. It then sends updates 
    to all clients in the channel and queue. The function handles EOFError exceptions and sleeps for 
    1 second between iterations.
    Status: TODO
    Args:
        channel (Channel): The channel whose queue to process.
    Returns:
        None
    """
    #print(channel.queue.empty())
    # Write your code here...
    while True:
        try:
            if not channel.queue.empty() and len(channel.clients) < channel.capacity:
                # Dequeue a client from the queue and add them to the channel
                user = channel.queue.get()
                channel.clients.append(user)
                # Send join message to all clients in the channel
                bcast = f"[Server message ({time.strftime('%H:%M:%S')})] You have joined the {channel.name} channel."
                for x in channel.clients:
                    x.connection.send(bcast.encode())
                # Update the queue messages for remaining clients in the queue
                for x in range(len(channel.queue)):
                    queuecast = f"[Server message ({time.strftime('%H:%M:%S')})] You are in the waiting queue and there are {x} user(s) ahead of you."
                    channel.queue[x].connection.send(queuecast.encode()) 
                # Reset the remaining time to 100 before AFK
                user.remaining_time = 100
                time.sleep(1)
        except EOFError:
            continue

def kick_user(command, channels) -> None:
    """
    Implement /kick function
    Status: TODO
    Args:
        command (str): The command to kick a user from a channel.
        channels (dict): A dictionary of all channels.
    Returns:
        None
    """
    # Write your code here...
    # validate command structure
    values = command.split()
    channel_name = values[1]
    username = values[2] 
    # check if the channel exists in the dictionary
    if channel_name in channels:
        channel = channels[channel_name]
        #print(len(channel.clients))
    # if channel exists, check if the user is in the channel
        for client in channel.clients:
    # if user is in the channel, kick the user
            if client.username == username:
                #print(username)
                channel.clients.remove(client)
                for x in channel.clients:
                    leave_msg = f"[Server message ({time.strftime('%H:%M:%S')})] {username} has left the channel."
                    x.connection.send(leave_msg.encode())
                print(f"[Server message ({time.strftime('%H:%M:%S')})] Kicked {username}.") 
    # if user is not in the channel, print error message
    else:
        print(f"[Server message ({time.strftime('%H:%M:%S')})] {username} is not in {channel_name}.")    
    

def empty(command, channels) -> None:
    """
    Implement /empty function
    Status: TODO
    Args:
        command (str): The command to empty a channel.
        channels (dict): A dictionary of all channels.
    """
    # Write your code here...
    # validate the command structure
    values = command.split()
    channel_name = values[1]
    # check if the channel exists in the server
    if channel_name in channels:
        channel = channels[channel_name]
        #print(len(channel.clients))
    # if the channel exists, close connections of all clients in the channel
        for client in channel.clients:
            channel.clients.remove(client)
        print(f"[Server message ({time.strftime('%H:%M:%S')})] {channel_name} has been emptied.")    
    else:
        print(f"[Server message ({time.strftime('%H:%M:%S')})] {channel_name} does not exist.")    

def mute_user(command, channels) -> None:
    """
    Implement /mute function
    Status: TODO
    Args:
        command (str): The command to mute a user in a channel.
        channels (dict): A dictionary of all channels.
    """
    # Write your code here...
    # validate the command structure
    values = command.split()
    channel_name = values[1]
    username = values[2] 
    mute_time = int(values[3])
    # check if the mute time is valid
    if mute_time < 1:
        print(f"[Server message ({time.strftime('%H:%M:%S')})] Invalid mute time.")
        return
    # check if the channel exists in the server
    inchannel = False
    if channel_name in channels:
        channel = channels[channel_name]
    # if the channel exists, check if the user is in the channel
        for client in channel.clients:
            if client.username == username:
    # if user is in the channel, mute it and send messages to all clients
                inchannel = True
                client.muted = True
                client.mute_duration = mute_time
                break
    
    if inchannel:
        #server
        print(f"[Server message ({time.strftime('%H:%M:%S')})] Muted {username} for {mute_time} seconds.")
        client_msg = f"[Server message ({time.strftime('%H:%M:%S')})] You have been muted for {mute_time} seconds."
        #muted client
        client.connection.send(client_msg.encode())
        #all other people
        x_msg = f"[Server message ({time.strftime('%H:%M:%S')})] {username} has been muted for {mute_time} seconds."
        for _, channel in channels.items():
            for x in channel.clients:
                x.connection.send(x_msg.encode())
        return
    # if user is not in the channel, print error message
    if inchannel == False:
        print(f"[Server message ({time.strftime('%H:%M:%S')})] {username} is not here.")  
        return  

def shutdown(channels) -> None:
    """
    Implement /shutdown function
    Status: TODO
    Args:
        channels (dict): A dictionary of all channels.
    """
    # Write your code here...
    # close connections of all clients in all channels and exit the server
    for _, channel in channels.items():
        for client in channel.clients:
            client.connection.close()
    # end of code insertion, keep the os._exit(0) as it is
    os._exit(0)

def server_commands(channels) -> None:
    """
    Implement commands to kick a user, empty a channel, mute a user, and shutdown the server.
    Each command has its own validation and error handling. 
    Status: Given
    Args:
        channels (dict): A dictionary of all channels.
    Returns:
        None
    """
    while True:
        try:
            command = input()
            if command.startswith('/kick'):
                kick_user(command, channels)
            elif command.startswith("/empty"):
                empty(command, channels)
            elif command.startswith("/mute"):
                mute_user(command, channels)
            elif command == "/shutdown":
                shutdown(channels)
            else:
                continue
        except EOFError:
            continue
        except Exception as e:
            print(f"{e}")
            sys.exit(1)

def check_inactive_clients(channels) -> None:
    """
    Continuously manages clients in all channels. Checks if a client is muted, in queue, or has run out of time. 
    If a client's time is up, they are removed from the channel and their connection is closed. 
    A server message is sent to all clients in the channel. The function also handles EOFError exceptions.
    Status: TODO
    Args:
        channels (dict): A dictionary of all channels.
    """
    # Write your code here...
    # parse through all the clients in all the channels
    for _, channel in channels.items():
        for client in channel.clients:
    # if client is muted or in queue, do nothing
            if client.muted or client.in_queue:
                continue
    # remove client from the channel and close connection, print AFK message
            if client.remaining_time <= 0:
                print(f"[Server message ({time.strftime('%H:%M:%S')})] {client.username} went AFK")
                client.connection.close()
                
                channel.clients.remove(client)
    # if client is not muted, decrement remaining time
            client.remaining_time -= 1

def handle_mute_durations(channels) -> None:
    """
    Continuously manages the mute status of clients in all channels. If a client's mute duration has expired, 
    their mute status is lifted. If a client is still muted, their mute duration is decremented. 
    The function sleeps for 0.99 seconds between iterations and handles EOFError exceptions.
    Status: Given
    Args:
        channels (dict): A dictionary of all channels.
    """
    while True:
        try:
            for channel_name in channels:
                channel = channels[channel_name]
                for client in channel.clients:
                    if client.mute_duration <= 0:
                        client.muted = False
                        client.mute_duration = 0
                    if client.muted and client.mute_duration > 0:
                        client.mute_duration -= 1
            time.sleep(0.99)
        except EOFError:
            continue

def main():
    try:
        if len(sys.argv) != 2:
            print("Usage: python3 chatserver.py configfile")
            sys.exit(1)

        config_file = sys.argv[1]

        # parsing and creating channels
        parsed_lines = parse_config(config_file)
        channels = get_channels_dictionary(parsed_lines)

        # creating individual threads to handle channels connections
        for _, channel in channels.items():
            thread = threading.Thread(target=channel_handler, args=(channel, channels))
            thread.start()

        server_commands_thread = threading.Thread(target=server_commands, args=(channels,))
        server_commands_thread.start()

        inactive_clients_thread = threading.Thread(target=check_inactive_clients, args=(channels,))
        inactive_clients_thread.start()

        mute_duration_thread = threading.Thread(target=handle_mute_durations, args=(channels,))
        mute_duration_thread.start()
    except KeyboardInterrupt:
        print("Ctrl + C Pressed. Exiting...")
        os._exit(0)


if __name__ == "__main__":
    main()
