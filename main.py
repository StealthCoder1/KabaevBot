import asyncio
from db.ssh_tunnel import start_ssh_tunnel_from_env, stop_ssh_tunnel
from Data.config import DEBUG


async def main():
    tunnel_started = False
    if DEBUG:
        start_ssh_tunnel_from_env(force=True)
        tunnel_started = True
    try:
        from db.connect import create_all_tables
        from tgBot.general import start_bot

        await create_all_tables()
        await start_bot()
    finally:
        if tunnel_started:
            stop_ssh_tunnel()


if __name__ == '__main__':
    print('[+]Start bot[+]')
    asyncio.run(main())
