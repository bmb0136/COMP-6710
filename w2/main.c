#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define MAX_LINE_SIZE 10

int main() {
    FILE *file = fopen("data.csv", "r");
    
    if (file == NULL) {
        perror("Unable to open file");
        return 1;
    }

    char line[MAX_LINE_SIZE];
    while (fgets(line, sizeof(line), file)) {
        
        line[strcspn(line, "\n")] = 0;
        char *token = strtok(line, ",");
        int column = 0;

        while (token != NULL) {
            printf("Row %d, Col %d: %s\n", column / 3, column % 3, token);
            token = strtok(NULL, ",");
            column++;
        }
    }
    fclose(file);
    return 0;
}
