from google.protobuf.timestamp_pb2 import Timestamp

from ry_proto_utils import increment_timestamp


def test_increment_timestamp() -> None:
    ts = Timestamp(seconds=1, nanos=0)
    out = increment_timestamp(1.5, ts)
    assert out.seconds == 2
