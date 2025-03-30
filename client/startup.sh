#!/bin/sh

# Cambiar la ruta por defecto
ip route del default 
ip route add default via 10.0.10.254

# Lanzar Streamlit
exec streamlit run app.py --server.port=8501 --server.address=0.0.0.0