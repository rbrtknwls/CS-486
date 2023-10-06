#include <iostream>
#include <string>
#include <chrono>
#include <vector>
#include <random>
#include <algorithm>
#include <numeric>

using namespace std::chrono;
using namespace std;

// Store the boards as strings
std::string easyBoard  =  "010900053040300681070050900590070040700805009020030067009010070157003090480002030";
std::string mediumBoard = "000160925007000180000080006780200000025010630000008017100070000062000700874023000";
std::string hardBoard =   "103005400800000000000080600006049000079608240000210900005070000000000006007500103";
std::string evilBoard =   "001970000090003008000402000610000405003000100407000029000705000200300010000089500";

// This counter will be used to keep track of the number of nodes expanded
int nodesExpanded = 0;


// Helper function to display the grid
void printGrid(const int map[81]) {
    for (int i = 0; i < 9; i++) {
        cout << "{";
        for (int x = 0; x<9; x++) {
            cout << map[i*9+x];
            if (x != 8) {
                cout << ", ";
            }
        }
        cout << "}," << endl;
    }
}


/*
 * This function is used to set the domain, the domain stores all the possible values at each index.
 *  Each time we add a value we need to update the domain accordingly, thus we take in the index we
 *  want to change
 */
bool setDomain(int map[81], int domain[][10], int idx) {
    int row = idx/9;
    int column = idx%9;

    for ( int i = 0; i < 9; i++ ) {
        domain[i+row*9][map[idx]] = 1;              // Update along the row
        domain[i*9 +column][map[idx]] = 1;          // Update along the column
    }

    int rowStart = row/3;                           // Start position of grid (row)
    int columnStart = column/3;                     // Start position of grid (column)

    for (int x = 0; x < 3; x++) {
        for (int y = 0; y < 3; y++) {
            domain[columnStart*3 + (y+rowStart*3)*9 + x][map[idx]] = 1;
        }
    }
    return true;


}



/* We treat the original array like doing n insert, where n
 *  is the number of non zero elements in our array
 */
void init(int map[81], int takenValues[][10]) {
    for ( int y = 0; y < 9 ; y++ ) {
        for ( int x = 0; x < 9 ; x++ ) {
            if ( map[y*9+x] != 0 ) {
                setDomain(map, takenValues, y*9+x);
            }
        }
    }

}

/*
 * This is the main method for solving any sukodku problem, to begin we will pick a random
 *  index to loop through, after this we will we will check if there are any more values to read
 *  in. After this we will check our domain for that variable, and continue if theres a valid placement.
 *  We continue until we get a solution
 */
bool sukodku(const int board[81], const int domain[][10], const vector<int>* const valsToReplace, int pos) {

    int positionToCheck = valsToReplace->operator[](pos);
    pos++;

    if (valsToReplace->size() < pos) {
        printGrid(board);                   // Print the solution!
        return true;
    }

    for (int idx = 1; idx < 10; idx++) {

        if (domain[positionToCheck][idx] != 1) { // Check if the domain is empty

            nodesExpanded++;                     // Expand the nodes


            int newDomain[81][10];               // Make a deep copy of the domain
            int newMap[81];                      // Make a deep copy of the matrix

            for (int i = 0; i < 81; i++) {
                newMap[i] = board[i];
                for (int x = 0; x < 10; x++) {
                    newDomain[i][x] = domain[i][x];
                }
            }

            newMap[positionToCheck] = idx;
            setDomain(newMap, newDomain, positionToCheck);

            // Recurse until we can find the proper solution
            bool result = sukodku(newMap, newDomain, valsToReplace, pos);

            if (result) {
                return true;
            }
        }
    }

    return false;
}
int main() {

    vector<int> timings;                             // Vector for storing the timings per run
    vector<int> nodes;                               // Vector for storing the number of nodes per run

    auto rng = std::default_random_engine{};         // Random needed for shuffle
    rng.seed(getpid());

    for (int runs = 0; runs < 5 ; runs++ ) {         // Number of runs to do

        std::string readin = evilBoard;              // Which board to use

        // This will convert the string into a 1D int array
        int board[81];
        for (int y = 0; y < 9; y++) {
            for (int x = 0; x < 9; x++) {
                board[y * 9 + x] = readin[y * 9 + x] - '0';
            }
        }

        int takenValues[81][10];

        for (int i = 0; i < 81; i++) {
            for (int x = 0; x < 10; x++) {
                takenValues[i][x] = 0;
            }
        }

        init(board, takenValues);
        // This will store all the indexes where we have a zero
        vector<int> valsToReplace;

        for (int i = 0; i < 81; i++) {
            if (board[i] == 0) {
                valsToReplace.push_back(i);
            }
        }

        // Shuffle the list of positions to check
        shuffle(valsToReplace.begin(), valsToReplace.end(), rng);

        nodesExpanded = 0;
        // Start the time
        auto start = high_resolution_clock::now();

        sukodku(board, takenValues, &valsToReplace, 0);
        // Finish the time
        auto stop = high_resolution_clock::now();

        auto duration = duration_cast<microseconds>(stop - start);

        timings.push_back(duration.count());
        nodes.push_back(nodesExpanded);

        std::cout << runs << endl;
    }


    // The below code will calculate the timiing and number of nodes for each run
    double sum = std::accumulate(timings.begin(), timings.end(), 0.0);
    double mean = sum / timings.size();

    double var = 0;
    for( int n = 0; n < timings.size(); n++ )
    {
        var += (timings[n] - mean) * (timings[n] - mean);
    }
    var /= timings.size();
    double stdev = sqrt(var);

    std::cout << "Timing average: " << mean << " | Timing std deviation: " << stdev << endl;

    sum = std::accumulate(nodes.begin(), nodes.end(), 0.0);
    mean = sum / nodes.size();



    var = 0;
    for( int n = 0; n < nodes.size(); n++ )
    {
        var += (nodes[n] - mean) * (nodes[n] - mean);
    }
    var /= nodes.size();
    stdev = sqrt(var);

    std::cout << "Node average: " << mean << " | Node std deviation: " << stdev << endl;

    return 0;
}
