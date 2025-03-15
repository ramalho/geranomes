package main

import (
	"bufio"
	"encoding/gob"
	"fmt"
	"math/rand"
	"os"
	"path/filepath"
	"strings"
)

const (
	ModelPath = "markov-model.gob"
	Order     = 6
	BatchSize = 10000
)

// MarkovModel maps n-grams to possible next characters
type MarkovModel map[string][]string

// Starters is a list of possible starting sequences
type Starters []string

// MarkovNameMaker generates plausible names using a Markov chain model
type MarkovNameMaker struct {
	order    int
	endChar  string
	model    MarkovModel
	starters Starters
}

// Set of prepositions that shouldn't be the last word in a name
var prefixes = map[string]bool{}

// Initialize prefixes set
func init() {
	prepositions := "da das de di do dos du del von van"
	prepositions += " " + strings.Title(prepositions)
	for _, prefix := range strings.Split(prepositions, " ") {
		prefixes[prefix] = true
	}
}

// NewMarkovNameMaker creates a new name generator
func NewMarkovNameMaker(namesFilePath string, order int) (*MarkovNameMaker, error) {
	maker := &MarkovNameMaker{
		order:   order,
		endChar: "\n", // Default to newline as end character
		model:   make(MarkovModel),
	}

	if _, err := os.Stat(ModelPath); err == nil {
		// Model file exists, load it
		file, err := os.Open(ModelPath)
		if err != nil {
			return nil, fmt.Errorf("error opening model file: %w", err)
		}
		defer file.Close()

		decoder := gob.NewDecoder(file)
		if err := decoder.Decode(&maker.model); err != nil {
			return nil, fmt.Errorf("error decoding model: %w", err)
		}
		if err := decoder.Decode(&maker.starters); err != nil {
			return nil, fmt.Errorf("error decoding starters: %w", err)
		}
	} else {
		// Build new model
		fmt.Fprintf(os.Stderr, "Indexing %d-grams %s...\n", order, ModelPath)

		// Read names from file
		file, err := os.Open(namesFilePath)
		if err != nil {
			return nil, fmt.Errorf("error opening names file: %w", err)
		}
		defer file.Close()

		var names []string
		scanner := bufio.NewScanner(file)
		for scanner.Scan() {
			// Get the line without newline character (Scanner.Text() strips it)
			name := scanner.Text()
			if name != "" {
				// Explicitly append the newline to mark end of name
				names = append(names, name+"\n")
			}
		}

		if err := scanner.Err(); err != nil {
			return nil, fmt.Errorf("error reading names file: %w", err)
		}

		// Build model from names
		if err := maker.buildModel(names); err != nil {
			return nil, fmt.Errorf("error building model: %w", err)
		}

		// Save model to file
		outputFile, err := os.Create(ModelPath)
		if err != nil {
			return nil, fmt.Errorf("error creating model file: %w", err)
		}
		defer outputFile.Close()

		encoder := gob.NewEncoder(outputFile)
		if err := encoder.Encode(maker.model); err != nil {
			return nil, fmt.Errorf("error encoding model: %w", err)
		}
		if err := encoder.Encode(maker.starters); err != nil {
			return nil, fmt.Errorf("error encoding starters: %w", err)
		}
	}

	return maker, nil
}

// buildModel builds a Markov chain model from a list of names
func (m *MarkovNameMaker) buildModel(names []string) error {
	m.model = make(MarkovModel)
	m.starters = make(Starters, 0)

	for _, name := range names {
		if len(name) <= m.order {
			continue
		}

		// Check that all names have the same ending character
		if m.endChar == "" {
			m.endChar = string(name[len(name)-1])
		} else if string(name[len(name)-1]) != m.endChar {
			return fmt.Errorf("all names must have the same last character, example: \\n")
		}

		// Add to starters
		m.starters = append(m.starters, name[:m.order])

		// Build model
		for i := 0; i <= len(name)-m.order-1; i++ {
			key := name[i : i+m.order]
			nextChar := string(name[i+m.order])
			m.model[key] = append(m.model[key], nextChar)
		}
	}

	return nil
}

// plausibleName checks if a name meets criteria for being plausible
func plausibleName(name string) bool {
	parts := strings.Split(name, " ")
	lastPart := parts[len(parts)-1]
	return len(parts) >= 3 &&
		!prefixes[lastPart] &&
		len(lastPart) > 1
}

// MakeName generates a new name
func (m *MarkovNameMaker) MakeName() string {
	var name string

	for {
		// Select random starter
		name = m.starters[rand.Intn(len(m.starters))]

		for {
			key := name[len(name)-m.order:]
			nextChars, exists := m.model[key]
			if !exists {
				break
			}

			nextChar := nextChars[rand.Intn(len(nextChars))]

			// Check plausibility of name without end character
			nameToCheck := strings.TrimSuffix(name, m.endChar)
			okToEnd := plausibleName(nameToCheck)

			if okToEnd && nextChar == " " && rand.Intn(3) < 2 {
				break
			} else if nextChar == m.endChar {
				if okToEnd {
					break
				} else {
					nextChar = " "
				}
			}

			name += nextChar
		}

		// Remove endChar from name before checking word count
		nameWithoutEndChar := strings.TrimSuffix(name, m.endChar)
		if len(strings.Split(nameWithoutEndChar, " ")) >= 3 {
			break
		}
	}

	// Return the name without the endChar character and with any extra spaces trimmed
	return strings.TrimSpace(strings.TrimSuffix(name, m.endChar))
}

// MakeNames generates a specified number of names
func MakeNames(sampleFilePath string, quantity, order int) error {
	maker, err := NewMarkovNameMaker(sampleFilePath, order)
	if err != nil {
		return err
	}

	fileInfo, err := os.Stdout.Stat()
	if err != nil {
		return err
	}

	writingToFile := (fileInfo.Mode() & os.ModeCharDevice) == 0

	for i := 0; i < quantity; i++ {
		fmt.Println(maker.MakeName())
		if writingToFile && i%BatchSize == 0 {
			fmt.Fprintf(os.Stderr, "\r%d names generated", i)
		}
	}

	if writingToFile {
		fmt.Fprintf(os.Stderr, "\r%s\r", strings.Repeat(" ", 80))
	}

	return nil
}

func main() {
	if len(os.Args) < 2 {
		fmt.Printf("Usage: %s <how_many_names>\n", os.Args[0])
		os.Exit(1)
	}

	var quantity int
	_, err := fmt.Sscanf(os.Args[1], "%d", &quantity)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error parsing quantity: %v\n", err)
		os.Exit(1)
	}

	samplePath := filepath.Join("amostras", "nomes.txt")
	if err := MakeNames(samplePath, quantity, Order); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
}
