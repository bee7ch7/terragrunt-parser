
import yaml
import os

from functions.get_only_changed_folders import get_only_changed_folders
from functions.download_and_unzip import download_and_unzip
from functions.get_terragrunt_groups import get_terragrunt_groups
from functions.args_parser import parse_arguments

args = parse_arguments()

terragrunt_input_file = args.path
image_version = args.image_version
expire_in = args.expire_in
only_changed_folders = args.only_changed_folders
before_script = { "before_script": args.before_script }
when_validate = args.validate
when_plan = args.plan
when_apply = args.apply

if args.tf_version:
    download_and_unzip(args.tf_version, "/tmp/terraform.zip", "/app")
if args.tg_version:
    download_and_unzip(args.tg_version, "/app/terragrunt", False)

# Parse the content and create the desired object

if only_changed_folders:
    repository_path = only_changed_folders[0]
    source_branch = only_changed_folders[1] #os.getenv('GITHUB_SHA', 'origin/feature/tests')
    target_branch = only_changed_folders[2] #'origin/main'
    
    terragrunt_groups = get_only_changed_folders(repository_path, source_branch, target_branch)
    print(terragrunt_groups)
else:
    terragrunt_groups = get_terragrunt_groups(terragrunt_input_file)

transformed_object = {"stages": []}

region = os.environ.get("REGION", None)
env_name = os.environ.get("ENV_NAME", "dev")

for group, paths in terragrunt_groups.items():
    for path in paths:
        index = path.find(env_name)
        module_name = path[path.find(env_name):] if env_name in path else path
        region = region
        env_name = env_name

        for type in ["validate", "plan", "apply", "destroy"]:

            if type == "validate":
                when = {"when": when_validate}

            elif type == "plan":
                when = {"when": when_plan}

            elif type == "apply":
                when = {"when": when_apply}

            else:
                when = {}

            entry = {
                "name": f"{type}-{group}-{module_name}",
                "stage": f"{type}-{group}",
                "terragrunt_path": path,
                "region": region,
                "env_name": env_name,
            }

            if type != "destroy":
                entry = {**entry, **when}

            transformed_object["stages"].extend([
                entry
            ])


find_stages = []
for k in transformed_object["stages"]:
    find_stages.append(k["stage"])

all_stages = list(set(find_stages))

validate_all = {}
plan_all = {}
apply_all = {}
destroy_all = {}

for stage in transformed_object["stages"]:
    if "validate-" in stage["name"]:
        validate_job = {
                stage["name"]: {
                "stage": "validate-all",
                "variables": {},
                "script": [
                    "env",
                    "cd {}".format(stage["terragrunt_path"]),
                    "terragrunt run-all validate --terragrunt-non-interactive"
                ],
                "rules": [
                    {
                        "when": stage["when"]
                    }
                ]
            }
        }

        validate_all = {**validate_all, **validate_job}

    if "plan-" in stage["name"]:

        plan_artifact = "$CI_PIPELINE_IID-{}.plan".format(stage["name"].replace("/", "-"))
        plan_job = {
                stage["name"]: {
                "stage": stage["stage"],
                "variables": {},
                "script": [
                    "cd {}".format(stage["terragrunt_path"]),
                    "terragrunt plan --terragrunt-non-interactive -out {}/{}".format("$(pwd)", plan_artifact),
                ],
                "artifacts": {
                    "name": plan_artifact,
                    "paths": [
                        "{}/{}".format(stage["terragrunt_path"], plan_artifact)
                    ],
                    "expire_in": expire_in
                },
                "needs": [
                    stage["name"].replace("plan", "validate")
                ],
                "rules": [
                    {
                        "when": stage["when"]
                    }
                ]
            }
        }

        plan_all = {**plan_all, **plan_job}

    if "apply-" in stage["name"]:
        plan_artifact = "$CI_PIPELINE_IID-{}.plan".format(stage["name"].replace("apply", "plan").replace("/", "-"))
        apply_job = {
                stage["name"]: {
                "stage": stage["stage"],
                "variables": {},
                "script": [
                    "cd {}".format(stage["terragrunt_path"]),
                    "ls",
                    "terragrunt apply {}/{}  --terragrunt-non-interactive".format("$(pwd)", plan_artifact),
                ],
                "artifacts": {
                    "name": plan_artifact,
                    "paths": [
                        "{}/{}".format(stage["terragrunt_path"], plan_artifact)
                    ],
                    "expire_in": expire_in
                },
                "needs": [
                    stage["name"].replace("apply", "plan")
                ],
                "rules": [
                    {
                        "when": stage["when"]
                    }
                ]
            }
        }

        apply_all = {**apply_all, **apply_job}
        
    if "destroy-" in stage["name"]:
        destroy_job = {
                stage["name"]: {
                "stage": stage["stage"],
                "variables": {},
                "script": [
                    "cd {}".format(stage["terragrunt_path"]),
                    "terragrunt destroy --terragrunt-non-interactive"
                ],
                "rules": [
                    {
                        "if": '$DESTROY_ENABLED == "false"',
                        "when": "never"
                    },
                    {
                        "if": '$DESTROY_ENABLED == "true"',
                        "when": "manual"
                    }   
                ]
            }
        }

        destroy_all = {**destroy_all, **destroy_job}

def custom_sort(item):
    parts = item.split('-')
    return (int(parts[-1]), parts[:-1])

plan = sorted([value for value in all_stages if "plan" in value], key=custom_sort)
apply = sorted([value for value in all_stages if "apply" in value], key=custom_sort)
destroy = sorted([value for value in all_stages if "destroy" in value], key=custom_sort)


ordered_stages = ["validate-all"]
for i in range(len(plan)):
    ordered_stages.extend([plan[i],  apply[i], destroy[i]])

pipeline = {
    "image": {
        "name": f"{image_version}",
        "pull_policy": "always",
    },
    "stages": ordered_stages
}


tags = os.environ.get("RUNNERS", None)

if before_script is not None:
    pipeline = {**pipeline, **before_script}

if tags is not None:
    tags = {"tags": tags.split(",")}
    pipeline = {**pipeline, **tags}

pipeline = {**pipeline, **validate_all, **plan_all, **apply_all, **destroy_all}

yaml_output = yaml.dump(pipeline, sort_keys=False) 

out_path = args.out_path if args.out_path else f"/app/gitlab-{env_name}-{region}.yml"

with open(out_path, "w") as save_downstream_pipeline:
    save_downstream_pipeline.write(yaml_output)
