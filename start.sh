#!/bin/bash

echo "======================================"
echo " Uruchamianie systemu Valve Detector"
echo "======================================"
echo ""

# Ustawienie pułapki (trap) - gdy zamkniesz skrypt przez Ctrl+C, zabije on oba włączone serwery w tle
trap 'echo "Zamykanie serwerów..."; kill 0' SIGINT SIGTERM EXIT

echo "[1/2] Uruchamianie backendu Flask..."
python app.py &

echo "[2/2] Uruchamianie frontendu Vite..."
cd frontend
npm run dev &

echo ""
echo "Serwery zostały uruchomione!"
echo "Użyj Ctrl+C aby wyłączyć oba serwery jednocześnie."
echo "======================================"

# Czekaj w nieskończoność na działające w tle procesy
wait
