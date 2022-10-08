resource "null_resource" "resource2" {
  triggers = {
    key = var.a_string_variable
  }
}

module "module_using_module2" {
  source = "./platform-team/modules/module2"
}
