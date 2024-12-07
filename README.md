# Becker CentralControl HAS

Control your Centronic, CentronicPLUS and B-Tronic devices with Homeassistant.

Support is limited to Cover-type devices, lights and switches.

Requires a fully set-up CC31, CC41 or CC51.

## Installation:

Navigate to the ```YOUR_HAS_CONFIG_DIR/custom_components``` directory.   

Clone the repository: ```git clone https://github.com/DominikStarke/becker_centralcontrol_has.git```

Restart Homeassistant to load the new integration.

## Usage:
![Step 1](assets/1.png)
Got to settings > add integration.

![Step 2](assets/2.png)
Add the CentralControl integration.

![Step 3](assets/3.png)
Configure the host: ```http://IP_OF_CENTRAL_CONTROL/cgi-bin/cc51rpc.cgi```  
Leave the cookie field empty.

![Step 4](assets/4.png)
If everything went smoothly you should be presented a list of devices.
*Note:* Sometimes only 1 device is listed. After selection the other devices will be listed.

![Step 5](assets/5.png)
Devices are mapped to entities and added accordingly

Once the integration is added it will prompt to input the central controls host and an optional cookie.  
The host needs to include the api endpoints path: ```http://IP_OF_CENTRAL_CONTROL/cgi-bin/cc51rpc.cgi```  


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

Then during integration setup use ```http://host.docker.internal:8080/cgi-bin/cc51rpc.cgi``` as hostname.

## Contributing
Contributions are welcome
