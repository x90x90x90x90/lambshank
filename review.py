#!/usr/bin/env python
#
# AWS Lambda Code Grabber
# v1.0 - TJ
#
# Grab all Lambda code bases in one mighty swoop
# Yes yes, it is just a wrapper around aws :)
#
import os
import sys
import subprocess
import errno
import json
import argparse

# Requirements
AWS="/usr/local/bin/aws"
JQ="/usr/bin/jq"

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

             \033[0;32mLambshank v1.0 
       Lambda Functions Downloader\033[0m


""")


def setvars(profile, region):
    if profile is not None:
        profile = " --profile " + profile
    else:
        profile = ""
    if region is not None:
        region = " --region " + region
    return(profile,region)

def createbase():
    print("Making Functions Directory: " + FUNDIR)
    try:
        os.mkdir(FUNDIR)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            print("Working directory exists... exiting")
            sys.exit()
    try:
        os.chdir(FUNDIR)
        print("Current working directory: {0}".format(os.getcwd()))
    except FileNotFoundError:
        print("Directory: {0} does not exist".format(path))
    except NotADirectoryError:
        print("{0} is not a directory".format(path))
    except PermissionError:
        print("You do not have permissions to change to {0}".format(path))

def checkident(profile,region):
    print("Checking all our ducks are in a row, verifying STS identity:")
    sts = subprocess.check_output(AWS + profile + region  + " sts get-caller-identity", shell=True);
    print("\n" + str(json.loads(sts)))
    checksts = input('\nEverything look good? (y/n):').lower()
    if checksts.startswith('y'):
        pass
    else:
        print("ok buhbye")
        sys.exit()

def listfunctions(profile,region):
    print("Listing discovered functions:")
    funcs = subprocess.check_output(AWS + profile + region + " lambda list-functions --output json | "+JQ+" '.Functions[].FunctionName' | sed 's/\"//g' >> all-lambda-functions.txt", shell=True);


def pullfunctions(profile,region):
    file = open("all-lambda-functions.txt","r")
    line = file.readline().rstrip('\n')
    while line:
        print("Pulling function config: " + line)
        os.mkdir(line)
        os.chdir(line)
        getfunc = subprocess.check_output(AWS + profile + region + " lambda get-function --function " + line + "  >> function-config.txt", shell=True);
        os.chdir("..")
        line = file.readline().rstrip('\n')

    file.close()


def pullcode():
    file = open("all-lambda-functions.txt","r")
    line = file.readline().rstrip('\n')
    while line:
        print("Pulling function code: " + line)
        os.chdir(line)
        getcodeurl = subprocess.check_output(JQ + "  '.Code.Location' function-config.txt | sed 's/\"//g' >> function-codeurl.txt", shell=True);
        getcode = subprocess.check_output("wget -i function-codeurl.txt -O function-code.zip", shell=True);
        os.chdir("..")
        line = file.readline().rstrip('\n')

    file.close()


if __name__ == "__main__":

    banner()

    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", help="Specify a specific profile")
    parser.add_argument("--region", help="Specify a specific region", required=True)
    args = parser.parse_args()

    profile, region = setvars(args.profile, args.region)

    createbase()
    
    checkident(profile,region)

    listfunctions(profile,region)

    pullfunctions(profile,region)
    
    pullcode()

