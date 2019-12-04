package main

import (
	"bufio"
	"encoding/json"
	"flag"
	"fmt"
	"hash/fnv"
	"log"
	"os"
	"os/exec"
	"os/signal"
	"path/filepath"
	"runtime/debug"
	"strings"
	"sync"
	"syscall"
	"time"

	"github.com/stackimpact/stackimpact-go"
)

//import _ "net/http/pprof"
//import "net/http"

type Date struct {
	year  string
	month string
	day   string
}

func (d Date) String() string {
	return fmt.Sprintf("%s-%s-%s", d.year, d.month, d.day)
}

type Key struct {
	date        Date
	bucket      string
	comsys_date string
	tool        string
	source      string
}

func (k Key) String() string {
	return fmt.Sprintf("%s (%s, %s, %s)", k.tool, k.source, k.date.String(), k.bucket)
}

type Worker struct {
	key                  Key
	queue                chan *string
	just_hit_queue_limit bool
	running              bool
	close_once           sync.Once
}

func (w *Worker) close_channel() {
	w.close_once.Do(func() {
		close(w.queue)
	})
}

type WorkManager struct {
	lock      sync.RWMutex
	workerMap map[Key]*Worker
}

type TeeLogger struct {
	tee *log.Logger
}

func (l *TeeLogger) Panic(s string) {
	l.tee.Print(s) // don't panic, yet
	log.Panic(s)
}

func (l *TeeLogger) Panicf(format string, v ...interface{}) {
	l.tee.Printf(format, v...) // don't panic, yet
	log.Panicf(format, v...)
}

func (l *TeeLogger) Printf(format string, v ...interface{}) {
	l.tee.Printf(format, v...)
	log.Printf(format, v...)
}

