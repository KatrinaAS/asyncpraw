"""Provide the Rule class."""
from typing import TYPE_CHECKING, Any, AsyncIterator, Dict, List, Optional, Union
from urllib.parse import quote
from warnings import warn

from ...const import API_PATH
from ...exceptions import ClientException
from ...util.cache import cachedproperty
from .base import RedditBase

if TYPE_CHECKING:  # pragma: no cover
    import asyncpraw


class Rule(RedditBase):
    """An individual :class:`.Rule` object.

    .. include:: ../../typical_attributes.rst

    ==================== =============================================================
    Attribute            Description
    ==================== =============================================================
    ``created_utc``      Time the rule was created, represented in `Unix Time`_.
    ``description``      The description of the rule, if provided, otherwise a blank
                         string.
    ``kind``             The kind of rule. Can be ``"link"``, ``comment"``, or
                         ``"all"``.
    ``priority``         Represents where the rule is ranked. For example, the first
                         rule is at priority ``0``. Serves as an index number on the
                         list of rules.
    ``short_name``       The name of the rule.
    ``violation_reason`` The reason that is displayed on the report menu for the rule.
    ==================== =============================================================

    .. _unix time: https://en.wikipedia.org/wiki/Unix_time

    """

    STR_FIELD = "short_name"

    @cachedproperty
    def mod(self) -> "asyncpraw.models.reddit.rules.RuleModeration":
        """Contain methods used to moderate rules.

        To delete ``"No spam"`` from r/test try:

        .. code-block:: python

            subreddit = await reddit.subreddit("test")
            rule = await subreddit.rules.get_rule("No Spam")
            await rule.mod.delete()

        To update ``"No spam"`` from r/test try:

        .. code-block:: python

            subreddit = await reddit.subreddit("test")
            await subreddit.rules.get_rule("No spam")
            await rule.mod.update(description="Don't do this!", violation_reason="Spam post")

        """
        return RuleModeration(self)

    def __init__(
        self,
        reddit: "asyncpraw.Reddit",
        subreddit: Optional["asyncpraw.models.Subreddit"] = None,
        short_name: Optional[str] = None,
        _data: Optional[Dict[str, str]] = None,
    ):
        """Initialize a :class:`.Rule` instance."""
        if (short_name, _data).count(None) != 1:
            raise ValueError("Either short_name or _data needs to be given.")
        if short_name:
            self.short_name = short_name
        # Note: The subreddit parameter can be None, because the objector does not know
        # this info. In that case, it is the responsibility of the caller to set the
        # `subreddit` property on the returned value
        self.subreddit = subreddit
        super().__init__(reddit, _data=_data)

    def __getattribute__(self, attribute: str) -> Any:
        """Get the value of an attribute."""
        value = super().__getattribute__(attribute)
        if attribute == "subreddit" and value is None:
            raise ValueError(
                "The Rule is missing a subreddit. File a bug report at Async PRAW."
            )
        return value

    async def _fetch(self):
        async for rule in self.subreddit.rules:
            if rule.short_name == self.short_name:
                self.__dict__.update(rule.__dict__)
                self._fetched = True
                return
        raise ClientException(
            f"Subreddit {self.subreddit} does not have the rule {self.short_name}"
        )


