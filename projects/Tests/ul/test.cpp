#include<iostream>
#include<vector>
#include<algorithm>
using namespace std;

int& get_median(vector<int> values) {
	auto* temp = new vector<int>();
	for (auto x : values) temp->push_back(x);
	sort(temp->begin(), temp->end());
	return (*temp)[(temp->size()-1) / 2];
}

int main() {
	cout << "median: " << get_median({ 4,5,6,3 }) << endl;
	cout << "median: " << get_median({ 6,3 }) << endl;
	cout << "median: " << get_median({ 5,3,6 }) << endl;
	return EXIT_SUCCESS;
}