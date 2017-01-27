import random

from hypothesis import note
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, rule

import priority


class PriorityQueue(RuleBasedStateMachine):

    def __init__(self):
        super(PriorityQueue, self).__init__()
        self.tree = priority.PriorityTree()
        self.stream_ids = set([0])
        self.blocked_stream_ids = set()

    @rule(stream_id=st.integers())
    def insert_stream(self, stream_id):
        try:
            self.tree.insert_stream(stream_id)
        except priority.DuplicateStreamError:
            assert stream_id in self.stream_ids
        else:
            assert stream_id not in self.stream_ids
            self.stream_ids.add(stream_id)

    def _run_action(self, action, stream_id):
        try:
            action(stream_id)
        except priority.MissingStreamError:
            assert stream_id not in self.stream_ids
        except priority.PseudoStreamError:
            assert stream_id == 0
        else:
            assert stream_id in self.stream_ids

    @rule(stream_id=st.integers())
    def remove_stream(self, stream_id):
        self._run_action(self.tree.remove_stream, stream_id)
        self.stream_ids.discard(stream_id)

    @rule(stream_id=st.integers())
    def block_stream(self, stream_id):
        self._run_action(self.tree.block, stream_id)
        if (stream_id != 0) and (stream_id in self.stream_ids):
            self.blocked_stream_ids.add(stream_id)

    @rule(stream_id=st.integers())
    def unblock_stream(self, stream_id):
        self._run_action(self.tree.unblock, stream_id)
        self.blocked_stream_ids.discard(stream_id)

    @rule()
    def tree_advances_unless_all_streams_are_blocked(self):
        """There is always a next stream unless every stream is blocked."""
        try:
            next(self.tree)
        except priority.DeadlockError:
            assert len(self.blocked_stream_ids) == len(self.stream_ids) - 1


TestPriorityQueueStateful = PriorityQueue.TestCase
