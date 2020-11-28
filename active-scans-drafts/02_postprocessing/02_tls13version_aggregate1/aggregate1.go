package main

import (
	"bufio"
	"encoding/json"
	"flag"
	"fmt"
	"runtime"
	"runtime/debug"

	//"hash/fnv"
	"log"
	//"math/bits"
	"os"
	"os/exec"
	"strings"
	"syscall"

	//"os/exec"
	"os/signal"
	"path/filepath"
	"sync"

	//"syscall"
	"time"

	"github.com/gofrs/flock"
	"github.com/stackimpact/stackimpact-go"
)

//import _ "net/http/pprof"
//import "net/http"

const (
	NUM_BUCKETS = 512
	BUCKETSIZE  = 1000000
)

type Date struct {
	year  string
	month string
}

func (d Date) String() string {
	return fmt.Sprintf("%s-%s", d.year, d.month)
}

type Key struct {
	date Date
	part string
}

func (k Key) String() string {
	return fmt.Sprintf("%s-%s", k.date.String(), k.part)
}

type VersionInfo struct {
	Suite   int `json:"suite"`
	Group   int `json:"group"`
	Version int `json:"version"`
}

type InputSample struct {
	Domain    string       `json:"domain"`
	IP        string       `json:"ip"`
	Timestamp time.Time    `json:"timestamp"`
	Error     bool         `json:"error"`
	ErrorMsg  string       `json:"errormsg,omitempty"`
	Version   *VersionInfo `json:"tls,omitempty"`
}

type TimeVersionIP struct {
	IP          string       `json:"ip"`
	Timestamp   time.Time    `json:"timestamp"`
	VersionInfo *VersionInfo `json:"tls,omitempty"`
}

type Bitmaps struct {
	Success uint16 `json:"full"`
	Failed  uint16 `json:"SH"`
}

type AggregatedSample struct {
	MostRecentSuccess *TimeVersionIP `json:"tls-full,omitempty"`
	MostRecentPartial *TimeVersionIP `json:"tls-SH,omitempty"`
	Bitmaps           Bitmaps        `json:"tls-ver-bitmaps"`
	SeenRefuse        bool           `json:"443_refused"`
}

type MappedAggregatedSample struct {
	Domain string `json:"domain"`
	*AggregatedSample
}

var VERSION2BIT = map[int]uint16{
	0x0300:      0x0001, // SSL 3.0
	0x0301:      0x0002, // TLS 1.0
	0x0302:      0x0004, // TLS 1.1
	0x0303:      0x0008, // TLS 1.2
	0x7f00 | 18: 0x0010, // Draft18
	0x7f00 | 19: 0x0020,
	0x7f00 | 20: 0x0040,
	0x7f00 | 21: 0x0080,
	0x7f00 | 22: 0x0100,
	0x7f00 | 23: 0x0200,
	0x7f00 | 24: 0x0400,
	0x7f00 | 25: 0x0800,
	0x7f00 | 26: 0x1000,
	0x7f00 | 27: 0x2000,
	0x7f00 | 28: 0x4000,
	0x0304:      0x8000, // TLS 1.3
}

func (self *AggregatedSample) merge(other *AggregatedSample) {
	success := self.Bitmaps.Success | other.Bitmaps.Success
	failed := self.Bitmaps.Failed | other.Bitmaps.Failed

	self.Bitmaps.Success = success
	self.Bitmaps.Failed = failed

	self.SeenRefuse = self.SeenRefuse || other.SeenRefuse

	if other.MostRecentPartial != nil {
		if self.MostRecentPartial == nil {
			// we don't have one at all, take others
			self.MostRecentPartial = other.MostRecentPartial
		} else if self.MostRecentPartial.VersionInfo == nil && other.MostRecentPartial.VersionInfo != nil {
			// other has a version, prefer that sample
			self.MostRecentPartial = other.MostRecentPartial
		} else if (self.MostRecentPartial.VersionInfo == nil) == (other.MostRecentPartial.VersionInfo == nil) {
			// both have a version or both dont, take newest
			if self.MostRecentPartial.Timestamp.Before(other.MostRecentPartial.Timestamp) {
				self.MostRecentPartial = other.MostRecentPartial
			}
		}
	}
	if other.MostRecentSuccess != nil {
		if (self.MostRecentSuccess == nil) ||
			(self.MostRecentSuccess.Timestamp.Before(other.MostRecentSuccess.Timestamp)) {
			self.MostRecentSuccess = other.MostRecentSuccess
		}
	}
}

