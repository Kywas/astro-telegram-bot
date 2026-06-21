from aiohttp import ClientSession
from aiohttp_socks import ProxyConnector
from aiogram import __version__
from aiogram.client.session.aiohttp import SERVER_SOFTWARE, USER_AGENT, AiohttpSession


class HttpProxyAiohttpSession(AiohttpSession):
    """
    Telegram API session via HTTP or SOCKS proxy.

    Supported BOT_PROXY values:
    - http://host:port
    - http://user:pass@host:port
    - socks5://host:port
    - socks5://user:pass@host:port
    """

    def __init__(self, proxy_url: str, **kwargs: object) -> None:
        self._proxy_url = proxy_url
        super().__init__(proxy=None, **kwargs)

    async def create_session(self) -> ClientSession:
        if self._should_reset_connector:
            await self.close()

        if self._session is None or self._session.closed:
            connector = ProxyConnector.from_url(self._proxy_url)
            self._session = ClientSession(
                connector=connector,
                headers={
                    USER_AGENT: f"{SERVER_SOFTWARE} aiogram/{__version__}",
                },
            )
            self._should_reset_connector = False

        return self._session
