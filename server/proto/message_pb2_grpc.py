# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from proto import message_pb2 as message__pb2

GRPC_GENERATED_VERSION = '1.70.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in message_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class MessageServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.PostMessage = channel.unary_unary(
                '/tweety.MessageService/PostMessage',
                request_serializer=message__pb2.PostMessageRequest.SerializeToString,
                response_deserializer=message__pb2.PostMessageResponse.FromString,
                _registered_method=True)
        self.GetMessages = channel.unary_unary(
                '/tweety.MessageService/GetMessages',
                request_serializer=message__pb2.GetMessagesRequest.SerializeToString,
                response_deserializer=message__pb2.GetMessagesResponse.FromString,
                _registered_method=True)
        self.RepostMessage = channel.unary_unary(
                '/tweety.MessageService/RepostMessage',
                request_serializer=message__pb2.RepostMessageRequest.SerializeToString,
                response_deserializer=message__pb2.RepostMessageResponse.FromString,
                _registered_method=True)


class MessageServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def PostMessage(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetMessages(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RepostMessage(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_MessageServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'PostMessage': grpc.unary_unary_rpc_method_handler(
                    servicer.PostMessage,
                    request_deserializer=message__pb2.PostMessageRequest.FromString,
                    response_serializer=message__pb2.PostMessageResponse.SerializeToString,
            ),
            'GetMessages': grpc.unary_unary_rpc_method_handler(
                    servicer.GetMessages,
                    request_deserializer=message__pb2.GetMessagesRequest.FromString,
                    response_serializer=message__pb2.GetMessagesResponse.SerializeToString,
            ),
            'RepostMessage': grpc.unary_unary_rpc_method_handler(
                    servicer.RepostMessage,
                    request_deserializer=message__pb2.RepostMessageRequest.FromString,
                    response_serializer=message__pb2.RepostMessageResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'tweety.MessageService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('tweety.MessageService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class MessageService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def PostMessage(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/tweety.MessageService/PostMessage',
            message__pb2.PostMessageRequest.SerializeToString,
            message__pb2.PostMessageResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def GetMessages(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/tweety.MessageService/GetMessages',
            message__pb2.GetMessagesRequest.SerializeToString,
            message__pb2.GetMessagesResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def RepostMessage(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/tweety.MessageService/RepostMessage',
            message__pb2.RepostMessageRequest.SerializeToString,
            message__pb2.RepostMessageResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