func worker_func(work *Worker, manager *WorkManager, wg *sync.WaitGroup) {
	defer func() {
		if r := recover(); r != nil {
			log.Printf("Panic in worker: %s\n%s\n", r, string(debug.Stack()))
			os.Exit(1)
		}

		manager.lock.Lock()
		work.close_channel()
		delete(manager.workerMap, work.key)
		manager.lock.Unlock()
		wg.Done()
	}()
	log.Printf("Starting new worker for %s\n", work.key.String())

	filename := fmt.Sprintf("%[1]s/%[2]s/%[3]s/%[4]s/%[1]s_%[2]s_%[3]s-%[4]s-%[5]s_orig%[6]s%[7]s.json.gz", work.key.tool, work.key.source, work.key.date.year, work.key.date.month, work.key.date.day, work.key.comsys_date, work.key.bucket)
	logfile := fmt.Sprintf("%[1]s_LOG/%[2]s/%[3]s/%[4]s/%[1]s_%[2]s_%[3]s-%[4]s-%[5]s_orig%[6]s%[7]s.log", work.key.tool, work.key.source, work.key.date.year, work.key.date.month, work.key.date.day, work.key.comsys_date, work.key.bucket)

	os.MkdirAll(filepath.Dir(filename), 0755)
	os.MkdirAll(filepath.Dir(logfile), 0755)

	flog, err := os.OpenFile(logfile, os.O_APPEND|os.O_WRONLY|os.O_CREATE, 0755)
	if err != nil {
		log.Panicf("Failed creating log file %s\n", err.Error())
	}
	logger := TeeLogger{tee: log.New(flog, "", log.Lmicroseconds)}

	// we simply pipe all data through bzip2 unix cmd line utility
	bzip := exec.Command("gzip", "-c", "-6")
	f, err := os.OpenFile(filename, os.O_APPEND|os.O_WRONLY|os.O_CREATE, 0755)
	if err != nil {
		logger.Panicf("Failed creating output file %s\n", err.Error())
	}

	// make sure that the spawned process will get its own process group such that it does not receive SIGINT from us
	// unix magic
	bzip.SysProcAttr = &syscall.SysProcAttr{
		Setpgid: true,
		Pgid:    0,
	}
	// pipe into file
	bzip.Stdout = f
	bzip.Stderr = os.Stderr
	writer, err := bzip.StdinPipe()
	if err != nil {
		logger.Panicf("Failed getting stdin from bzip2 for %s: %s\n", work.key.String(), err.Error())
		return
	}
	// closing hopefully stops bzip2 :D

	numLines := 0
	numBytes := uint64(0)

	defer func() {
		logger.Printf("Sent %d bytes in %d lines to gzip\n", numBytes, numLines)
		logger.Printf("Flushing worker for %s ....\n", work.key.String())
		if err := writer.Close(); err != nil {
			logger.Panicf("Failed closing stdin for bzip for %s: %s", work.key.String(), err.Error())
		}
		if err := bzip.Wait(); err != nil {
			// Try to output exit status before panic
			if exiterr, ok := err.(*exec.ExitError); ok {
				if status, ok := exiterr.Sys().(syscall.WaitStatus); ok {
					logger.Printf("Exit code from gzip was: %d", status.ExitStatus())
				}
			}
			logger.Panicf("Failed waiting for bzip for %s\n%s\n", work.key.String(), err.Error())
		}
		if err := f.Sync(); err != nil {
			logger.Panicf("Failed syncing for bzip for %s\n%s\n", work.key.String(), err.Error())
		}
		if err := f.Close(); err != nil {
			logger.Panicf("Failed closing for bzip for %s\n%s\n", work.key.String(), err.Error())
		}
		if !bzip.ProcessState.Success() {
			logger.Panic("gzip returned with error")
		}

		logger.Printf(".... done flushing worker for %s\n", work.key.String())
	}()
	/*	defer f.Close()
		compress_writer, err := bzip2.NewWriter(f, &bzip2.WriterConfig{Level: bzip2.BestCompression})
		if err != nil {
			log.Printf("Failed initialzing compression for %s\n", work.key.String())
			return
		}
		buffered_writer := bufio.NewWriterSize(compress_writer, 256*1024*1024) // what size to choose? Here 256MB of buffer
		if err != nil {
			log.Printf("Failed initialzing buffer for %s\n", work.key.String())
			return
		}
		defer func() {
			// for bzip2 it flushed on close
			log.Printf("Flushing worker for %s\n", work.key.String())
			buffered_writer.Flush()
			compress_writer.Close()
		}()
	*/
	err = bzip.Start()
	if err != nil {
		logger.Panicf("Failed starting bzip2 for %s with error:\n%s\n", work.key.String(), err.Error())
	}
	timeout := time.NewTimer(1 * time.Minute)
insert:
	for {
		select {
		case line, ok := <-work.queue:
			if !ok {
				// channel was closed
				return
			}
			if line == nil {
				// end of input
				return
			}

			timeout.Reset(1 * time.Minute)
			mem := []byte(fmt.Sprintf("%s\n", *line))
			n, err := writer.Write(mem)
			numLines++
			numBytes += uint64(n)
			if err != nil {
				logger.Panicf("Failed to write to zip stream: %s", err.Error())
			}
			if n != len(mem) {
				logger.Panicf("Could only write %d/%d bytes: %s", n, len(mem), err.Error())
			}
		case <-timeout.C:
			// okay we got a timeout
			// can it happen that we get a timeout while somebody writes to the channel???
			manager.lock.Lock()
			if len(work.queue) > 0 {
				manager.lock.Unlock()
				goto insert
			}
			work.running = false

			manager.lock.Unlock()
			return
		}
	}
}

func line_from_stdin(stdin_chan chan<- string) {
	fscanner := bufio.NewScanner(os.Stdin)
	maxsize := 1024 * 1024 * 1024
	inbuff := make([]byte, maxsize, maxsize)
	fscanner.Buffer(inbuff, maxsize)
	for fscanner.Scan() {
		stdin_chan <- fscanner.Text()
	}
	close(stdin_chan)
}

var (
	server_hello_path = []string{"request", "tls_handshake", "server_hello"}
)

type ServerHello struct {
	CipherSuite   float64 `json:"suite"`
	KeyshareGroup float64 `json:"group"`
	Version       float64 `json:"version"`
}

