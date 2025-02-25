"""This file should be updated as files/classes/functions are deprecated."""

import pytest

from asyncpraw import Reddit
from asyncpraw.exceptions import APIException, AsyncPRAWException, WebSocketException
from asyncpraw.models import Comment, Subreddit
from asyncpraw.models.reddit.user_subreddit import UserSubreddit
from asyncpraw.util.token_manager import FileTokenManager

from . import UnitTest

pytestmark = pytest.mark.filterwarnings(
    "ignore:Unclosed client session", category=ResourceWarning
)


@pytest.mark.filterwarnings("error", category=DeprecationWarning)
class TestDeprecation(UnitTest):
    def test_api_exception(self):
        exc = APIException(["test", "testing", "test"])
        with pytest.raises(DeprecationWarning):
            exc.error_type
        with pytest.raises(DeprecationWarning):
            exc.message
        with pytest.raises(DeprecationWarning):
            exc.field

    async def test_comment_forest_async_iterator(self):
        submission = await self.reddit.submission("1234", fetch=False)
        submission._fetched = True
        submission.comments._comments = [Comment(None, id="1234")]
        with pytest.deprecated_call():
            async for comment in submission.comments:
                assert isinstance(comment, Comment)

    async def test_comment_forest_list_async(self):
        submission = await self.reddit.submission("1234", fetch=False)
        submission._fetched = True
        submission.comments._comments = []
        with pytest.deprecated_call():
            await submission.comments.list()

    async def test_conversations_after_argument(self):
        with pytest.deprecated_call():
            subreddit = await self.reddit.subreddit("all")
            subreddit.modmail.conversations(after="after")

    async def test_gild_method(self):
        with pytest.raises(DeprecationWarning) as excinfo:
            submission = await self.reddit.submission("1234", fetch=False)
            await submission.gild()
            assert excinfo.value.args[0] == "`.gild` has been renamed to `.award`."

    def test_gold_method(self):
        with pytest.raises(DeprecationWarning) as excinfo:
            self.reddit.subreddits.gold()
            assert (
                excinfo.value.args[0]
                == "`subreddits.gold` has be renamed to `subreddits.premium`."
            )

    async def test_lazy_argument_rename(self):
        with pytest.deprecated_call() as warning_info:
            await self.reddit.submission("1234", lazy=True)
        assert (
            str(warning_info.list[0].message)
            == "The parameter ``lazy`` has been renamed to ``fetch`` and support for"
            " the ``lazy`` parameter will be removed in a future version of Async PRAW."
        )

    def test_praw_exception_rename(self):
        with pytest.raises(AsyncPRAWException):
            Reddit()

        with pytest.raises(DeprecationWarning):
            import asyncpraw

            asyncpraw.exceptions.PRAWException

        with pytest.raises(DeprecationWarning):
            from asyncpraw import exceptions

            exceptions.PRAWException

        with pytest.raises(DeprecationWarning):
            from asyncpraw.exceptions import PRAWException  # noqa: F401

    async def test_reddit_token_manager(self):
        with pytest.raises(DeprecationWarning):
            async with Reddit(
                client_id="dummy",
                client_secret=None,
                redirect_uri="dummy",
                user_agent="dummy",
                token_manager=FileTokenManager("name"),
            ) as reddit:
                reddit._core._requestor._http = None

    async def test_reddit_user_me_read_only(self):
        with pytest.raises(DeprecationWarning):
            await self.reddit.user.me()

    async def test_submission_comments_async(self):
        submission = await self.reddit.submission("1234", fetch=False)
        submission._fetched = True
        with pytest.deprecated_call():
            await submission.comments()

    async def test_subreddit_rules_call(self):
        with pytest.raises(DeprecationWarning) as excinfo:
            subreddit = Subreddit(self.reddit, display_name="test")
            await subreddit.rules()
        assert (
            excinfo.value.args[0]
            == "Calling SubredditRules to get a list of rules is deprecated. Remove the"
            " parentheses to use the iterator. View the Async PRAW documentation on how"
            " to change the code in order to use the iterator"
            " (https://asyncpraw.readthedocs.io/en/latest/code_overview/other/subredditrules.html#asyncpraw.models.reddit.rules.SubredditRules.__call__)."
        )

    async def test_synchronous_context_manager(self):
        with pytest.raises(DeprecationWarning) as excinfo:
            with self.reddit:
                pass
            assert (
                excinfo.value.args[0]
                == "Using this class as a synchronous context manager is deprecated and"
                " will be removed in the next release. Use this class as an"
                " asynchronous context manager instead."
            )

    def test_user_subreddit_as_dict(self):
        user_subreddit = UserSubreddit(None, display_name="test")
        with pytest.deprecated_call() as warning_info:
            display_name = user_subreddit["display_name"]
            assert display_name == "test"
            assert (
                warning_info.list[0].message.args[0]
                == "`Redditor.subreddit` is no longer a dict and is now an"
                " `UserSubreddit` object. Accessing attributes using string indices is"
                " deprecated."
            )
            assert user_subreddit.keys() == user_subreddit.__dict__.keys()
            assert (
                warning_info.list[1].message.args[0]
                == "`Redditor.subreddit` is no longer a dict and is now an"
                " `UserSubreddit` object. Using `keys` is deprecated and will be"
                " removed in Async PRAW 8."
            )

    def test_validate_on_submit(self):
        with pytest.raises(DeprecationWarning):
            self.reddit.validate_on_submit
        self.reddit.validate_on_submit = True
        assert self.reddit.validate_on_submit
        self.reddit.validate_on_submit = False
        with pytest.raises(DeprecationWarning):
            self.reddit.validate_on_submit

    def test_web_socket_exception_attribute(self):
        exc = WebSocketException("Test", Exception("Test"))
        with pytest.raises(DeprecationWarning) as excinfo:
            _ = exc.original_exception
        assert (
            excinfo.value.args[0]
            == "Accessing the attribute original_exception is deprecated. Please"
            " rewrite your code in such a way that this attribute does not need to"
            " be used. It will be removed in Async PRAW 8.0."
        )
