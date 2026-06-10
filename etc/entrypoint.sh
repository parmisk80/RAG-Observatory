#!/bin/bash
ollama serve &
sleep 5
ollama pull ${MODEL:-llama3}
wait
