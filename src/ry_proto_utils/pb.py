import typing as T

from google.protobuf.internal.enum_type_wrapper import EnumTypeWrapper
from google.protobuf.message import Message
from google.protobuf.timestamp_pb2 import Timestamp


def get_enum_val_from_str(raw: str, enum_type: T.Any) -> T.Optional[int]:
    value = raw.strip().upper()
    if not isinstance(enum_type, EnumTypeWrapper):
        return None
    enum_val = enum_type.DESCRIPTOR.values_by_name.get(value)
    return None if enum_val is None else int(enum_val.number)


def increment_timestamp(incremental_time_seconds: float, timestamp_pb: Timestamp) -> Timestamp:
    timestamp_pb.nanos = timestamp_pb.nanos + int(
        (incremental_time_seconds - int(incremental_time_seconds)) * 1e9
    )
    if timestamp_pb.nanos >= 1e9:
        timestamp_pb.seconds += 1
        timestamp_pb.nanos -= int(1e9)

    timestamp_pb.seconds += int(incremental_time_seconds)
    return timestamp_pb


def get_all_field_names(
    message: Message | None, all_fields: list[str], fields: list[str] | None = None
) -> None:
    if message is None:
        return

    for field in fields or list(message.DESCRIPTOR.fields_by_name.keys()):
        try:
            descriptor = message.DESCRIPTOR.fields_by_name[field]
            all_fields.append(field)
            if descriptor.message_type:
                field_value = getattr(message, field)
                if field_value:
                    nested: list[str] = []
                    get_all_field_names(field_value, nested)
                    for item in nested:
                        all_fields.append(f"{field}.{item}")
        except KeyError:
            pass


def redact_fields(message: Message, redacted_fields: dict[str, bool]) -> None:
    for field_path, should_redact in redacted_fields.items():
        if not should_redact:
            continue

        parts = field_path.split(".")
        current: T.Any = message
        for part in parts[:-1]:
            if hasattr(current, part):
                current = getattr(current, part)
            else:
                current = None
                break

        if current is None:
            continue

        final_field = parts[-1]
        if hasattr(current, final_field):
            current.ClearField(final_field)
