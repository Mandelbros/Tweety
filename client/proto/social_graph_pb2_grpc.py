# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

from proto import social_graph_pb2 as social__graph__pb2

GRPC_GENERATED_VERSION = '1.68.0'
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
        + f' but the generated code in social_graph_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class SocialGraphServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Follow = channel.unary_unary(
                '/SocialGraphService/Follow',
                request_serializer=social__graph__pb2.FollowRequest.SerializeToString,
                response_deserializer=social__graph__pb2.FollowResponse.FromString,
                _registered_method=True)
        self.Unfollow = channel.unary_unary(
                '/SocialGraphService/Unfollow',
                request_serializer=social__graph__pb2.UnfollowRequest.SerializeToString,
                response_deserializer=social__graph__pb2.UnfollowResponse.FromString,
                _registered_method=True)
        self.GetFollowers = channel.unary_unary(
                '/SocialGraphService/GetFollowers',
                request_serializer=social__graph__pb2.FollowersRequest.SerializeToString,
                response_deserializer=social__graph__pb2.FollowersResponse.FromString,
                _registered_method=True)
        self.GetFollowing = channel.unary_unary(
                '/SocialGraphService/GetFollowing',
                request_serializer=social__graph__pb2.FollowingRequest.SerializeToString,
                response_deserializer=social__graph__pb2.FollowingResponse.FromString,
                _registered_method=True)


class SocialGraphServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Follow(self, request, context):
        """RPC to follow a user
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Unfollow(self, request, context):
        """RPC to unfollow a user
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetFollowers(self, request, context):
        """RPC to get a list of followers
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetFollowing(self, request, context):
        """RPC to get a list of users the user is following
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_SocialGraphServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Follow': grpc.unary_unary_rpc_method_handler(
                    servicer.Follow,
                    request_deserializer=social__graph__pb2.FollowRequest.FromString,
                    response_serializer=social__graph__pb2.FollowResponse.SerializeToString,
            ),
            'Unfollow': grpc.unary_unary_rpc_method_handler(
                    servicer.Unfollow,
                    request_deserializer=social__graph__pb2.UnfollowRequest.FromString,
                    response_serializer=social__graph__pb2.UnfollowResponse.SerializeToString,
            ),
            'GetFollowers': grpc.unary_unary_rpc_method_handler(
                    servicer.GetFollowers,
                    request_deserializer=social__graph__pb2.FollowersRequest.FromString,
                    response_serializer=social__graph__pb2.FollowersResponse.SerializeToString,
            ),
            'GetFollowing': grpc.unary_unary_rpc_method_handler(
                    servicer.GetFollowing,
                    request_deserializer=social__graph__pb2.FollowingRequest.FromString,
                    response_serializer=social__graph__pb2.FollowingResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'SocialGraphService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('SocialGraphService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class SocialGraphService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Follow(request,
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
            '/SocialGraphService/Follow',
            social__graph__pb2.FollowRequest.SerializeToString,
            social__graph__pb2.FollowResponse.FromString,
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
    def Unfollow(request,
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
            '/SocialGraphService/Unfollow',
            social__graph__pb2.UnfollowRequest.SerializeToString,
            social__graph__pb2.UnfollowResponse.FromString,
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
    def GetFollowers(request,
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
            '/SocialGraphService/GetFollowers',
            social__graph__pb2.FollowersRequest.SerializeToString,
            social__graph__pb2.FollowersResponse.FromString,
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
    def GetFollowing(request,
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
            '/SocialGraphService/GetFollowing',
            social__graph__pb2.FollowingRequest.SerializeToString,
            social__graph__pb2.FollowingResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)