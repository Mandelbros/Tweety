#!/bin/sh

# Cambiar la ruta por defecto
ip route del default 
ip route add default via 10.0.11.254

# Ejecutar el servidor
exec python main.py