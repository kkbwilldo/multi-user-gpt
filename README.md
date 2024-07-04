# Multi-User-GPT                   

A simple package to interact with OpenAI's GPT-4 with multiple users by sharing a terminal context.             
                      
Developed by:                       
- Kyubin Kim (a.k.a kbkim)           
- kimkyu1515@naver.com
                
## Note              
                 
This package supports zsh only. If you are using bash, you can modify the package to work with bash.         
There is nothing special about zsh. I just developed this package with zsh.

## Installation                   
                  
```bash
# install the package
$ pip install .
# source your run commands
$ source ~/.zshrc
```

## Requirements

### OpenAI API Key

You need to have an OpenAI API key to use this package. You can get one by signing up at [OpenAI](https://platform.openai.com/signup).              
Or you can use other LLMs by modifying `mug_core/api.py`        

### Optional: AWS account for S3 bucket

You can use an S3 bucket to store the session logs. If you want to use an S3 bucket, you need to have an AWS account and an S3 bucket. You can create an S3 bucket by following the instructions [here](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html).                  
But this is optional. You can use the package without an S3 bucket. And all the logs will be stored locally.                                
                 
## Usage                  

The session cycle is as follows:                         
1. Start a new session with `mug --start`                         
2. Use the prefix `mug` to your linux commands to log them to the session                      
3. End the session with `mug --end` to unset the environment variables and functions                       


### `mug --start`

This command will start a new session and set the environment variables and functions required for the session.

```bash
$ mug --start
```

### `mug ${complex command}`

This command will log the input command and the output of the input command to the session.

```bash
$ mug ls -l
```

### `mug --llm "your prompt to ChatGPT or local machine"`

This command will request a response to the prompt from ChatGPT or the local machine.

```bash
$ mug --llm "What is the capital of France?"
```

### `mug --content "your prompt to ChatGPT or local machine"`

This command will request a response to the prompt based on the session log from ChatGPT or the local machine.

```bash
$ mug python index_error.py
Traceback (most recent call last):
  File "index_error.py", line 10, in <module>
    cause_index_error()
  File "index_error.py", line 6, in cause_index_error
    return lst[5]
IndexError: list index out of range
$ mug --content "why does an 'out of range' error occur here??"
```

### `mug --end`

This command will end the session and unset the environment variables and functions.

```bash
$ mug --end
```

