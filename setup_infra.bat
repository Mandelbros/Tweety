@echo off

rem check clients docker networks existence

docker network inspect tweety_clients > nul 2>&1
if %errorlevel% equ 0 (
    echo Network tweety_clients exists.
) else (
    docker network create tweety_clients --subnet 10.0.10.0/24
    echo Network tweety_clients created.
)

rem check servers docker network existence 

docker network inspect tweety_servers > nul 2>&1
if %errorlevel% equ 0 (
    echo Network tweety_servers exists.
) else (
    docker network create tweety_servers --subnet 10.0.11.0/24
    echo Network tweety_servers created.
)

rem check router:base docker image existence 

docker image inspect router:base > nul 2>&1
if %errorlevel% equ 0 (
    echo Image router:base exists.
) else (
    docker build -t router:base -f router/router_base.Dockerfile router/
    echo Image router:base created.
)

rem check router docker image existence 

docker image inspect router > nul 2>&1
if %errorlevel% equ 0 (
    echo Image router exists.
) else (
    docker build -t router -f router/router.Dockerfile router/
    echo Image router created.
)

rem check router container existence

docker container inspect router > nul 2>&1
if %errorlevel% equ 0 (
    docker container stop router
    docker container rm router
    echo Container router removed.
)

docker run -d --rm --name router --cap-add NET_ADMIN router
echo Container router executed.

docker network connect --ip 10.0.10.254 tweety_clients router
docker network connect --ip 10.0.11.254 tweety_servers router

echo Container router connected to client and server networks