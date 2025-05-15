import argparse
import asyncio
import json
import sys
import importlib
from datetime import datetime

async def readJSON(reader):
    buffer = ''
    while True:
        chunk = await reader.read(1024)
        if not chunk:
            raise Exception('Connection closed')
        buffer += chunk.decode('utf8')
        try:
            return json.loads(buffer)
        except json.JSONDecodeError:
            continue

async def writeJSON(writer, obj):
    message = json.dumps(obj).encode('utf8')
    writer.write(message)
    await writer.drain()

async def handle_connection(reader, writer, strategy_mod):
    request = await readJSON(reader)
    req_type = request.get('request')
    if req_type == 'ping':
        print('[PING]')
        await writeJSON(writer, {'response': 'pong'})
    elif req_type == 'play':
        state = request.get('state')
        print(f"[PLAY] Etat reçu: {state}")
        try:
            move = strategy_mod.gen_move(state)
            print(f"[MOVE] Coup proposé: {move}")
            await writeJSON(writer, {'response': 'move', 'move': move})
        except Exception as e:
            print(f"[ERROR] Erreur lors de la génération du coup: {e}")
            await writeJSON(writer, {'response': 'error', 'error': str(e)})
    else:
        print(f"[ERROR] Requête inconnue: {req_type}")
        await writeJSON(writer, {'response': 'error', 'error': f"Unknown request '{req_type}'"})
    writer.close()
    await writer.wait_closed()

async def check_server(host, port, timeout=2):
    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=timeout
        )
        writer.close()
        await writer.wait_closed()
        return True
    except (ConnectionRefusedError, asyncio.TimeoutError):
        return False

async def subscribe(host, port_server, port_client, name, matricules, max_retries=3):
    print(f"Checking server availability at {host}:{port_server}...")
    if not await check_server(host, port_server):
        print(f"⚠️  ERROR: Server at {host}:{port_server} is not responding.")
        print("Please ensure the server is running and the port is correct.")
        return False
    for attempt in range(1, max_retries + 1):
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port_server),
                timeout=5
            )
            request = {
                'request': 'subscribe',
                'name': name,
                'port': port_client,
                'matricules': [str(m) for m in matricules]
            }
            await writeJSON(writer, request)
            response = await readJSON(reader)
            writer.close()
            await writer.wait_closed()
            if response.get('response') != 'ok':
                print(f"⚠️  Subscription failed: {response}")
                return False
            print(f"✅ Successfully subscribed as '{name}' to {host}:{port_server}")
            return True
        except ConnectionRefusedError:
            if attempt < max_retries:
                wait_time = attempt * 2
                print(f"Connection refused. Retrying in {wait_time} seconds... (Attempt {attempt}/{max_retries})")
                await asyncio.sleep(wait_time)
            else:
                print(f"⚠️  ERROR: Could not connect to server at {host}:{port_server} after {max_retries} attempts.")
                print("Please check if:")
                print("  - The server is running")
                print("  - The port {port_server} is correct and open")
                print("  - There are no firewall issues blocking the connection")
                return False
        except asyncio.TimeoutError:
            print(f"⚠️  ERROR: Connection to {host}:{port_server} timed out.")
            print("The server might be slow or unresponsive.")
            return False
        except Exception as e:
            print(f"⚠️  ERROR: Unexpected error during subscription: {e}")
            return False
    return False

async def main():
    parser = argparse.ArgumentParser(description='Quarto IA Client')
    parser.add_argument('--host', required=True, help='Server IP address')
    parser.add_argument('--port-server', type=int, required=True, help='Server subscription port')
    parser.add_argument('--port-client', type=int, required=True, help='Port this client listens on')
    parser.add_argument('--name', required=True, help='Client name')
    parser.add_argument('--matricules', nargs='+', required=True, help='Matricules of the two students')
    parser.add_argument('--strategy', required=True, help='Strategy module to use (strategy, strategy_random, strategy_strong)')
    args = parser.parse_args()
    strategy_mod = importlib.import_module(args.strategy)
    if not await subscribe(args.host, args.port_server, args.port_client, args.name, args.matricules):
        print(f"Could not subscribe to server. Exiting.")
        return
    try:
        async def handler(reader, writer):
            await handle_connection(reader, writer, strategy_mod)
        server = await asyncio.start_server(handler, '0.0.0.0', args.port_client)
        print(f"Client listening on port {args.port_client}")
        async with server:
            await server.serve_forever()
    except OSError as e:
        if e.errno == 10048:
            print(f"⚠️  ERROR: Port {args.port_client} is already in use.")
            print("Try specifying a different port with --port-client option.")
        else:
            print(f"⚠️  ERROR: {e}")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nClient stopped by user.")
