package util

import (
	"bytes"
	"os/exec"
)

//DetermineExecutors looks for available execution engines
func DetermineExecutors(platform string, arch string) string {
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