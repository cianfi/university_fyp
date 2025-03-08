## Interface Configuration - Router 1
    interface g2
        desc Interface to Router-2
        ip address 100.100.100.1 255.255.255.252

## Interface Configuration - Router 2
    interface g2
        desc Interface to Router-1
        ip address 100.100.100.2 255.255.255.252

## BGP Configuration - Router 1
    router bgp 1
        bgp router-id 20.20.30.2
        bgp log-neighbor-changes
        network 5.5.5.0 mask 255.255.255.0
        network 6.6.6.0 mask 255.255.255.0
        neighbor 20.20.30.3 remote-as 2

## BGP Configuration - Router 2
    router bgp 2
        bgp router-id 20.20.30.3
        bgp log-neighbor-changes
        network 7.7.7.0 mask 255.255.255.0
        network 8.8.8.0 mask 255.255.255.0
        neighbor 20.20.30.2 remote-as 1