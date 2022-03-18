"""Provide the ModAction class."""
from typing import TYPE_CHECKING, Union

from asyncpraw.models.base import AsyncPRAWBase

if TYPE_CHECKING:  # pragma: no cover
    import asyncpraw


class ModNote(AsyncPRAWBase):
    """Represent a moderator action."""

    def __str__(self) -> str:
        """Return a string representation of the instance."""
        return getattr(self, "id")

    @property
    async def user(self) :
        """Return the :class:`.Redditor` who the action was issued by."""
        return self._reddit.redditor(self._user)  # pylint: disable=no-member

    @user.setter
    def user(self, value: Union[str, "asyncpraw.models.Redditor"]):
        self._user = value  # pylint: disable=attribute-defined-outside-init

    @property
    async def operator(self) :
        """Return the :class:`.Redditor` who the action was issued by."""
        return self._reddit.redditor(self._operator)  # pylint: disable=no-member

    @operator.setter
    def operator(self, value: Union[str, "asyncpraw.models.Redditor"]):
        self._operator = value  # pylint: disable=attribute-defined-outside-init

    @property
    async def subreddit(self) :
        """Return the :class:`.Redditor` who the action was issued by."""
        return self._reddit.subreddit(self._subreddit)  # pylint: disable=no-member

    @subreddit.setter
    def subreddit(self, value: Union[str, "asyncpraw.models.Subreddit"]):
        self._subreddit = value  # pylint: disable=attribute-defined-outside-init