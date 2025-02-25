"""Provide the Multireddit class."""
import re
from json import dumps
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from ...const import API_PATH
from ...util.cache import cachedproperty
from ..listing.mixins import SubredditListingMixin
from .base import RedditBase
from .redditor import Redditor
from .subreddit import Subreddit, SubredditStream

if TYPE_CHECKING:  # pragma: no cover
    import asyncpraw


class Multireddit(SubredditListingMixin, RedditBase):
    r"""A class for users' multireddits.

    This is referred to as a "Custom Feed" on the Reddit UI.

    .. include:: ../../typical_attributes.rst

    ==================== ==============================================================
    Attribute            Description
    ==================== ==============================================================
    ``can_edit``         A ``bool`` representing whether or not the authenticated user
                         may edit the multireddit.
    ``copied_from``      The multireddit that the multireddit was copied from, if it
                         exists, otherwise ``None``.
    ``created_utc``      When the multireddit was created, in `Unix Time`_.
    ``description_html`` The description of the multireddit, as HTML.
    ``description_md``   The description of the multireddit, as Markdown.
    ``display_name``     The display name of the multireddit.
    ``name``             The name of the multireddit.
    ``over_18``          A ``bool`` representing whether or not the multireddit is
                         restricted for users over 18.
    ``subreddits``       A list of :class:`.Subreddit`\ s that make up the multireddit.
    ``visibility``       The visibility of the multireddit, either ``"private"``,
                         ``"public"``, or ``"hidden"``.
    ==================== ==============================================================

    .. _unix time: https://en.wikipedia.org/wiki/Unix_time

    """

    STR_FIELD = "path"
    RE_INVALID = re.compile(r"[\W_]+", re.UNICODE)

    @staticmethod
    def sluggify(title: str):
        """Return a slug version of the title.

        :param title: The title to make a slug of.

        Adapted from Reddit's utils.py.

        """
        title = Multireddit.RE_INVALID.sub("_", title).strip("_").lower()
        if len(title) > 21:  # truncate to nearest word
            title = title[:21]
            last_word = title.rfind("_")
            if last_word > 0:
                title = title[:last_word]
        return title or "_"

    @cachedproperty
    def stream(self) -> SubredditStream:
        """Provide an instance of :class:`.SubredditStream`.

        Streams can be used to indefinitely retrieve new comments made to a multireddit,
        like:

        .. code-block:: python

            multireddit = await reddit.multireddit("spez", "fun")
            async for comment in multireddit.stream.comments():
                print(comment)

        Additionally, new submissions can be retrieved via the stream. In the following
        example all new submissions to the multireddit are fetched:

        .. code-block:: python

            multireddit = await reddit.multireddit("bboe", "games")
            async for submission in multireddit.stream.submissions():
                print(submission)

        """
        return SubredditStream(self)

    def __init__(self, reddit: "asyncpraw.Reddit", _data: Dict[str, Any]):
        """Initialize a :class:`.Multireddit` instance."""
        self.path = None
        super().__init__(reddit, _data=_data)
        self._author = Redditor(reddit, self.path.split("/", 3)[2])
        self._path = API_PATH["multireddit"].format(multi=self.name, user=self._author)
        self.path = f"/{self._path[:-1]}"  # Prevent requests for path
        if "subreddits" in self.__dict__:
            self.subreddits = [Subreddit(reddit, x["name"]) for x in self.subreddits]

    async def _ensure_author_fetched(self):
        if not self._author._fetched:
            await self._author._fetch()

    async def _fetch_info(self):
        await self._ensure_author_fetched()
        return (
            "multireddit_api",
            {"multi": self.name, "user": self._author.name},
            None,
        )

    async def _fetch_data(self):
        name, fields, params = await self._fetch_info()
        path = API_PATH[name].format(**fields)
        return await self._reddit.request("GET", path, params)

    async def _fetch(self):
        data = await self._fetch_data()
        data = data["data"]
        other = type(self)(self._reddit, _data=data)
        self.__dict__.update(other.__dict__)
        self._fetched = True

    async def add(self, subreddit: "asyncpraw.models.Subreddit"):
        """Add a subreddit to this multireddit.

        :param subreddit: The subreddit to add to this multi.

        For example, to add r/test to multireddit ``bboe/test``:

        .. code-block:: python

            subreddit = await reddit.subreddit("test")
            multireddit = await reddit.multireddit("bboe", "test")
            await multireddit.add(subreddit)

        """
        await self._ensure_author_fetched()
        url = API_PATH["multireddit_update"].format(
            multi=self.name, user=self._author, subreddit=subreddit
        )
        await self._reddit.put(url, data={"model": dumps({"name": str(subreddit)})})
        self._reset_attributes("subreddits")

    async def copy(
        self, display_name: Optional[str] = None
    ) -> "asyncpraw.models.Multireddit":
        """Copy this multireddit and return the new multireddit.

        :param display_name: The display name for the copied multireddit. Reddit will
            generate the ``name`` field from this display name. When not provided the
            copy will use the same display name and name as this multireddit.

        To copy the multireddit ``bboe/test`` with a name of ``"testing"``:

        .. code-block:: python

            multireddit = await reddit.multireddit("bboe", "test")
            await multireddit.copy("testing")

        """
        if display_name:
            name = self.sluggify(display_name)
        else:
            await self.load()
            display_name = self.display_name
            name = self.name
        data = {
            "display_name": display_name,
            "from": self.path,
            "to": API_PATH["multireddit"].format(
                multi=name, user=await self._reddit.user.me()
            ),
        }
        return await self._reddit.post(API_PATH["multireddit_copy"], data=data)

    async def delete(self):
        """Delete this multireddit.

        For example, to delete multireddit ``bboe/test``:

        .. code-block:: python

            multireddit = await reddit.multireddit("bboe", "test")
            await multireddit.delete()

        """
        await self._ensure_author_fetched()
        path = API_PATH["multireddit_api"].format(
            multi=self.name, user=self._author.name
        )
        await self._reddit.delete(path)

    async def remove(self, subreddit: "asyncpraw.models.Subreddit"):
        """Remove a subreddit from this multireddit.

        :param subreddit: The subreddit to remove from this multi.

        For example, to remove r/test from multireddit ``bboe/test``:

        .. code-block:: python

            subreddit = await reddit.subreddit("test")
            multireddit = await reddit.multireddit("bboe", "test")
            await multireddit.remove(subreddit)

        """
        await self._ensure_author_fetched()
        url = API_PATH["multireddit_update"].format(
            multi=self.name, user=self._author, subreddit=subreddit
        )
        await self._reddit.delete(url, data={"model": dumps({"name": str(subreddit)})})
        self._reset_attributes("subreddits")

    async def update(
        self,
        **updated_settings: Union[
            str, List[Union[str, "asyncpraw.models.Subreddit", Dict[str, str]]]
        ],
    ):
        """Update this multireddit.

        Keyword arguments are passed for settings that should be updated. They can any
        of:

        :param display_name: The display name for this multireddit. Must be no longer
            than 50 characters.
        :param subreddits: Subreddits for this multireddit.
        :param description_md: Description for this multireddit, formatted in Markdown.
        :param icon_name: Can be one of: ``"art and design"``, ``"ask"``, ``"books"``,
            ``"business"``, ``"cars"``, ``"comics"``, ``"cute animals"``, ``"diy"``,
            ``"entertainment"``, ``"food and drink"``, ``"funny"``, ``"games"``,
            ``"grooming"``, ``"health"``, ``"life advice"``, ``"military"``, ``"models
            pinup"``, ``"music"``, ``"news"``, ``"philosophy"``, ``"pictures and
            gifs"``, ``"science"``, ``"shopping"``, ``"sports"``, ``"style"``,
            ``"tech"``, ``"travel"``, ``"unusual stories"``, ``"video"``, or ``None``.
        :param key_color: RGB hex color code of the form ``"#FFFFFF"``.
        :param visibility: Can be one of: ``"hidden"``, ``"private"``, or ``"public"``.
        :param weighting_scheme: Can be one of: ``"classic"`` or ``"fresh"``.

        For example, to rename multireddit ``"bboe/test"`` to ``"bboe/testing"``:

        .. code-block:: python

            multireddit = await reddit.multireddit("bboe", "test")
            await multireddit.update(display_name="testing")

        """
        if "subreddits" in updated_settings:
            updated_settings["subreddits"] = [
                {"name": str(sub)} for sub in updated_settings["subreddits"]
            ]
        await self._ensure_author_fetched()
        path = API_PATH["multireddit_api"].format(
            multi=self.name, user=self._author.name
        )
        new = await self._reddit.put(path, data={"model": dumps(updated_settings)})
        self.__dict__.update(new.__dict__)
