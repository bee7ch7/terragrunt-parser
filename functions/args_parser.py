import argparse

def parse_arguments():
  parser = argparse.ArgumentParser()

  parser.add_argument("--path", 
                      default="/app/terragrunt_init", 
                      help="Path to init file of terragrunt run-all init. Default: /app/terragrunt_init"
                      )

  parser.add_argument("-tf", "--tf-version", 
                      required=False, 
                      help="Terraform version, for example: 1.7.0"
                      )

  parser.add_argument("-tg", "--tg-version", 
                      required=False, 
                      help="Terragrunt version, for example: v0.50.14"
                      )

  parser.add_argument("-i", "--image-version",
                      default="bee7ch/terragrunt-parser:latest", 
                      required=False, 
                      help="Terragrunt parser docker image version. Default: bee7ch/terragrunt-parser:latest"
                      )

  parser.add_argument("-e", "--expire-in",
                      default="1 week", 
                      required=False, 
                      help="Artifact expiration for terraform plan"
                      )

  parser.add_argument("-v", "--validate",
                      default="always", 
                      required=False, 
                      help="When to run 'validate' command, always or manual"
                      )

  parser.add_argument("-p", "--plan",
                      default="manual", 
                      required=False, 
                      help="When to run 'plan' command, always or manual"
                      )

  parser.add_argument("-a", "--apply",
                      default="manual", 
                      required=False, 
                      help="When to run 'apply' command, always or manual"
                      )

  parser.add_argument("--only-changed-folders",
                      nargs=3,
                      metavar=('/path/to/git/repo', '"commit1 or source branch"', '"commit2 or target branch"'),
                      default=False, 
                      required=False, 
                      help="Find only changed terragrunt folders between two commits/branches"
                      )
  
  parser.add_argument("-bs", "--before-script", 
                      action="append",
                      required=False,
                      help="List of command for before_script in the pipeline"
                      )
  
  
  parser.add_argument("-o", "--out-path", 
                      required=False,
                      help="Path to save downstream pipeline configuration."
                      )
  

  return  parser.parse_args()