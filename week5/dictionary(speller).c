// Implements a dictionary's functionality

#include <ctype.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <cs50.h>
#include <strings.h>

#include "dictionary.h"

// Represents a node in a hash table
typedef struct node
{
    char word[LENGTH + 1];
    struct node *next;
}
node;

// TODO: Choose number of buckets in hash table
const unsigned int N = 26;

// Hash table
node *table[N];

// Useful global variables
int word_count = 0;
node *checker;

// Returns true if word is in dictionary, else false
bool check(const char *word)
{
    for (checker = table[hash(word)]; checker != NULL; checker = checker->next)
    {
        if (strcasecmp(word, checker->word) == 0)
        {
            return true; // if word is in doctionary return true
        }
    }
    return false; // if word is not in doctionary return false
}

// Hashes word to a number
unsigned int hash(const char *word)
{
    unsigned int index;
    index = tolower(word[0]) - 'a'; // calculating index
    return index;
}

// Loads dictionary into memory, returning true if successful, else false
bool load(const char *dictionary)
{
    // Open dictionary file
    FILE *words = fopen(dictionary, "r");
    if (words == NULL)
    {
        fclose(words);
        return false;
    }

    // Read strings from file one at a time
    char word[LENGTH + 1];
    int index;

    for (int i = 0; i < N; i++)
    {
        table[i] = NULL;
    }
    while (fscanf(words, "%s", word) != EOF)
    {
        // Create a new node for each word
        node *n = malloc(sizeof(node));
        if (n == NULL)
        {
            free(n);
            return false;
        }

        index = hash(word); // Hash word to obtain a hash value

        // Insert node into hash table in that location
        strcpy(n->word, word);
        n->next = table[index];
        table[index] = n;
        word_count++;
    }
    fclose(words);
    return true;
}

// Returns number of words in dictionary if loaded, else 0 if not yet loaded
unsigned int size(void)
{
    return word_count; // Return word count
}

// Unloads dictionary from memory, returning true if successful, else false
bool unload(void)
{
    node *next_word, *word;
    for (int i = 0; i < N; i++)
    {
        next_word = table[i];
        while (next_word != NULL)
        {
            word = next_word;
            next_word = next_word->next;
            free(word);
        }
    }

    return true;
}
