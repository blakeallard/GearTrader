#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <iomanip>

struct Guitar
{
    std::string title{};
    double price{};
    std::string url;
    std::string condition;
    std::string year;
    std::string searchTerm;
    std::string scrapedAt;

    Guitar() { price = 0.0; }
};

class GuitarAnalyzer
{
private:
    std::vector<Guitar> guitars;

    void bubbleSort(std::vector<double> &prices)
    {
        std::cout << "Using Bubble Sort..." << std::endl;
        int n = prices.size();

        for (int i = 0; i < n - 1; i++)
        {
            for (int j = 0; j < n - i - 1; j++)
            {
                if (prices[j] > prices[j + 1])
                {
                    double temp = prices[j];
                    prices[j] = prices[j + 1];
                    prices[j + 1] = temp;
                }
            }
        }
    } // end bubbleSort()


    void selectionSort(std::vector<Guitar> &guitarList)
    {
        std::cout << "Using Selection Sort..." << std::endl;
        int n = guitarList.size();

        for (int i = 0; i < n - 1; i ++)
        {
            int minIndex = i;

            for (int j = i + 1; j < n; j++)
            {
                if (guitarList[j].price < guitarList[minIndex].price)
                {
                    minIndex = j;
                }
            }

            if (minIndex != i)
            {
                Guitar temp          = guitarList[i];
                guitarList[i]        = guitarList[minIndex];
                guitarList[minIndex] = temp;
            }
        }
    } // end selectionSort()


    int binarySearch(std::vector<double> &sortedPrices, double target)
    {
        std::cout << "Using Binary Search to find $" << target << "..." << std::endl;
        int left = 0;
        int right = sortedPrices.size() - 1;
        int comparisons = 0;

        while (left <= right)
        {
            comparisons++;

            int midPoint = left + (right - left) / 2;

            std::cout << " Checking position " << midPoint << " (value: $" << sortedPrices[midPoint] << ")" << std::endl;

            if (sortedPrices[midPoint] == target)
            {
                std::cout << " Found after only " << comparisons << " comparisons!" << std::endl;
                return midPoint;
            }
            if (sortedPrices[midPoint] < target)
            {
                std::cout << " Target is higher, searching right half..." << std::endl;
                left = midPoint + 1;
            }
            else 
            {
                std::cout << " Target is lower, searching left half..." << std::endl;
                right = midPoint - 1;
            }
        }
        std::cout << " Not found after " << comparisons << " comparisons.\n";
        return -1;
    } // end binarySearch()
    

    void countByPricesRanges()
    {
        std::cout << "\n COUNTING GUITARS BY PRICE RANGES " << std::endl;

        int under1000{};
        int between1000and2000{};
        int between2000and3000{};
        int between3000and4000{};
        int over4000{};

        for (Guitar &g : guitars)
        {
            if (g.price < 1000)
            {
                under1000++;
            }
            else if (g.price < 2000) 
            {
                between1000and2000++;
            }
            else if (g.price < 3000)
            {
                between2000and3000++;
            }
            else if (g.price < 4000)
            {
                between3000and4000++;            }
            else 
            {
                over4000++;            
            }
        } // end for()

        std::cout << "Under $1,000: "    << under1000          << " guitars" << std::endl;
        std::cout << "$1,000 - $2,000: " << between1000and2000 << " guitars" << std::endl;
        std::cout << "$2,000 - $3,000: " << between2000and3000 << " guitars" << std::endl;
        std::cout << "$3,000 - $4,000: " << between3000and4000 << " guitars" << std::endl;
        std::cout << "Over $4,000: "     << over4000           << " guitars" << std::endl;

    } // end countByPricesRanges()

    void stringSearch(std::string &searchWord)
    {
        std::cout << "\nSEARCHING FOR: \"" << searchWord << "\"" << std::endl;
        int found = 0;

        for (Guitar &g : guitars)
        {
            std::string title  = g.title;
            std::string search = searchWord;

            for (char &c : title)
            {
                if (c >= 'A' && c <= 'Z')
                {
                    c += 32;
                }
            }

            for (char &c : search)
            {
                if (c >= 'A' && c <= 'Z')
                {
                    c += 32;
                }
            } 
        
            bool contains = false;
            if (search.length() <= title.length())
            {
                for (int i = 0; i <= title.length() - search.length(); i++)
                {
                    bool match =  true;

                    for (int j = 0; j < search.length(); j++)
                    {
                        if (title[i + j] != search[j])
                        {
                            match = false;
                            break;
                        }
                    } // end for(j)
                    if (match)
                    {
                        contains = true;
                        break;
                    }
                } // end for(i)
            } // end if (search<=title)

            if (contains)
            {
                std::cout << "$"   << std::fixed << std::setprecision(2) << g.price
                          << " - " << g.title    << std::endl;
                found++;
            }
        } // end for(Guitar &g)
        
        if (found == 0)
        {
            std::cout << "No guitars found with \"" << searchWord << "\"" << std::endl;
        }
        else
        {
            std::cout << "Found " << found << " guitars!" << std::endl;
        }
    } // end stringSearch()


