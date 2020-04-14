package main

import (
	"bufio"
	"encoding/json"
	"flag"
	"fmt"
	"runtime/debug"

	"log"
	"math/bits"
	"os"

	//"strings"

	//"os/exec"
	"os/signal"
	"path/filepath"
	"sync"

	//"syscall"
	"time"

	"github.com/stackimpact/stackimpact-go"
)

//import _ "net/http/pprof"
//import "net/http"

type Date struct {
	year  string
	month string
}

func (d Date) String() string {
	return fmt.Sprintf("%s-%s", d.year, d.month)
}

type VersionInfo struct {
	Suite   int `json:"suite"`
	Group   int `json:"group"`
	Version int `json:"version"`
}

type TimeVersionIP struct {
	IP        string    `json:"ip"`
	Timestamp time.Time `json:"timestamp"`
	VersionInfo *VersionInfo `json:"tls,omitempty"`
}

func (v *TimeVersionIP) hasVersion() bool {
	return (v != nil) && (v.VersionInfo != nil)
}

type Bitmaps struct {
	Success uint16 `json:"full"`
	Failed  uint16 `json:"SH"`
}

type AggregatedSample struct {
	MostRecentSuccess *TimeVersionIP `json:"tls-full,omitempty"`
	MostRecentPartial *TimeVersionIP `json:"tls-SH,omitempty"`
	Bitmaps           Bitmaps        `json:"tls-ver-bitmaps"`
}

type MappedAggregatedSample struct {
	Domain string `json:"domain"`
	*AggregatedSample
}

type VersionCount struct {
	Counts [16]uint
	Total  uint
}

func (v *VersionCount) incrementVer(ver int) {
	v.Counts[VERSION2INDEX[ver]]++
	v.Total++
}

func (vc VersionCount) MarshalJSON() ([]byte, error) {
	return json.Marshal(&struct {
		SSLv3   uint `json:"SSLv3"`
		TLS10   uint `json:"TLSv1.0"`
		TLS11   uint `json:"TLSv1.1"`
		TLS12   uint `json:"TLSv1.2"`
		Draft18 uint `json:"TLSv1.3draft18"`
		Draft19 uint `json:"TLSv1.3draft19"`
		Draft20 uint `json:"TLSv1.3draft20"`
		Draft21 uint `json:"TLSv1.3draft21"`
		Draft22 uint `json:"TLSv1.3draft22"`
		Draft23 uint `json:"TLSv1.3draft23"`
		Draft24 uint `json:"TLSv1.3draft24"`
		Draft25 uint `json:"TLSv1.3draft25"`
		Draft26 uint `json:"TLSv1.3draft26"`
		Draft27 uint `json:"TLSv1.3draft27"`
		Draft28 uint `json:"TLSv1.3draft28"`
		TLS13   uint `json:"TLSv1.3"`
	}{
		SSLv3:   vc.Counts[0],
		TLS10:   vc.Counts[1],
		TLS11:   vc.Counts[2],
		TLS12:   vc.Counts[3],
		Draft18: vc.Counts[4],
		Draft19: vc.Counts[5],
		Draft20: vc.Counts[6],
		Draft21: vc.Counts[7],
		Draft22: vc.Counts[8],
		Draft23: vc.Counts[9],
		Draft24: vc.Counts[10],
		Draft25: vc.Counts[11],
		Draft26: vc.Counts[12],
		Draft27: vc.Counts[13],
		Draft28: vc.Counts[14],
		TLS13:   vc.Counts[15],
	})
}

