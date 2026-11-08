"""Bound stateless history uploads before JSON parsing."""
from starlette.responses import JSONResponse


class HistoryBodyLimit:
    def __init__(self, app, limit=32_000_000):
        self.app = app
        self.limit = limit

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http' or scope['method'] != 'POST' or not scope['path'].startswith('/api/history/'):
            return await self.app(scope, receive, send)
        chunks = []
        length = 0
        while True:
            message = await receive()
            if message['type'] == 'http.disconnect':
                return
            chunk = message.get('body', b'')
            length += len(chunk)
            if length > self.limit:
                return await JSONResponse({'detail': 'Dataset request exceeds 32 MB.'}, status_code=413)(scope, receive, send)
            chunks.append(chunk)
            if not message.get('more_body', False):
                break
        body = b''.join(chunks)
        delivered = False

        async def replay():
            nonlocal delivered
            if delivered:
                return await receive()
            delivered = True
            return {'type': 'http.request', 'body': body, 'more_body': False}

        await self.app(scope, replay, send)
