#!/usr/bin/env python
#
# AWS Lambda Code Grabber
# v1.0 - TJ - Initial version!
# v2.0 - TJ - New version after months of guilt for not using boto
# Grab all Lambda code bases in one mighty swoop
# 
#
import errno
import os
import sys
import argparse
import boto3
from botocore.config import Config
import requests

# Define the directory that's going to store all this
FUNDIR="functions"



##### Get awf my land  ######

def banner():
    print("""
           __  _
       .-.'  `; `-._  __  _
      (_,         .-:'  `; `-._
    ,'o"(        (_,           )
   (__,-'      ,'o"(            )>
      (       (__,-'            )
       `-'._.--._(             )
          |||  |||`-'._.--._.-'
                     |||  |||

             \033[0;32mLambshank v2.0 
       Lambda Functions Downloader\033[0m


""")


def create_base():
    print("Making Functions Directory: " + FUNDIR)
    try:
        os.mkdir(FUNDIR)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            print("Working directory exists... exiting")
            sys.exit()
    try:
        os.chdir(FUNDIR)
        #print("Current working directory: {0}".format(os.getcwd()))
    except FileNotFoundError:
        print("Directory: {0} does not exist".format(path))
    except NotADirectoryError:
        print("{0} is not a directory".format(path))
    except PermissionError:
        print("You do not have permissions to change to {0}".format(path))

def check_ident():
    print("\033[0;32mChecking all our sheep are in a row, verifying STS identity:\033[0m")
    stsclient = boto3.client('sts', config=shank_config)
    sts = stsclient.get_caller_identity()
    print("""
	Access Key  = """ + sts['UserId'] + """
	AWS Account = """ + sts['Account'] + """
	User ARN    = """ + sts['Arn'] + """
""")

    checksts = input('\n\033[0;32mEverything look good? (y/n):\033[0m').lower()
    if not checksts.startswith('y'):
        print("ok buhbye")
        sys.exit()

def list_functions():
    print("\n\033[0;32mListing discovered functions:\033[0m")
    funcsclient = boto3.client('lambda', config=shank_config)
    funcs = funcsclient.list_functions()
    file = open("all-lambda-functions.txt", "w")
    for item in funcs['Functions']:
        print(item['FunctionName'])
        file.write(item['FunctionName']+"\n")
    file.close

def pull_functions():
    print("\n\033[0;32mPulling Function Configurations:\033[0m")
    file = open("all-lambda-functions.txt")
    line = file.readline().rstrip('\n')
    funcsclient = boto3.client('lambda', config=shank_config)


    while line:
        print("Pulling function config: " + line)
        os.mkdir(line)
        os.chdir(line)
        funcsdetail = funcsclient.get_function(FunctionName= line)
        #print(funcsdetail['Configuration']['FunctionName'])
        file2 = open(str(funcsdetail['Configuration']['FunctionName'])+".json", "w")
        file2.write(str(funcsdetail['Configuration']))
        file2.close
        os.chdir("..")
        line = file.readline().rstrip('\n')
    file.close()


def pull_code():
    print("\n\033[0;32mPulling Function Code:\033[0m")
    file = open("all-lambda-functions.txt")
    line = file.readline().rstrip('\n')
    codeclient = boto3.client('lambda', config=shank_config)
    while line:
        print("Pulling function code: " + line)
        codedetail = codeclient.get_function(FunctionName= line)
        os.chdir(line)
        codeurl = codedetail['Code']['Location']
        codefile = requests.get(codeurl)
        open(str(codedetail['Configuration']['FunctionName'])+".zip", 'wb').write(codefile.content)
        os.chdir("..")
        line = file.readline().rstrip('\n')

    file.close()

if __name__ == "__main__":

    banner()

    parser = argparse.ArgumentParser()
    parser.add_argument("--region", help="Specify a specific region", required=True)
    args = parser.parse_args()

    region = args.region

    shank_config = Config(
        region_name = region,
        retries = {
            'max_attempts': 10,
            'mode': 'standard'
        }
    )
    
    check_ident()
    
    create_base()

    list_functions()

    pull_functions()
    
    pull_code()

    print("\n\033[0;32mw00t w00t - all done:\033[0m")
