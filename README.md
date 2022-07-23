# ArtonLabel

## Introduction

## Update

## License

## Requirements
### Windows 10
|GPU|Tensorflow|CUDA|cuDNN|python|
|---|----------|----|-----|------|
|RTX 2080Ti|2.2.0|10.1.105_418.96|v7.6.5.32, for CUDA 10.1|3.8.10|
|RTX 3050ti|2.9.1|11.1.0_456.43|v8.2.2.26, for CUDA 11.4|3.10.5|
|RTX 3060|2.7.0|11.1.0_456.43|v8.2.2.26, for CUDA 11.4|3.8.10|
|RTX 3080ti|2.9.1|11.1.0_456.43|v8.2.2.26, for CUDA 11.4|3.10.5|

## Installation
### Windows 10
1. Install python to .\runtime\python\
2. Install dependency
* Edit .\runtime\dependency.bat, replace the value of DEVICE_VERSION according to your device, such as:
```cmd
SET DEVICE_VERSION=rtx3080ti
```
* Run .\runtime\dependency.bat
* Create config file .\conf\tornado.conf, for example:
```python
db_type = "mysql"
http_port = 9000
logging = "info"
log_to_stderr = False
log_file_prefix = "./logs/server.log"
log_rotate_mode = "time"
log_rotate_when = "D"
log_rotate_interval = 1
model_path = "./models"
site_packages_path = "./runtime/python/site-packages-rtx3080ti"
static_path = "./static"
```
## References
