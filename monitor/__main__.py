import asyncio as aio

from common.topology import create_topology


async def main():
    await create_topology()
    print("hello from monitor")


if __name__ == "__main__":
    with aio.Runner() as runner:
        runner.run(main())