func (s InputSample) to_aggregated() *AggregatedSample {
	res := AggregatedSample{}

	tvi := TimeVersionIP{Timestamp: s.Timestamp, IP: s.IP}
	if s.Version != nil {
		if bit, ok := VERSION2BIT[s.Version.Version]; ok {
			if s.Error || len(s.ErrorMsg) > 0 {
				res.Bitmaps.Failed = bit
			} else {
				res.Bitmaps.Success = bit
			}
		}
		tvi.VersionInfo = s.Version
	}

	res.SeenRefuse = false
	if s.Error || len(s.ErrorMsg) > 0 {
		res.MostRecentPartial = &tvi
		if s.Version == nil {
			res.SeenRefuse = strings.Contains(s.ErrorMsg, "connection refused") ||
				strings.Contains(s.ErrorMsg, "blacklisted") ||
				(strings.Contains(s.ErrorMsg, "dial tcp") &&
					(strings.Contains(s.ErrorMsg, "i/o timeout") ||
					strings.Contains(s.ErrorMsg, "connect: connection reset by peer") ||
					strings.Contains(s.ErrorMsg, "connect: network is unreachable") ||
					strings.Contains(s.ErrorMsg, "connect: no route to host") ||
					strings.Contains(s.ErrorMsg, "no such host") ||
					strings.Contains(s.ErrorMsg, "connect: invalid argument")))
		}
	} else {
		res.MostRecentSuccess = &tvi
	}

	return &res
}

type Worker struct {
	key                  Key
	queue                chan *InputSample
	just_hit_queue_limit bool
	running              bool
	prefix               string
	part                 string
	aggregate            map[string]*AggregatedSample
	close_once           sync.Once
}

func (w *Worker) close_channel() {
	w.close_once.Do(func() {
		close(w.queue)
	})
}

type IndexEntry struct {
	Domain [190]byte
	Index  uint32
}

const DNSAlphabet = " .-0123456789abcdefghijklmnopqrstuvwxyz"

//                   0         1         2         3
//                   012345678901234567890123456789012345678

func compactDNS(dns string) [190]byte {
	// Domain names are
	// - 253 characters at most
	// - case insensitive
	// - Sufficient alphabet is " .-0123456789abcdefghijklmnopqrstuvwxyz" (size 40)
	//   -> 5.32192809489 bits are sufficient
	//   -> 1347 bits (167 bytes) for full DNS
	dns = strings.ToLower(dns)
	var out [190]byte
	outpos := 0
	var avail uint = 8
	for _, chr := range dns {
		cbits := strings.IndexRune(DNSAlphabet, chr) // encode to 6 bits
		if avail < 6 {
			out[outpos] |= byte(cbits << byte(8-avail))
			outpos++
			out[outpos] |= byte(cbits >> byte(avail))
			avail += 2 // +8 -6
		} else {
			out[outpos] |= byte(cbits << byte(8-avail))
			avail -= 6
		}
	}
	return out
}

func unpackDNS(mem [190]byte) string {
	var sb strings.Builder

	var left uint = 0
	var b uint = 0
	for i := 0; i < 190; i++ {
		b = b | (uint(mem[i]) << left)
		left += 2 // +8 -6
	more:
		chr := DNSAlphabet[b&0x3F]
		sb.WriteByte(chr)
		if chr == ' ' {
			break
		}
		b >>= 6
		if left >= 6 {
			left -= 6
			goto more
		}
	}
	return sb.String()
}

