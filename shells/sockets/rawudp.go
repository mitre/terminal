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
func (contact UDP) Listen(key string, port string, server string, profile string) {
	paw := buildPaw()
	updatedProfile := fmt.Sprintf("%s$%s$%s", profile, paw, key)
	for {
	   conn, err := net.Dial("udp", port)
	   if err == nil {
			beacon(conn, updatedProfile)
		} else {
			fmt.Println(fmt.Sprintf("[-] %s", err))
		}
		conn.Close()
		time.Sleep(60 * time.Second)
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
