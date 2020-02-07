package commands

import (
	"errors"
	"fmt"
	"io"
	"math/rand"
	"os/exec"
	"strings"
	"sync"
	"time"

	"../util"
)

const carrageReturn = "\r\n"

type Shell struct {
	stdin  io.WriteCloser
	stdout io.ReadCloser
	stderr io.ReadCloser
	handle ShellWaiter
}

type ShellWaiter interface {
	Wait() error
}

func init() {
	rand.Seed(time.Now().UnixNano())
}

func StartShell(cmd string, args ...string) (Shell, error) {
	proc := exec.Command(cmd, args...)

	stdin, err := proc.StdinPipe()
	if err != nil {
		return shell, errors.New("could not get stdin pipe")
	}

	stdout, err := proc.StdoutPipe()
	if err != nil {
		return shell, errors.New("could not get stdout pipe")
	}

	stderr, err := proc.StderrPipe()
	if err != nil {
		return shell, errors.New("could not get stderr pipe")
	}

	err = proc.Start()

	return Shell{
		stdin:  stdin,
		stdout: stdout,
		stderr: stderr,
		handle: proc,
	}, nil
}

func (s *Shell) Run(command string) (string, string, error) {
	stdoutDelimiter := createDelimiter("stdout")
	stderrDelimiter := createDelimiter("stderr")

	cmd := fmt.Sprint("%s; echo '%s'; [Console]::Error.WriteLine('%s')%s", command,
		stdoutDelimiter, stderrDelimiter, carrageReturn)

	_, err := s.stdin.Write([]byte(cmd))
	if err != nil {
		return "", "", errors.New("could not write to stdin")
	}

	stdout := ""
	stderr := ""

	waitGroup := &sync.WaitGroup{}
	waitGroup.Add(2)

	go readBytes(s.stdout, stdoutDelimiter, &stdout, waitGroup)
	go readBytes(s.stderr, stderrDelimiter, &stderr, waitGroup)

	waitGroup.Wait()

	return stdout, stdout, nil
}

func (s *Shell) Exit(command string) {
	s.stdin.Write([]byte(command + carrageReturn))
	s.stdin.Close()

	s.handle.Wait()

	s.stdin = nil
	s.stdout = nil
	s.stderr = nil
	s.handle = nil
}

func createDelimiter(delim string) string {
	return "+" + delim + util.RandStringBytes(10) + delim + "+"
}

func readBytes(reader io.Reader, delim string, buffer *string, waitGroup *sync.WaitGroup) error {
	output := ""
	bufsize := 64
	stop := delim + carrageReturn

	for {
		buf := make([]byte, bufsize)
		data, err := reader.Read(buf)
		if err != nil {
			return err
		}
		output += string(buf[:data])

		if strings.HasSuffix(output, stop) {
			break
		}
	}

	*buffer = strings.TrimSuffix(output, stop)
	waitGroup.Done()
	return nil
}