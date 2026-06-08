import asyncio
from typing import cast

from aiohttp import ClientError
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramNetworkError
from aiogram.methods.base import TelegramType


class HttpProxyAiohttpSession(AiohttpSession):
    """
    Aiohttp session with native HTTP proxy support.

    This avoids optional aiohttp-socks dependency and works for HTTP proxies
    like: http://user:password@host:port
    """

    def __init__(self, proxy_url: str, **kwargs: object) -> None:
        self._http_proxy_url = proxy_url
        super().__init__(proxy=None, **kwargs)

    async def make_request(
        self,
        bot,
        method,
        timeout: int | None = None,
    ) -> TelegramType:
        session = await self.create_session()

        url = self.api.api_url(token=bot.token, method=method.__api_method__)
        form = self.build_form_data(bot=bot, method=method)

        try:
            async with session.post(
                url,
                data=form,
                timeout=self.timeout if timeout is None else timeout,
                proxy=self._http_proxy_url,
            ) as resp:
                raw_result = await resp.text()
        except asyncio.TimeoutError as e:
            raise TelegramNetworkError(method=method, message="Request timeout error") from e
        except ClientError as e:
            raise TelegramNetworkError(method=method, message=f"{type(e).__name__}: {e}") from e

        response = self.check_response(
            bot=bot,
            method=method,
            status_code=resp.status,
            content=raw_result,
        )
        return cast(TelegramType, response.result)
