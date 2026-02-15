import unittest

from google.protobuf.timestamp_pb2 import Timestamp

from ry_proto_utils import increment_timestamp


class BasicTest(unittest.TestCase):
    def test_increment_timestamp(self) -> None:
        timestamp = Timestamp(seconds=1, nanos=0)
        output = increment_timestamp(1.5, timestamp)
        self.assertEqual(output.seconds, 2)