class SubredditRules:
    """Provide a set of functions to access a :class:`.Subreddit`'s rules.

    For example, to list all the rules for a subreddit:

    .. code-block:: python

        subreddit = await reddit.subreddit("test")
        async for rule in subreddit.rules:
            print(rule)

    Moderators can also add rules to the subreddit. For example, to make a rule called
    ``"No spam"`` in r/test:

    .. code-block:: python

        subreddit = await reddit.subreddit("test")
        await subreddit.rules.mod.add(
            short_name="No spam", kind="all", description="Do not spam. Spam bad"
        )

    """

    @cachedproperty
    def mod(self) -> "SubredditRulesModeration":
        """Contain methods to moderate subreddit rules as a whole.

        To add rule ``"No spam"`` to r/test try:

        .. code-block:: python

            subreddit = await reddit.subreddit("test")
            await subreddit.rules.mod.add(
                short_name="No spam", kind="all", description="Do not spam. Spam bad"
            )

        To move the fourth rule to the first position, and then to move the prior first
        rule to where the third rule originally was in r/test:

        .. code-block:: python

            subreddit = await reddit.subreddit("test")
            rules = [rule async for rule in subreddit.rules]
            new_rules = rules[3:4] + rules[1:3] + rules[0:1] + rules[4:]
            # Alternate: [rules[3]] + rules[1:3] + [rules[0]] + rules[4:]
            new_rule_list = await subreddit.rules.mod.reorder(new_rules)

        """
        return SubredditRulesModeration(self)

    async def __call__(self) -> List["asyncpraw.models.Rule"]:
        r"""Return a list of :class:`.Rule`\ s (Deprecated).

        :returns: A list of instances of :class:`.Rule`.

        .. deprecated:: 7.1

            Use the iterator by removing the call to :class:`.SubredditRules`. For
            example, in order to use the iterator:

            .. code-block:: python

                subreddit = await reddit.subreddit("test")
                async for rule in subreddit.rules:
                    print(rule)

        """
        warn(
            "Calling SubredditRules to get a list of rules is deprecated. Remove the"
            " parentheses to use the iterator. View the Async PRAW documentation on how"
            " to change the code in order to use the iterator"
            " (https://asyncpraw.readthedocs.io/en/latest/code_overview/other/subredditrules.html#asyncpraw.models.reddit.rules.SubredditRules.__call__).",
            category=DeprecationWarning,
            stacklevel=2,
        )
        return await self._reddit.request(
            "GET", API_PATH["rules"].format(subreddit=self.subreddit)
        )

    async def get_rule(
        self, short_name: Union[str, int, slice]
    ) -> "asyncpraw.models.Rule":
        """Return the :class:`.Rule` for the subreddit with short_name ``short_name``.

        :param short_name: The short_name of the rule, or the rule number.

        This method is to be used to fetch a specific rule, like so:

        .. code-block:: python

            rule_name = "No spam"
            subreddit = await reddit.subreddit("test")
            rule = await subreddit.rules.get_rule(rule_name)
            print(rule)

        You can also fetch a numbered rule of a subreddit.

        Rule numbers start at ``0``, so the first rule is at index ``0``, and the second
        rule is at index ``1``, and so on.

        :raises: :py:class:`IndexError` if a rule of a specific number does not exist.

        .. note::

            You can use negative indexes, such as ``-1``, to get the last rule. You can
            also use slices, to get a subset of rules, such as the last three rules with
            ``get_rule(slice(-3, None))``.

        For example, to fetch the second rule of r/test:

        .. code-block:: python

            subreddit = await reddit.subreddit("test")
            rule = await subreddit.rules.get_rule(1)

        """
        if not isinstance(short_name, str):
            rules = await self._rule_list()
            return rules[short_name]
        rule = Rule(self._reddit, subreddit=self.subreddit, short_name=short_name)
        await rule._fetch()
        return rule

    def __init__(self, subreddit: "asyncpraw.models.Subreddit"):
        """Initialize a :class:`.SubredditRules` instance.

        :param subreddit: The subreddit whose rules to work with.

        """
        self.subreddit = subreddit
        self._reddit = subreddit._reddit

    async def __aiter__(self) -> AsyncIterator["asyncpraw.models.Rule"]:
        """Iterate through the rules of the subreddit.

        :returns: An asynchronous iterator containing all the rules of a subreddit.

        This method is used to discover all rules for a subreddit.

        For example, to get the rules for r/test:

        .. code-block:: python

            subreddit = await reddit.subreddit("test")
            async for rule in subreddit.rules:
                print(rule)

        """
        rules = await self._rule_list()
        for rule in rules:
            yield rule

    async def _rule_list(self) -> List[Rule]:
        """Get a list of :class:`.Rule` objects.

        :returns: A list of instances of :class:`.Rule`.

        """
        rule_list = await self._reddit.get(
            API_PATH["rules"].format(subreddit=self.subreddit)
        )
        for rule in rule_list:
            rule.subreddit = self.subreddit
        return rule_list


class RuleModeration:
    """Contain methods used to moderate rules.

    To delete ``"No spam"`` from r/test try:

    .. code-block:: python

        subreddit = await reddit.subreddit("test")
        rule = await subreddit.rules.get_rule("No Spam")
        await rule.mod.delete()

    To update ``"No spam"`` from r/test try:

    .. code-block:: python

        subreddit = await reddit.subreddit("test")
        rule = await subreddit.rules.get_rule("No Spam")
        await rule.mod.update(description="Don't do this!", violation_reason="Spam post")

    """

    def __init__(self, rule: "asyncpraw.models.Rule"):
        """Initialize a :class:`.RuleModeration` instance."""
        self.rule = rule

    async def delete(self):
        """Delete a rule from this subreddit.

        To delete ``"No spam"`` from r/test try:

        .. code-block:: python

            subreddit = await reddit.subreddit("test")
            rule = await subreddit.rules.get_rule("No Spam")
            await rule.mod.delete()

        """
        data = {
            "r": str(self.rule.subreddit),
            "short_name": self.rule.short_name,
        }
        await self.rule._reddit.post(API_PATH["remove_subreddit_rule"], data=data)

    async def update(
        self,
        description: Optional[str] = None,
        kind: Optional[str] = None,
        short_name: Optional[str] = None,
        violation_reason: Optional[str] = None,
    ) -> "asyncpraw.models.Rule":
        """Update the rule from this subreddit.

        .. note::

            Existing values will be used for any unspecified arguments.

        :param description: The new description for the rule. Can be empty.
        :param kind: The kind of item that the rule applies to. One of ``"link"``,
            ``"comment"``, or ``"all"``.
        :param short_name: The name of the rule.
        :param violation_reason: The reason that is shown on the report menu.

        :returns: A Rule object containing the updated values.

        To update ``"No spam"`` from r/test try:

        .. code-block:: python

            subreddit = reddit.subreddit("test")
            rule = await subreddit.rules.get_rule("No Spam")
            await rule.mod.update(description="Don't do this!", violation_reason="Spam post")

        """
        data = {
            "r": str(self.rule.subreddit),
            "old_short_name": self.rule.short_name,
        }
        for name, value in {
            "description": description,
            "kind": kind,
            "short_name": short_name,
            "violation_reason": violation_reason,
        }.items():
            data[name] = getattr(self.rule, name) if value is None else value
        response = await self.rule._reddit.post(
            API_PATH["update_subreddit_rule"], data=data
        )
        updated_rule = response[0]
        updated_rule.subreddit = self.rule.subreddit
        return updated_rule


