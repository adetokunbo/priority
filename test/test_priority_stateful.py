from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, rule

import priority


class PriorityQueue(RuleBasedStateMachine):

    def __init__(self):
        super(PriorityQueue, self).__init__()
        self.tree = priority.PriorityTree()
        self.stream_ids = [0]

    @rule(stream_id=st.integers())
    def insert_stream(self, stream_id):
        try:
            self.tree.insert_stream(stream_id)
        except priority.DuplicateStreamError:
            assert stream_id in self.stream_ids
        else:
            assert stream_id not in self.stream_ids
            self.stream_ids.append(stream_id)


TestPriorityQueueStateful = PriorityQueue.TestCase
