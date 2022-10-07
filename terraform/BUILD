filegroup(
    name = "terraform",
    srcs = ["terraform.build_defs"],
    visibility = ["PUBLIC"],
)

python_binary(
    name = "prepare_workspace",
    main = "prepare_workspace/main.py",
    visibility = ["PUBLIC"],
    zip_safe = True,
) 

python_binary(
    name = "prepare_module",
    main = "prepare_module/main.py",
    visibility = ["PUBLIC"],
    zip_safe = True,
)
