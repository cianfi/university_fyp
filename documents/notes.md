To curl the Telegraf Ingestion:
    curl -i -POST 'http://localhost:8080/telegraf' -d "fruits,location=store1 apple=2,kiwi=2,pineapple=2,rasberry=5"

To curl the Ollama container:
    curl -X POST localhost:11434/api/generate -H "Content-Type: application/json" -d '{"prompt": "what is 24 X 466 and why?", "stream": false, "model": "mistral"}'

To console onto router via terminal:
    screen /dev/tty.usbserial-A50285BI

To SSH onto the test router:
    ssh -o KexAlgorithms=+diffie-hellman-group14-sha1 -o HostKeyAlgorithms=+ssh-rsa admin@10.10.10.1

To see all open ports locally to ensure ports from Docker are open:
    lsof -i -P

To do basic see all in Flux:
    from(bucket: "network_data")
        |> range(start: -1d)