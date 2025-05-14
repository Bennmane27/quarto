import json
import subprocess
import os
import signal
import sys
import socket
import time

def check_server_availability(host, port, timeout=2):
    """Check if a server is available before starting clients."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def main():
    # load clients configuration
    here = os.path.dirname(__file__)
    cfg = os.path.join(here, 'players.json')
    
    try:
        with open(cfg, encoding='utf8') as f:
            players = json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file '{cfg}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Configuration file '{cfg}' contains invalid JSON.")
        sys.exit(1)
    
    # Check server availability before starting clients
    for p in players:
        host = p['host']
        port = p['port_server']
        print(f"Checking server at {host}:{port}...")
        if not check_server_availability(host, port):
            print(f"⚠️  WARNING: Server at {host}:{port} does not appear to be running!")
            response = input("Do you want to continue anyway? (y/n): ")
            if response.lower() != 'y':
                print("Exiting.")
                sys.exit(1)
            break  # Only check the first server configuration

    procs = []
    try:
        for p in players:
            cmd = [
                'python', 'client.py',
                '--host',        p['host'],
                '--port-server', str(p['port_server']),
                '--port-client', str(p['port_client']),
                '--name',        p['name'],
                '--matricules',
            ] + list(map(str, p['matricules']))
            # start client in quarto folder
            proc = subprocess.Popen(cmd, cwd=here)
            procs.append(proc)
            print(f"Started {p['name']} on port {p['port_client']}")
            time.sleep(0.5)  # Small delay to avoid race conditions
    except Exception as e:
        print(f"Error starting clients: {e}")
        # Make sure to clean up any started processes
        for proc in procs:
            try:
                proc.terminate()
            except:
                pass

    try:
        # wait for all to exit
        for proc in procs:
            proc.wait()
    except KeyboardInterrupt:
        print("Stopping all clients...")
        for proc in procs:
            try:
                proc.send_signal(signal.SIGINT)
            except:
                pass
        print("Waiting for clients to exit...")
        for proc in procs:
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()

if __name__ == '__main__':
    main()