type Output struct {
	Domain      string       `json:"domain"`
	IP          string       `json:"ip"`
	Timestamp   string       `json:"timestamp"`
	Error       bool         `json:"error"`
	ErrorMsg    string       `json:"errormsg,omitempty"`
	ServerHello *ServerHello `json:"tls,omitempty"`
}

func tls_eval_filter(parsed_json map[string]interface{}) (string, bool) {
	timestamp, _ := parsed_json["timestamp"].(string) // already validated

	ip, ok := parsed_json["ip"].(string)
	if !ok {
		return "", false
	}
	domain, ok := parsed_json["domain"].(string)
	if !ok {
		return "", false
	}

	result := Output{Domain: domain, IP: ip, Timestamp: timestamp}

	error_str, ok := parsed_json["error"].(string)
	if ok {
		result.ErrorMsg = error_str
	}

	make_result := func() string {
		mem, err := json.Marshal(result)
		if err != nil {
			fmt.Println("Failed to marshal: ", err.Error())
			return ""
		}

		return string(mem)
	}

	data, ok := parsed_json["data"].(map[string]interface{})
	if !ok {
		return make_result(), true
	}
	http, ok := data["http"].(map[string]interface{})
	if !ok {
		return make_result(), true
	}

	var response map[string]interface{}
	if chain, ok := http["redirect_response_chain"]; ok {
		// initial hop is the first chain entry
		chana, ok := chain.([]interface{})
		if !ok {
			return make_result(), true
		}
		response, ok = chana[0].(map[string]interface{})
		if !ok {
			return make_result(), true
		}
	} else {
		// initial hop is the response
		response, ok = http["response"].(map[string]interface{})
		if !ok {
			return make_result(), true
		}
	}

	// lookup handshake success via status_code
	_, success := response["status_code"]
	result.Error = !success

	// finally look up the version(which might be missing)
	server_hello := response
	for _, k := range server_hello_path {
		server_hello, ok = server_hello[k].(map[string]interface{})
		if !ok {
			server_hello = nil
			break
		}
	}

	if server_hello != nil {
		var hello ServerHello
		result.ServerHello = &hello

		if version, ok := server_hello["version"].(map[string]interface{}); ok {
			vernum, ok := version["value"].(float64)
			if ok {
				hello.Version = vernum
			}
		}

		if suite, ok := server_hello["cipher_suite"].(map[string]interface{}); ok {
			hex, ok := suite["value"].(float64)
			if ok {
				hello.CipherSuite = hex
			}
		}

		if suite, ok := server_hello["keyshare"].(map[string]interface{}); ok {
			if group, ok := suite["group"].(map[string]interface{}); ok {
				hex, ok := group["value"].(float64)
				if ok {
					hello.KeyshareGroup = hex
				}
			}
		}
	}
	return make_result(), true
}

var profile string
var tls_eval bool
var split_to_buckets uint

func init() {
	flag.StringVar(&profile, "profile", "", "Should open pprof on ip:port")
	flag.BoolVar(&tls_eval, "tls-eval", false, "Split according to .timestamp and filter data")
	flag.UintVar(&split_to_buckets, "buckets", 0, "Split data to the given amount of buckets")
	flag.Parse()
}

