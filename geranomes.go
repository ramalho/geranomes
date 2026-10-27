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
	ModelPrefix  = "model-order"
	DefaultOrder = 6
	BatchSize    = 10000
	MinParts     = 2 // minimum number of words in a name

	Prepositions = "da das de di do dos du del von van"
)

// MarkovModel maps n-grams to possible next characters
type MarkovModel map[string][]string

// Starters is a list of possible starting sequences
type Starters []string

// PartCounts maps number of words to number of names with that many words
type PartCounts map[int]int

// MarkovNameMaker generates plausible names using a Markov chain model
type MarkovNameMaker struct {
	order      int
	endChar    string
	model      MarkovModel
	starters   Starters
	partCounts PartCounts
}

// Set of prepositions that shouldn't be the last word in a name
var prefixes = map[string]bool{}

// Initialize prefixes set
func init() {
	prepositions := strings.Fields(Prepositions)
	for _, prep := range prepositions {
		prepositions = append(prepositions, strings.ToUpper(prep[:1])+prep[1:])
	}
	for _, prefix := range prepositions {
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

	modelPath := modelPathFor(order)
	if _, err := os.Stat(modelPath); err == nil {
		// Model file exists, load it
		maker.model, maker.starters, maker.partCounts, err = loadModel(modelPath)
		if err != nil {
			return nil, err
		}
	} else {
		fmt.Fprintf(os.Stderr, "Indexing %d-grams to %s...\n", order, modelPath)
		if err := maker.buildModelFromText(namesFilePath); err != nil {
			return nil, err
		}
		if err := saveModel(modelPath, maker.model, maker.starters, maker.partCounts); err != nil {
			return nil, err
		}
	}

	return maker, nil
}

// modelPathFor returns the model cache file name for the given order
func modelPathFor(order int) string {
	return fmt.Sprintf("%s-%d.gob", ModelPrefix, order)
}

// loadModel reads a model, its starters and part counts saved by saveModel
func loadModel(modelPath string) (MarkovModel, Starters, PartCounts, error) {
	file, err := os.Open(modelPath)
	if err != nil {
		return nil, nil, nil, fmt.Errorf("error opening model file: %w", err)
	}
	defer file.Close()

	var model MarkovModel
	var starters Starters
	var partCounts PartCounts
	decoder := gob.NewDecoder(file)
	if err := decoder.Decode(&model); err != nil {
		return nil, nil, nil, fmt.Errorf("error decoding model: %w", err)
	}
	if err := decoder.Decode(&starters); err != nil {
		return nil, nil, nil, fmt.Errorf("error decoding starters: %w", err)
	}
	if err := decoder.Decode(&partCounts); err != nil {
		return nil, nil, nil, fmt.Errorf("error decoding part counts: %w", err)
	}
	return model, starters, partCounts, nil
}

// buildModelFromText builds the model from a file with one name per line
func (m *MarkovNameMaker) buildModelFromText(namesFilePath string) error {
	// Read names from file
	file, err := os.Open(namesFilePath)
	if err != nil {
		return fmt.Errorf("error opening names file: %w", err)
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
		return fmt.Errorf("error reading names file: %w", err)
	}

	// Build model from names
	if err := m.buildModel(names); err != nil {
		return fmt.Errorf("error building model: %w", err)
	}
	return nil
}

// saveModel writes a model, its starters and part counts to modelPath
func saveModel(modelPath string, model MarkovModel, starters Starters, partCounts PartCounts) error {
	outputFile, err := os.Create(modelPath)
	if err != nil {
		return fmt.Errorf("error creating model file: %w", err)
	}
	defer outputFile.Close()

	encoder := gob.NewEncoder(outputFile)
	if err := encoder.Encode(model); err != nil {
		return fmt.Errorf("error encoding model: %w", err)
	}
	if err := encoder.Encode(starters); err != nil {
		return fmt.Errorf("error encoding starters: %w", err)
	}
	if err := encoder.Encode(partCounts); err != nil {
		return fmt.Errorf("error encoding part counts: %w", err)
	}
	return nil
}

// buildModel builds a Markov chain model from a list of names
func (m *MarkovNameMaker) buildModel(names []string) error {
	m.model = make(MarkovModel)
	m.starters = make(Starters, 0)
	m.partCounts = make(PartCounts)

	for _, name := range names {
		if len(name) <= m.order {
			continue
		}

		// Check that all names end with endChar
		if string(name[len(name)-1]) != m.endChar {
			return fmt.Errorf("all names must end with %q", m.endChar)
		}

		// Add to starters
		m.starters = append(m.starters, name[:m.order])
		m.partCounts[len(strings.Fields(name))]++

		// Build model
		for i := 0; i <= len(name)-m.order-1; i++ {
			key := name[i : i+m.order]
			nextChar := string(name[i+m.order])
			m.model[key] = append(m.model[key], nextChar)
		}
	}

	return nil
}

// targetParts draws a number of words with the frequencies found in the sample
func (m *MarkovNameMaker) targetParts() int {
	total := 0
	for parts, count := range m.partCounts {
		if parts >= MinParts {
			total += count
		}
	}
	r := rand.Intn(total)
	for parts, count := range m.partCounts {
		if parts < MinParts {
			continue
		}
		if r < count {
			return parts
		}
		r -= count
	}
	return MinParts
}

// plausibleName checks if a name meets criteria for being plausible
func plausibleName(name string, minParts int) bool {
	parts := strings.Fields(name)
	if len(parts) < minParts {
		return false
	}
	lastPart := parts[len(parts)-1]
	return !prefixes[lastPart] &&
		len(lastPart) > 1
}

// MakeName generates a new name
func (m *MarkovNameMaker) MakeName() string {
	var name string

	for {
		target := m.targetParts()
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
			okToEnd := plausibleName(nameToCheck, target)

			if okToEnd && (nextChar == " " || nextChar == m.endChar) {
				break
			} else if nextChar == m.endChar {
				nextChar = " "
			}

			name += nextChar
		}

		// Remove endChar from name before checking word count
		nameWithoutEndChar := strings.TrimSuffix(name, m.endChar)
		if len(strings.Fields(nameWithoutEndChar)) >= MinParts {
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

	for i := range quantity {
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

	samplePath := filepath.Join("amostras", "nomes-reais.txt")
	if err := MakeNames(samplePath, quantity, DefaultOrder); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
}
