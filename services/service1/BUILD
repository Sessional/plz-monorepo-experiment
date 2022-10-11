subinclude("//terraform:terraform")

terraform_root(
    name = TERRAFORM_TARGET,
    srcs = glob("**.tf", "modules/module1/**.tf") + glob("backends/**.tfbackend") + glob("variables/**.tfvars"),
    modules = ["//platform-team/modules/module1:terraform", "//services/service1/modules/module1:terraform"]
)
