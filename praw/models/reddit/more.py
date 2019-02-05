"""Provide the MoreComments class."""
from ...const import API_PATH
from ..base import PRAWBase


class MoreComments(PRAWBase):
    """A class indicating there are more comments."""

    def __init__(self, reddit, _data):
        """Construct an instance of the MoreComments object."""
        self.count = self.parent_id = None
        self.children = []
        super(MoreComments, self).__init__(reddit, _data)
        self._comments = None
        self.submission = None

    def __eq__(self, other):
        """Return True if these MoreComments instances are the same."""
        return isinstance(other, self.__class__) and self.count == other.count and self.children == other.children

    def __lt__(self, other):
        """Provide a sort order on the MoreComments object."""
        # To work with heapq a "smaller" item is the one with the most comments
        # We are intentionally making the biggest element the smallest element
        # to turn the min-heap implementation in heapq into a max-heap.
        return self.count > other.count

    def __repr__(self):
        """Return a string representation of the MoreComments instance."""
        children = self.children[:4]
        if len(self.children) > 4:
            children[-1] = '...'
        return '<{} count={}, children={!r}>'.format(self.__class__.__name__, self.count, children)

    async def _continue_comments(self, update):
        assert not self.children
        parent = await self._load_comment(self.parent_id.split('_', 1)[1])
        self._comments = parent.replies
        if update:
            for comment in self._comments:
                comment.submission = self.submission
        return self._comments

    async def _load_comment(self, comment_id):
        path = '{}_/{}'.format(API_PATH['submission'].format(id=self.submission.id), comment_id)
        _, comments = await self._reddit.get(path, params={'limit': self.submission.comment_limit, 'sort': self.submission.comment_sort})
        assert len(await comments.children) == 1
        return await comments.children[0]

    async def comments(self, update=True):
        """Fetch and return the comments for a single MoreComments object."""
        if self._comments is None:
            if self.count == 0:  # Handle 'continue this thread'
                return await self._continue_comments(update)
            assert self.children
            data = {'children': ','.join(self.children), 'link_id': self.submission.fullname, 'sort': self.submission.comment_sort}
            self._comments = await self._reddit.post(API_PATH['morechildren'], data=data)
            if update:
                for comment in self._comments:
                    comment.submission = self.submission
        return self._comments