type SecondAggregate struct {
	// multiversion count
	MultiVersionCountsSuccess VersionCount `json:"versionmap_countAny_full"`
	MultiVersionCountsFailed  VersionCount `json:"versionmap_countAny_sh"`
	MultiVersionCountsBoth    VersionCount `json:"versionmap_countAny_full_and_sh"`
	MultiVersionCountsEither  VersionCount `json:"versionmap_countAny_full_or_sh"`

	// full/sh only
	FullLatest            VersionCount `json:"full_latest"`
	FullPreferredSHLatest VersionCount `json:"full_preferred_over_sh_latest"`
	FullOrSHLatest        VersionCount `json:"full_or_sh_latest"`
	FullAndSHLatest       VersionCount `json:"full_and_sh_latest"`

	// global counters
	MultiVersionsFull     int `json:"multi_versions_full"`
	MultiVersionsFullOrSH int `json:"multi_versions_full_or_sh"`
	FullTotal             int `json:"full"`
	FullOrShTotal         int `json:"full_or_SH"`
	FullAndSHTotal        int `json:"full_and_SH"`
	Total                 int `json:"all"`
}

func (v *SecondAggregate) aggregate(sample *AggregatedSample) {
	// Total counters
	v.Total++

	if bits.Len16(uint16(sample.Bitmaps.Success)) > 1 {
		v.MultiVersionsFull++
	}
	if bits.Len16(uint16(sample.Bitmaps.Success|
		sample.Bitmaps.Failed)) > 1 {
		v.MultiVersionsFullOrSH++
	}

	// Full/SH counters

	//full_latest
	//full_preferred_over_sh_latest # full.version if full else (sh.version if sh else None)
	//full_or_sh_latest             # if (full and sh) {if (full.timestamp >= sh.timestamp) {full.version} else {sh.version}}; if (full and !sh) {full.version}; if (!full and sh) {sh.version}; if (!full and !sh) {None}
	//full_and_sh_latest            # if(full and sh and full.version == sh.version) {full.version} else {None}
	if sample.MostRecentSuccess != nil {
		// full
		v.FullTotal++
		v.FullOrShTotal++
		//log.Printf("VersionDebug: %s", sample.MostRecentSuccess.Version.Version)
		v.FullLatest.incrementVer(sample.MostRecentSuccess.VersionInfo.Version)
		v.FullPreferredSHLatest.incrementVer(sample.MostRecentSuccess.VersionInfo.Version)
		if sample.MostRecentPartial.hasVersion() {
			v.FullAndSHTotal++
			// full and sh
			if sample.MostRecentPartial.Timestamp.Before(sample.MostRecentSuccess.Timestamp) {
				v.FullOrSHLatest.incrementVer(sample.MostRecentSuccess.VersionInfo.Version)
			} else {
				v.FullOrSHLatest.incrementVer(sample.MostRecentPartial.VersionInfo.Version)
			}
			// full and sh and full.version == sh.version
			if sample.MostRecentSuccess.VersionInfo.Version == sample.MostRecentPartial.VersionInfo.Version {
				v.FullAndSHLatest.incrementVer(sample.MostRecentSuccess.VersionInfo.Version)
			}
		} else {
			// full and !sh
			v.FullOrSHLatest.incrementVer(sample.MostRecentSuccess.VersionInfo.Version)
		}
	} else if sample.MostRecentPartial.hasVersion() {
		// !full and sh
		v.FullOrShTotal++
		v.FullPreferredSHLatest.incrementVer(sample.MostRecentPartial.VersionInfo.Version)
		v.FullOrSHLatest.incrementVer(sample.MostRecentPartial.VersionInfo.Version)
	}

	// Multimap counters
	succ := sample.Bitmaps.Success
	fail := sample.Bitmaps.Failed

	for i := uint(0); i < 16; i++ {
		mask := uint16(1) << i
		s := (succ & mask) != 0
		f := (fail & mask) != 0

		if s {
			v.MultiVersionCountsSuccess.Counts[i]++
		}
		if f {
			v.MultiVersionCountsFailed.Counts[i]++
		}
		if s && f {
			v.MultiVersionCountsBoth.Counts[i]++
		}
		if s || f {
			v.MultiVersionCountsEither.Counts[i]++
		}
	}
}

