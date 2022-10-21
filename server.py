import asyncio
import json
import secrets
from typing import Any, Literal, Type, TypedDict

import websockets

from Game import TicTacToe

socket_t = Type[websockets.legacy.client.WebSocketClientProtocol]
games: dict[str, tuple[TicTacToe, set[socket_t]]] = {}


class Event(TypedDict):
    type: Literal["init"] | Literal["play"]
    join: str
    msg: dict[str, Any]

    row: int
    col: int


async def error(socket, msg: str):
    await socket.send(json.dumps({"type": "error", "message": msg}))


async def wait_until_game_full(join_key: str):
    while True:
        # get the game
        _, connected = games[join_key]

        if len(connected) == 2:
            break

        await asyncio.sleep(0.5)


async def broadcast(sockets, msg: str, exclude_sockets=None):
    if not exclude_sockets:
        exclude_sockets = []

    for sock in sockets:
        if sock in exclude_sockets:
            continue
        await sock.send(msg)


async def play(socket, join_key: str, player: str):
    await wait_until_game_full(join_key)

    game, connected = games[join_key]

    await broadcast(connected, json.dumps({"type": "gameReady"}), [socket])

    async for msg in socket:
        event: Event = json.loads(msg)
        assert event["type"] == "play"

        print(player, ":", event)

        try:
            game.play(player, event["row"], event["col"])

            await broadcast(
                connected,
                json.dumps(
                    {
                        "type": "move",
                        "row": event["row"],
                        "col": event["col"],
                        "player": player,
                    }
                ),
            )

            if game.winner:
                await broadcast(
                    connected, json.dumps({"type": "win", "player": game.winner})
                )

                await asyncio.sleep(3)
                # clear the board
                game.clear()

                await broadcast(connected, json.dumps({"type": "reset"}))

        except RuntimeError as e:
            await error(socket, str(e))


async def start_game(socket):
    connected = {socket}

    game = TicTacToe()
    join_key = secrets.token_urlsafe(6)
    games[join_key] = (game, connected)  # type: ignore

    try:
        event = {"type": "init", "join": join_key}

        await socket.send(json.dumps(event))

        print("first player started game", id(game))

        await play(socket, join_key, "X")
    except Exception:
        print("Socket unexpecdedly disconnected")
    finally:
        del games[join_key]


async def join(socket, join_key: str):
    # Try and find the game
    try:
        game, connected = games[join_key]
    except KeyError:
        await error(socket, "Game not found")
        return

    connected.add(socket)

    try:
        print("second player joined game", id(game))
        await play(socket, join_key, "O")
    finally:
        connected.remove(socket)


async def handle(socket):
    message = await socket.recv()
    event: Event = json.loads(message)

    assert event["type"] == "init"

    if "join" in event:
        await join(socket, event["join"])
    else:
        await start_game(socket)


async def main():
    async with websockets.serve(handle, "", 8003):  # type: ignore
        print("Server listening on ws://localhost:8003")
        await asyncio.Future()  # type: ignore


if __name__ == "__main__":
    asyncio.run(main())
