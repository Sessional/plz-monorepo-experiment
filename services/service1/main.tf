terraform {
  backend "local" {}
}

module "module1" {
  source            = "./platform-team/modules/module1"
  a_string_variable = var.module_string
}

module "module2" {
  source = "./services/service1/modules/module1"
}

module "local_module1" {
  source = "./modules/module2"
}