type Result struct {
	SecondAggregate
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

var VERSION2INDEX = map[int]uint16{
	0x0300:      0, // SSL 3.0
	0x0301:      1, // TLS 1.0
	0x0302:      2, // TLS 1.1
	0x0303:      3, // TLS 1.2
	0x7f00 | 18: 4, // Draft18
	0x7f00 | 19: 5,
	0x7f00 | 20: 6,
	0x7f00 | 21: 7,
	0x7f00 | 22: 8,
	0x7f00 | 23: 9,
	0x7f00 | 24: 10,
	0x7f00 | 25: 11,
	0x7f00 | 26: 12,
	0x7f00 | 27: 13,
	0x7f00 | 28: 14,
	0x0304:      15, // TLS 1.3
}

type Worker struct {
	queue                chan *MappedAggregatedSample
	just_hit_queue_limit bool
	running              bool
	prefix               string
	aggregate            Result
	close_once           sync.Once
}

func (w *Worker) close_channel() {
	w.close_once.Do(func() {
		close(w.queue)
	})
}

type WorkManager struct {
	lock            sync.RWMutex
	workerSingleton *Worker
}

func worker_func(work *Worker, manager *WorkManager, wg *sync.WaitGroup) {
	defer func() {
		if r := recover(); r != nil {
			log.Printf("Panic in worker: %s\n%s\n", r, string(debug.Stack()))
			os.Exit(1)
		}

		manager.lock.Lock()
		work.close_channel()
		manager.workerSingleton = nil
		manager.lock.Unlock()
		wg.Done()
	}()
	filename := fmt.Sprintf("%[1]s.json", prefix)
	log.Printf("Starting new worker for %s\n", filename)

	os.MkdirAll(filepath.Dir(filename), 0755)

	defer func() {
		log.Printf("Flushing to %s\n", filename)
		f, err := os.OpenFile(filename, os.O_CREATE|os.O_WRONLY, 0644)
		if err != nil {
			log.Panicf("Failed to open output file %s", err.Error())
		}

		encoder := json.NewEncoder(f)
		if err := encoder.Encode(work.aggregate); err != nil {
			log.Panicf("Failed to encode json: %s", err.Error())
		}
	}()

	//timeout := time.NewTimer(1 * time.Minute)
//insert:
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
			//timeout.Reset(1 * time.Minute)
			work.aggregate.aggregate(sample.AggregatedSample)

		/*case <-timeout.C:
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
		*/

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
)

func init() {
	flag.StringVar(&profile, "profile", "", "Should open pprof on ip:port")
	flag.StringVar(&prefix, "prefix", ".", "Path prefix to add")
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

	workManager := WorkManager{lock: sync.RWMutex{}}
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
				current_worker := workManager.workerSingleton
				if current_worker != nil {
					current_worker.queue <- nil
				}
				workManager.lock.Unlock()
				break endloop
			}

			var sample MappedAggregatedSample
			if json.Unmarshal([]byte(json_line), &sample) != nil {
				log.Printf("Failed parsing line to json object, affected line:\n%s\n", json_line)
				break
			}

		insert:
			workManager.lock.Lock()
			current_worker := workManager.workerSingleton
			if current_worker == nil {
				// okay this does not yet exist
				current_worker = &Worker{
					queue:                make(chan *MappedAggregatedSample, 10000),
					just_hit_queue_limit: false,
					prefix:               prefix,
				}
				workManager.workerSingleton = current_worker
				wg.Add(1)
				current_worker.running = true
				go worker_func(current_worker, &workManager, &wg)
			}

			// this should not stall the rest...
			if len(current_worker.queue) == cap(current_worker.queue) && !current_worker.just_hit_queue_limit {
				current_worker.just_hit_queue_limit = true
				log.Printf("Oh boy, channel is full on send for worker (silencing for 10 seconds)\n")
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
	if workManager.workerSingleton != nil {
		workManager.workerSingleton.close_channel()
	}
	workManager.lock.RUnlock()
	log.Printf("Waiting for all workers to finish\n")
	wg.Wait()
}
