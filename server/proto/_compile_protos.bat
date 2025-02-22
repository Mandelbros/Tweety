for %%f in (*.proto) do (
    python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. %%f
)