func main() {
	if profile != "" {
		log.Println("Starting profiler")
		//go func() {
		//	log.Println(http.ListenAndServe(*profile, nil))
		//}()
		agent := stackimpact.Start(stackimpact.Options{
			AgentKey: "835094058259b182360d6ba2c2dc275b27289ff1",
			AppName:  "disk-writer",
		})
		if agent == nil {
			log.Println("Error starting agent")
		}
	}
	sig_chan := make(chan os.Signal, 1)
	signal.Notify(sig_chan, os.Interrupt)

	workManager := WorkManager{lock: sync.RWMutex{}, workerMap: make(map[Key]*Worker)}
	stdin_chan := make(chan string, 10)

	go line_from_stdin(stdin_chan)
	var wg sync.WaitGroup

	fnv := fnv.New32a()

endloop:
	for {
		select {
		case json_line, ok := <-stdin_chan:
			if !ok {
				break endloop
			}
			if json_line == "" {
				break
			}
			if json_line == "END" {
				fmt.Println("Received END, shutting down")
				workManager.lock.Lock()
				// close all workers
				for _, v := range workManager.workerMap {
					v.queue <- nil
				}
				workManager.lock.Unlock()
				break endloop
			}
			var parsed_json map[string]interface{}
			if json.Unmarshal([]byte(json_line), &parsed_json) != nil {
				log.Printf("Failed parsing line to json object, affected line:\n%s\n", json_line)
				break
			}
			comsys_source, ok := parsed_json["comsys-source"].(string)
			if !ok {
				log.Printf("No comsys-source in json object")
				break
			}
			comsys_tool, ok := parsed_json["comsys-tool"].(string)
			if !ok {
				log.Printf("No comsys-tool in json object")
				break
			}

			var ymd []string

			comsys_date, ok := parsed_json["comsys-date"].(string)
			if !ok {
				log.Printf("No comsys-date in json object")
				break
			}

			if tls_eval {
				timestamp_str, ok := parsed_json["timestamp"].(string)
				if !ok {
					log.Printf("No timestamp in json object")
					break
				}
				timestamp, err := time.Parse(time.RFC3339, timestamp_str)
				if err != nil {
					log.Printf("Illegal timestamp: %s", err.Error())
					break
				}

				// normalize to UTC, in case there are different time offsets
				// and extract the ymd from the timestamp
				//timestamp = timestamp.UTC()
				ymd = []string{
					timestamp.Format("2006"),
					timestamp.Format("01"),
					timestamp.Format("02"),
				}

				json_line, ok = tls_eval_filter(parsed_json)
				if !ok {
					log.Printf("Failed TLS eval")
					break
				}
			} else {
				ymd := strings.Split(comsys_date, "-")
				if len(ymd) != 3 {
					log.Printf("Illegal date format in json string, must be *-*-*")
					break
				}
			}

			// if a toplevel .timestamp for the actual measurement exists,
			// use it to override the comsys-date
			bucket := ""
			if split_to_buckets != 0 {
				domain, ok := parsed_json["domain"].(string)
				if !ok {
					log.Printf("Missing or wrong .domain entry")
					break
				}
				fnv.Reset()
				fnv.Write([]byte(domain))
				i_bucket := fnv.Sum32() % uint32(split_to_buckets)
				bucket = fmt.Sprintf("_part%04d", i_bucket)
			}

			k := Key{tool: comsys_tool, source: comsys_source, date: Date{year: ymd[0], month: ymd[1], day: ymd[2]}, comsys_date: comsys_date, bucket: bucket}
		insert:
			workManager.lock.Lock()
			current_worker := workManager.workerMap[k]
			if current_worker == nil {
				// okay this does not yet exist
				current_worker = &Worker{key: k, queue: make(chan *string, 10000), just_hit_queue_limit: false}
				workManager.workerMap[k] = current_worker
				wg.Add(1)
				current_worker.running = true
				go worker_func(current_worker, &workManager, &wg)
			}
			// this should not stall the rest...
			if len(current_worker.queue) == cap(current_worker.queue) && !current_worker.just_hit_queue_limit {
				current_worker.just_hit_queue_limit = true
				log.Printf("Oh boy, channel is full on send for worker: %s (silencing for 10 seconds)\n", current_worker.key.String())
				go func() {
					<-time.After(10 * time.Second)
					current_worker.just_hit_queue_limit = false
				}()
			}
			if !current_worker.running {
				workManager.lock.Unlock()
				goto insert
			}
			current_worker.queue <- &json_line
			workManager.lock.Unlock()

		case <-sig_chan:
			// lets close stdin and make sure everything is finished
			os.Stdin.Close()
			break endloop
		}
	}
	// make sure everybody flushes :)
	// i.e., close all channels and wait for workers to die :)
	log.Printf("Finishing all workers\n")
	workManager.lock.RLock()
	for _, work := range workManager.workerMap {
		work.close_channel()
	}
	workManager.lock.RUnlock()
	log.Printf("Waiting for all workers to finish\n")
	wg.Wait()
}
