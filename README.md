# University Final Year Project
This is the Artifact for my Final Year Project for my degree, "Computer Systems and Network Engineering" at Solent Southampton University. 


## Objective
The objective of this Git Repository is to create a working flow from collecting data from network devices, to alerting when issues occur, to utilising an AI agent utilising a large language model (LLM), such as ChatGPT.

Once the Minimal Viable Product (MVP) is complete, there will be a test of multple types of LLMs and an evaluation of which ones were better and why.


## Future Ideas for this project. 
As an engineer, there are many routes I want to explore once I have built out a minimal viable product. The first is the use of different LLMs and seeing the results. The second is using other types of artificial intelligence, such as the following:
    - Graphical Neural Networks (GNN).
    - LLM and Retrieval-Augmented Generation (RAG).
    - Fine Tuning.


## Documentation
All the documentation will be put into the documents folder. Here is a brief explanation of each document:
- For more information on the process of this project, look at ["process.md"](./documents/process.md)
- For more information on the architecture of this project, look at ["architecture.md"](./documents/architecture.md)
- To see the network configuration used for this project, look at ["network_config.md"](./documents/network_config.md)
- To see a drawio diagram of the new architecture, look at ["architecture.md"](./documents/architecture.drawio)


## How to use
For this project, you will need to do the following steps.

Note - you will need to change the testbed data in "agent/ai/testbed" and "data_collecter/code/device/*" to your specific needs.

### Step 1 - Download the requirements
For this project, you will need to download dependencies for running the API and calling Ollama locally.
```bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

### Step 2 - Docker Compose
```bash
make docker
```
This will run the three containers, "data_collecter", "InfluxDB" and "Grafana".

### Step 3 - FastAPI
```bash
make api
```
This will run the API locally on your computer.

### Step 4 - Ollama
```bash
ollama serve
```
This will turn on the Ollama server locally on your laptop, allowing for the API to communicate with it. Within the file "agent/ai/llm.py" file, you can add in whatever LLM you want to use. Ensure the LLM is downloaded locally on your laptop before using.s

### Step 5 - Configure the Network
```bash
make default
make ospf/bgp #OSPF or BGP
```
This will configure the two network devices with the basic configuration that was used for this project on two network devices.

### NOTE
This project was tested on by the below commands on router-1. Depending on what LLM model you use, will differ the result you get on analyzation of issue and configuration of solution. Qwen2.5:14b worked seamlessly for this project.
```bash
router bgp 1
neighbor 100.100.100.2 shutdown
```