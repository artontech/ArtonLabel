@ECHO OFF
cd %~dp0
SET NODE_OPTIONS=--openssl-legacy-provider
yarn run serve
pause