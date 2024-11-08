import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)

class GameServer:
    def __init__(self):
        self.clients = set()
        self.game_state = {}  # Stores player positions and other game state

    async def register(self, websocket):
        client_id = id(websocket)
        self.clients.add(websocket)
        self.game_state[client_id] = {
            "x": 100,
            "y": 100,
            "direction": 0
        }
        logging.info(f"New client connected. Total clients: {len(self.clients)}")
        return client_id

    async def unregister(self, websocket):
        self.clients.remove(websocket)
        client_id = id(websocket)
        if client_id in self.game_state:
            del self.game_state[client_id]
        logging.info(f"Client disconnected. Total clients: {len(self.clients)}")

    async def handle_message(self, websocket, message):
        client_id = id(websocket)
        data = json.loads(message)
        
        # Update game state with received player data
        if client_id in self.game_state:
            self.game_state[client_id].update(data)
        
        # Send updated game state to all clients
        for client in self.clients:
            try:
                await client.send(json.dumps(self.game_state))
            except websockets.ConnectionClosed:
                pass

    async def handle_client(self, websocket, path):
        logging.info(f"Connection attempt from {websocket.remote_address}")
        try:
            client_id = await self.register(websocket)
            logging.info(f"Client {client_id} successfully registered from {websocket.remote_address}")
            async for message in websocket:
                logging.info(f"Received message from client {client_id}: {message[:100]}...")  # Log first 100 chars of message
                await self.handle_message(websocket, message)
        except websockets.ConnectionClosed:
            logging.warning(f"Client connection closed unexpectedly: {websocket.remote_address}")
        except Exception as e:
            logging.error(f"Error handling client: {str(e)}")
        finally:
            await self.unregister(websocket)

async def start_server():
    game_server = GameServer()
    async with websockets.serve(
        game_server.handle_client,
        host="0.0.0.0",
        port=8765,
        ping_interval=None
    ):
        logging.info("Server started on port 8765")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(start_server()) 