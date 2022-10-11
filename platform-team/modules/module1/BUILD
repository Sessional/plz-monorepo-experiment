subinclude("//terraform:terraform")

terraform_module(
    name = TERRAFORM_TARGET,
    srcs = glob("**.tf"),
    deps = ["//platform-team/modules/module2:terraform"],
    visibility = ["PUBLIC"]
)
