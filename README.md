# BackupSunlight
Backup Telemetry system on a Raspberry PI for Sunlight

## Setup for Debugging on the Pi
1. Clone the repository.
2. Install mutagen here: https://mutagen.io/documentation/introduction/installation
3. Power on the Pi and verify that you can SSH into it (usually via an Ethernet connection).
4. In the local copy of the repository, open a mutagen synchronization session by running:
    ```
    mutagen sync create --name=backup-sunlight . pi@raspberrypi.local:~/DataAcq-BackupSunlight
    ```
    Once the session is created, any changes made to the local repository will be reflected on the Pi itself.