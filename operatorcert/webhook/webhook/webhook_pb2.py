# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: webhook/webhook.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from operatorcert.webhook.marketplace import pc_api_pb2 as pyxis_dot_pc__api__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
    name="webhook/webhook.proto",
    package="marketplace.redhat.com.package.certification",
    syntax="proto3",
    serialized_options=b"Z1redhat-marketplace/pipeline-mirroring/rpc/webhook",
    create_key=_descriptor._internal_create_key,
    serialized_pb=b'\n\x15webhook/webhook.proto\x12,marketplace.redhat.com.package.certification\x1a\x12pyxis/pc_api.proto\x1a\x1bgoogle/protobuf/empty.proto"P\n\x19NewOperatorBundlesRequest\x12\x33\n\x04\x64\x61ta\x18\n \x03(\x0b\x32%.pyxis.redhat.com.package.pc_api.Data2\x86\x01\n\rMirrorService\x12u\n\x12NewOperatorBundles\x12G.marketplace.redhat.com.package.certification.NewOperatorBundlesRequest\x1a\x16.google.protobuf.EmptyB3Z1redhat-marketplace/pipeline-mirroring/rpc/webhookb\x06proto3',
    dependencies=[
        pyxis_dot_pc__api__pb2.DESCRIPTOR,
        google_dot_protobuf_dot_empty__pb2.DESCRIPTOR,
    ],
)


_NEWOPERATORBUNDLESREQUEST = _descriptor.Descriptor(
    name="NewOperatorBundlesRequest",
    full_name="marketplace.redhat.com.package.certification.NewOperatorBundlesRequest",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name="data",
            full_name="marketplace.redhat.com.package.certification.NewOperatorBundlesRequest.data",
            index=0,
            number=10,
            type=11,
            cpp_type=10,
            label=3,
            has_default_value=False,
            default_value=[],
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=120,
    serialized_end=200,
)

_NEWOPERATORBUNDLESREQUEST.fields_by_name[
    "data"
].message_type = pyxis_dot_pc__api__pb2._DATA
DESCRIPTOR.message_types_by_name[
    "NewOperatorBundlesRequest"
] = _NEWOPERATORBUNDLESREQUEST
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

NewOperatorBundlesRequest = _reflection.GeneratedProtocolMessageType(
    "NewOperatorBundlesRequest",
    (_message.Message,),
    {
        "DESCRIPTOR": _NEWOPERATORBUNDLESREQUEST,
        "__module__": "webhook.webhook_pb2"
        # @@protoc_insertion_point(class_scope:marketplace.redhat.com.package.certification.NewOperatorBundlesRequest)
    },
)
_sym_db.RegisterMessage(NewOperatorBundlesRequest)


DESCRIPTOR._options = None

_MIRRORSERVICE = _descriptor.ServiceDescriptor(
    name="MirrorService",
    full_name="marketplace.redhat.com.package.certification.MirrorService",
    file=DESCRIPTOR,
    index=0,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
    serialized_start=203,
    serialized_end=337,
    methods=[
        _descriptor.MethodDescriptor(
            name="NewOperatorBundles",
            full_name="marketplace.redhat.com.package.certification.MirrorService.NewOperatorBundles",
            index=0,
            containing_service=None,
            input_type=_NEWOPERATORBUNDLESREQUEST,
            output_type=google_dot_protobuf_dot_empty__pb2._EMPTY,
            serialized_options=None,
            create_key=_descriptor._internal_create_key,
        ),
    ],
)
_sym_db.RegisterServiceDescriptor(_MIRRORSERVICE)

DESCRIPTOR.services_by_name["MirrorService"] = _MIRRORSERVICE

# @@protoc_insertion_point(module_scope)
