#!/bin/bash
ollama serve &
sleep 5
python api_server.py