class SubredditRulesModeration:
    """Contain methods to moderate subreddit rules as a whole.

    To add rule ``"No spam"`` to r/test try:

    .. code-block:: python

        subreddit = await reddit.subreddit("test")
        await subreddit.rules.mod.add(
            short_name="No spam", kind="all", description="Do not spam. Spam bad"
        )

    To move the fourth rule to the first position, and then to move the prior first rule
    to where the third rule originally was in r/test:

    .. code-block:: python

        subreddit = await reddit.subreddit("test")
        rules = [rule async for rule in subreddit.rules]
        new_rules = rules[3:4] + rules[1:3] + rules[0:1] + rules[4:]
        # Alternate: [rules[3]] + rules[1:3] + [rules[0]] + rules[4:]
        new_rule_list = await subreddit.rules.mod.reorder(new_rules)

    """

    def __init__(self, subreddit_rules: SubredditRules):
        """Initialize a :class:`.SubredditRulesModeration` instance."""
        self.subreddit_rules = subreddit_rules

    async def add(
        self,
        short_name: str,
        kind: str,
        description: str = "",
        violation_reason: Optional[str] = None,
    ) -> "asyncpraw.models.Rule":
        """Add a removal reason to this subreddit.

        :param short_name: The name of the rule.
        :param kind: The kind of item that the rule applies to. One of ``"link"``,
            ``"comment"``, or ``"all"``.
        :param description: The description for the rule.
        :param violation_reason: The reason that is shown on the report menu. If a
            violation reason is not specified, the short name will be used as the
            violation reason.

        :returns: The Rule added.

        To add rule ``"No spam"`` to r/test try:

        .. code-block:: python

            subreddit = await reddit.subreddit("test")
            await subreddit.rules.mod.add(
                short_name="No spam", kind="all", description="Do not spam. Spam bad"
            )

        """
        data = {
            "r": str(self.subreddit_rules.subreddit),
            "description": description,
            "kind": kind,
            "short_name": short_name,
            "violation_reason": short_name
            if violation_reason is None
            else violation_reason,
        }
        response = await self.subreddit_rules._reddit.post(
            API_PATH["add_subreddit_rule"], data=data
        )
        new_rule = response[0]
        new_rule.subreddit = self.subreddit_rules.subreddit
        return new_rule

    async def reorder(
        self, rule_list: List["asyncpraw.models.Rule"]
    ) -> List["asyncpraw.models.Rule"]:
        """Reorder the rules of a subreddit.

        :param rule_list: The list of rules, in the wanted order. Each index of the list
            indicates the position of the rule.

        :returns: A list containing the rules in the specified order.

        For example, to move the fourth rule to the first position, and then to move the
        prior first rule to where the third rule originally was in r/test:

        .. code-block:: python

            subreddit = await reddit.subreddit("test")
            rules = [rule async for rule in subreddit.rules]
            new_rules = rules[3:4] + rules[1:3] + rules[0:1] + rules[4:]
            # Alternate: [rules[3]] + rules[1:3] + [rules[0]] + rules[4:]
            new_rule_list = await subreddit.rules.mod.reorder(new_rules)

        """
        order_string = quote(
            ",".join([rule.short_name for rule in rule_list]), safe=","
        )
        data = {
            "r": str(self.subreddit_rules.subreddit),
            "new_rule_order": order_string,
        }
        response = await self.subreddit_rules._reddit.post(
            API_PATH["reorder_subreddit_rules"], data=data
        )
        for rule in response:
            rule.subreddit = self.subreddit_rules.subreddit
        return response
