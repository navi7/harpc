import asyncio
import aiohttp
from aiohttp import web

async def handle(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Account: " + name
    return web.Response(body=text.encode('utf-8'))

async def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/{name}', handle)

    srv = await loop.create_server(app.make_handler(),
                                   '0.0.0.0', 8081)
    print("Server started at http://0.0.0.0:8081")
    return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass