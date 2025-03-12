## Interface Configuration - Router 1
    interface g2
        desc Interface to Router-2
        ip address 100.100.100.1 255.255.255.252
        no shut

## Interface Configuration - Router 2
    interface g2
        desc Interface to Router-1
        ip address 100.100.100.2 255.255.255.252
        no shut

## BGP Configuration - Router 1
    router bgp 1
        bgp router-id 100.100.100.1
        bgp log-neighbor-changes
        network 5.5.5.0 mask 255.255.255.0
        network 6.6.6.0 mask 255.255.255.0
        neighbor 100.100.100.2 remote-as 2

## BGP Configuration - Router 2
    router bgp 2
        bgp router-id 100.100.100.2
        bgp log-neighbor-changes
        network 7.7.7.0 mask 255.255.255.0
        network 8.8.8.0 mask 255.255.255.0
        neighbor 100.100.100.1 remote-as 1

## BGP Break Configuration - Router 1
    router bgp 1
        neighbor 100.100.100.2 shutdown

## BGP Solution Configuration - Router 1
    router bgp 1
        no neighbor 100.100.100.2 shutdown

## OSPF Configuration - Router 1
    router ospf 1
        network 5.5.5.0 0.0.0.255 area 0
        network 6.6.6.0 0.0.0.255 area 0
        network 100.100.100.0 0.0.0.3 area 0
    
    interface GigabitEthernet2
        ip ospf 1 area 0

## OSPF Configuration - Router 2
    router ospf 1
        network 7.7.7.0 0.0.0.255 area 0
        network 8.8.8.0 0.0.0.255 area 0
        network 100.100.100.0 0.0.0.3 area 0
    
    interface GigabitEthernet2
        ip ospf 1 area 0

## OSPF Break Configuration - Router 1
    interface GigabitEthernet2
        mtu 1600