# Robots Metrics Generator

Simple couple of scripts to generate robot statuses and send them to the MQTT broker.

## Pre-Requisites

[Python](https://www.python.org/downloads/) needs to be installed on your system.

## Setup

With Python set up, you can choose to clone the project or download it's Zip.

When the project is downloaded locally, move the terminal into the `robot_metrics_gen` directory and run

```bash
pip install -r requirements.txt
```

This will install the package dependencies used by the scripts.

## Playback

For playback, the script will read the `playback.txt` file and send the messages there continuously. When the end of the file is reached, it will loop back to the first message.

Run with `python playback.py`

# Generate Random

For random generations of measured values, simply run `python gen_rand.py` and it will send fluctuating values every second.
