# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: server/proto/auth.proto
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
    'server/proto/auth.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x17server/proto/auth.proto\"5\n\x0fRegisterRequest\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x10\n\x08password\x18\x02 \x01(\t\"\x12\n\x10RegisterResponse\"2\n\x0cLoginRequest\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x10\n\x08password\x18\x02 \x01(\t\"\x0f\n\rLoginResponse2f\n\x0b\x41uthService\x12/\n\x08Register\x12\x10.RegisterRequest\x1a\x11.RegisterResponse\x12&\n\x05Login\x12\r.LoginRequest\x1a\x0e.LoginResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'server.proto.auth_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_REGISTERREQUEST']._serialized_start=27
  _globals['_REGISTERREQUEST']._serialized_end=80
  _globals['_REGISTERRESPONSE']._serialized_start=82
  _globals['_REGISTERRESPONSE']._serialized_end=100
  _globals['_LOGINREQUEST']._serialized_start=102
  _globals['_LOGINREQUEST']._serialized_end=152
  _globals['_LOGINRESPONSE']._serialized_start=154
  _globals['_LOGINRESPONSE']._serialized_end=169
  _globals['_AUTHSERVICE']._serialized_start=171
  _globals['_AUTHSERVICE']._serialized_end=273
# @@protoc_insertion_point(module_scope)
