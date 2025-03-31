#!/bin/sh

# Determinar el gateway en función de la variable de entorno NETWORK_TYPE
if [ "$NETWORK_TYPE" = "servers" ]; then
    GATEWAY="10.0.11.254"
elif [ "$NETWORK_TYPE" = "clients" ]; then
    GATEWAY="10.0.10.254"
else
    echo "NETWORK_TYPE no está definido o es inválido. Especifícalo como 'servers' o 'clients'."
    exit 1
fi

# Cambiar la ruta por defecto
ip route del default 
ip route add default via $GATEWAY

# Ejecutar el servidor
exec python main.py