    void findMinMax()
    {
        std::cout << "\nFINDING MIN AND MAX PRICES " << std::endl;

        if (guitars.empty())
        {
            std::cout << "No guitars to analyze!" << std::endl;
            return;
        }

        double minPrice = -1;
        double maxPrice = -1;
        Guitar cheapest, mostExpensive;

        for (Guitar &g : guitars)
        {
            if (g.price > 0)
            {
                if (minPrice == -1 || g.price < minPrice)
                {
                    minPrice = g.price;
                    cheapest = g;
                }
                if (maxPrice == -1 || g.price > maxPrice)
                {
                    maxPrice = g.price;
                    mostExpensive = g;
                }
            }
        } // end for(guitars)

        if (minPrice != -1)
        {
            std::cout << " CHEAPEST: $" << std::fixed << std::setprecision(2) << minPrice << std::endl;
            std::cout << " " << cheapest.title.substr(0, 50) << "..." << std::endl;
            std::cout << " MOST EXPENSIVE: $" << maxPrice << std::endl;
            std::cout << " " << mostExpensive.title.substr(0, 50) << "..." << std::endl;
            std::cout << " PRICE DIFFERENCE: $" << (maxPrice - minPrice) << std::endl;
        }
    } // end findMinMax()


    double calcAverage()
    {
        std::cout << "\nCALCULATING AVERAGE PRICE " << std::endl;

        double sum{};
        int count{};


        for (Guitar &g : guitars)
        {
            if (g.price > 0)
            {
                sum+= g.price;
                count++;
            }
        }

        if (count == 0)
        {
            std::cout << "No valid prices found!" << std::endl;
            return 0;
        }

        double average = sum / count;


        std::cout << " Total guitars with prices: " << count      << std::endl;
        std::cout << " Sum of all prices: $"        << std::fixed << std::setprecision(2) << sum << std::endl;
        std::cout << " Average price: $"            << average    << std::endl;

        return average;
    }

public:
    void runAnalysis()
    {
        std::cout << " Running Guitar Analysis " << std::endl;
        printBasicStats();
        findMinMax();
        calcAverage();
        countByPricesRanges();
    }

    bool loadCSV(const std::string &filename)
    {
        std::ifstream file(filename);

        if (!file.is_open())
        {
            std::cerr << "ERROR: Could not open file " << filename << std::endl;
            return false;
        }

        std::string line{};
        bool isFirstLine = true;

        std::cout << "Loading guitar data from " << filename << "..." << std::endl;

        while (getline(file, line))
        {
            if (isFirstLine)
            {
                isFirstLine = false;
                continue;
            }
        
            Guitar guitar = parseCSVLine(line);
            if (!guitar.title.empty())
            {
                guitars.push_back(guitar);
            }
        } // end while()

        file.close();
        std::cout << " Loaded " << guitars.size() << " guitars!" << std::endl;
        return true;

    } // end loadCSV()

    Guitar parseCSVLine(const std::string &line)
    {
        Guitar guitar;
        std::stringstream ss(line);
        std::string cell;
        int column{};

        while (std::getline(ss, cell, ','))
        {
            if (!cell.empty() && cell.front() == '"' && cell.back() == '"')
            {
                cell = cell.substr(1, cell.length() - 2);
            }

            switch (column)
            {
                case 0: guitar.title = cell;
                        break;
                
                case 1: try
                        {
                            guitar.price = std::stod(cell);
                        }
                        catch (...)
                        {
                            guitar.price = 0.0;
                        }
                        break;

                case 2: guitar.url = cell;
                        break;

                case 3: guitar.condition = cell;
                        break;

                case 4: guitar.year = cell;
                        break;

                case 5: guitar.searchTerm = cell;
                        break;

                case 6: guitar.scrapedAt = cell;
                        break;
            } // end switch(column)
            column++;
        }
        return guitar;
    } // end parseCSVLine()

    void printBasicStats()
    {
        if (guitars.empty())
        {
            std::cout << "No guitar data to analyze\n";
            return;
        }

        std::cout << "\n===GUITAR PRICE ANALYSIS===\n";
        std::cout << "=" << std::string(40, '=') << std::endl;

        std::cout << "Total guitars found: " << guitars.size() << std::endl;

        std::vector<double> prices;
        for (Guitar &g : guitars)
        {
            if (g.price > 0)
            {
                prices.push_back(g.price);
            }
        }

        if (prices.empty())
        {
            std::cout << "No valid prices found!" << std::endl;
            return;
        }

        bubbleSort(prices);

        double sum{};

        for (double price : prices)
        {
            sum += price;
        }
        double average = sum / prices.size();


        std::cout << std::fixed << std::setprecision(2);

        std::cout << "Average price: $" << average       << std::endl;
        std::cout << "Lowest price: $"  << prices[0]     << std::endl;
        std::cout << "Highest price: $" << prices.back() << std::endl;

    }
};


int main()
{
    std::cout << "Guitar Analyzer with Basic DSA!" << std::endl;

    GuitarAnalyzer analyzer;

    std::string filename;
    std::cout << "Enter CSV filename: ";
    std::getline(std::cin, filename);

    if (!analyzer.loadCSV(filename))
    {
        std::cerr << "Failed to load CSV file!" << std::endl;
        return 1;
    }

    analyzer.runAnalysis(); 

    return 0;
}
