#include<stdio.h>
#include<iostream>
#include<set>
#include<unordered_set>
#include<unordered_map>
#include<vector>
#include<map>

using namespace std;
#define MX_NODE 100
#define INFINITY 99999999

typedef struct nde {
    int u,v, weight;
    nde() : u(0), v(0), weight(0){}
    nde(int uu, int vv, int w) : u(uu), v(vv), weight(w){}
    bool operator<(const nde &obj) const {
        return (weight <= obj.weight || ( weight < obj.weight && u > obj.u));
    }
} Node;

vector<Node> graph[MX_NODE];
int nnode;
int nedge;

void load_graph(){
    FILE *fd = fopen("inpput.txt", "r");
    int u, v, w;
    fscanf(fd, "%d", &nnode);
    fscanf(fd, "%d", &nedge);
    for(int i = 0; i < nedge; i++) { 
        fscanf(fd, "%d %d %d", &u, &v, &w);
        graph[u].push_back(Node(u,v,w));
        graph[v].push_back(Node(v,u,w));
    }
    fclose(fd);
}

void print_graph() {
    for(int i = 0; i < nnode; i++) {
        printf("[%d]-> ", i);
        for (auto x : graph[i]) { 
            printf("(%d->%d: %d),\n", x.u, x.v, x.weight);
        }
        printf("\n");
    }
}


set<Node>pnodes;
void populate_pnodes() {
    for(int i = 0; i < nnode; i++) pnodes.insert(Node(i,0, INFINITY));
}

void print_pnodes() {
    for(auto x : pnodes) { printf("%d: %d, %d\n", x.u, x.weight, x.v);}
}

unordered_set<int> visited_node;
unordered_set<int> unvisited_node;

void set_all_unvisited(){
    for(int i=0; i<nnode; i++) unvisited_node.insert(i);
}

int main() {
    load_graph();
    print_graph();

    populate_pnodes();
    print_pnodes();

    /*     
    set_all_unvisited();
    while(!unvisited_node.empty()){
        int node = *unvisited_node.begin();
        printf("from: %d", node);
        unvisited_node.erase(unvisited_node.begin());
    } */


    


    return EXIT_SUCCESS;
}