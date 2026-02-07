from fastapi.websockets import WebSocket


class WSConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self.active_connections.append(ws)

    async def disconnect(self, ws: WebSocket) -> None:
        self.active_connections.remove(ws)
        await ws.close()

    @staticmethod
    async def send(ws: WebSocket, message: str | bytes | list | dict) -> None:
        if isinstance(message, str):
            await ws.send_text(message)
        elif isinstance(message, bytes):
            await ws.send_bytes(message)
        else:
            await ws.send_json(message)

    @staticmethod
    async def receive(ws: WebSocket) -> str:
        return await ws.receive_text()


ws_manager = WSConnectionManager()