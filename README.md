# plz-monorepo-experiment

This mono repo lifts a bit of code from the [pleasings](https://github.com/thought-machine/pleasings) repository in regards to the terraform rules.

The primary goal of this experiment is to explore a monorepo set up in such a manner that discovery of dependencies is simpler and building a container that can apply terraform for a given application (see [CNABs](https://cnab.io/)) can be trivialized without recurring Dockerfile overhead.

It chooses to ignore managing terraform binaries and providers, and also ignores managing remote repositories. These are things that are trivially done during the init phase regardless of method that is bundled. This means it is not fully hermetic like please is designed for.

## Using the terraform build rules

Include `subinclude("//terraform:terraform")` in your `BUILD` file.

### Defining custom configs

There's an opinionated set up about how environments are bundled that matches the use case [I've] encountered most commonly in the workplace. The defaults
for this opinionated workflow provide only two environments (development and production). It may be preferable to override them to add an additional one,
which is also very common.

`opt_environment` is essentially an alias to set what your default environment should be. When running `please`, and not including `-c` as an option, `opt`
appears to be the default `-c`. One can run with a specific configuration by specifying `plz run //services/service1:terraform_destroy -c production`.
In the case this monorepo is structured around, this would be considered a power user technique, as most engineers do not need to be playing with production.

```
terraform_root(
    name = "terraform",
    srcs = glob("**.tf"),
    modules = ["//platform-team/modules/module1:terraform"],
    opt_environment = "development",
    environment_configs = {
        "development": {
            "var-files": ["variables/development.tfvars"],
            "backend-files": ["backends/development.tfbackend"]
        },
        "production": {
            "var-files": ["variables/production.tfvars"],
            "backend-files": ["backends/production.tfbackend"]
        }
    }
)
```

In the situation where one does NOT want opinionated workflows added (the environment ones above), one can just pass the following flag
into the terraform_root rule and they will be left out. Leaving out the opinionated flag does not remove the ability to prove extra inputs with `--`.

```
add_opinionated_workflows = False,
```

### Creating a terraform root
The terraform root is the directory that is intended to be utilized for running terraform.

```
terraform_root(
    name = "terraform",
    srcs = glob("**.tf"),
    modules = ["//platform-team/modules/module1:terraform"]
)
```

### Creating a terraform module
The terraform module is a reusable chunk of terraform that can be included as a dependency in multiple terraform roots.

```
terraform_module(
    name = "terraform",
    srcs = glob("**.tf"),
    visibility = ["PUBLIC"]
)
```

### Running tasks

Sub-tasks are added to the `terraform_module` target. In this case, since the `name` is `terraform`, the subtasks are located at `terraform_plan`, `terraform_apply`, `terraform_destroy` and `terraform_validate`.

```
> plz run //services/service1:terraform_plan
Initializing modules...
- module1 in platform-team/modules/module1

Initializing the backend...

Initializing provider plugins...
- Finding latest version of hashicorp/null...
- Installing hashicorp/null v3.1.1...
- Installed hashicorp/null v3.1.1 (signed by HashiCorp)

Terraform has created a lock file .terraform.lock.hcl to record the provider
selections it made above. Include this file in your version control repository
so that Terraform can guarantee to make the same selections by default when
you run "terraform init" in the future.

Terraform has been successfully initialized!

You may now begin working with Terraform. Try running "terraform plan" to see
any changes that are required for your infrastructure. All Terraform commands
should now work.

If you ever set or change modules or backend configuration for Terraform,
rerun this command to reinitialize your working directory. If you forget, other
commands will detect it and remind you to do so if necessary.

Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # module.module1.null_resource.resource1 will be created
  + resource "null_resource" "resource1" {
      + id = (known after apply)
    }

  # module.module1.null_resource.resource2 will be created
  + resource "null_resource" "resource2" {
      + id       = (known after apply)
      + triggers = {
          + "key" = "stuff"
        }
    }

Plan: 2 to add, 0 to change, 0 to destroy.
```

### Discovering consumers

```
> plz query revdeps //platform-team/modules/module1:terraform
//services/service1:terraform
```

### Discovering dependencies

```
> plz query deps //services/service1:terraform --exclude //_please:all --exclude //terraform:all
//services/service1:terraform
  //platform-team/modules/module1:terraform
```
### Building all terraform modules

```
plz build -i terraform_module
Build finished; total time 240ms, incrementality 0.0%. Outputs:
//platform-team/modules/module1:terraform:
  plz-out/gen/platform-team/modules/module1/terraform
//platform-team/modules/module2:terraform:
  plz-out/gen/platform-team/modules/module2/terraform
//services/service1/modules/module1:terraform:
  plz-out/gen/services/service1/modules/module1/terraform
```

### Building all terraform roots

```
plz build -i terraform_root
Build finished; total time 60ms, incrementality 92.9%. Outputs:
//services/service1:terraform:
  plz-out/gen/services/service1/_terraform
```

### Building all terraform

```
plz build -i terraform
Build finished; total time 40ms, incrementality 100.0%. Outputs:
//platform-team/modules/module1:terraform:
  plz-out/gen/platform-team/modules/module1/terraform
//platform-team/modules/module2:terraform:
  plz-out/gen/platform-team/modules/module2/terraform
//services/service1:terraform:
  plz-out/gen/services/service1/_terraform
//services/service1/modules/module1:terraform:
  plz-out/gen/services/service1/modules/module1/terraform
```

## Notable quirks:

Module source paths: The module source paths are relative to the monorepo root (`.plzconfig` file) if targeting a module defined by the `terraform_module` rule. Module source paths are relative to the current working directory if targeting a module that is in the application folder.

rule name: there is baked in assumptions that the rule names used across the board for all `terraform_roots` and `terraform_modules` is the same. By default it expects `terraform`, but it can be configured by setting the build config `terraform-target`.

## Pre-reqs

- If the please wrapper (pleasew) does not work, install please from the [website.](https://please.build/index.html)
- A working version of terraform must be installed


## examples

### Module referencing another module
```
subinclude("//terraform:terraform")

terraform_module(
    name = "terraform",
    srcs = glob("**.tf"),
    deps = ["//platform-team/modules/module2:terraform"], # reference the terraform_module target
    visibility = ["PUBLIC"]
)
```

### Using a local module without defining it as a terraform_module

```
terraform_root(
    name = "terraform",
    srcs = glob("**.tf", "modules/module1/**.tf"), # include it with glob, be sure to exclude the things included with modules
    #srcs = glob("*.tf") + glob("modules/module2/*.tf"), could also choose to be more picky with the globbing instead of excluding
    modules = ["//platform-team/modules/module1:terraform", "//services/service1/modules/module1:terraform"]
)
```

### Defining a module with no folder hierachy

```
subinclude("//terraform:terraform")

terraform_module(
    name = "terraform",
    srcs = glob("**.tf"),
    visibility = ["PUBLIC"]
)
```

### Defining a terraform root

```
subinclude("//terraform:terraform")

terraform_root(
    name = "terraform",
    srcs = glob("**.tf", "modules/module1/**.tf"),
    modules = ["//platform-team/modules/module1:terraform", "//services/service1/modules/module1:terraform"]
)
```

## User inputs

User inputs can be provided to `please` by using `--` after the command and providing any additional input, everything will be forwarded to the command.

```
plz run //services/service1:terraform_plan -c development -- --var-file fail.tfvars
Initializing modules...

Initializing the backend...

Initializing provider plugins...
- Reusing previous version of hashicorp/null from the dependency lock file
- Using previously-installed hashicorp/null v3.1.1

Terraform has been successfully initialized!

You may now begin working with Terraform. Try running "terraform plan" to see
any changes that are required for your infrastructure. All Terraform commands
should now work.

If you ever set or change modules or backend configuration for Terraform,
rerun this command to reinitialize your working directory. If you forget, other
commands will detect it and remind you to do so if necessary.
╷
│ Error: Failed to read variables file
│
│ Given variables file fail.tfvars does not exist.
╵
```

## Breaking out of plz

While not desired for the standard workflow, sometimes you REALLY just need to get at the root commands and files... `please` makes this VERY easy,
since it generates output files that are accessible. The `_terraform` directory may change if you opt to modify the target labels from `:terraform`.

```
cd plz-out/gen/services/service1/_terraform
terraform plan -var-file variables/dev.tfvars
```

## Things still missing
Building a docker container with the terraform (think CNAB), so one can run `terraform apply` via a docker container with all the terraform set up.
Can be worked around by using the generated folder for building a docker container.

Try to remove baked in dependency on a defined out folder label (`terraform-target`).