type WorkManager struct {
	lock      sync.RWMutex
	workerMap map[Key]*Worker
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

	path := fmt.Sprintf("%[1]s/%[2]s/", work.prefix, work.key.date.year)

	filename := path + fmt.Sprintf("%[1]s%[2]s.json.gz", work.key.date.month, work.key.part)
	filename_tmp := filename + ".tmp"
	filename_lock := filename + ".lock"

	os.MkdirAll(filepath.Dir(filename), 0755)

	do_aggregate := func(domain string, new_sample *AggregatedSample) {
		old_sample, ok := work.aggregate[domain]
		if ok {
			old_sample.merge(new_sample)
		} else {
			// just store
			work.aggregate[domain] = new_sample
		}
	}

	loaded_old := false
	locked_aggregate_with_file := func() {
		if _, err := os.Stat(filename); !os.IsNotExist(err) {
			// file exists, we need to merge it
			loaded_old = true

			bzip := exec.Command("gzip", "-d", "-c", filename)
			pipe, err := bzip.StdoutPipe()
			if err != nil {
				log.Printf("Failed to create pipe: %s\n", err.Error())
			}
			err = bzip.Start()
			if err != nil {
				log.Printf("Failed starting bzip2 for %s with error:\n%s\n", work.key.String(), err.Error())
			}

			scanner := bufio.NewScanner(pipe)
			for scanner.Scan() {
				var sample MappedAggregatedSample
				if json.Unmarshal([]byte(scanner.Text()), &sample) != nil {
					log.Printf("Failed parsing line to AggregatedSample, affected line:\n%s\n", scanner.Text())
					continue
				}
				do_aggregate(sample.Domain, sample.AggregatedSample)
			}
		}

		// write out current aggregate state

		// we simply pipe all data through bzip2 unix cmd line utility
		bzip := exec.Command("gzip", "-c", "-6")
		f, err := os.OpenFile(filename_tmp, os.O_WRONLY|os.O_CREATE, 0755)
		if err != nil {
			log.Panicf("Failed creating output file %s\n", err.Error())
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
			log.Panicf("Failed getting stdin from bzip2 for %s\n", work.key.String())
			return
		}
		// closing hopefully stops bzip2 :D
		defer func() {
			log.Printf("Flushing worker for %s ....\n", work.key.String())
			if err := writer.Close(); err != nil {
				log.Panicf("Failed closing stdin for bzip for %s", work.key.String())
			}
			if err := bzip.Wait(); err != nil {
				// Try to output exit status before panic
				if exiterr, ok := err.(*exec.ExitError); ok {
					if status, ok := exiterr.Sys().(syscall.WaitStatus); ok {
						log.Printf("Exit code from gzip was: %d", status.ExitStatus())
					}
				}
				log.Panicf("Failed waiting for bzip for %s\n%s\n", work.key.String(), err.Error())
			}
			if err := f.Sync(); err != nil {
				log.Panicf("Failed syncing for bzip for %s\n%s\n", work.key.String(), err.Error())
			}
			if err := f.Close(); err != nil {
				log.Panicf("Failed closing for bzip for %s\n%s\n", work.key.String(), err.Error())
			}
			if !bzip.ProcessState.Success() {
				log.Panic("gzip returned with error")
			}

			log.Printf(".... done flushing worker for %s\n", work.key.String())
		}()

		err = bzip.Start()
		if err != nil {
			log.Panicf("Failed starting bzip2 for %s with error:\n%s\n", work.key.String(), err.Error())
		}

		encoder := json.NewEncoder(writer)
		for k, v := range work.aggregate {
			s := MappedAggregatedSample{Domain: k, AggregatedSample: v}
			if err := encoder.Encode(s); err != nil {
				log.Panicf("Encoding failed: %s\n", err.Error())
			}
		}

		if loaded_old {
			// delete original
			if err = os.Remove(filename); err != nil {
				log.Printf("Failed to delete old file: %s\n", err.Error())
			}
		}
		if err = os.Rename(filename_tmp, filename); err != nil {
			log.Panicf("Failed to rename: %s\n", err.Error())
		}
	}

	aggregate_with_file := func() {
		file_lock := flock.New(filename_lock)
		if err := file_lock.Lock(); err != nil {
			log.Panicf("Failed aquire lock for ", filename, err.Error())
		}

		locked_aggregate_with_file()

		if err := file_lock.Unlock(); err != nil {
			log.Panicf("Failed release lock for ", filename, err.Error())
		}

		work.aggregate = make(map[string]*AggregatedSample)
		runtime.GC()
	}

	// flush bucket to file when done
	defer aggregate_with_file()

	timeout := time.NewTimer(1 * time.Minute)
insert:
	for {
		select {
		case sample, ok := <-work.queue:
			if !ok {
				// channel was closed
				return
			}
			if sample == nil {
				// end of input
				return
			}

			timeout.Reset(1 * time.Minute)

			do_aggregate(sample.Domain, sample.to_aggregated())

			//writer.Write([]byte(fmt.Sprintf("%s\n", *line)))
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
	profile string
	prefix  string
	part    string
)

func init() {
	flag.StringVar(&profile, "profile", "", "Should open pprof on ip:port")
	flag.StringVar(&prefix, "prefix", ".", "Path prefix to add")
	flag.StringVar(&part, "part", "", "Part")
	flag.Parse()
}

func main() {
	//hash := fnv.New32a()

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

			var sample InputSample
			if json.Unmarshal([]byte(json_line), &sample) != nil {
				log.Printf("Failed parsing line to json object, affected line:\n%s\n", json_line)
				break
			}

			/*
				year, week := sample.Timestamp.ISOWeek()
				year_str := fmt.Sprintf("%d", year)
				week_str := fmt.Sprintf("%02d", week)
			*/

			year_str := sample.Timestamp.Format("2006")
			month_str := sample.Timestamp.Format("01")

			/*
				hash.Reset()
				if _, err := hash.Write([]byte(sample.Domain)); err != nil {
					log.Printf("Failed to hash domain: %s", err.Error())
				}
				bucket := hash.Sum32() % NUM_BUCKETS
			*/

			k := Key{date: Date{year: year_str, month: month_str}, part: part}
		insert:
			workManager.lock.Lock()
			current_worker := workManager.workerMap[k]
			if current_worker == nil {
				// okay this does not yet exist
				current_worker = &Worker{
					key:                  k,
					queue:                make(chan *InputSample, 10000),
					just_hit_queue_limit: false,
					prefix:               prefix,
					aggregate:            make(map[string]*AggregatedSample),
				}
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
			current_worker.queue <- &sample
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
