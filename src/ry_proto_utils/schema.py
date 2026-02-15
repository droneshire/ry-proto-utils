import typing as T

from google.protobuf.descriptor_pb2 import DescriptorProto, FileDescriptorProto, FileDescriptorSet

JsonType = T.Union[str, dict[str, T.Any]]


def process_proto_message(
    message: DescriptorProto, file_descriptor: FileDescriptorProto
) -> dict[str, T.Any]:
    schema: dict[str, T.Any] = {}
    for field in message.field:
        json_type: JsonType

        if field.type in (1, 2):
            json_type = "number"
        elif field.type in (3, 4, 5, 13, 17, 18):
            json_type = "integer"
        elif field.type == 9:
            json_type = "string"
        elif field.type == 11:
            json_type = "object"
        elif field.type == 14:
            json_type = "enum"
        else:
            json_type = "string"

        if field.label == 3:
            json_type = {"type": "array", "items": {"type": json_type}}

        if field.type == 11:
            nested_name = field.type_name.split(".")[-1]
            nested_message = next(
                (m for m in file_descriptor.message_type if m.name == nested_name),
                None,
            )
            schema[field.name] = (
                process_proto_message(nested_message, file_descriptor)
                if nested_message
                else {"type": "object"}
            )
        else:
            schema[field.name] = json_type

    return schema


def proto_to_schema(descriptor_file: str, message_name: str) -> dict[str, T.Any]:
    fds = FileDescriptorSet()
    with open(descriptor_file, "rb") as infile:
        fds.ParseFromString(infile.read())

    message = None
    file_descriptor = None
    for current_file_descriptor in fds.file:
        for msg in current_file_descriptor.message_type:
            if msg.name == message_name:
                message = msg
                file_descriptor = current_file_descriptor
                break
        if message is not None:
            break

    if message is None or file_descriptor is None:
        raise ValueError(f"Message {message_name} not found in descriptor file")

    return process_proto_message(message, file_descriptor)
