# Automated Web App Enumeration (Wapp Enum)

## Authors

- [Bhallamudi Sai Narasimha Abhiram](https://github.com/abhirambsn)

## Introduction

The Automated Web Application Enumeration Tool is a command-line tool that automates the process of web application enumeration. The tool takes a hostname and performs basic enumeration such as nmap scan, nikto scan, and directory busting. The tool can also execute custom Python scripts.

### Currently Working Enumeration Techniques

- [x] Nmap Scan
- [x] Nikto Scan
- [x] Directory Busting
- [ ] API Fuzzing
- [ ] Virtual Host Enumeration

## Installation

### Docker (Recommended)

This tool can also be used in a Docker container. To use the tool in Docker, follow the instructions below:

1. Clone the repository and build the image

```sh
git clone https://github.com/abhirambsn/wapp-enum.git
cd wapp-enum
```

```sh
docker build -f DockerFile .
```

**OR**

1. Pull from the docker registry

```sh
docker pull abhirambsn/wapp-enum:latest
```

2. Run the container

```sh
docker run -it --name abhirambsn/wapp-enum:latest <arguments here>
```

### Via Repo

1. Clone the repository

```sh
git clone https://github.com/abhirambsn/wapp-enum.git
cd wapp-enum
```

2. Create a new virtual environment to separate the dependencies

```sh
python -m virtualenv env
```

3. Install the Dependencies from the requirements.txt file

```sh
python -m pip install -r ./requirements.txt
```

4. Run the Command

```sh
python main.py <arguments here>
```

## Creating Custom Scripts

Follow the below steps to create your custom script

- If you want the script to run in a sequential manner, place the script into `scripts/default` directory with naming as `sequenceNo_name`, make sure the sequence number is **greater than 2**

- If you want the script to run parallely after the initial script sequence, place the script into `scripts/custom` directory with a meaningful name.

Once done with the naming, the python file should contain the following:

1. A `run` function that will run the script.
2. All parameters should be named as per the given convention, and they should be included in the definition of the `run` function, you can use other names for the helper function (if needed).
    - Host: `host`
    - Port: `port`
    - No. of Threads: `n_threads`
    - Wordlist Path: `wordlist`

## LICENSE

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
