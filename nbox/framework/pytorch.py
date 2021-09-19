# this file has the utilities and functions required for processing pytorch items
# such as conversion to ONNX, getting the metadata and so on.

import torch


def get_meta(
    input_names,
    input_shapes,
    args,
    output_names,
    output_shapes,
    outputs,
):
    # get the meta object
    def __get_struct(names_, shapes_, tensors_):
        return {
            name: {
                "dtype": str(tensor.dtype),
                "tensorShape": {"dim": [{"name": "", "size": x} for x in shapes], "unknownRank": False},
                "name": name,
            }
            for name, shapes, tensor in zip(names_, shapes_, tensors_)
        }

    meta = {"inputs": __get_struct(input_names, input_shapes, args), "outputs": __get_struct(output_names, output_shapes, outputs)}

    return meta


def export_to_onnx(
    model,
    args,
    outputs,
    onnx_model_path,
    input_names,
    dynamic_axes,
    output_names,
    export_params=True,
    verbose=False,
    opset_version=12,
    do_constant_folding=True,
    use_external_data_format=False,
    **kwargs
):
    torch.onnx.export(
        model,
        args=args,
        f=onnx_model_path,
        input_names=input_names,
        verbose=verbose,
        output_names=output_names,
        use_external_data_format=use_external_data_format,  # RuntimeError: Exporting model exceed maximum protobuf size of 2GB
        export_params=export_params,  # store the trained parameter weights inside the model file
        opset_version=opset_version,  # the ONNX version to export the model to
        do_constant_folding=do_constant_folding,  # whether to execute constant folding for optimization
        dynamic_axes=dynamic_axes,
    )
    meta = get_meta(input_names, args, output_names, outputs)
    return meta


def export_to_torchscript(model, args, outputs, torchscript_model_path, input_names, output_names, **kwargs):
    traced_model = torch.jit.trace(model.model, args, check_tolerance=0.0001)
    torch.jit.save(traced_model, torchscript_model_path)
    meta = get_meta(input_names, args, output_names, outputs)
    return meta
