package main

import (
	"bufio"
	"compress/gzip"
	// "fmt"
	"log"
	"os"
	"runtime"
	"strings"
	"sync"

	"github.com/jessevdk/go-flags"
)

var opts struct {
	Args struct {
		DomainFile flags.Filename `description:"Input: gzipped domain file containinig original domains" value-name:"DOMAINFILE"`
		InFile     flags.Filename `description:"Input: massdns result file" value-name:"INFILE"`
		//OutFile    flags.Filename `description:"Output file containing IP,domain" value-name:"OUTFILE"`
	} `positional-args:"yes" required:"yes"`
}

// Global variables for CNAME and IN lookup
var cnames map[string](map[string]bool)
var ins map[string](map[string]bool)

const limit = 20

func init() {
	// Set the number of Go processes to 6
	runtime.GOMAXPROCS(6)
}

func cnameLookup(origDomain, currDomain string, level int, outputChan chan<- []string) {

	if level > limit {
		log.Printf("followcnames: depth exceeded for domain %s from origdomain %s \n", currDomain, origDomain)
		return
	}

	if ipMap, ok := ins[currDomain]; ok {
		for ip, _ := range ipMap {
			outputChan <- []string{ip, origDomain}
		}
	}

	if domainMap, ok := cnames[currDomain]; ok {
		for domain, _ := range domainMap {
			cnameLookup(origDomain, domain, level+1, outputChan)
		}
	}
}

func processRecords(recordChan <-chan string, outputChan chan<- []string, wg *sync.WaitGroup) {

	wg.Add(1)

	for record := range recordChan {
		// Canonicalize input (finaldot, tolower(),…)
		canon := strings.TrimRight(record, ".\n ") + "."
		canon = strings.ToLower(canon)
		cnameLookup(canon, canon, 0, outputChan)
	}

	wg.Done()
}

func outputResult(outputChan <-chan []string) {
	logger := log.New(os.Stdout, "", 0)
	for res := range outputChan {
		// Backward compatibility
		if res[0] == "\\# 0" {
			res[0] = "\\#"
		}
		// most recent: decision to *not* drop any outputs, as this is systematically done at later steps
		// TODO: once stable, drop all the short and crappy outputs
		//if (len(res[0]) < 3) || (len(res[1]) <3) && (res[0] != "::" ) && (res[0] != "\\#") {
		//	log.Printf("Short output: " + res[0] + "," + res[1] + "\n")
		//}
		// fmt.Print(res[0] + "," + res[1] + "\n")
		// print should do, and this is only one routine, but lets try this anyway:
		// https://stackoverflow.com/questions/14694088/is-it-safe-for-more-than-one-goroutine-to-print-to-stdout/43327441#43327441
		logger.Print(res[0] + "," + res[1] + "\n")
	}
}

func readInput(recordChan chan<- string, outputChan chan<- []string, filename string) {

	// Close channel at the end of input sending
	defer close(recordChan)

	// Read input file into two dicts
	cnames = make(map[string](map[string]bool))
	ins = make(map[string](map[string]bool))

	fh, _ := os.Open(filename)
	scanner2 := bufio.NewScanner(fh)
	for scanner2.Scan() {
		sc := scanner2.Text()
		record := strings.Split(sc, "\t")
		if len(record) < 5 {
			log.Fatal("incorrect number of fields:" + sc)
			break
		}

		domain := record[0]
		rrType := record[3]
		value := record[4]
		var correctDict map[string](map[string]bool)

		if rrType == "CNAME" {
			correctDict = cnames
		} else if rrType == "A" || rrType == "AAAA" || rrType == "SRV" || rrType == "PTR" || rrType == "NS" || rrType == "MX" {
			correctDict = ins
		} else if rrType == "DNAME"  {
			// ignore the very few DNAMEs we have
			continue
		} else {
			panic("Should not happen: incorrect rrType = " + rrType)
		}

		domainSet, ok := correctDict[domain]
		if !ok {
			domainSet = make(map[string]bool)
		}
		domainSet[value] = true

		correctDict[domain] = domainSet
	}
	fh.Close()

	fh, err := os.Open(string(opts.Args.DomainFile))
	if err != nil {
		log.Fatal(err)
	}

	zr, err := gzip.NewReader(fh)
	if err != nil {
		log.Fatal(err)
	}

	scanner := bufio.NewScanner(zr)
	for scanner.Scan() {
		recordChan <- scanner.Text()
	}
	if err := scanner.Err(); err != nil {
		log.Println("Reading standard input:", err)
	}
}

func main() {

	// Parse command line arguments
	parser := flags.NewParser(&opts, flags.Default)
	if _, err := parser.Parse(); err != nil {
		if err.(*flags.Error).Type == flags.ErrHelp {
			return
		} else if err.(*flags.Error).Type != flags.ErrRequired {
			log.Fatal(err)
		} else {
			os.Exit(1)
		}
	}

	numRoutines := 10000
	recordChan := make(chan string)
	outputChan := make(chan []string)

	// wg makes sure that all processing goroutines have terminated before exiting
	var wg sync.WaitGroup
	// This 1 is for the main goroutine and makes sure that the output is not immediately closed
	wg.Add(1)

	go func() {
		// Close output channel when all processing goroutines finish
		defer close(outputChan)
		wg.Wait()
	}()

	// Start goroutines for record processing
	for i := 0; i < numRoutines; i++ {
		go processRecords(recordChan, outputChan, &wg)
	}

	// Start goroutine for input CSV reading
	go readInput(recordChan, outputChan, string(opts.Args.InFile))

	wg.Done()

	// Start output writing
	outputResult(outputChan)
}
