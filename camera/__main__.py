import asyncio as aio

from common.topology import create_topology


async def main():
    create_topology()
    print("hello from camera")


if __name__ == "__main__":
    with aio.Runner() as runner:
        runner.run(main())
