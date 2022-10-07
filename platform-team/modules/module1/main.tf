resource "null_resource" "resource2" {
  triggers = {
    key = var.a_string_variable
  }
}
