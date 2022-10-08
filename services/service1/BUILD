subinclude("//terraform:terraform")

terraform_root(
    name = "terraform",
    srcs = glob("**.tf", "modules/module1/**.tf"),
    modules = ["//platform-team/modules/module1:terraform", "//services/service1/modules/module1:terraform"]
)
