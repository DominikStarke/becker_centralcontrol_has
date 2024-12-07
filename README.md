# Becker CentralControl HAS

Control your Centronic, CentronicPLUS and B-Tronic devices with Homeassistant.

Support is limited to Cover-type devices, lights and switches.

Requires a fully set-up CC31, CC41 or CC51.

## Installation:

Navigate to the ```custom_components``` directory of your Homeassistant configuration:  

Copy the code from the cloned repository to the ```custom_components/beckerantriebe``` directory.

Restart Homeassistant to load the new integration.

## Usage:
Once the integration is added it will prompt to input the ip and an optional cookie.  
Leave the cookie empty.

You'll be prompted with a list of devices to add to your homeassistant installation.

## Zero-Conf / MDNS / AVAHI
Currently not supported.

## CentralControl API

The API allows to:
* list devices
* send commands
* get the current state of devices which support feedback

See [central_control.py](central_control.py) for a more comprehensive guide on API usage.


## Forward tunneling (MacOS development in HASS Container)
Due to limitations of the Linux VM of Docker on MacOS we cannot use --network host.  
That means it's not possible to connect to a CentralControl on the same Network as the host machine.

It's possible to use ssh to open a forward tunnel:
```
ssh -fN -L 8080:{CC_ADDRESS}:80 {CC_ADDRESS}
```

Then during integration setup use ```http://host.docker.internal:8080``` as hostname.

