from code.server.server import Server

server = Server()

if not server.failed: server.start()