package main

import (
	"encoding/csv"
	"fmt"
	"net/http"
	"os"
	"strings"
	"sync"
	"time"

	"github.com/PuerkitoBio/goquery" // Pour le parsing HTML
)

// Nombre de workers pour chaque étape
const (
	PageWorkerCount = 5
	LinkWorkerCount = 10
)

// Structure pour stocker les données extraites
type Data struct {
	Title string
	URL   string
	Info  string
}

func main() {
	start := time.Now()

	// Fichier CSV
	file, err := os.Create("output.csv")
	if err != nil {
		fmt.Println("Erreur lors de la création du fichier CSV :", err)
		return
	}
	writer := csv.NewWriter(file)
	defer file.Close()
	defer writer.Flush()

	// Channels
	pageChan := make(chan string, 100)   // URLs des pages
	linkChan := make(chan string, 1000)  // URLs des éléments
	dataChan := make(chan Data, 1000)    // Données récupérées

	var wg sync.WaitGroup

	// Lancement des workers pour scraper les pages
	for i := 0; i < PageWorkerCount; i++ {
		wg.Add(1)
		go scrapePages(&wg, pageChan, linkChan)
	}

	// Lancement des workers pour scraper les liens
	for i := 0; i < LinkWorkerCount; i++ {
		wg.Add(1)
		go scrapeLinks(&wg, linkChan, dataChan)
	}

	// Routine unique pour écrire dans le fichier CSV
	go func() {
		for data := range dataChan {
			writer.Write([]string{data.Title, data.URL, data.Info})
			writer.Flush()
		}
	}()

	// Envoi des URLs des pages (1000 pages)
	for i := 1; i <= 1000; i++ {
		pageChan <- fmt.Sprintf("https://example.com/page/%d", i)
	}

	// Fermeture des channels au bon moment
	close(pageChan)
	wg.Wait() // Attend la fin du scraping des pages et liens
	close(linkChan)
	close(dataChan)

	fmt.Println("Scraping terminé en :", time.Since(start))
}

// Scraping des pages pour récupérer les liens
func scrapePages(wg *sync.WaitGroup, pageChan <-chan string, linkChan chan<- string) {
	defer wg.Done()
	for pageURL := range pageChan {
		func() { // Fonction anonyme pour encapsuler `defer`
			resp, err := http.Get(pageURL)
			if err != nil {
				fmt.Println("Erreur de requête :", err)
				return
			}
			defer resp.Body.Close()

			doc, err := goquery.NewDocumentFromReader(resp.Body)
			if err != nil {
				fmt.Println("Erreur de parsing HTML :", err)
				return
			}

			doc.Find("a.item-link").Each(func(i int, s *goquery.Selection) {
				href, exists := s.Attr("href")
				if exists {
					linkChan <- "https://example.com" + href
				}
			})
		}()
	}
}

// Scraping des pages des éléments
func scrapeLinks(wg *sync.WaitGroup, linkChan <-chan string, dataChan chan<- Data) {
	defer wg.Done()
	for linkURL := range linkChan {
		func() {
			resp, err := http.Get(linkURL)
			if err != nil {
				fmt.Println("Erreur de requête :", err)
				return
			}
			defer resp.Body.Close()

			doc, err := goquery.NewDocumentFromReader(resp.Body)
			if err != nil {
				fmt.Println("Erreur de parsing HTML :", err)
				return
			}

			title := doc.Find("h1").Text()
			info := strings.TrimSpace(doc.Find(".info").Text())

			dataChan <- Data{Title: title, URL: linkURL, Info: info}
		}()
	}
}
