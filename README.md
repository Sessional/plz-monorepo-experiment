# plz-monorepo-experiment

This mono repo lifts a bit of code from the [pleasings](https://github.com/thought-machine/pleasings) repository in regards to the terraform rules.

The primary goal of this experiment is to explore a mono repo set up in such a manner that discovery of dependencies is simpler and building a container that can apply terraform for a given application (see [CNABs](https://cnab.io/)) can be trivialized without recurring Dockerfile overhead.

It chooses to ignore managing terraform binaries and providers, and also ignores managing remote repositories. These are things that are trivially done during the init phase regardless of method that is bundled.

## Using the terraform build rules

Include `subinclude("//terraform:terraform")` in your `BUILD` file.

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

## Notable quirks:

Module source paths: The module source paths are relative to the monorepo root (`.plzconfig` file) if targeting a module defined by the `terraform_module` rule. Module source paths are relative to the current working directory if targeting a module that is in the application folder.

rule name: there is baked in assumptions that the rule names used across the board for all `terraform_roots` and `terraform_modules` is the same. By default it expects `terraform`, but it can be configured by setting the build config `terraform-target`.

## Pre-reqs

- If the please wrapper (pleasew) does not work, install please from the [website.](https://please.build/index.html)


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

## Things still missing
Building a docker container with the terraform (think CNAB), so one can run `terraform apply` via a docker container with all the terraform set up.

Try to remove baked in dependency on a defined out folder label (`terraform-target`)

Allow user provided inputs (--var-file, --var) into the terraform workflow targets
