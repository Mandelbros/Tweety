# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: server/proto/models.proto
# Protobuf Python Version: 5.28.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    28,
    1,
    '',
    'server/proto/models.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x19server/proto/models.proto\x12\x06tweety\"\x83\x01\n\x07Message\x12\x12\n\nmessage_id\x18\x01 \x01(\t\x12\x10\n\x08username\x18\x02 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x03 \x01(\t\x12\x11\n\ttimestamp\x18\x04 \x01(\t\x12\x11\n\tis_repost\x18\x05 \x01(\x08\x12\x1b\n\x13original_message_id\x18\x06 \x01(\t\"/\n\x04User\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x15\n\rpassword_hash\x18\x02 \x01(\t\"*\n\x0bUserFollows\x12\x1b\n\x13\x66ollowing_users_ids\x18\x01 \x03(\t\"!\n\tUserPosts\x12\x14\n\x0cmessages_ids\x18\x01 \x03(\tb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'server.proto.models_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_MESSAGE']._serialized_start=38
  _globals['_MESSAGE']._serialized_end=169
  _globals['_USER']._serialized_start=171
  _globals['_USER']._serialized_end=218
  _globals['_USERFOLLOWS']._serialized_start=220
  _globals['_USERFOLLOWS']._serialized_end=262
  _globals['_USERPOSTS']._serialized_start=264
  _globals['_USERPOSTS']._serialized_end=297
# @@protoc_insertion_point(module_scope)
