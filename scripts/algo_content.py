#!/usr/bin/env python3
"""Algorithm topic content for the Algorithms learning hub.

Authoring convention
--------------------
* All prose (what / why / when / how-to-select / when-not / applications) is
  original text written specifically for this project from standard, widely
  known computer-science knowledge. Nothing is copied from any website.
* Reference links (e.g. GeeksforGeeks) are plain citations for further
  reading only -- they are never quoted or reproduced.
* Every topic carries three original implementations (C, C++, Python) plus
  a ``sim()`` generator that replays the algorithm step-by-step. The build
  pipeline (build_algorithms.py) compiles and runs the C/C++ code, runs the
  Python code, verifies all three produce identical test output, captures the
  real output for the page, and records the simulation trace.

Schema of a topic dict
----------------------
id, name, slug, type (key into TYPES), priority (1-5), difficulty, icon,
complexity {best, average, worst, space, stable, in_place},
what (str), why (str), when_needed [str], how_to_select [str],
when_not [str], outline [str], applications [{title, detail}],
impl_c, impl_cpp, impl_py (source strings), sim (callable -> [step dicts]),
references [{title, url}], kind (sim renderer: array|grid|graph|board|tree)
"""

# ---------------------------------------------------------------------------
# Type registry (the 6 focus areas)
# ---------------------------------------------------------------------------

TYPES = {
    "sorting-searching": {
        "label": "Sorting & Searching",
        "icon": "🔍",
        "blurb": "Core ordering and lookup algorithms, from O(n²) sorts to divide-and-conquer and non-comparison sorts.",
    },
    "backtracking": {
        "label": "Backtracking",
        "icon": "🔁",
        "blurb": "Systematic search over all candidates with pruning for constraint-satisfaction problems.",
    },
    "tree": {
        "label": "Tree",
        "icon": "🌳",
        "blurb": "Hierarchical data structures and the algorithms that keep them balanced and searchable.",
    },
    "graph": {
        "label": "Graph",
        "icon": "🕸️",
        "blurb": "Traversal, shortest paths, ordering, and connectivity algorithms on networks.",
    },
    "greedy": {
        "label": "Greedy",
        "icon": "💰",
        "blurb": "Algorithms that make the locally optimal choice and provably reach a global optimum.",
    },
    "dynamic-programming": {
        "label": "Dynamic Programming",
        "icon": "📈",
        "blurb": "Breaking problems into overlapping subproblems with memoization and tabulation.",
    },
}

PRIORITY_LABELS = {
    5: "Must Know",
    4: "Important",
    3: "Useful",
    2: "Good to Know",
    1: "Optional",
}

PRIORITY_COLORS = {
    5: "#dc2626",
    4: "#ea580c",
    3: "#2563eb",
    2: "#64748b",
    1: "#94a3b8",
}


def priority_label(priority):
    return PRIORITY_LABELS.get(priority, "Useful")


def priority_color(priority):
    return PRIORITY_COLORS.get(priority, "#2563eb")

# ---------------------------------------------------------------------------
# Topic: Binary Search
# ---------------------------------------------------------------------------

def sim_binary_search():
    """Trace classic binary search on a sorted array (array renderer)."""
    data = [1, 3, 5, 7, 9, 11, 13, 15]
    target = 11
    lo, hi = 0, len(data) - 1
    out = []

    def step(caption, highlights, compare, lo, hi, mid=None, done=False):
        markers = {"lo": lo, "hi": hi}
        if mid is not None:
            markers["mid"] = mid
        out.append({
            "kind": "array",
            "data": list(data),
            "highlights": list(highlights),
            "compare": list(compare),
            "swap": [],
            "markers": markers,
            "caption": caption,
            "done": done,
        })

    step(f"Start: search space [{lo}, {hi}], looking for {target}", [], [], lo, hi)
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        step(
            f"mid = {mid} -> A[{mid}] = {data[mid]}; compare with {target}",
            [mid], [mid], lo, hi, mid,
        )
        if data[mid] == target:
            step(f"Match! A[{mid}] == {target}. Return index {mid}.", [mid], [mid], lo, hi, mid, True)
            return out
        if data[mid] < target:
            step(f"A[{mid}] = {data[mid]} < {target} -> discard left half, lo = {mid + 1}", [mid], [mid], mid + 1, hi, None)
            lo = mid + 1
        else:
            step(f"A[{mid}] = {data[mid]} > {target} -> discard right half, hi = {mid - 1}", [mid], [mid], lo, mid - 1, None)
            hi = mid - 1
    step("Search space exhausted: target is not in the array.", [], [], lo, hi, None, True)
    return out


BINARY_SEARCH_C = r'''#include <stdio.h>

/* Binary search: inspect at most log2(n) pivots, halving the space each time.
 * Returns an index where a[i] == target, or -1. */
int binary_search(int a[], int n, int target) {
    int lo = 0, hi = n - 1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;   /* avoids lo+hi overflow */
        if (a[mid] == target) return mid;
        if (a[mid] < target) lo = mid + 1;
        else                 hi = mid - 1;
    }
    return -1;
}

/* Lower bound: first index i with a[i] >= target (duplicates / boundary
 * queries). Returns n when no such index exists. */
int lower_bound_idx(int a[], int n, int target) {
    int lo = 0, hi = n;
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (a[mid] < target) lo = mid + 1;
        else                 hi = mid;
    }
    return lo;
}

int main(void) {
    int a[] = {1, 3, 5, 7, 9, 11, 13, 15};
    int b[] = {1, 1, 2, 2, 2, 3};
    printf("Test 1: %d\n", binary_search(a, 8, 7));       /* 3  */
    printf("Test 2: %d\n", binary_search(a, 8, 10));      /* -1 */
    printf("Test 3: %d\n", binary_search(a, 8, 1));       /* 0  */
    printf("Test 4: %d\n", lower_bound_idx(a, 8, 8));     /* 4  */
    printf("Test 5: %d\n", binary_search(b, 6, 2));       /* 2  */
    printf("Test 6: %d\n", lower_bound_idx(b, 6, 2));     /* 2  */
    return 0;
}
'''


BINARY_SEARCH_CPP = r'''#include <iostream>
#include <vector>
using namespace std;

/* Returns an index holding target, else -1. */
int binarySearch(const vector<int>& a, int target) {
    int lo = 0, hi = (int)a.size() - 1;
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        if (a[mid] == target) return mid;
        if (a[mid] < target) lo = mid + 1;
        else                 hi = mid - 1;
    }
    return -1;
}

/* First index with value >= target (std::lower_bound behaviour). */
int lowerBound(const vector<int>& a, int target) {
    int lo = 0, hi = (int)a.size();
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (a[mid] < target) lo = mid + 1;
        else                 hi = mid;
    }
    return lo;
}

int main() {
    vector<int> a = {1, 3, 5, 7, 9, 11, 13, 15};
    vector<int> b = {1, 1, 2, 2, 2, 3};
    cout << "Test 1: " << binarySearch(a, 7)  << "\n";
    cout << "Test 2: " << binarySearch(a, 10) << "\n";
    cout << "Test 3: " << binarySearch(a, 1)  << "\n";
    cout << "Test 4: " << lowerBound(a, 8)    << "\n";
    cout << "Test 5: " << binarySearch(b, 2)  << "\n";
    cout << "Test 6: " << lowerBound(b, 2)    << "\n";
    return 0;
}
'''


BINARY_SEARCH_PY = r'''def binary_search(a, target):
    """Return an index where a[index] == target, else -1."""
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if a[mid] == target:
            return mid
        if a[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def lower_bound(a, target):
    """Return the first index with a[index] >= target."""
    lo, hi = 0, len(a)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if a[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo


if __name__ == "__main__":
    a = [1, 3, 5, 7, 9, 11, 13, 15]
    b = [1, 1, 2, 2, 2, 3]
    print(f"Test 1: {binary_search(a, 7)}")
    print(f"Test 2: {binary_search(a, 10)}")
    print(f"Test 3: {binary_search(a, 1)}")
    print(f"Test 4: {lower_bound(a, 8)}")
    print(f"Test 5: {binary_search(b, 2)}")
    print(f"Test 6: {lower_bound(b, 2)}")
'''
TOPIC_BINARY_SEARCH = {
    "id": "binary-search",
    "name": "Binary Search",
    "slug": "binary-search",
    "type": "sorting-searching",
    "type_label": TYPES["sorting-searching"]["label"],
    "type_icon": TYPES["sorting-searching"]["icon"],
    "priority": 5,
    "difficulty": "Medium",
    "icon": "🎯",
    "kind": "array",
    "complexity": {
        "best": "O(1)",
        "average": "O(log n)",
        "worst": "O(log n)",
        "space": "O(1) (iterative)",
        "stable": "—",
        "in_place": "—",
    },
    "what": (
        "Binary search is a divide-and-conquer lookup that finds a target in a sorted array by repeatedly "
        "comparing it with the middle element and discarding the half that cannot contain the target. Each "
        "step halves the remaining search space, so a million-element array needs at most about twenty "
        "comparisons instead of a million."
    ),
    "why": (
        "Linear scanning costs O(n) per lookup, which is too slow when data is large and lookups are frequent. "
        "Much real data is kept sorted (IDs, timestamps, dictionary keys, records in a database), and binary "
        "search exploits that ordering to answer a lookup in O(log n). That difference turns an unusable "
        "search into one that scales to billions of records."
    ),
    "when_needed": [
        "The collection is sorted (or can be sorted), and you need to know whether a value exists or where it is.",
        "You need a boundary rather than an exact match: first/last occurrence, lower or upper bound, or a count of equal values.",
        "The problem is a minimisation/maximisation with a monotonic feasibility check (search on the answer space).",
        "Records are large and you cannot afford to read them one by one.",
    ],
    "how_to_select": [
        "Confirm the input is sorted (or sortable); for unsorted data binary search does not apply directly.",
        "Use the classic find-any variant when a single match is enough.",
        "Switch to lower_bound / upper_bound variants when duplicates exist or a boundary index is wanted.",
        "Use the search-on-answer form when the task is \"smallest value where predicate(v) is true\" and predicate is monotonic.",
        "Keep the loop invariant in mind: the search space shrinks each round, and mid = lo + (hi - lo) / 2 avoids overflow.",
    ],
    "when_not": [
        "Data is not sorted and a full sort (O(n log n)) would cost more than one linear scan.",
        "The collection is tiny — a linear pass is equally fast and simpler to write.",
        "Random access is expensive, e.g. a linked list, where binary search degrades badly.",
        "You are searching unstructured text or fuzzy matches where ordering is not meaningful.",
    ],
    "outline": [
        "Divide-and-conquer lookup on sorted data: halve the search space every step",
        "O(log n) time with O(1) extra space when written iteratively",
        "Lower bound / upper bound variants handle duplicates and boundary queries",
        "Search-on-answer form solves monotonic optimisation problems",
    ],
    "applications": [
        {"title": "Database & library lookups", "detail": "B-tree and dictionary indexes use bisection to locate keys among millions of entries."},
        {"title": "git bisect", "detail": "Finds the first \"bad\" commit in a history by binary-search-style partitioning of the commit range."},
        {"title": "Search-on-answer problems", "detail": "Book allocation, ship capacity, and \"smallest feasible X\" problems reduce to monotonic binary search."},
        {"title": "Standard library building block", "detail": "bisect in Python, lower_bound in C++, and Arrays.binarySearch in Java rest on this idea."},
    ],
    "impl_c": BINARY_SEARCH_C,
    "impl_cpp": BINARY_SEARCH_CPP,
    "impl_py": BINARY_SEARCH_PY,
    "sim": sim_binary_search,
    "references": [
        {"title": "GeeksforGeeks — Binary Search (reference)", "url": "https://www.geeksforgeeks.org/binary-search/"},
    ],
}
# ---------------------------------------------------------------------------
# Topic: Merge Sort
# ---------------------------------------------------------------------------

def sim_merge_sort():
    """Trace divide-and-conquer merge sort (array renderer)."""
    a = [38, 27, 43, 3, 9, 82, 10]
    n = len(a)
    out = []

    def emit(caption, highlights, compare, swap, data, done=False):
        out.append({
            "kind": "array",
            "data": list(data),
            "highlights": list(highlights),
            "compare": list(compare),
            "swap": list(swap),
            "markers": {},
            "caption": caption,
            "done": done,
        })

    def merge(lo, mid, hi):
        left = a[lo:mid + 1]
        right = a[mid + 1:hi + 1]
        i = j = 0
        k = lo
        merged = list(a)
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                merged[k] = left[i]
                emit(f"Take {left[i]} from left into position {k}", [k], [lo + i, mid + 1 + j], [], merged)
                i += 1
            else:
                merged[k] = right[j]
                emit(f"Take {right[j]} from right into position {k}", [k], [lo + i, mid + 1 + j], [], merged)
                j += 1
            k += 1
        while i < len(left):
            merged[k] = left[i]
            emit(f"Copy remaining left value {left[i]} to position {k}", [k], [], [], merged)
            i += 1
            k += 1
        while j < len(right):
            merged[k] = right[j]
            emit(f"Copy remaining right value {right[j]} to position {k}", [k], [], [], merged)
            j += 1
            k += 1
        a[lo:hi + 1] = merged[lo:hi + 1]
        emit(f"Merged range [{lo}..{hi}] -> {a}", list(range(lo, hi + 1)), [], [], list(a))

    def sort_range(lo, hi):
        if lo >= hi:
            return
        mid = (lo + hi) // 2
        emit(f"Divide range [{lo}..{hi}] at mid = {mid}", list(range(lo, hi + 1)), [], [], list(a))
        sort_range(lo, mid)
        sort_range(mid + 1, hi)
        merge(lo, mid, hi)

    emit("Start — array to sort", [], [], [], list(a))
    sort_range(0, n - 1)
    emit("Sorted!", list(range(n)), [], [], list(a), True)
    return out


MERGE_SORT_C = r'''#include <stdio.h>
#include <stdlib.h>

/* Merge two sorted halves a[lo..mid] and a[mid+1..hi] into a[lo..hi]. */
void merge(int a[], int lo, int mid, int hi) {
    int n1 = mid - lo + 1, n2 = hi - mid;
    int *L = (int *)malloc((size_t)n1 * sizeof(int));
    int *R = (int *)malloc((size_t)n2 * sizeof(int));
    for (int i = 0; i < n1; i++) L[i] = a[lo + i];
    for (int j = 0; j < n2; j++) R[j] = a[mid + 1 + j];
    int i = 0, j = 0, k = lo;
    while (i < n1 && j < n2) {
        if (L[i] <= R[j]) a[k++] = L[i++];
        else              a[k++] = R[j++];
    }
    while (i < n1) a[k++] = L[i++];
    while (j < n2) a[k++] = R[j++];
    free(L);
    free(R);
}

void merge_sort(int a[], int lo, int hi) {
    if (lo >= hi) return;
    int mid = lo + (hi - lo) / 2;
    merge_sort(a, lo, mid);
    merge_sort(a, mid + 1, hi);
    merge(a, lo, mid, hi);
}

void print_array(int a[], int n) {
    for (int i = 0; i < n; i++) printf("%d ", a[i]);
    printf("\n");
}

int main(void) {
    int a1[] = {38, 27, 43, 3, 9, 82, 10};
    int a2[] = {5, 4, 3, 2, 1};
    int a3[] = {1, 2, 3, 4, 5};
    merge_sort(a1, 0, 6); print_array(a1, 7);
    merge_sort(a2, 0, 4); print_array(a2, 5);
    merge_sort(a3, 0, 4); print_array(a3, 5);
    return 0;
}
'''


MERGE_SORT_CPP = r'''#include <iostream>
#include <vector>
using namespace std;

void merge(vector<int>& a, int lo, int mid, int hi) {
    vector<int> L(a.begin() + lo, a.begin() + mid + 1);
    vector<int> R(a.begin() + mid + 1, a.begin() + hi + 1);
    int i = 0, j = 0, k = lo;
    while (i < (int)L.size() && j < (int)R.size()) {
        if (L[i] <= R[j]) a[k++] = L[i++];
        else              a[k++] = R[j++];
    }
    while (i < (int)L.size()) a[k++] = L[i++];
    while (j < (int)R.size()) a[k++] = R[j++];
}

void mergeSort(vector<int>& a, int lo, int hi) {
    if (lo >= hi) return;
    int mid = lo + (hi - lo) / 2;
    mergeSort(a, lo, mid);
    mergeSort(a, mid + 1, hi);
    merge(a, lo, mid, hi);
}

int main() {
    vector<int> a1 = {38, 27, 43, 3, 9, 82, 10};
    vector<int> a2 = {5, 4, 3, 2, 1};
    vector<int> a3 = {1, 2, 3, 4, 5};
    mergeSort(a1, 0, (int)a1.size() - 1); for (int x : a1) cout << x << " "; cout << "\n";
    mergeSort(a2, 0, (int)a2.size() - 1); for (int x : a2) cout << x << " "; cout << "\n";
    mergeSort(a3, 0, (int)a3.size() - 1); for (int x : a3) cout << x << " "; cout << "\n";
    return 0;
}
'''


MERGE_SORT_PY = r'''def merge(a, lo, mid, hi):
    """Merge the two sorted halves a[lo..mid] and a[mid+1..hi]."""
    left = a[lo:mid + 1]
    right = a[mid + 1:hi + 1]
    i = j = 0
    k = lo
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            a[k] = left[i]
            i += 1
        else:
            a[k] = right[j]
            j += 1
        k += 1
    while i < len(left):
        a[k] = left[i]
        i += 1
        k += 1
    while j < len(right):
        a[k] = right[j]
        j += 1
        k += 1


def merge_sort(a, lo, hi):
    if lo >= hi:
        return
    mid = (lo + hi) // 2
    merge_sort(a, lo, mid)
    merge_sort(a, mid + 1, hi)
    merge(a, lo, mid, hi)


if __name__ == "__main__":
    for arr in ([38, 27, 43, 3, 9, 82, 10], [5, 4, 3, 2, 1], [1, 2, 3, 4, 5]):
        merge_sort(arr, 0, len(arr) - 1)
        print(" ".join(map(str, arr)))
'''
TOPIC_MERGE_SORT = {
    "id": "merge-sort",
    "name": "Merge Sort",
    "slug": "merge-sort",
    "type": "sorting-searching",
    "type_label": TYPES["sorting-searching"]["label"],
    "type_icon": TYPES["sorting-searching"]["icon"],
    "priority": 5,
    "difficulty": "Medium",
    "icon": "🧩",
    "kind": "array",
    "complexity": {
        "best": "O(n log n)",
        "average": "O(n log n)",
        "worst": "O(n log n)",
        "space": "O(n) auxiliary",
        "stable": "Yes",
        "in_place": "No",
    },
    "what": (
        "Merge sort is a divide-and-conquer sort. It splits the array into two halves, recursively sorts each "
        "half, then merges the two sorted halves back into one sorted sequence using an auxiliary buffer. "
        "Because every input order follows the same deterministic schedule, its running time is always O(n log n)."
    ),
    "why": (
        "Quick sort can hit a quadratic worst case, and some problems require a stable sort or a guaranteed "
        "O(n log n) bound. Merge sort provides both, and its merge step is exactly the operation used to "
        "combine already-sorted runs — which is why it underpins external sorting and library hybrid sorts."
    ),
    "when_needed": [
        "You need a guaranteed O(n log n) worst case regardless of input order.",
        "Stability matters: equal keys must keep their original relative order (multi-key sorting).",
        "You are sorting a linked list, where merging needs no random access.",
        "The data does not fit in memory — external merge sort repeatedly merges sorted runs on disk.",
    ],
    "how_to_select": [
        "Pick merge sort when the worst-case bound must be reliable and stability is required.",
        "Prefer it for linked lists; for arrays, quicksort is usually faster in practice (better constants).",
        "For tiny subproblems switch to insertion sort inside the recursion — real libraries do this.",
        "Use the inversion-count variant when a sorted order diagnosis is part of the task.",
    ],
    "when_not": [
        "When space is tight and an in-place sort is needed (merge sort costs O(n) auxiliary memory).",
        "For small arrays in hot loops — insertion sort has better constants.",
        "For near-sorted data — insertion sort runs in O(n) on such input, merge sort still pays O(n log n).",
        "When you need the fastest average sort and memory is constrained — quicksort usually wins.",
    ],
    "outline": [
        "Divide-and-conquer: split, sort both halves, merge in O(n)",
        "Worst-case O(n log n) and stable — no input can break it",
        "Costs O(n) auxiliary space; merges map directly to external sorting",
        "Variant — count inversions while merging",
    ],
    "applications": [
        {"title": "Library sorting", "detail": "Python's sorted() and Java's object sorts are merge-based hybrids (TimSort); merge sort is their backbone."},
        {"title": "External sorting", "detail": "Databases merge sorted runs on disk because merging reads data sequentially and needs little memory."},
        {"title": "Linked list sorting", "detail": "Merging needs no random access, making merge sort the natural choice for list-based containers."},
        {"title": "Inversion counting", "detail": "A tiny change to the merge step counts how many pairs are out of order — used in collaborative filtering and similarity measures."},
    ],
    "impl_c": MERGE_SORT_C,
    "impl_cpp": MERGE_SORT_CPP,
    "impl_py": MERGE_SORT_PY,
    "sim": sim_merge_sort,
    "references": [
        {"title": "GeeksforGeeks — Merge Sort (reference)", "url": "https://www.geeksforgeeks.org/merge-sort/"},
    ],
}
# ---------------------------------------------------------------------------
# Topic: Backtracking Fundamentals (Subsets, Permutations, Combination Sum)
# ---------------------------------------------------------------------------

def sim_backtracking_basics():
    """Trace include/skip subset generation of [1, 2, 3] (array renderer)."""
    a = [1, 2, 3]
    n = len(a)
    out = []
    chosen, chosen_idx = [], []

    def emit(caption, highlights, cur=None, done=False):
        markers = {} if cur is None else {"hi": cur}
        out.append({
            "kind": "array",
            "data": list(a),
            "highlights": list(highlights),
            "compare": [],
            "swap": [],
            "markers": markers,
            "caption": caption,
            "done": done,
        })

    def fmt_sel(idxs):
        return "[" + " ".join(str(a[i]) for i in idxs) + "]"

    def rec(idx):
        if idx == n:
            last = len(out) > 0
            emit(f"Decision made for every element -> record subset {fmt_sel(chosen_idx)}",
                 chosen_idx, done=last and chosen_idx == [])
            return
        # include branch
        chosen.append(a[idx])
        chosen_idx.append(idx)
        emit(f"Include A[{idx}] = {a[idx]} -> chosen so far {fmt_sel(chosen_idx)}", chosen_idx, idx)
        rec(idx + 1)
        chosen.pop()
        chosen_idx.pop()
        emit(f"Backtrack: undo the include of A[{idx}] -> chosen {fmt_sel(chosen_idx)}", chosen_idx, idx)
        # skip branch
        emit(f"Skip A[{idx}] -> chosen stays {fmt_sel(chosen_idx)}", chosen_idx, idx)
        rec(idx + 1)

    emit("Start — every subset of [1, 2, 3]: at each index decide include or skip", [])
    rec(0)
    if out and not out[-1]["done"]:
        out[-1]["done"] = True
    return out


BACKTRACKING_BASICS_C = r'''#include <stdio.h>

void swap_int(int *x, int *y) { int t = *x; *x = *y; *y = t; }

void print_sel(const int sel[], int k) {
    printf("[");
    for (int i = 0; i < k; i++) printf(i ? " %d" : "%d", sel[i]);
    printf("]");
}

/* 1) All subsets: at each index choose "include" or "skip". O(2^n) leaves. */
void subsets_rec(int a[], int n, int idx, int sel[], int k) {
    if (idx == n) {
        print_sel(sel, k);
        printf("\n");
        return;
    }
    sel[k] = a[idx];                            /* include a[idx] */
    subsets_rec(a, n, idx + 1, sel, k + 1);
    subsets_rec(a, n, idx + 1, sel, k);         /* skip a[idx] (implicit undo) */
}

/* 2) All permutations: try every candidate in the remaining suffix for slot
 * idx, recurse, then swap back to restore state. O(n * n!) total. */
void perms_rec(int a[], int n, int idx) {
    if (idx == n) {
        int tmp[16];
        for (int i = 0; i < n; i++) tmp[i] = a[i];
        print_sel(tmp, n);
        printf("\n");
        return;
    }
    for (int i = idx; i < n; i++) {
        swap_int(&a[idx], &a[i]);               /* choose a[i] for slot idx */
        perms_rec(a, n, idx + 1);
        swap_int(&a[idx], &a[i]);               /* undo (backtrack) */
    }
}

/* 3) Combination sum (reuse allowed): pick candidates in non-decreasing
 * index order so each combination is produced exactly once. */
void combo_rec(int cand[], int m, int idx, int rem, int sel[], int k) {
    if (rem == 0) {
        print_sel(sel, k);
        printf("\n");
        return;
    }
    for (int i = idx; i < m; i++) {
        if (cand[i] > rem) continue;            /* prune: would overshoot */
        sel[k] = cand[i];
        combo_rec(cand, m, i, rem - cand[i], sel, k + 1);  /* i reused */
    }
}

int main(void) {
    int a[] = {1, 2, 3}, sel[16];

    printf("Test 1 (subsets of [1 2 3]):\n");
    subsets_rec(a, 3, 0, sel, 0);

    printf("Test 2 (permutations of [1 2 3]):\n");
    int p[] = {1, 2, 3};
    perms_rec(p, 3, 0);

    printf("Test 3 (combination sum 7 from [2 3 6 7]):\n");
    int cand[] = {2, 3, 6, 7};
    combo_rec(cand, 4, 0, 7, sel, 0);
    return 0;
}
'''


BACKTRACKING_BASICS_CPP = r'''#include <iostream>
#include <vector>
using namespace std;

void printSel(const vector<int>& sel) {
    cout << "[";
    for (size_t i = 0; i < sel.size(); i++) {
        if (i) cout << " ";
        cout << sel[i];
    }
    cout << "]";
}

/* 1) All subsets: include-or-skip decision per index. */
void subsetsRec(const vector<int>& a, int idx, vector<int>& sel) {
    if (idx == (int)a.size()) {
        printSel(sel);
        cout << "\n";
        return;
    }
    sel.push_back(a[idx]);          /* include a[idx] */
    subsetsRec(a, idx + 1, sel);
    sel.pop_back();                 /* undo, then skip */
    subsetsRec(a, idx + 1, sel);
}

/* 2) All permutations: swap each suffix candidate into slot idx, recurse,
 * swap back. */
void permsRec(vector<int>& a, int idx) {
    if (idx == (int)a.size()) {
        printSel(a);
        cout << "\n";
        return;
    }
    for (int i = idx; i < (int)a.size(); i++) {
        swap(a[idx], a[i]);         /* choose */
        permsRec(a, idx + 1);
        swap(a[idx], a[i]);         /* undo (backtrack) */
    }
}

/* 3) Combination sum (reuse allowed), DFS in non-decreasing index order. */
void comboRec(const vector<int>& cand, int idx, int rem, vector<int>& sel) {
    if (rem == 0) {
        printSel(sel);
        cout << "\n";
        return;
    }
    for (int i = idx; i < (int)cand.size(); i++) {
        if (cand[i] > rem) continue;   /* prune: would overshoot */
        sel.push_back(cand[i]);
        comboRec(cand, i, rem - cand[i], sel);   /* i reused */
        sel.pop_back();                          /* undo */
    }
}

int main() {
    vector<int> a = {1, 2, 3}, sel;

    cout << "Test 1 (subsets of [1 2 3]):\n";
    subsetsRec(a, 0, sel);

    cout << "Test 2 (permutations of [1 2 3]):\n";
    vector<int> p = {1, 2, 3};
    permsRec(p, 0);

    cout << "Test 3 (combination sum 7 from [2 3 6 7]):\n";
    vector<int> cand = {2, 3, 6, 7};
    comboRec(cand, 0, 7, sel);
    return 0;
}
'''


BACKTRACKING_BASICS_PY = r'''def print_sel(sel):
    print("[" + " ".join(map(str, sel)) + "]")


def subsets_rec(a, idx, sel):
    """All subsets: include-or-skip decision per index."""
    if idx == len(a):
        print_sel(sel)
        return
    sel.append(a[idx])          # include a[idx]
    subsets_rec(a, idx + 1, sel)
    sel.pop()                   # undo, then skip
    subsets_rec(a, idx + 1, sel)


def perms_rec(a, idx):
    """All permutations: swap each suffix candidate into slot idx, recurse,
    swap back to restore state."""
    if idx == len(a):
        print_sel(a)
        return
    for i in range(idx, len(a)):
        a[idx], a[i] = a[i], a[idx]     # choose
        perms_rec(a, idx + 1)
        a[idx], a[i] = a[i], a[idx]     # undo (backtrack)


def combo_rec(cand, idx, rem, sel):
    """Combination sum (reuse allowed), DFS in non-decreasing index order."""
    if rem == 0:
        print_sel(sel)
        return
    for i in range(idx, len(cand)):
        if cand[i] > rem:               # prune: would overshoot
            continue
        sel.append(cand[i])
        combo_rec(cand, i, rem - cand[i], sel)   # i reused
        sel.pop()                                # undo


if __name__ == "__main__":
    a = [1, 2, 3]
    sel = []

    print("Test 1 (subsets of [1 2 3]):")
    subsets_rec(a, 0, sel)

    print("Test 2 (permutations of [1 2 3]):")
    perms_rec([1, 2, 3], 0)

    print("Test 3 (combination sum 7 from [2 3 6 7]):")
    combo_rec([2, 3, 6, 7], 0, 7, sel)
'''
TOPIC_BACKTRACKING_BASICS = {
    "id": "backtracking-fundamentals",
    "name": "Backtracking Fundamentals",
    "slug": "backtracking-fundamentals",
    "type": "backtracking",
    "type_label": TYPES["backtracking"]["label"],
    "type_icon": TYPES["backtracking"]["icon"],
    "priority": 5,
    "difficulty": "Medium",
    "icon": "🧩",
    "kind": "array",
    "complexity": {
        "best": "O(2ⁿ) subsets (n decisions)",
        "average": "O(n · n!) permutations",
        "worst": "Exponential in the decision depth",
        "space": "O(n) recursion depth (excluding output)",
        "stable": "n/a",
        "in_place": "Yes (state is undone in place)",
    },
    "what": (
        "Backtracking is a systematic walk over a state-space tree: at every step you make one choice, "
        "recurse to explore everything that choice makes possible, and then undo the choice before trying "
        "the next one. The undo step is what makes it backtracking — the search reuses one small piece of "
        "state instead of copying it at every branch. Pruning rules kill whole subtrees as soon as they "
        "become impossible, which is where the real speedup over brute force comes from."
    ),
    "why": (
        "Many problems — generating every subset, permutation, puzzle solution, or exact cover — have "
        "exponentially many answers, so no polynomial algorithm can enumerate them all. Backtracking is "
        "the cleanest correct framework for that: it produces every candidate exactly once, spends O(depth) "
        "memory instead of copying paths, and its prune-early discipline often cuts practical runtimes by "
        "orders of magnitude even when the worst case stays exponential."
    ),
    "when_needed": [
        "The task asks for all solutions (all subsets, permutations, combinations, boards).",
        "A feasibility problem where any valid assignment will do (Sudoku, N-Queens).",
        "The search space is a tree of decisions and choices can be checked incrementally.",
        "Exponential output is inherent — no polynomial algorithm can list every answer.",
    ],
    "how_to_select": [
        "Draw the state-space tree first: what is a 'level', what are the 'choices' at each level?",
        "Prune as early as possible — reject a partial state the moment a constraint breaks.",
        "Order candidates (sorted order, most-constrained first) so good branches are found early.",
        "Count only distinct solutions: enforce an ordering rule (e.g., non-decreasing candidate index).",
        "Estimate the tree size before coding — 2ⁿ for subsets, n·n! for permutations, T/M branching for combination sums.",
    ],
    "when_not": [
        "Only one optimal value is needed and the problem has optimal substructure — DP usually beats it.",
        "The problem is polynomial (sorting, shortest path) — direct algorithms are far simpler.",
        "n is large and no effective pruning exists — exponential time will not finish.",
        "An approximation or heuristic answer is acceptable — local search or greedy may suffice.",
    ],
    "outline": [
        "Choose → explore → undo: the three-line recursion pattern behind every backtracking solution",
        "Subsets: include-or-skip decision per element, 2ⁿ leaves",
        "Permutations: swap each remaining candidate into the current slot, n·n! leaves",
        "Combination sum: reuse allowed, index-order rule keeps combinations distinct",
        "Pruning: bail out of a branch the instant a constraint is violated",
    ],
    "applications": [
        {"title": "Puzzle and game solvers", "detail": "Sudoku, crosswords, and constraint games are solved with exactly this include/test/undo loop."},
        {"title": "Combinatorial test generation", "detail": "Covering arrays and test-case enumeration walk a state-space tree with constraint pruning."},
        {"title": "Compiler register allocation", "detail": "Precise allocation can be phrased as backtracking over interference-graph colourings."},
        {"title": "Scheduling and packing", "detail": "Exact solvers for small job-shop and bin-packing instances branch, bound, and backtrack."},
    ],
    "impl_c": BACKTRACKING_BASICS_C,
    "impl_cpp": BACKTRACKING_BASICS_CPP,
    "impl_py": BACKTRACKING_BASICS_PY,
    "sim": sim_backtracking_basics,
    "references": [
        {"title": "GeeksforGeeks — Backtracking Algorithms (reference)", "url": "https://www.geeksforgeeks.org/backtracking-algorithms/"},
        {"title": "GeeksforGeeks — Combinational Sum (reference)", "url": "https://www.geeksforgeeks.org/combinational-sum/"},
    ],
}


# ---------------------------------------------------------------------------
# Topic: Sudoku Solver (Backtracking)
# ---------------------------------------------------------------------------

def sim_sudoku():
    """Trace backtracking fill of a classic Sudoku (board renderer)."""
    puzzle = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]
    g = [row[:] for row in puzzle]
    given = [[v != 0 for v in row] for row in puzzle]
    out = []

    def emit(caption, last=None, conflict=None, done=False):
        out.append({
            "kind": "board",
            "n": 9,
            "cells": [row[:] for row in g],
            "given": [row[:] for row in given],
            "last": last,
            "conflict": [list(c) for c in (conflict or [])],
            "caption": caption,
            "done": done,
        })

    def candidates(r, c):
        used = set(g[r]) | {g[i][c] for i in range(9)}
        br, bc = (r // 3) * 3, (c // 3) * 3
        used |= {g[i][j] for i in range(br, br + 3) for j in range(bc, bc + 3)}
        return [v for v in range(1, 10) if v not in used]

    def find_mrv():
        """Empty cell with the fewest legal digits (most constrained)."""
        best = None
        for i in range(9):
            for j in range(9):
                if g[i][j] == 0:
                    cands = candidates(i, j)
                    if best is None or len(cands) < len(best[2]):
                        best = (i, j, cands)
                        if len(cands) <= 1:
                            return best
        return best

    def solve():
        cell = find_mrv()
        if cell is None:
            emit("Solved — every row, column and 3×3 box holds 1-9 exactly once",
                 None, [], True)
            return True
        r, c, cands = cell
        if not cands:
            emit(f"Dead end: row {r}, col {c} has no legal digit — undo the previous placement",
                 [r, c], [[r, c]])
            return False
        for v in cands:
            g[r][c] = v
            emit(f"Place {v} at row {r}, col {c} — cell had {len(cands)} legal digit(s), "
                 "fewest on the board", [r, c])
            if solve():
                return True
            g[r][c] = 0
            emit(f"{v} at row {r}, col {c} fails deeper — undo it and try the next candidate",
                 [r, c], [[r, c]])
        return False

    emit("Given puzzle — 30 clues, 51 empty cells. Each step fills the most constrained "
         "cell (MRV heuristic)", None, [])
    solve()
    return out


SUDOKU_C = r'''#include <stdio.h>

/* Working grid; 0 marks an empty cell. */
int grid[9][9];

/* v conflicts with nothing in v's row, column or 3x3 box? */
int can_place(int r, int c, int v) {
    for (int i = 0; i < 9; i++)
        if (grid[r][i] == v || grid[i][c] == v) return 0;
    int br = (r / 3) * 3, bc = (c / 3) * 3;
    for (int i = 0; i < 3; i++)
        for (int j = 0; j < 3; j++)
            if (grid[br + i][bc + j] == v) return 0;
    return 1;
}

/* First empty cell in reading order; 0 if the grid is full. */
int find_empty(int *r, int *c) {
    for (int i = 0; i < 9; i++)
        for (int j = 0; j < 9; j++)
            if (grid[i][j] == 0) { *r = i; *c = j; return 1; }
    return 0;
}

/* Backtracking: choose a digit, recurse, undo on failure. */
int solve(void) {
    int r, c;
    if (!find_empty(&r, &c)) return 1;      /* no empty cell -> solved */
    for (int v = 1; v <= 9; v++) {
        if (can_place(r, c, v)) {
            grid[r][c] = v;                 /* choose */
            if (solve()) return 1;          /* explore */
            grid[r][c] = 0;                 /* undo (backtrack) */
        }
    }
    return 0;                               /* dead end */
}

void print_grid(void) {
    for (int i = 0; i < 9; i++) {
        for (int j = 0; j < 9; j++) printf("%d ", grid[i][j]);
        printf("\n");
    }
}

void load(int src[9][9]) {
    for (int i = 0; i < 9; i++)
        for (int j = 0; j < 9; j++)
            grid[i][j] = src[i][j];
}

int main(void) {
    int p1[9][9] = {
        {5, 3, 0, 0, 7, 0, 0, 0, 0},
        {6, 0, 0, 1, 9, 5, 0, 0, 0},
        {0, 9, 8, 0, 0, 0, 0, 6, 0},
        {8, 0, 0, 0, 6, 0, 0, 0, 3},
        {4, 0, 0, 8, 0, 3, 0, 0, 1},
        {7, 0, 0, 0, 2, 0, 0, 0, 6},
        {0, 6, 0, 0, 0, 0, 2, 8, 0},
        {0, 0, 0, 4, 1, 9, 0, 0, 5},
        {0, 0, 0, 0, 8, 0, 0, 7, 9},
    };
    int p2[9][9] = {
        {3, 0, 6, 5, 0, 8, 4, 0, 0},
        {5, 2, 0, 0, 0, 0, 0, 0, 0},
        {0, 8, 7, 0, 0, 0, 0, 3, 1},
        {0, 0, 3, 0, 1, 0, 0, 8, 0},
        {9, 0, 0, 8, 6, 3, 0, 0, 5},
        {0, 5, 0, 0, 9, 0, 6, 0, 0},
        {1, 3, 0, 0, 0, 0, 2, 5, 0},
        {0, 0, 0, 0, 0, 0, 0, 7, 4},
        {0, 0, 5, 2, 0, 6, 3, 0, 0},
    };

    load(p1);
    printf("Test 1 (solve classic puzzle):\n");
    if (solve()) print_grid(); else printf("No solution\n");

    load(p2);
    printf("Test 2 (solve second puzzle):\n");
    if (solve()) print_grid(); else printf("No solution\n");
    return 0;
}
'''


SUDOKU_CPP = r'''#include <iostream>
#include <vector>
using namespace std;

typedef vector<vector<int>> Grid;

/* v conflicts with nothing in v's row, column or 3x3 box? */
bool canPlace(const Grid& g, int r, int c, int v) {
    for (int i = 0; i < 9; i++)
        if (g[r][i] == v || g[i][c] == v) return false;
    int br = (r / 3) * 3, bc = (c / 3) * 3;
    for (int i = br; i < br + 3; i++)
        for (int j = bc; j < bc + 3; j++)
            if (g[i][j] == v) return false;
    return true;
}

/* First empty cell in reading order; false if the grid is full. */
bool findEmpty(const Grid& g, int& r, int& c) {
    for (int i = 0; i < 9; i++)
        for (int j = 0; j < 9; j++)
            if (g[i][j] == 0) { r = i; c = j; return true; }
    return false;
}

/* Backtracking: choose a digit, recurse, undo on failure. */
bool solve(Grid& g) {
    int r, c;
    if (!findEmpty(g, r, c)) return true;   /* no empty cell -> solved */
    for (int v = 1; v <= 9; v++) {
        if (canPlace(g, r, c, v)) {
            g[r][c] = v;                    /* choose */
            if (solve(g)) return true;      /* explore */
            g[r][c] = 0;                    /* undo (backtrack) */
        }
    }
    return false;                           /* dead end */
}

void printGrid(const Grid& g) {
    for (const auto& row : g) {
        for (int v : row) cout << v << " ";
        cout << "\n";
    }
}

int main() {
    Grid p1 = {
        {5, 3, 0, 0, 7, 0, 0, 0, 0},
        {6, 0, 0, 1, 9, 5, 0, 0, 0},
        {0, 9, 8, 0, 0, 0, 0, 6, 0},
        {8, 0, 0, 0, 6, 0, 0, 0, 3},
        {4, 0, 0, 8, 0, 3, 0, 0, 1},
        {7, 0, 0, 0, 2, 0, 0, 0, 6},
        {0, 6, 0, 0, 0, 0, 2, 8, 0},
        {0, 0, 0, 4, 1, 9, 0, 0, 5},
        {0, 0, 0, 0, 8, 0, 0, 7, 9},
    };
    Grid p2 = {
        {3, 0, 6, 5, 0, 8, 4, 0, 0},
        {5, 2, 0, 0, 0, 0, 0, 0, 0},
        {0, 8, 7, 0, 0, 0, 0, 3, 1},
        {0, 0, 3, 0, 1, 0, 0, 8, 0},
        {9, 0, 0, 8, 6, 3, 0, 0, 5},
        {0, 5, 0, 0, 9, 0, 6, 0, 0},
        {1, 3, 0, 0, 0, 0, 2, 5, 0},
        {0, 0, 0, 0, 0, 0, 0, 7, 4},
        {0, 0, 5, 2, 0, 6, 3, 0, 0},
    };

    cout << "Test 1 (solve classic puzzle):\n";
    if (solve(p1)) printGrid(p1); else cout << "No solution\n";

    cout << "Test 2 (solve second puzzle):\n";
    if (solve(p2)) printGrid(p2); else cout << "No solution\n";
    return 0;
}
'''


SUDOKU_PY = r'''def can_place(g, r, c, v):
    """v conflicts with nothing in v's row, column or 3x3 box?"""
    for i in range(9):
        if g[r][i] == v or g[i][c] == v:
            return False
    br, bc = (r // 3) * 3, (c // 3) * 3
    for i in range(br, br + 3):
        for j in range(bc, bc + 3):
            if g[i][j] == v:
                return False
    return True


def find_empty(g):
    """First empty cell in reading order; None if the grid is full."""
    for i in range(9):
        for j in range(9):
            if g[i][j] == 0:
                return i, j
    return None


def solve(g):
    """Backtracking: choose a digit, recurse, undo on failure."""
    cell = find_empty(g)
    if cell is None:
        return True                     # no empty cell -> solved
    r, c = cell
    for v in range(1, 10):
        if can_place(g, r, c, v):
            g[r][c] = v                 # choose
            if solve(g):
                return True             # explore
            g[r][c] = 0                 # undo (backtrack)
    return False                        # dead end


def print_grid(g):
    for row in g:
        print(" ".join(map(str, row)))


P1 = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]

P2 = [
    [3, 0, 6, 5, 0, 8, 4, 0, 0],
    [5, 2, 0, 0, 0, 0, 0, 0, 0],
    [0, 8, 7, 0, 0, 0, 0, 3, 1],
    [0, 0, 3, 0, 1, 0, 0, 8, 0],
    [9, 0, 0, 8, 6, 3, 0, 0, 5],
    [0, 5, 0, 0, 9, 0, 6, 0, 0],
    [1, 3, 0, 0, 0, 0, 2, 5, 0],
    [0, 0, 0, 0, 0, 0, 0, 7, 4],
    [0, 0, 5, 2, 0, 6, 3, 0, 0],
]

if __name__ == "__main__":
    import copy

    print("Test 1 (solve classic puzzle):")
    g1 = copy.deepcopy(P1)
    print_grid(g1) if solve(g1) else print("No solution")

    print("Test 2 (solve second puzzle):")
    g2 = copy.deepcopy(P2)
    print_grid(g2) if solve(g2) else print("No solution")
'''
TOPIC_SUDOKU = {
    "id": "sudoku-solver",
    "name": "Sudoku Solver",
    "slug": "sudoku-solver",
    "type": "backtracking",
    "type_label": TYPES["backtracking"]["label"],
    "type_icon": TYPES["backtracking"]["icon"],
    "priority": 3,
    "difficulty": "Medium",
    "icon": "🧷",
    "kind": "board",
    "complexity": {
        "best": "O(1) for a fixed 9×9 grid (bounded work)",
        "average": "Fast in practice with constraint checks",
        "worst": "O(9^m) where m = number of empty cells",
        "space": "O(m) recursion depth + O(1) grid",
        "stable": "n/a",
        "in_place": "Yes (fills the grid in place)",
    },
    "what": (
        "Sudoku is a constraint-satisfaction problem: fill a 9×9 grid so every row, every column, and "
        "every 3×3 box contains the digits 1–9 exactly once. The classic solver is backtracking in its "
        "purest form — find the first empty cell, try each digit 1–9 that breaks no constraint, recurse, "
        "and undo the digit when the branch leads to a dead end."
    ),
    "why": (
        "General Sudoku completion is NP-complete, so no known polynomial algorithm exists — yet puzzles "
        "are solved instantly because each placement prunes 27 cells of future choices. The solver is the "
        "standard teaching example for constraint propagation and shows how cheap validity checks plus "
        "undo make exponential search practical. The same find-cell/try-value/undo skeleton generalises "
        "to timetabling, layout, and other CSP solvers."
    ),
    "when_needed": [
        "Solving any 9×9 puzzle — the backtracking core handles every valid grid.",
        "Verifying or generating puzzles: fill an empty grid, then punch holes while uniqueness holds.",
        "A teaching example of constraint checking inside backtracking search.",
        "As a baseline against which constraint-propagation solvers are measured.",
    ],
    "how_to_select": [
        "Pick the empty cell with the fewest legal digits (MRV heuristic) — it cuts the tree dramatically.",
        "Keep per-row/column/box bitmasks of used digits to make validity checks O(1).",
        "Propagate forced moves (naked singles) before guessing to shrink the search.",
        "For puzzle generation, remove clues only while the solution stays unique.",
        "For the classic 9×9 the simple reading-order solver is already fast enough — optimise only if needed.",
    ],
    "when_not": [
        "The grid is huge (16×16, 25×25) and fast solving matters — add constraint propagation or a SAT/CP solver.",
        "You only need to validate a completed grid — a single linear check is enough, no search.",
        "Uniqueness of the solution matters — plain solving finds one answer; run a solution counter instead.",
        "An exact-cover formulation fits better — Algorithm X (DLX) is often faster on hard instances.",
    ],
    "outline": [
        "Find the first empty cell in reading order",
        "Try digits 1-9; a digit is legal only if its row, column and 3×3 box lack it",
        "Place, recurse, and undo on failure — the choose/explore/undo triangle",
        "Dead end: no digit fits the cell, undo the previous choice",
        "Grid full with no conflict = solution; 9^m worst case but heavily pruned in practice",
    ],
    "applications": [
        {"title": "Puzzle apps and validators", "detail": "Every Sudoku app's hint and check features run exactly this solver (or a constraint-propagation variant)."},
        {"title": "Puzzle generation", "detail": "Solvers fill an empty grid for the solution, then remove clues while a uniqueness check still passes."},
        {"title": "Constraint-satisfaction modelling", "detail": "Timetabling and scheduling tools reuse the same CSP machinery with stronger propagation."},
        {"title": "Benchmark for SAT/CP solvers", "detail": "Sudoku encodings are a standard first test for SAT solvers and exact-cover (DLX) implementations."},
    ],
    "impl_c": SUDOKU_C,
    "impl_cpp": SUDOKU_CPP,
    "impl_py": SUDOKU_PY,
    "sim": sim_sudoku,
    "references": [
        {"title": "GeeksforGeeks — Sudoku Backtracking-7 (reference)", "url": "https://www.geeksforgeeks.org/sudoku-backtracking-7/"},
    ],
}


# ---------------------------------------------------------------------------
# Topic: N-Queens (Backtracking)
# ---------------------------------------------------------------------------

def sim_n_queens():
    """Trace backtracking until the first valid 8-queens placement (board)."""
    n = 8
    queens = [-1] * n
    out = []

    def emit(caption, last=None, conflict=None, solved=False):
        out.append({
            "kind": "board",
            "n": n,
            "queens": list(queens),
            "last": last,
            "conflict": [list(c) for c in (conflict or [])],
            "caption": caption,
            "done": solved,
        })

    def safe(row, col):
        for r in range(row):
            if queens[r] == col or abs(queens[r] - col) == abs(r - row):
                return False
        return True

    placed = 0

    def solve(row):
        nonlocal placed
        if row == n:
            emit("Solved! Queens placed on every row without conflict.", solved=True)
            return True
        for col in range(n):
            if safe(row, col):
                queens[row] = col
                placed += 1
                emit(f"Placed queen at row {row}, column {col} (placement #{placed})", [row, col])
                if solve(row + 1):
                    return True
                queens[row] = -1
                emit(f"No safe column further down — backtrack to row {row}", [row, col])
        return False

    emit("Start: empty 8×8 board; place queens row by row", None, [], False)
    solve(0)
    return out


N_QUEENS_C = r'''#include <stdio.h>
#include <stdbool.h>

static bool first_captured = false;

/* True when placing a queen at (row, col) attacks no earlier queen. */
static bool safe(const int board[], int row, int col) {
    for (int i = 0; i < row; i++) {
        int dc = board[i] - col;              /* column difference */
        if (dc == 0) return false;            /* same column       */
        if (dc == i - row) return false;      /* main diagonal     */
        if (dc == row - i) return false;      /* anti-diagonal     */
    }
    return true;
}

static void solve(int n, int row, int board[], int *total, int *first) {
    if (row == n) {
        (*total)++;
        if (!first_captured) {
            for (int i = 0; i < n; i++) first[i] = board[i];
            first_captured = true;
        }
        return;
    }
    for (int col = 0; col < n; col++) {
        if (safe(board, row, col)) {
            board[row] = col;
            solve(n, row + 1, board, total, first);
        }
    }
}

int main(void) {
    int board[8], first8[8], total8 = 0;
    first_captured = false;
    solve(8, 0, board, &total8, first8);
    printf("Test 1: %d\n", total8);           /* 92 distinct boards  */
    printf("Test 2: [%d, %d, %d, %d, %d, %d, %d, %d]\n",
           first8[0], first8[1], first8[2], first8[3],
           first8[4], first8[5], first8[6], first8[7]);

    int board4[4], first4[4], total4 = 0;
    first_captured = false;
    solve(4, 0, board4, &total4, first4);
    printf("Test 3: %d\n", total4);           /* 2 distinct boards   */
    printf("Test 4: [%d, %d, %d, %d]\n", first4[0], first4[1], first4[2], first4[3]);
    return 0;
}
'''


N_QUEENS_CPP = r'''#include <iostream>
#include <vector>
using namespace std;

/* True when placing a queen at (row, col) attacks no earlier queen. */
bool safe(const vector<int>& board, int row, int col) {
    for (int i = 0; i < row; i++) {
        int dc = board[i] - col;
        if (dc == 0) return false;
        if (dc == i - row) return false;
        if (dc == row - i) return false;
    }
    return true;
}

void solve(int n, int row, vector<int>& board, int& total, vector<int>& first, bool& firstTaken) {
    if (row == n) {
        total++;
        if (!firstTaken) {
            first = board;
            firstTaken = true;
        }
        return;
    }
    for (int col = 0; col < n; col++) {
        if (safe(board, row, col)) {
            board[row] = col;
            solve(n, row + 1, board, total, first, firstTaken);
        }
    }
}

template <typename T>
void print_arr(const T& v) {
    cout << "[";
    for (size_t i = 0; i < v.size(); i++) {
        if (i) cout << ", ";
        cout << v[i];
    }
    cout << "]\n";
}

int main() {
    vector<int> board(8), first8(8);
    int total8 = 0;
    bool taken = false;
    solve(8, 0, board, total8, first8, taken);
    cout << "Test 1: " << total8 << "\n";
    cout << "Test 2: "; print_arr(first8);

    vector<int> board4(4), first4(4);
    int total4 = 0;
    taken = false;
    solve(4, 0, board4, total4, first4, taken);
    cout << "Test 3: " << total4 << "\n";
    cout << "Test 4: "; print_arr(first4);
    return 0;
}
'''


N_QUEENS_PY = r'''def n_queens(n):
    """Return (number of distinct solutions, first solution found)."""
    board = [-1] * n
    total = 0
    first = None

    def safe(row, col):
        for i in range(row):
            dc = board[i] - col
            if dc == 0 or dc == i - row or dc == row - i:
                return False
        return True

    def solve(row):
        nonlocal total, first
        if row == n:
            total += 1
            if first is None:
                first = list(board)
            return
        for col in range(n):
            if safe(row, col):
                board[row] = col
                solve(row + 1)

    solve(0)
    return total, first or []


def fmt(v):
    return "[" + ", ".join(map(str, v)) + "]"


if __name__ == "__main__":
    total8, first8 = n_queens(8)
    total4, first4 = n_queens(4)
    print(f"Test 1: {total8}")
    print(f"Test 2: {fmt(first8)}")
    print(f"Test 3: {total4}")
    print(f"Test 4: {fmt(first4)}")
'''
TOPIC_N_QUEENS = {
    "id": "n-queens",
    "name": "N-Queens",
    "slug": "n-queens",
    "type": "backtracking",
    "type_label": TYPES["backtracking"]["label"],
    "type_icon": TYPES["backtracking"]["icon"],
    "priority": 4,
    "difficulty": "Hard",
    "icon": "👑",
    "kind": "board",
    "complexity": {
        "best": "—",
        "average": "—",
        "worst": "O(n!)",
        "space": "O(n) recursion stack + board",
        "stable": "—",
        "in_place": "—",
    },
    "what": (
        "N-Queens asks for ways to place n queens on an n×n board so no two attack each other — no shared row, "
        "column, or diagonal. A backtracking search fills the board row by row, and the moment a placement "
        "conflicts with earlier queens it undoes it (backtracks) and tries the next column instead of "
        "exploring doomed subtrees."
    ),
    "why": (
        "The search space is enormous — roughly n^n row/column combinations — but most of it is pruned by "
        "constraint checks. Backtracking is the canonical technique for constraint-satisfaction problems "
        "(puzzles, scheduling, register allocation): it systematically enumerates candidates while cutting "
        "off whole branches as soon as a partial solution is impossible."
    ),
    "when_needed": [
        "A solution must be built incrementally from a sequence of choices.",
        "An early partial assignment can invalidate every completion of it (constraint satisfaction).",
        "You need all solutions or the first solution, not just a decision.",
        "The search tree can be pruned early; otherwise a smarter model (e.g. CSP solver) is better.",
    ],
    "how_to_select": [
        "Model the state as a sequence of decisions (one queen per row).",
        "Define a cheap safe() check using columns and the two diagonal families.",
        "Choose the next variable (row) deterministically and iterate over domain values (columns).",
        "Prune with the safe() test before recursing — never explore an invalid extension.",
        "For pure counting problems, symmetric reductions (rotate/reflect) can multiply efficiency.",
    ],
    "when_not": [
        "When a valid (non-constructive) decision alone is needed — other combinatorics may be easier.",
        "For very large n, plain backtracking is slow; use min-conflicts heuristics or bitmask optimization.",
        "When the problem has no obvious sequential structure that admits pruning.",
        "When a greedy or DP formulation exists for your exact problem — they are far cheaper.",
    ],
    "outline": [
        "Place one queen per row; check column + both diagonals",
        "Undo (backtrack) a choice as soon as it leads nowhere",
        "Worst case O(n!) but pruning makes practical growth much smaller",
        "First-class template for constraint-satisfaction problems",
    ],
    "applications": [
        {"title": "Constraint satisfaction puzzles", "detail": "Sudoku, crosswords, and scheduling map to the same place/check/undo pattern."},
        {"title": "Register allocation & map coloring", "detail": "Assign colors/registers to conflicting entities, backtracking on collisions."},
        {"title": "Circuit board & VLSI layout", "detail": "Placing components so no two violate spacing constraints resembles queen placement."},
        {"title": "Test-case combination generation", "detail": "Choosing parameter combinations that pairwise cover all cases uses backtracking search."},
    ],
    "impl_c": N_QUEENS_C,
    "impl_cpp": N_QUEENS_CPP,
    "impl_py": N_QUEENS_PY,
    "sim": sim_n_queens,
    "references": [
        {"title": "GeeksforGeeks — N-Queen Problem (reference)", "url": "https://www.geeksforgeeks.org/n-queen-problem-backtracking-3/"},
    ],
}
# ---------------------------------------------------------------------------
# Topic: Dijkstra's Shortest Path (Graph)
# ---------------------------------------------------------------------------

def sim_dijkstra():
    """Trace Dijkstra's algorithm on a 6-node weighted graph (graph view)."""
    n = 6
    edges = [(0, 1, 4), (0, 2, 2), (1, 2, 1), (1, 3, 5), (2, 3, 8),
             (2, 4, 10), (3, 4, 2), (3, 5, 6), (4, 5, 3)]
    labels = ["A", "B", "C", "D", "E", "F"]
    pos = {
        0: (70, 120), 1: (180, 30), 2: (180, 210),
        3: (330, 30), 4: (330, 210), 5: (470, 120),
    }
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))

    INF = float("inf")
    dist = [INF] * n
    done = [False] * n
    parent = [-1] * n
    dist[0] = 0
    out = []

    def step(caption, current=None, frontier=None, path_edges=None, final=False):
        node_states = {}
        for v in range(n):
            if done[v]:
                node_states[v] = "done"
            elif current is not None and v == current:
                node_states[v] = "current"
            elif frontier is not None and v in frontier:
                node_states[v] = "frontier"
            else:
                node_states[v] = "unvisited"
        edge_states = {}
        for (u, v, w) in edges:
            key = f"{u}-{v}"
            if path_edges and key in path_edges:
                edge_states[key] = "path"
            elif current is not None and (u == current or v == current):
                edge_states[key] = "active"
            else:
                edge_states[key] = "normal"
        out.append({
            "kind": "graph",
            "nodes": [
                {"id": i, "label": labels[i], "x": pos[i][0], "y": pos[i][1], "state": node_states[i]}
                for i in range(n)
            ],
            "edges": [
                {"from": u, "to": v, "weight": w, "state": edge_states.get(f"{u}-{v}", "normal")}
                for (u, v, w) in edges
            ],
            "dist": ["∞" if d == INF else int(d) for d in dist],
            "caption": caption,
            "done": final,
        })

    step("Start at A with distance 0; every other node is unreachable (∞).", current=0, frontier=[0])
    import heapq
    pq = [(0, 0)]
    while pq:
        d, u = heapq.heappop(pq)
        if done[u]:
            continue
        done[u] = True
        path = set()
        for v in range(n):
            if parent[v] != -1:
                path.add(f"{min(v, parent[v])}-{max(v, parent[v])}")
        step(
            f"Finalise {labels[u]} with distance {dist[u]}",
            current=u, frontier=[v for v in range(n) if not done[v] and dist[v] < INF], path_edges=path,
        )
        for v, w in adj[u]:
            if not done[v] and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                parent[v] = u
                heapq.heappush(pq, (dist[v], v))
                step(
                    f"Relax edge {labels[u]}→{labels[v]}: tentative distance becomes {dist[v]}",
                    current=u, frontier=[x for x in range(n) if not done[x] and dist[x] < INF],
                    path_edges={f"{min(x, parent[x])}-{max(x, parent[x])}" for x in range(n) if parent[x] != -1},
                )
    path = {f"{min(v, parent[v])}-{max(v, parent[v])}" for v in range(n) if parent[v] != -1}
    step("Done — all shortest paths from A computed (path edges highlighted).", path_edges=path, final=True)
    return out


DIJKSTRA_C = r'''#include <stdio.h>
#include <limits.h>

#define N 6
#define INF INT_MAX

static int g[N][N];

void dijkstra(int src, int *dist) {
    int done[N] = {0};
    for (int i = 0; i < N; i++) dist[i] = INF;
    dist[src] = 0;
    for (int iter = 0; iter < N; iter++) {
        /* pick the unsettled node with the smallest distance */
        int u = -1, best = INF;
        for (int i = 0; i < N; i++)
            if (!done[i] && dist[i] < best) { best = dist[i]; u = i; }
        if (u == -1) break;
        done[u] = 1;
        for (int v = 0; v < N; v++)
            if (g[u][v] < INF && !done[v] && dist[u] + g[u][v] < dist[v])
                dist[v] = dist[u] + g[u][v];
    }
}

int main(void) {
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++) g[i][j] = INF;
    int edges[][3] = {
        {0, 1, 4}, {0, 2, 2}, {1, 2, 1}, {1, 3, 5}, {2, 3, 8},
        {2, 4, 10}, {3, 4, 2}, {3, 5, 6}, {4, 5, 3},
    };
    for (int k = 0; k < 9; k++) {
        int u = edges[k][0], v = edges[k][1], w = edges[k][2];
        g[u][v] = w;
        g[v][u] = w;
    }
    int dist[N];
    dijkstra(0, dist);
    printf("Test: ");
    for (int i = 0; i < N; i++) printf("%d ", dist[i]);
    printf("\n");
    return 0;
}
'''
DIJKSTRA_CPP = r'''#include <iostream>
#include <vector>
#include <queue>
using namespace std;

/* Dijkstra with a binary min-heap: O((V + E) log V). */
vector<int> dijkstra(int src, const vector<vector<pair<int, int>>>& g) {
    int n = (int)g.size();
    const int INF = 1e9;
    vector<int> dist(n, INF);
    vector<bool> done(n, false);
    priority_queue<pair<int, int>, vector<pair<int, int>>, greater<pair<int, int>>> pq;
    dist[src] = 0;
    pq.push({0, src});
    while (!pq.empty()) {
        int d = pq.top().first, u = pq.top().second;
        pq.pop();
        if (done[u]) continue;           /* stale entry */
        done[u] = true;
        for (size_t k = 0; k < g[u].size(); k++) {
            int v = g[u][k].first, w = g[u][k].second;
            if (!done[v] && dist[u] + w < dist[v]) {
                dist[v] = dist[u] + w;
                pq.push({dist[v], v});
            }
        }
    }
    return dist;
}

int main() {
    int n = 6;
    vector<vector<pair<int, int>>> g(n);
    int edges[][3] = {
        {0, 1, 4}, {0, 2, 2}, {1, 2, 1}, {1, 3, 5}, {2, 3, 8},
        {2, 4, 10}, {3, 4, 2}, {3, 5, 6}, {4, 5, 3},
    };
    for (int k = 0; k < 9; k++) {
        int u = edges[k][0], v = edges[k][1], w = edges[k][2];
        g[u].push_back({v, w});
        g[v].push_back({u, w});
    }
    vector<int> dist = dijkstra(0, g);
    cout << "Test: ";
    for (int i = 0; i < n; i++) cout << dist[i] << " ";
    cout << "\n";
    return 0;
}
'''


DIJKSTRA_PY = r'''import heapq


def dijkstra(src, adj, n):
    """Shortest distances from src; all edge weights must be non-negative."""
    INF = float("inf")
    dist = [INF] * n
    done = [False] * n
    dist[src] = 0
    pq = [(0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if done[u]:
            continue
        done[u] = True
        for v, w in adj[u]:
            if not done[v] and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(pq, (dist[v], v))
    return dist


if __name__ == "__main__":
    n = 6
    edges = [(0, 1, 4), (0, 2, 2), (1, 2, 1), (1, 3, 5), (2, 3, 8),
             (2, 4, 10), (3, 4, 2), (3, 5, 6), (4, 5, 3)]
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))
    dist = dijkstra(0, adj, n)
    print("Test: " + " ".join(str(int(x)) for x in dist))
'''
TOPIC_DIJKSTRA = {
    "id": "dijkstra",
    "name": "Dijkstra's Shortest Path",
    "slug": "dijkstra",
    "type": "graph",
    "type_label": TYPES["graph"]["label"],
    "type_icon": TYPES["graph"]["icon"],
    "priority": 5,
    "difficulty": "Hard",
    "icon": "🗺️",
    "kind": "graph",
    "complexity": {
        "best": "O((V + E) log V) with binary heap",
        "average": "O((V + E) log V)",
        "worst": "O((V + E) log V)",
        "space": "O(V) for distances + heap",
        "stable": "—",
        "in_place": "—",
    },
    "what": (
        "Dijkstra's algorithm computes the shortest path from a single source node to every other node in a "
        "weighted graph, provided all edge weights are non-negative. It repeatedly finalises the closest "
        "unsettled node (kept in a priority queue) and relaxes its outgoing edges, improving tentative "
        "distances along the way."
    ),
    "why": (
        "Navigation, network routing, and logistics are shortest-path problems on enormous graphs. With a "
        "binary heap Dijkstra runs in O((V + E) log V), which is practical for road networks with millions "
        "of edges. Its greedy invariant — the settled node's distance can never be improved again — is what "
        "makes it fast, and it is exactly why negative edges break it."
    ),
    "when_needed": [
        "Single-source shortest paths on a weighted graph.",
        "All edge weights are non-negative (the algorithm assumes this).",
        "You need actual path reconstruction, not just the distance.",
        "The graph is large enough that an O(V·E) approach is too slow.",
    ],
    "how_to_select": [
        "Confirm the graph is non-negatively weighted; if any edge is negative use Bellman-Ford instead.",
        "Use a binary-heap priority queue to achieve O((V + E) log V); a simple scan is O(V²) and fine for dense small graphs.",
        "For unweighted graphs prefer BFS — it is simpler and O(V + E).",
        "For all-pairs shortest paths consider Floyd-Warshall (small graphs) or repeated Dijkstra per source.",
        "Use early termination if you only need the distance to one specific target.",
    ],
    "when_not": [
        "Negative edge weights exist — Dijkstra can finalise a node before a cheaper path through a negative edge is found.",
        "The graph is unweighted — BFS is faster and simpler.",
        "Edges change very frequently — incremental shortest-path algorithms are better suited.",
        "You need all-pairs distances on a dense graph — Floyd-Warshall is simpler there.",
    ],
    "outline": [
        "Single-source shortest paths on non-negative weighted graphs",
        "Greedy finalisation + priority queue gives O((V + E) log V)",
        "Fails on negative edges — Bellman-Ford covers those",
        "Reconstruct paths via a parent table",
    ],
    "applications": [
        {"title": "GPS route planning", "detail": "Map services compute shortest driving routes on road graphs with time/traffic weights."},
        {"title": "Network routing (OSPF/IS-IS)", "detail": "Link-state routing protocols compute shortest paths per router to build forwarding tables."},
        {"title": "Robotics & games pathfinding", "detail": "Grid-based A* is Dijkstra plus a heuristic; Dijkstra itself guarantees the optimum on uniform maps."},
        {"title": "Telecom & airline networks", "detail": "Finding least-cost routes over fiber or flight networks reduces to the same problem."},
    ],
    "impl_c": DIJKSTRA_C,
    "impl_cpp": DIJKSTRA_CPP,
    "impl_py": DIJKSTRA_PY,
    "sim": sim_dijkstra,
    "references": [
        {"title": "GeeksforGeeks — Dijkstra's Shortest Path Algorithm (reference)", "url": "https://www.geeksforgeeks.org/dijkstras-shortest-path-algorithm-greedy-algo-7/"},
    ],
}


# ---------------------------------------------------------------------------
# Topic: Quick Sort
# ---------------------------------------------------------------------------

def sim_quick_sort():
    """Trace Lomuto-partition quick sort (array renderer)."""
    a = [38, 27, 43, 3, 9, 82, 10]
    out = []

    def emit(caption, data, highlights=(), compare=(), swap=(), lo=None, hi=None, done=False):
        markers = {}
        if lo is not None:
            markers["lo"] = lo
        if hi is not None:
            markers["hi"] = hi
        out.append({
            "kind": "array",
            "data": list(data),
            "highlights": list(highlights),
            "compare": list(compare),
            "swap": list(swap),
            "markers": markers,
            "caption": caption,
            "done": done,
        })

    def partition(lo, hi):
        pivot = a[hi]
        emit(f"Partition [{lo}..{hi}]: pivot = A[{hi}] = {pivot}", a, [hi], (), (), lo, hi)
        i = lo - 1
        for j in range(lo, hi):
            emit(f"Compare A[{j}] = {a[j]} with pivot {pivot}", a, [hi], [j], (), lo, hi)
            if a[j] <= pivot:
                i += 1
                if i != j:
                    a[i], a[j] = a[j], a[i]
                    emit(f"A[{j}] <= pivot -> move into left part: swap A[{i}] <-> A[{j}]",
                         a, [hi], (), [i, j], lo, hi)
                else:
                    emit(f"A[{j}] <= pivot -> already inside the left part", a, [hi], (), [j], lo, hi)
        if i + 1 != hi:
            a[i + 1], a[hi] = a[hi], a[i + 1]
            emit(f"Place pivot: swap A[{i + 1}] <-> A[{hi}] -> pivot settles at index {i + 1}",
                 a, [i + 1], (), [i + 1, hi], lo, hi)
        else:
            emit(f"Place pivot: already at its final index {hi}", a, [hi], (), (), lo, hi)
        return i + 1

    def quick_sort(lo, hi):
        if lo >= hi:
            if lo == hi:
                emit(f"Range [{lo}..{hi}] holds one element -> already sorted", a, (), (), (), lo, hi)
            return
        emit(f"Sort range [{lo}..{hi}]", a, (), (), (), lo, hi)
        p = partition(lo, hi)
        quick_sort(lo, p - 1)
        quick_sort(p + 1, hi)

    emit("Start — array to sort", a)
    quick_sort(0, len(a) - 1)
    emit("Done — every element sits at its final position", a, done=True)
    return out


QUICK_SORT_C = r'''#include <stdio.h>

/* Lomuto partition: puts a[hi] (the pivot) at its final sorted position and
 * returns that position. Everything <= pivot ends up on its left. */
int partition(int a[], int lo, int hi) {
    int pivot = a[hi];
    int i = lo - 1;
    for (int j = lo; j < hi; j++) {
        if (a[j] <= pivot) {
            i++;
            int tmp = a[i]; a[i] = a[j]; a[j] = tmp;
        }
    }
    int tmp = a[i + 1]; a[i + 1] = a[hi]; a[hi] = tmp;
    return i + 1;
}

void quick_sort(int a[], int lo, int hi) {
    if (lo >= hi) return;
    int p = partition(a, lo, hi);
    quick_sort(a, lo, p - 1);
    quick_sort(a, p + 1, hi);
}

/* Quickselect: k-th smallest (1-based), average O(n) — same partition loop
 * but only the side that contains rank k is followed. */
int quickselect(int a[], int lo, int hi, int k) {
    for (;;) {
        if (lo == hi) return a[lo];
        int p = partition(a, lo, hi);
        if (k == p + 1) return a[p];
        if (k < p + 1)  hi = p - 1;
        else            lo = p + 1;
    }
}

void print_array(int a[], int n) {
    for (int i = 0; i < n; i++) printf("%d ", a[i]);
    printf("\n");
}

int main(void) {
    int a1[] = {38, 27, 43, 3, 9, 82, 10};
    int a2[] = {5, 4, 3, 2, 1};
    int a3[] = {1, 2, 3, 4, 5};
    int a4[] = {2, 1, 2, 1, 2};
    quick_sort(a1, 0, 6); printf("Test 1: "); print_array(a1, 7);
    quick_sort(a2, 0, 4); printf("Test 2: "); print_array(a2, 5);
    quick_sort(a3, 0, 4); printf("Test 3: "); print_array(a3, 5);
    quick_sort(a4, 0, 4); printf("Test 4: "); print_array(a4, 5);

    int b[] = {38, 27, 43, 3, 9, 82, 10};
    printf("Test 5: %d\n", quickselect(b, 0, 6, 3));   /* 10 */
    printf("Test 6: %d\n", quickselect(b, 0, 6, 4));   /* 27 */
    return 0;
}
'''


QUICK_SORT_CPP = r'''#include <iostream>
#include <vector>
using namespace std;

/* Lomuto partition: pivot a[hi] lands at its final position. */
int partition(vector<int>& a, int lo, int hi) {
    int pivot = a[hi];
    int i = lo - 1;
    for (int j = lo; j < hi; j++) {
        if (a[j] <= pivot) {
            i++;
            swap(a[i], a[j]);
        }
    }
    swap(a[i + 1], a[hi]);
    return i + 1;
}

void quickSort(vector<int>& a, int lo, int hi) {
    if (lo >= hi) return;
    int p = partition(a, lo, hi);
    quickSort(a, lo, p - 1);
    quickSort(a, p + 1, hi);
}

/* k-th smallest (1-based), average O(n). */
int quickselect(vector<int>& a, int lo, int hi, int k) {
    for (;;) {
        if (lo == hi) return a[lo];
        int p = partition(a, lo, hi);
        if (k == p + 1) return a[p];
        if (k < p + 1)  hi = p - 1;
        else            lo = p + 1;
    }
}

void print_array(const vector<int>& a) {
    for (int x : a) cout << x << " ";
    cout << "\n";
}

int main() {
    vector<int> a1 = {38, 27, 43, 3, 9, 82, 10};
    vector<int> a2 = {5, 4, 3, 2, 1};
    vector<int> a3 = {1, 2, 3, 4, 5};
    vector<int> a4 = {2, 1, 2, 1, 2};
    quickSort(a1, 0, (int)a1.size() - 1); cout << "Test 1: "; print_array(a1);
    quickSort(a2, 0, (int)a2.size() - 1); cout << "Test 2: "; print_array(a2);
    quickSort(a3, 0, (int)a3.size() - 1); cout << "Test 3: "; print_array(a3);
    quickSort(a4, 0, (int)a4.size() - 1); cout << "Test 4: "; print_array(a4);

    vector<int> b = {38, 27, 43, 3, 9, 82, 10};
    cout << "Test 5: " << quickselect(b, 0, (int)b.size() - 1, 3) << "\n";
    cout << "Test 6: " << quickselect(b, 0, (int)b.size() - 1, 4) << "\n";
    return 0;
}
'''


QUICK_SORT_PY = r'''def partition(a, lo, hi):
    """Pivot a[hi] lands at its final sorted position; return that index."""
    pivot = a[hi]
    i = lo - 1
    for j in range(lo, hi):
        if a[j] <= pivot:
            i += 1
            a[i], a[j] = a[j], a[i]
    a[i + 1], a[hi] = a[hi], a[i + 1]
    return i + 1


def quick_sort(a, lo, hi):
    if lo >= hi:
        return
    p = partition(a, lo, hi)
    quick_sort(a, lo, p - 1)
    quick_sort(a, p + 1, hi)


def quickselect(a, lo, hi, k):
    """k-th smallest (1-based), average O(n)."""
    while True:
        if lo == hi:
            return a[lo]
        p = partition(a, lo, hi)
        if k == p + 1:
            return a[p]
        if k < p + 1:
            hi = p - 1
        else:
            lo = p + 1


def fmt(a):
    return " ".join(map(str, a))


if __name__ == "__main__":
    a1 = [38, 27, 43, 3, 9, 82, 10]
    a2 = [5, 4, 3, 2, 1]
    a3 = [1, 2, 3, 4, 5]
    a4 = [2, 1, 2, 1, 2]
    for i, arr in enumerate((a1, a2, a3, a4), 1):
        quick_sort(arr, 0, len(arr) - 1)
        print(f"Test {i}: {fmt(arr)}")

    b = [38, 27, 43, 3, 9, 82, 10]
    print(f"Test 5: {quickselect(b, 0, len(b) - 1, 3)}")   # 10
    print(f"Test 6: {quickselect(b, 0, len(b) - 1, 4)}")   # 27
'''
TOPIC_QUICK_SORT = {
    "id": "quick-sort",
    "name": "Quick Sort",
    "slug": "quick-sort",
    "type": "sorting-searching",
    "type_label": TYPES["sorting-searching"]["label"],
    "type_icon": TYPES["sorting-searching"]["icon"],
    "priority": 5,
    "difficulty": "Medium",
    "icon": "⚡",
    "kind": "array",
    "complexity": {
        "best": "O(n log n)",
        "average": "O(n log n)",
        "worst": "O(n²) — avoidable with random pivots",
        "space": "O(log n) recursion stack",
        "stable": "No",
        "in_place": "Yes",
    },
    "what": (
        "Quick sort is a divide-and-conquer sort built around partitioning. It picks a pivot value, "
        "rearranges the array so everything smaller sits to the pivot's left and everything larger to "
        "its right, drops the pivot into its final slot, then repeats independently on the two sides. "
        "Unlike merge sort it does all of its work inside the original array."
    ),
    "why": (
        "Quick sort has the best real-world constants of the classic O(n log n) sorts: tight inner loops, "
        "in-place partitioning, and sequential memory access that plays well with CPU caches. That is why "
        "language libraries build their sorts on quicksort variants, and the same partition step doubles "
        "as quickselect — the standard tool for medians and order statistics in average O(n)."
    ),
    "when_needed": [
        "General-purpose in-memory sorting where average speed matters most.",
        "Memory is tight — the sort works in place with only O(log n) stack.",
        "You need order statistics (k-th smallest, median, percentiles) via quickselect.",
        "Sorting large arrays where cache-friendly sequential access pays off.",
    ],
    "how_to_select": [
        "Randomise or median-of-three the pivot — a fixed last-element pivot degrades to O(n²) on sorted input.",
        "Expect many duplicate keys? Use 3-way partitioning so equal keys group in a single pass.",
        "Need stability or a hard worst-case guarantee? Choose merge sort or heap sort instead.",
        "Recurse on the smaller side first (or tail-call optimise) to cap stack depth at O(log n).",
        "For tiny ranges switch to insertion sort — production libraries cut over like this.",
    ],
    "when_not": [
        "A guaranteed O(n log n) bound is required (hard real-time, adversarial input) — heap sort never degrades.",
        "Stability must be preserved — partitioning reorders equal keys.",
        "The data is a linked list — merging needs no random access and suits lists far better.",
        "Input is nearly sorted and small — insertion sort finishes in O(n).",
    ],
    "outline": [
        "Partition around a pivot: smaller | pivot | larger, pivot locked in place",
        "Recurse independently on both sides — O(n log n) on average",
        "Randomised pivot / median-of-three defeats the O(n²) worst case",
        "3-way partition groups duplicates in one pass",
        "Quickselect reuses the same partition for k-th smallest in average O(n)",
    ],
    "applications": [
        {"title": "Language and library sorts", "detail": "C's qsort and the quicksort core inside C++ introsort hybrids descend from this algorithm."},
        {"title": "Order statistics", "detail": "Median finding, percentile cutoffs, and top-k screens use quickselect, which shares quick sort's partition."},
        {"title": "Database engines", "detail": "In-memory sort operators partition runs exactly this way before handing off to external merge steps."},
        {"title": "Memory-limited systems", "detail": "In-place sorting with O(log n) extra space fits where merge sort's O(n) buffer would not."},
    ],
    "impl_c": QUICK_SORT_C,
    "impl_cpp": QUICK_SORT_CPP,
    "impl_py": QUICK_SORT_PY,
    "sim": sim_quick_sort,
    "references": [
        {"title": "GeeksforGeeks — Quick Sort (reference)", "url": "https://www.geeksforgeeks.org/quick-sort/"},
    ],
}


# ---------------------------------------------------------------------------
# Topic: Heap Sort
# ---------------------------------------------------------------------------

def sim_heap_sort():
    """Trace build-heap + extract-max heap sort (array renderer)."""
    a = [4, 10, 3, 5, 1]
    n = len(a)
    out = []

    def emit(caption, data, highlights=(), compare=(), swap=(), hi=None, done=False):
        markers = {}
        if hi is not None:
            markers["hi"] = hi
        out.append({
            "kind": "array",
            "data": list(data),
            "highlights": list(highlights),
            "compare": list(compare),
            "swap": list(swap),
            "markers": markers,
            "caption": caption,
            "done": done,
        })

    def sift_down(i, size):
        while True:
            largest, l, r = i, 2 * i + 1, 2 * i + 2
            kids = [k for k in (l, r) if k < size]
            if kids:
                emit(f"Sift down from A[{i}] = {a[i]}: compare with children "
                     + ", ".join(f"A[{k}] = {a[k]}" for k in kids),
                     a, [i], kids, (), hi=size - 1)
            else:
                emit(f"Sift down from A[{i}] = {a[i]}: it is a leaf, stop", a, [i], (), (), hi=size - 1)
            if l < size and a[l] > a[largest]:
                largest = l
            if r < size and a[r] > a[largest]:
                largest = r
            if largest == i:
                break
            a[i], a[largest] = a[largest], a[i]
            emit(f"A[{largest}] is the largest child -> swap A[{i}] <-> A[{largest}]",
                 a, [], (), [i, largest], hi=size - 1)
            i = largest

    emit("Start — array to sort", a)
    emit("Phase 1 — build a max-heap (sift down every internal node)", a)
    for i in range(n // 2 - 1, -1, -1):
        sift_down(i, n)
    emit("Max-heap ready: the largest value sits at the root A[0]", a, [0], (), ())
    emit("Phase 2 — repeatedly swap the root with the last heap slot, then re-heapify", a)
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]
        emit(f"Extract max {a[end]}: swap A[0] <-> A[{end}] — it is now in final position "
             f"({n - end} of {n} sorted)", a, [], (), [0, end], hi=end - 1)
        sift_down(0, end)
    emit("Done — the array is fully sorted", a, done=True)
    return out


HEAP_SORT_C = r'''#include <stdio.h>

/* Restore the max-heap property for the subtree rooted at i (children of i
 * live at 2i+1 and 2i+2 in the array). O(log n). */
void sift_down(int a[], int i, int size) {
    for (;;) {
        int largest = i, l = 2 * i + 1, r = 2 * i + 2;
        if (l < size && a[l] > a[largest]) largest = l;
        if (r < size && a[r] > a[largest]) largest = r;
        if (largest == i) break;
        int tmp = a[i]; a[i] = a[largest]; a[largest] = tmp;
        i = largest;
    }
}

void heap_sort(int a[], int n) {
    /* build a max-heap in O(n) by sifting internal nodes bottom-up */
    for (int i = n / 2 - 1; i >= 0; i--) sift_down(a, i, n);
    /* repeatedly move the max to the end and shrink the heap */
    for (int end = n - 1; end > 0; end--) {
        int tmp = a[0]; a[0] = a[end]; a[end] = tmp;
        sift_down(a, 0, end);
    }
}

/* k largest values in descending order: build a heap, extract k times. */
void k_largest(int a[], int n, int k, int out[]) {
    for (int i = n / 2 - 1; i >= 0; i--) sift_down(a, i, n);
    int size = n;
    for (int t = 0; t < k; t++) {
        out[t] = a[0];
        a[0] = a[size - 1];
        size--;
        sift_down(a, 0, size);
    }
}

void print_array(int a[], int n) {
    for (int i = 0; i < n; i++) printf("%d ", a[i]);
    printf("\n");
}

int main(void) {
    int a1[] = {4, 10, 3, 5, 1};
    int a2[] = {12, 11, 13, 5, 6, 7};
    int a3[] = {2, 2, 1};
    heap_sort(a1, 5); printf("Test 1: "); print_array(a1, 5);
    heap_sort(a2, 6); printf("Test 2: "); print_array(a2, 6);
    heap_sort(a3, 3); printf("Test 3: "); print_array(a3, 3);

    int b[] = {7, 10, 4, 3, 20, 15};
    int top3[3], top1[1];
    k_largest(b, 6, 3, top3);
    printf("Test 4: "); print_array(top3, 3);
    int c[] = {7, 10, 4, 3, 20, 15};
    k_largest(c, 6, 1, top1);
    printf("Test 5: "); print_array(top1, 1);
    return 0;
}
'''


HEAP_SORT_CPP = r'''#include <iostream>
#include <vector>
using namespace std;

void siftDown(vector<int>& a, int i, int size) {
    for (;;) {
        int largest = i, l = 2 * i + 1, r = 2 * i + 2;
        if (l < size && a[l] > a[largest]) largest = l;
        if (r < size && a[r] > a[largest]) largest = r;
        if (largest == i) break;
        swap(a[i], a[largest]);
        i = largest;
    }
}

void heapSort(vector<int>& a) {
    int n = (int)a.size();
    for (int i = n / 2 - 1; i >= 0; i--) siftDown(a, i, n);
    for (int end = n - 1; end > 0; end--) {
        swap(a[0], a[end]);
        siftDown(a, 0, end);
    }
}

/* k largest values in descending order (heap-based, no full sort). */
vector<int> kLargest(vector<int> a, int k) {
    int n = (int)a.size();
    for (int i = n / 2 - 1; i >= 0; i--) siftDown(a, i, n);
    vector<int> out;
    int size = n;
    for (int t = 0; t < k; t++) {
        out.push_back(a[0]);
        a[0] = a[size - 1];
        size--;
        siftDown(a, 0, size);
    }
    return out;
}

void print_array(const vector<int>& a) {
    for (int x : a) cout << x << " ";
    cout << "\n";
}

int main() {
    vector<int> a1 = {4, 10, 3, 5, 1};
    vector<int> a2 = {12, 11, 13, 5, 6, 7};
    vector<int> a3 = {2, 2, 1};
    heapSort(a1); cout << "Test 1: "; print_array(a1);
    heapSort(a2); cout << "Test 2: "; print_array(a2);
    heapSort(a3); cout << "Test 3: "; print_array(a3);

    cout << "Test 4: "; print_array(kLargest({7, 10, 4, 3, 20, 15}, 3));
    cout << "Test 5: "; print_array(kLargest({7, 10, 4, 3, 20, 15}, 1));
    return 0;
}
'''


HEAP_SORT_PY = r'''def sift_down(a, i, size):
    """Restore the max-heap property for the subtree rooted at i."""
    while True:
        largest, l, r = i, 2 * i + 1, 2 * i + 2
        if l < size and a[l] > a[largest]:
            largest = l
        if r < size and a[r] > a[largest]:
            largest = r
        if largest == i:
            return
        a[i], a[largest] = a[largest], a[i]
        i = largest


def heap_sort(a):
    n = len(a)
    for i in range(n // 2 - 1, -1, -1):
        sift_down(a, i, n)
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]
        sift_down(a, 0, end)


def k_largest(a, k):
    """k largest values in descending order (heap-based)."""
    a = list(a)
    n = len(a)
    for i in range(n // 2 - 1, -1, -1):
        sift_down(a, i, n)
    out, size = [], n
    for _ in range(k):
        out.append(a[0])
        a[0] = a[size - 1]
        size -= 1
        sift_down(a, 0, size)
    return out


def fmt(a):
    return " ".join(map(str, a))


if __name__ == "__main__":
    for i, arr in enumerate(([4, 10, 3, 5, 1], [12, 11, 13, 5, 6, 7], [2, 2, 1]), 1):
        heap_sort(arr)
        print(f"Test {i}: {fmt(arr)}")

    print(f"Test 4: {fmt(k_largest([7, 10, 4, 3, 20, 15], 3))}")
    print(f"Test 5: {fmt(k_largest([7, 10, 4, 3, 20, 15], 1))}")
'''
# ---------------------------------------------------------------------------
# Topic: Huffman Coding
# ---------------------------------------------------------------------------

def sim_huffman():
    """Trace min-heap merge of the smallest two frequencies (array renderer)."""
    freqs = [("b", 1), ("c", 2), ("d", 3), ("a", 5), ("e", 9), ("f", 15)]
    out = []
    next_id = len(freqs)

    def emit(caption, data, highlights=(), compare=(), swap=(), done=False):
        out.append({
            "kind": "array",
            "data": list(data),
            "highlights": list(highlights),
            "compare": list(compare),
            "swap": list(swap),
            "markers": {},
            "caption": caption,
            "done": done,
        })

    emit("Start — symbol frequencies to be merged. Smallest two always combine into a new node.", freqs)
    q = [list(x) for x in freqs]  # [label, weight, [members]]
    for i, x in enumerate(q):
        x.append([i])  # track original members
    emit("Sort the queue by weight ascending.", sorted(q, key=lambda x: x[1]), highlights=())
    q = sorted(q, key=lambda x: x[1])
    while len(q) > 1:
        a = q[0]
        b = q[1]
        w = a[1] + b[1]
        emit(f"Pick smallest two: {a[0]}(w={a[1]}) + {b[0]}(w={b[1]}) -> merged node w={w}",
             q, [0, 1], (), (), )
        merged = [f"({a[0]}+{b[0]})", w, a[2] + b[2]]
        q = q[2:] + [merged]
        q.sort(key=lambda x: x[1])
        emit(f"Re-insert merged node; queue now sorted:", q)
        emit(f"Single tree left: root weight {q[0][1]} = total frequency. "
         "Codes follow left=0 / right=1 to each leaf.", None, done=True)
    return out


HUFFMAN_CPP = r'''#include <iostream>
#include <queue>
#include <string>
#include <unordered_map>
#include <vector>
using namespace std;

struct Node {
    int freq, order;                 /* order: creation counter for deterministic tie-break */
    char ch;
    Node *left, *right;
    Node(int f, int o, char c = 0, Node *l = nullptr, Node *r = nullptr)
        : freq(f), order(o), ch(c), left(l), right(r) {}
};

struct Cmp {
    bool operator()(Node *a, Node *b) const {
        if (a->freq != b->freq) return a->freq > b->freq;   /* min-heap by freq */
        return a->order > b->order;                         /* tie: smaller order first */
    }
};

Node *build_tree(const string &s) {
    int freq[256] = {0};
    for (char c : s) freq[(unsigned char)c]++;
    priority_queue<Node *, vector<Node *>, Cmp> pq;
    int ord = 0;
    for (int c = 0; c < 256; c++)
        if (freq[c]) pq.push(new Node(freq[c], ord++, (char)c));
    while (pq.size() > 1) {
        Node *a = pq.top(); pq.pop();
        Node *b = pq.top(); pq.pop();
        pq.push(new Node(a->freq + b->freq, ord++, 0, a, b));
    }
    Node *root = pq.top(); pq.pop();
    return root;
}

void build_codes(Node *root, string path, unordered_map<char, string> &code) {
    if (!root->left && !root->right) { code[root->ch] = path; return; }
    if (root->left)  build_codes(root->left,  path + "0", code);
    if (root->right) build_codes(root->right, path + "1", code);
}

string encode(const string &s, const unordered_map<char, string> &code) {
    string out;
    for (char c : s) out += code.at(c);
    return out;
}

void free_tree(Node *r) { if (r) { free_tree(r->left); free_tree(r->right); delete r; } }

int main() {
    string s = "huffman coding";
    Node *root = build_tree(s);
    unordered_map<char, string> code;
    build_codes(root, "", code);

    cout << "Test 1 codes:";
    for (char c = 0; c < 128; c++)
        if (code.count(c)) cout << " '" << c << "'=" << code[c];
    cout << endl;

    string enc = encode(s, code);
    cout << "Test 2 encoded: " << enc << endl;
    cout << "Test 3 length: " << enc.size()
         << " vs original " << 8 * s.size() << " bits" << endl;
    free_tree(root);
    return 0;
}
'''


HUFFMAN_C = r'''#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Deterministic Huffman: tie-break on a creation counter so C, C++ and
 * Python build the identical tree (and thus emit identical codes). */
typedef struct Node {
    int freq, order;                 /* order: creation index; smaller = picked first on ties */
    char ch;                         /* only set for leaves */
    struct Node *left, *right;
} Node;

static int cmp_node(const void *a, const void *b) {
    const Node *x = *(Node **)a, *y = *(Node **)b;
    if (x->freq != y->freq) return x->freq - y->freq;
    return x->order - y->order;
}
static void sort_pick(Node **arr, int n) { qsort(arr, (size_t)n, sizeof(Node *), cmp_node); }

static Node *new_leaf(char c, int f, int ord) {
    Node *n = (Node *)malloc(sizeof(Node));
    n->freq = f; n->order = ord; n->ch = c; n->left = n->right = NULL;
    return n;
}
static Node *new_internal(Node *l, Node *r, int ord) {
    Node *n = (Node *)malloc(sizeof(Node));
    n->freq = l->freq + r->freq; n->order = ord; n->ch = 0; n->left = l; n->right = r;
    return n;
}
static void free_tree(Node *r) { if (!r) return; free_tree(r->left); free_tree(r->right); free(r); }

static Node *build_tree(int *freq) {
    Node *nodes[256];
    int n = 0, ord = 0;
    for (int c = 0; c < 256; c++)
        if (freq[c]) nodes[n++] = new_leaf((char)c, freq[c], ord++);
    while (n > 1) {
        sort_pick(nodes, n);
        Node *a = nodes[0], *b = nodes[1];
        nodes[0] = new_internal(a, b, ord++);
        for (int i = 1; i < n - 1; i++) nodes[i] = nodes[i + 1];
        n--;
    }
    return nodes[0];
}

static void build_codes(Node *root, char *path, int depth, char codes[256][256]) {
    if (!root->left && !root->right) {
        for (int i = 0; i < depth; i++) codes[(unsigned char)root->ch][i] = path[i];
        codes[(unsigned char)root->ch][depth] = '\0';
        return;
    }
    if (root->left)  { path[depth] = '0'; build_codes(root->left,  path, depth + 1, codes); }
    if (root->right) { path[depth] = '1'; build_codes(root->right, path, depth + 1, codes); }
}

int main(void) {
    const char *s = "huffman coding";
    int freq[256] = {0};
    for (const char *p = s; *p; p++) freq[(unsigned char)*p]++;

    Node *root = build_tree(freq);
    char codes[256][256];
    memset(codes, 0, sizeof(codes));
    char path[256];
    build_codes(root, path, 0, codes);

    printf("Test 1 codes:");
    for (int c = 0; c < 256; c++)
        if (codes[c][0]) printf(" '%c'=%s", (char)c, codes[c]);
    printf("\n");

    char enc[4096] = "";
    for (const char *p = s; *p; p++) strcat(enc, codes[(unsigned char)*p]);
    printf("Test 2 encoded: %s\n", enc);
    printf("Test 3 length: %d vs original %d bits\n", (int)strlen(enc), (int)(strlen(s) * 8));
    free_tree(root);
    return 0;
}
'''


HUFFMAN_PY = r'''from heapq import heappop, heappush, heapify


def build_codes(root):
    """Return {char: code} by walking the merged tree."""
    codes = {}
    def walk(node, path):
        if not node[1]:                       # leaf: (char, freq, None, None)
            codes[node[0]] = path or "0"
            return
        _, _, left, right = node
        walk(left, path + "0")
        walk(right, path + "1")
    walk(root, "")
    return codes


def encode(s, codes):
    return "".join(codes[c] for c in s)


def huffman(s):
    freq = {}
    for c in s:
        freq[c] = freq.get(c, 0) + 1
    # node = (freq, order, char_or_None, left_or_None, right_or_None)
    heap = [(f, i, c, None, None) for i, (c, f) in enumerate(sorted(freq.items()))]
    heapify(heap)
    order = len(heap)
    while len(heap) > 1:
        a = heappop(heap)
        b = heappop(heap)
        heappush(heap, (a[0] + b[0], order, None, a, b))
        order += 1
    root = heap[0]
    codes = build_codes(root)
    enc = encode(s, codes)
    return codes, enc


if __name__ == "__main__":
    s = "huffman coding"
    codes, enc = huffman(s)
        print("Test 1 codes:" + "".join(f" '{c}'={codes[c]}" for c in sorted(codes)))
    print(f"Test 2 encoded: {enc}")
    print(f"Test 3 length: {len(enc)} vs original {8 * len(s)} bits")
'''

TOPIC_HEAP_SORT = {
    "id": "heap-sort",
    "name": "Heap Sort",
    "slug": "heap-sort",
    "type": "sorting-searching",
    "type_label": TYPES["sorting-searching"]["label"],
    "type_icon": TYPES["sorting-searching"]["icon"],
    "priority": 3,
    "difficulty": "Medium",
    "icon": "🏔️",
    "kind": "array",
    "complexity": {
        "best": "O(n log n)",
        "average": "O(n log n)",
        "worst": "O(n log n)",
        "space": "O(1) auxiliary",
        "stable": "No",
        "in_place": "Yes",
    },
    "what": (
        "Heap sort treats the array as a binary max-heap: a complete tree where every parent is at "
        "least as large as its children, stored implicitly in the array itself (children of index i live "
        "at 2i+1 and 2i+2). It first builds the heap in O(n), then repeatedly swaps the maximum (the "
        "root) with the last heap slot and re-heapifies the shrunk heap."
    ),
    "why": (
        "Heap sort is the only classic comparison sort that is simultaneously in-place AND guaranteed "
        "O(n log n) in the worst case — quick sort can degrade to O(n²) and merge sort needs an O(n) "
        "buffer. The same heap structure powers priority queues, so mastering it unlocks schedulers, "
        "Dijkstra, and streaming top-k selection."
    ),
    "when_needed": [
        "A hard worst-case O(n log n) guarantee with in-place operation is required.",
        "The workload is really about repeated max/min extraction — a priority queue.",
        "You need only the k largest/smallest items, not a full sort.",
        "Memory constraints rule out merge sort's auxiliary buffer.",
    ],
    "how_to_select": [
        "Worst-case bound matters more than average speed? Heap sort; raw average speed? quick sort.",
        "Use Floyd's bottom-up build-heap — it is O(n), not n separate O(log n) insertions.",
        "For top-k only, stop after k extractions instead of sorting everything.",
        "Stability required? Heap sort reorders equal keys — use merge sort.",
        "Tiny arrays: insertion sort's constants win; heap machinery is overkill.",
    ],
    "when_not": [
        "Stability is required — equal keys change relative order.",
        "The array is nearly sorted — insertion sort is O(n) here.",
        "Cache-sensitive sorting of huge arrays — quick sort's locality beats heap jumps.",
        "You just need a sorted result from a library — use the built-in sort.",
    ],
    "outline": [
        "Max-heap property: parent >= children, stored implicitly in the array",
        "Build-heap bottom-up in O(n) (Floyd's method)",
        "Extract max n-1 times: swap root with last slot, sift down O(log n)",
        "In-place and worst-case O(n log n) — but not stable",
        "Same structure = priority queues, Dijkstra's frontier, streaming top-k",
    ],
    "applications": [
        {"title": "Priority queues", "detail": "OS schedulers, event simulations, and print queues are heaps; heap sort is the queue's batch mode."},
        {"title": "Introsort fallback", "detail": "C++ std::sort switches from quick sort to heap sort when recursion depth suggests quadratic behaviour."},
        {"title": "Streaming top-k", "detail": "Leaderboards and 'top N' dashboards keep a bounded heap instead of sorting every arrival."},
        {"title": "Graph algorithms", "detail": "Dijkstra and Prim pick their next node from a heap — the extraction loop here is exactly that operation."},
    ],
    "impl_c": HEAP_SORT_C,
    "impl_cpp": HEAP_SORT_CPP,
    "impl_py": HEAP_SORT_PY,
    "sim": sim_heap_sort,
    "references": [
        {"title": "GeeksforGeeks — Heap Sort (reference)", "url": "https://www.geeksforgeeks.org/heap-sort/"},
    ],
}


# ---------------------------------------------------------------------------
# Topic: Counting Sort & Radix Sort
# ---------------------------------------------------------------------------

def sim_counting_radix():
    """Trace stable counting sort: count -> prefix sums -> placement."""
    a = [4, 2, 2, 8, 3, 3, 1]
    max_v = max(a)
    out_steps = []

    def emit(caption, data, highlights=(), compare=(), swap=(), done=False):
        out_steps.append({
            "kind": "array",
            "data": list(data),
            "highlights": list(highlights),
            "compare": list(compare),
            "swap": list(swap),
            "markers": {},
            "caption": caption,
            "done": done,
        })

    emit("Start — values in [0, 8], small range is counting sort's sweet spot", a)
    count = [0] * (max_v + 1)
    emit("Frequency table (bar at index v counts how often value v appears)", count)
    for x in a:
        count[x] += 1
        emit(f"Scan A: value {x} occurs -> count[{x}] = {count[x]}", count, [x], (), ())
    emit("Frequency table complete — counts per value 0..8", count)
    for v in range(1, max_v + 1):
        count[v] += count[v - 1]
    emit("Prefix sums: count[v] = how many values are <= v (final positions)", count)
    result = [0] * len(a)
    emit("Place values from right to left — moving backwards preserves stability", result)
    for i in range(len(a) - 1, -1, -1):
        x = a[i]
        pos = count[x] - 1
        result[pos] = x
        count[x] -= 1
        emit(f"Value {x} -> position {pos} (count[{x}] now {count[x]})", result, [pos], (), ())
    emit("Done — output is sorted and equal keys kept their original order", result, done=True)
    return out_steps


COUNTING_RADIX_C = r'''#include <stdio.h>
#include <stdlib.h>

/* Stable counting sort for values in [0, max]. Three linear passes:
 * count frequencies, prefix-sum them into final positions, place backwards. */
void counting_sort(int a[], int n, int max) {
    int *count = (int *)calloc((size_t)max + 1, sizeof(int));
    int *out = (int *)malloc((size_t)n * sizeof(int));
    for (int i = 0; i < n; i++) count[a[i]]++;
    for (int v = 1; v <= max; v++) count[v] += count[v - 1];
    for (int i = n - 1; i >= 0; i--) {   /* reverse scan = stability */
        out[count[a[i]] - 1] = a[i];
        count[a[i]]--;
    }
    for (int i = 0; i < n; i++) a[i] = out[i];
    free(count);
    free(out);
}

/* One stable counting pass on a single decimal digit (exp = 1, 10, 100...). */
void digit_pass(int a[], int n, int exp) {
    int count[10] = {0};
    int *out = (int *)malloc((size_t)n * sizeof(int));
    for (int i = 0; i < n; i++) count[(a[i] / exp) % 10]++;
    for (int d = 1; d < 10; d++) count[d] += count[d - 1];
    for (int i = n - 1; i >= 0; i--) {
        int d = (a[i] / exp) % 10;
        out[count[d] - 1] = a[i];
        count[d]--;
    }
    for (int i = 0; i < n; i++) a[i] = out[i];
    free(out);
}

/* LSD radix sort: repeated digit passes from least to most significant. */
void radix_sort(int a[], int n) {
    int max = a[0];
    for (int i = 1; i < n; i++) if (a[i] > max) max = a[i];
    for (int exp = 1; max / exp > 0; exp *= 10) digit_pass(a, n, exp);
}

void print_array(int a[], int n) {
    for (int i = 0; i < n; i++) printf("%d ", a[i]);
    printf("\n");
}

int main(void) {
    int a1[] = {4, 2, 2, 8, 3, 3, 1};
    int a2[] = {0, 5, 0, 2};
    int a3[] = {170, 45, 75, 90, 802, 24, 2, 66};
    int a4[] = {5, 100, 3};
    counting_sort(a1, 7, 8); printf("Test 1: "); print_array(a1, 7);
    counting_sort(a2, 4, 5); printf("Test 2: "); print_array(a2, 4);
    radix_sort(a3, 8);       printf("Test 3: "); print_array(a3, 8);
    radix_sort(a4, 3);       printf("Test 4: "); print_array(a4, 3);
    return 0;
}
'''


COUNTING_RADIX_CPP = r'''#include <iostream>
#include <vector>
using namespace std;

/* Stable counting sort for values in [0, max]. */
void countingSort(vector<int>& a, int max) {
    vector<int> count(max + 1, 0), out(a.size());
    for (int x : a) count[x]++;
    for (int v = 1; v <= max; v++) count[v] += count[v - 1];
    for (int i = (int)a.size() - 1; i >= 0; i--) {  /* reverse scan = stability */
        out[count[a[i]] - 1] = a[i];
        count[a[i]]--;
    }
    a = out;
}

/* One stable counting pass on a single decimal digit (exp = 1, 10, 100...). */
void digitPass(vector<int>& a, int exp) {
    vector<int> count(10, 0), out(a.size());
    for (int x : a) count[(x / exp) % 10]++;
    for (int d = 1; d < 10; d++) count[d] += count[d - 1];
    for (int i = (int)a.size() - 1; i >= 0; i--) {
        int d = (a[i] / exp) % 10;
        out[count[d] - 1] = a[i];
        count[d]--;
    }
    a = out;
}

/* LSD radix sort: repeated digit passes, least to most significant. */
void radixSort(vector<int>& a) {
    int max = a[0];
    for (int x : a) max = x > max ? x : max;
    for (int exp = 1; max / exp > 0; exp *= 10) digitPass(a, exp);
}

void print_array(const vector<int>& a) {
    for (int x : a) cout << x << " ";
    cout << "\n";
}

int main() {
    vector<int> a1 = {4, 2, 2, 8, 3, 3, 1};
    vector<int> a2 = {0, 5, 0, 2};
    vector<int> a3 = {170, 45, 75, 90, 802, 24, 2, 66};
    vector<int> a4 = {5, 100, 3};
    countingSort(a1, 8); cout << "Test 1: "; print_array(a1);
    countingSort(a2, 5); cout << "Test 2: "; print_array(a2);
    radixSort(a3);       cout << "Test 3: "; print_array(a3);
    radixSort(a4);       cout << "Test 4: "; print_array(a4);
    return 0;
}
'''


COUNTING_RADIX_PY = r'''def counting_sort(a, max_value):
    """Stable counting sort for values in [0, max_value]."""
    count = [0] * (max_value + 1)
    for x in a:
        count[x] += 1
    for v in range(1, max_value + 1):
        count[v] += count[v - 1]
    out = [0] * len(a)
    for i in range(len(a) - 1, -1, -1):  # reverse scan = stability
        out[count[a[i]] - 1] = a[i]
        count[a[i]] -= 1
    return out


def _digit_pass(a, exp):
    """One stable counting pass on a single decimal digit."""
    count = [0] * 10
    for x in a:
        count[(x // exp) % 10] += 1
    for d in range(1, 10):
        count[d] += count[d - 1]
    out = [0] * len(a)
    for i in range(len(a) - 1, -1, -1):
        d = (a[i] // exp) % 10
        out[count[d] - 1] = a[i]
        count[d] -= 1
    return out


def radix_sort(a):
    """LSD radix sort: digit passes from least to most significant."""
    max_value = max(a)
    exp = 1
    while max_value // exp > 0:
        a = _digit_pass(a, exp)
        exp *= 10
    return a


if __name__ == "__main__":
    print("Test 1:", " ".join(map(str, counting_sort([4, 2, 2, 8, 3, 3, 1], 8))))
    print("Test 2:", " ".join(map(str, counting_sort([0, 5, 0, 2], 5))))
    print("Test 3:", " ".join(map(str, radix_sort([170, 45, 75, 90, 802, 24, 2, 66]))))
    print("Test 4:", " ".join(map(str, radix_sort([5, 100, 3]))))
'''
TOPIC_COUNTING_RADIX = {
    "id": "counting-radix-sort",
    "name": "Counting Sort & Radix Sort",
    "slug": "counting-radix-sort",
    "type": "sorting-searching",
    "type_label": TYPES["sorting-searching"]["label"],
    "type_icon": TYPES["sorting-searching"]["icon"],
    "priority": 3,
    "difficulty": "Easy",
    "icon": "🔢",
    "kind": "array",
    "complexity": {
        "best": "O(n + k) counting · O(d(n+k)) radix",
        "average": "O(n + k) counting · O(d(n+k)) radix",
        "worst": "O(n + k) counting · O(d(n+k)) radix",
        "space": "O(n + k)",
        "stable": "Yes (with reverse-scan placement)",
        "in_place": "No",
    },
    "what": (
        "Counting sort never compares elements. It tallies how many times each key value occurs, converts "
        "those counts into prefix sums (value v's final block ends at position count[v]), then places every "
        "element directly into its slot. Radix sort scales this to large numbers by sorting digit by digit "
        "with a stable counting pass per digit, from least significant to most significant."
    ),
    "why": (
        "Comparison sorts cannot beat O(n log n); counting and radix sidestep that bound by exploiting key "
        "structure — bounded integers — to sort in linear time. They are also inherently stable, which "
        "comparison sorts like quick sort and heap sort are not, and they underpin suffix-array construction "
        "and DC3, where linear-time radix passes sort ranks recursively."
    ),
    "when_needed": [
        "Keys are integers (or fixed-length digit strings) in a small known range [0, k].",
        "Linear-time sorting is needed and k is O(n) or better.",
        "Stability matters — e.g., sorting records by one field of a composite key.",
        "Radix passes shine on very large sets of fixed-width integers (phone numbers, IDs, dates).",
    ],
    "how_to_select": [
        "Range k close to n? Counting sort directly — its arrays are only O(n + k).",
        "Huge range but fixed digit count d? LSD radix with base 10 (or 256 for bytes).",
        "All keys distinct and range huge? A bit-set or hash set may beat both.",
        "Need to sort arbitrary comparable objects (strings of varying length, floats)? Use comparison sorts.",
        "Stability across passes is mandatory for radix — a non-stable inner pass silently breaks correctness.",
    ],
    "when_not": [
        "The key range k is much larger than n (e.g., 32-bit spread) — counting arrays waste memory.",
        "Keys are general comparison objects without a digit structure.",
        "Extra O(n + k) memory is unavailable (counting/radix are not in-place).",
        "n is tiny — the setup passes cost more than a simple insertion sort.",
    ],
    "outline": [
        "Count frequencies of each key in one linear scan",
        "Prefix-sum counts so count[v] = number of elements <= v",
        "Place elements right-to-left — the reverse scan guarantees stability",
        "Radix sort = one stable counting pass per digit, LSD first",
        "Runs in O(n + k) / O(d(n+k)) — no element comparison ever happens",
    ],
    "applications": [
        {"title": "Suffix arrays in linear time", "detail": "DC3/skew construction uses radix passes on rank pairs — the same counting routine shown here."},
        {"title": "Sorting fixed-width IDs", "detail": "Phone numbers, dates, IP octets: radix on fixed-width keys is the classic linear-time workhorse."},
        {"title": "Grading systems", "detail": "Scores bounded 0–100 make counting sort natural — tally and rebuild in two linear passes."},
        {"title": "Graphics / signal pipelines", "detail": "Depth sorting and histogram equalisation process bounded integer keys, exactly this regime."},
    ],
    "impl_c": COUNTING_RADIX_C,
    "impl_cpp": COUNTING_RADIX_CPP,
    "impl_py": COUNTING_RADIX_PY,
    "sim": sim_counting_radix,
    "references": [
        {"title": "GeeksforGeeks — Counting Sort (reference)", "url": "https://www.geeksforgeeks.org/counting-sort/"},
        {"title": "GeeksforGeeks — Radix Sort (reference)", "url": "https://www.geeksforgeeks.org/radix-sort/"},
    ],
}


# ---------------------------------------------------------------------------
# Topic: Binary Tree & Traversals
# ---------------------------------------------------------------------------

def sim_traversals():
    """Trace an inorder traversal of a perfect 7-node tree (tree renderer)."""
    nodes = [
        {"id": 1, "value": 1, "parent": None},
        {"id": 2, "value": 2, "parent": 1},
        {"id": 3, "value": 3, "parent": 1},
        {"id": 4, "value": 4, "parent": 2},
        {"id": 5, "value": 5, "parent": 2},
        {"id": 6, "value": 6, "parent": 3},
        {"id": 7, "value": 7, "parent": 3},
    ]
    left = {1: 2, 2: 4, 3: 6}
    right = {1: 3, 2: 5, 3: 7}
    out = []
    visited = []

    def emit(caption, cur, done=False):
        tree = []
        for nd in nodes:
            st = "done" if nd["id"] in visited else "normal"
            if cur is not None and nd["id"] == cur:
                st = "current"
            tree.append({"id": nd["id"], "value": nd["value"], "parent": nd["parent"], "state": st})
        out.append({"kind": "tree", "tree": tree, "caption": caption, "done": done})

    def inorder(v):
        if v is None:
            return
        inorder(left.get(v))
        visited.append(v)
        emit(f"Visit node {v} — output so far: {' '.join(map(str, visited))}", v)
        inorder(right.get(v))

    emit("Inorder = left subtree, node, right subtree — start at the root 1", 1)
    inorder(1)
    emit("Done — inorder emitted the keys in sorted order for this BST-shaped tree",
         None, done=True)
    return out


TRAVERSALS_C = r'''#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int value;
    struct Node *left, *right;
} Node;

Node *new_node(int v) {
    Node *n = (Node *)malloc(sizeof(Node));
    n->value = v;
    n->left = n->right = NULL;
    return n;
}

/* Depth-first traversals: node position relative to its two subtrees. */
void preorder(Node *r) {
    if (!r) return;
    printf("%d ", r->value);
    preorder(r->left);
    preorder(r->right);
}

void inorder(Node *r) {
    if (!r) return;
    inorder(r->left);
    printf("%d ", r->value);
    inorder(r->right);
}

void postorder(Node *r) {
    if (!r) return;
    postorder(r->left);
    postorder(r->right);
    printf("%d ", r->value);
}

/* Level order = breadth-first with an explicit ring-buffer queue. */
void level_order(Node *root) {
    if (!root) return;
    Node *queue[64];
    int head = 0, tail = 0;
    queue[tail++] = root;
    while (head < tail) {
        Node *cur = queue[head++];
        printf("%d ", cur->value);
        if (cur->left)  queue[tail++] = cur->left;
        if (cur->right) queue[tail++] = cur->right;
    }
}

void free_tree(Node *r) {
    if (!r) return;
    free_tree(r->left);
    free_tree(r->right);
    free(r);
}

int main(void) {
    /*        1
     *       / \
     *      2   3
     *     / \ / \
     *    4  5 6  7      */
    Node *root = new_node(1);
    root->left = new_node(2);  root->right = new_node(3);
    root->left->left = new_node(4);  root->left->right = new_node(5);
    root->right->left = new_node(6); root->right->right = new_node(7);

    printf("Test 1 (preorder):  "); preorder(root);  printf("\n");
    printf("Test 2 (inorder):   "); inorder(root);   printf("\n");
    printf("Test 3 (postorder): "); postorder(root); printf("\n");
    printf("Test 4 (level order): "); level_order(root); printf("\n");
    free_tree(root);
    return 0;
}
'''


TRAVERSALS_CPP = r'''#include <iostream>
#include <memory>
#include <vector>
using namespace std;

struct Node {
    int value;
    unique_ptr<Node> left, right;
    explicit Node(int v) : value(v) {}
};

void preorder(const Node* r) {
    if (!r) return;
    cout << r->value << " ";
    preorder(r->left.get());
    preorder(r->right.get());
}

void inorder(const Node* r) {
    if (!r) return;
    inorder(r->left.get());
    cout << r->value << " ";
    inorder(r->right.get());
}

void postorder(const Node* r) {
    if (!r) return;
    postorder(r->left.get());
    postorder(r->right.get());
    cout << r->value << " ";
}

/* Level order: breadth-first with a queue (iterative). */
void level_order(const Node* root) {
    if (!root) return;
    vector<const Node*> queue{root};
    for (size_t head = 0; head < queue.size(); head++) {
        const Node* cur = queue[head];
        cout << cur->value << " ";
        if (cur->left)  queue.push_back(cur->left.get());
        if (cur->right) queue.push_back(cur->right.get());
    }
}

int main() {
    /*        1
     *       / \
     *      2   3
     *     / \ / \
     *    4  5 6  7      */
    auto root = make_unique<Node>(1);
    root->left = make_unique<Node>(2);  root->right = make_unique<Node>(3);
    root->left->left = make_unique<Node>(4);  root->left->right = make_unique<Node>(5);
    root->right->left = make_unique<Node>(6); root->right->right = make_unique<Node>(7);

    cout << "Test 1 (preorder):  "; preorder(root.get());  cout << "\n";
    cout << "Test 2 (inorder):   "; inorder(root.get());   cout << "\n";
    cout << "Test 3 (postorder): "; postorder(root.get()); cout << "\n";
    cout << "Test 4 (level order): "; level_order(root.get()); cout << "\n";
    return 0;
}
'''


TRAVERSALS_PY = r'''from collections import deque


class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


def preorder(r):
    if r is None:
        return []
    return [r.value] + preorder(r.left) + preorder(r.right)


def inorder(r):
    if r is None:
        return []
    return inorder(r.left) + [r.value] + inorder(r.right)


def postorder(r):
    if r is None:
        return []
    return postorder(r.left) + postorder(r.right) + [r.value]


def level_order(root):
    """Breadth-first with a queue."""
    if root is None:
        return []
    out, queue = [], deque([root])
    while queue:
        cur = queue.popleft()
        out.append(cur.value)
        if cur.left:
            queue.append(cur.left)
        if cur.right:
            queue.append(cur.right)
    return out


if __name__ == "__main__":
    #        1
    #       / \
    #      2   3
    #     / \ / \
    #    4  5 6  7
    root = Node(1)
    root.left, root.right = Node(2), Node(3)
    root.left.left, root.left.right = Node(4), Node(5)
    root.right.left, root.right.right = Node(6), Node(7)

    print(f"Test 1 (preorder):  {' '.join(map(str, preorder(root)))}")
    print(f"Test 2 (inorder):   {' '.join(map(str, inorder(root)))}")
    print(f"Test 3 (postorder): {' '.join(map(str, postorder(root)))}")
    print(f"Test 4 (level order): {' '.join(map(str, level_order(root)))}")
'''
TOPIC_TRAVERSALS = {
    "id": "binary-tree-traversals",
    "name": "Binary Tree & Traversals",
    "slug": "binary-tree-traversals",
    "type": "tree",
    "type_label": TYPES["tree"]["label"],
    "type_icon": TYPES["tree"]["icon"],
    "priority": 5,
    "difficulty": "Easy",
    "icon": "🌲",
    "kind": "tree",
    "complexity": {
        "best": "O(n) — every node visited once",
        "average": "O(n)",
        "worst": "O(n)",
        "space": "O(h) recursion stack (O(n) worst, O(log n) balanced); O(w) queue for level order",
        "stable": "n/a",
        "in_place": "Read-only traversal",
    },
    "what": (
        "A binary tree is a hierarchy where each node has at most two children. Traversals define the "
        "order in which nodes are visited: the three depth-first orders (preorder: node-left-right, "
        "inorder: left-node-right, postorder: left-right-node) differ only in when the node itself is "
        "emitted relative to its subtrees, while level order walks breadth-first with a queue."
    ),
    "why": (
        "Almost every tree algorithm is a traversal wearing a different coat: expression trees evaluate "
        "in postorder, BSTs print in sorted order via inorder, serialization uses preorder with sentinels, "
        "and GUI/logic frameworks free or process children after parents with postorder. Learning these "
        "four patterns first makes every later tree topic — BST, heap, LCA, diameter — a small variation."
    ),
    "when_needed": [
        "Printing, copying, or serialising a whole tree.",
        "Inorder on a BST gives sorted output; preorder serialises a tree for rebuild.",
        "Postorder for evaluate-children-first problems (expression trees, directory sizes, freeing memory).",
        "Level order for breadth-related questions: height by levels, right-side view, nearest match.",
    ],
    "how_to_select": [
        "Need the root before its subtrees (prefix output, copying)? Preorder.",
        "Need a BST's keys in sorted order, or to validate a BST? Inorder.",
        "Need children fully processed before the parent (evaluate, delete, aggregate)? Postorder.",
        "Need nodes layer by layer (shortest depth, per-level aggregation)? Level order with a queue.",
        "Very deep skewed trees: an explicit stack avoids recursion-overflow in languages without TCO.",
    ],
    "when_not": [
        "You need a specific node lookup in a BST — direct search is O(h), traversal is O(n).",
        "The 'tree' is really a graph with cycles — plain traversal must track visited states first.",
        "Huge trees in memory-tight settings — Morris inorder (O(1) extra) trades pointer rewrites for the stack.",
        "The data is a heap stored in an array — implicit indices beat pointer traversal.",
    ],
    "outline": [
        "Depth-first recursion: preorder (N-L-R), inorder (L-N-R), postorder (L-R-N)",
        "Level order: BFS with a queue, processing layers left to right",
        "All DFS traversals cost O(n) time and O(h) stack; BFS costs O(w) queue width",
        "Inorder on a BST emits keys in sorted order — the base of many BST proofs",
        "Iterative variants use an explicit stack; Morris inorder achieves O(1) extra space",
    ],
    "applications": [
        {"title": "Expression evaluation", "detail": "Compilers and calculators walk expression trees postorder — children are evaluated before their operator."},
        {"title": "File-system walks", "detail": "du-style tools aggregate directory sizes with postorder; listings use preorder."},
        {"title": "Serialization", "detail": "Tree data saved to JSON/flatbuffers is written preorder with null markers and rebuilt by the same order."},
        {"title": "UI frameworks", "detail": "Render and layout passes traverse widget trees; teardown frees children before parents (postorder)."},
    ],
    "impl_c": TRAVERSALS_C,
    "impl_cpp": TRAVERSALS_CPP,
    "impl_py": TRAVERSALS_PY,
    "sim": sim_traversals,
    "references": [
        {"title": "GeeksforGeeks — Tree Traversals (reference)", "url": "https://www.geeksforgeeks.org/tree-traversals-inorder-preorder-and-postorder/"},
    ],
}


# ---------------------------------------------------------------------------
# Topic: Binary Search Tree
# ---------------------------------------------------------------------------

def sim_bst():
    """Trace inserting into a BST, then searching (tree renderer)."""
    nodes = {}          # value -> {"left": v|None, "right": v|None}
    parent = {}         # value -> parent value (None for root)
    root = None
    out = []

    def snapshot(caption, cur=None, path=(), fresh=None, done=False):
        tree = []
        for v in nodes:
            st = "normal"
            if v in path:
                st = "path"
            if cur == v:
                st = "current"
            if fresh == v:
                st = "frontier"
            tree.append({
                "id": v, "value": v, "parent": parent.get(v), "state": st,
                "edgeState": "path" if (v in path or fresh == v) else "normal",
            })
        out.append({"kind": "tree", "tree": tree, "caption": caption, "done": done})

    def insert(v):
        nonlocal root
        if root is None:
            root = v
            nodes[v] = {"left": None, "right": None}
            parent[v] = None
            snapshot(f"Insert {v} as the root", fresh=v)
            return
        path, cur = [], root
        while True:
            path.append(cur)
            go_left = v < cur
            snapshot(f"Insert {v}: compare with {cur} -> go {'left' if go_left else 'right'}",
                     cur=cur, path=path)
            child = nodes[cur]["left" if go_left else "right"]
            if child is None:
                nodes[v] = {"left": None, "right": None}
                parent[v] = cur
                nodes[cur]["left" if go_left else "right"] = v
                snapshot(f"Attach {v} as the {'left' if go_left else 'right'} child of {cur}",
                         fresh=v)
                return
            cur = child

    def search(v):
        path, cur = [], root
        while cur is not None:
            path.append(cur)
            if v == cur:
                snapshot(f"Search {v}: found at node {cur} after {len(path) - 1} comparison(s)",
                         cur=cur, path=path)
                return True
            snapshot(f"Search {v}: {v} {'<' if v < cur else '>'} {cur} -> go "
                     f"{'left' if v < cur else 'right'}", cur=cur, path=path)
            cur = nodes[cur]["left" if v < cur else "right"]
        snapshot(f"Search {v}: hit an empty subtree — {v} is not in the tree", path=path)
        return False

    for v in [50, 30, 70, 20, 40, 60, 80]:
        insert(v)
    snapshot("Tree built — 7 nodes; inorder traversal of a BST emits keys in sorted order")
    search(60)
    search(35)
    out[-1]["done"] = True
    return out


BST_C = r'''#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int key;
    struct Node *left, *right;
} Node;

Node *new_node(int key) {
    Node *n = (Node *)malloc(sizeof(Node));
    n->key = key;
    n->left = n->right = NULL;
    return n;
}

/* Insert: smaller keys go left, larger go right. O(h). */
Node *insert(Node *r, int key) {
    if (!r) return new_node(key);
    if (key < r->key)      r->left = insert(r->left, key);
    else if (key > r->key) r->right = insert(r->right, key);
    return r;               /* duplicates are ignored */
}

int search(Node *r, int key) {
    while (r) {
        if (key == r->key) return 1;
        r = (key < r->key) ? r->left : r->right;
    }
    return 0;
}

int find_min(Node *r) {
    while (r->left) r = r->left;
    return r->key;
}

/* Delete: three cases — leaf, one child, two children (replace with the
 * inorder successor = minimum of the right subtree). O(h). */
Node *delete_node(Node *r, int key) {
    if (!r) return NULL;
    if (key < r->key)      r->left = delete_node(r->left, key);
    else if (key > r->key) r->right = delete_node(r->right, key);
    else {
        if (!r->left)  { Node *t = r->right; free(r); return t; }
        if (!r->right) { Node *t = r->left;  free(r); return t; }
        r->key = find_min(r->right);
        r->right = delete_node(r->right, r->key);
    }
    return r;
}

void inorder(Node *r) {
    if (!r) return;
    inorder(r->left);
    printf("%d ", r->key);
    inorder(r->right);
}

void free_tree(Node *r) {
    if (!r) return;
    free_tree(r->left);
    free_tree(r->right);
    free(r);
}

Node *build(int keys[], int n) {
    Node *root = NULL;
    for (int i = 0; i < n; i++) root = insert(root, keys[i]);
    return root;
}

int main(void) {
    int keys[] = {50, 30, 70, 20, 40, 60, 80};
    Node *t = build(keys, 7);
    printf("Test 1 (inorder): "); inorder(t); printf("\n");

    printf("Test 2: search 40 -> %s\n", search(t, 40) ? "found" : "not found");
    printf("Test 3: search 35 -> %s\n", search(t, 35) ? "found" : "not found");
    printf("Test 4: min = %d\n", find_min(t));

    t = delete_node(t, 20);   /* leaf */
    t = delete_node(t, 30);   /* two children */
    printf("Test 5 (after deleting 20, 30): "); inorder(t); printf("\n");
    free_tree(t);

    int asc[] = {1, 2, 3, 4, 5};   /* degenerates into a linked list */
    Node *w = build(asc, 5);
    printf("Test 6 (skewed insert order, inorder still sorted): "); inorder(w); printf("\n");
    free_tree(w);
    return 0;
}
'''


BST_CPP = r'''#include <iostream>
#include <memory>
using namespace std;

struct Node {
    int key;
    unique_ptr<Node> left, right;
    explicit Node(int k) : key(k) {}
};

class BST {
public:
    void insert(int key) { root_ = insert(move(root_), key); }
    bool search(int key) const {
        const Node* r = root_.get();
        while (r) {
            if (key == r->key) return true;
            r = (key < r->key) ? r->left.get() : r->right.get();
        }
        return false;
    }
    int min_key() const {
        const Node* r = root_.get();
        while (r->left) r = r->left.get();
        return r->key;
    }
    void erase(int key) { root_ = erase(move(root_), key); }

    void inorder(ostream& os) const { inorder(os, root_.get()); }

private:
    unique_ptr<Node> root_;

    static unique_ptr<Node> insert(unique_ptr<Node> r, int key) {
        if (!r) return make_unique<Node>(key);
        if (key < r->key)      r->left  = insert(move(r->left), key);
        else if (key > r->key) r->right = insert(move(r->right), key);
        return r;                       /* duplicates ignored */
    }

    static unique_ptr<Node> erase(unique_ptr<Node> r, int key) {
        if (!r) return nullptr;
        if (key < r->key)      r->left  = erase(move(r->left), key);
        else if (key > r->key) r->right = erase(move(r->right), key);
        else {
            if (!r->left)  return move(r->right);
            if (!r->right) return move(r->left);
            r->key = min_node(r->right.get())->key;
            r->right = erase(move(r->right), r->key);
        }
        return r;
    }

    static const Node* min_node(const Node* r) {
        while (r->left) r = r->left.get();
        return r;
    }

    static void inorder(ostream& os, const Node* r) {
        if (!r) return;
        inorder(os, r->left.get());
        os << r->key << " ";
        inorder(os, r->right.get());
    }
};

int main() {
    BST t;
    for (int k : {50, 30, 70, 20, 40, 60, 80}) t.insert(k);

    cout << "Test 1 (inorder): "; t.inorder(cout); cout << "\n";
    cout << "Test 2: search 40 -> " << (t.search(40) ? "found" : "not found") << "\n";
    cout << "Test 3: search 35 -> " << (t.search(35) ? "found" : "not found") << "\n";
    cout << "Test 4: min = " << t.min_key() << "\n";

    t.erase(20);   /* leaf */
    t.erase(30);   /* two children */
    cout << "Test 5 (after deleting 20, 30): "; t.inorder(cout); cout << "\n";

    BST w;
    for (int k : {1, 2, 3, 4, 5}) w.insert(k);   /* degenerates into a list */
    cout << "Test 6 (skewed insert order, inorder still sorted): "; w.inorder(cout); cout << "\n";
    return 0;
}
'''


BST_PY = r'''class Node:
    __slots__ = ("key", "left", "right")

    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None


class BST:
    def __init__(self):
        self.root = None

    def insert(self, key):
        self.root = self._insert(self.root, key)

    def _insert(self, r, key):
        if r is None:
            return Node(key)
        if key < r.key:
            r.left = self._insert(r.left, key)
        elif key > r.key:
            r.right = self._insert(r.right, key)
        return r                          # duplicates ignored

    def search(self, key):
        r = self.root
        while r is not None:
            if key == r.key:
                return True
            r = r.left if key < r.key else r.right
        return False

    def min_key(self):
        r = self.root
        while r.left is not None:
            r = r.left
        return r.key

    def erase(self, key):
        self.root = self._erase(self.root, key)

    def _erase(self, r, key):
        if r is None:
            return None
        if key < r.key:
            r.left = self._erase(r.left, key)
        elif key > r.key:
            r.right = self._erase(r.right, key)
        else:
            if r.left is None:
                return r.right
            if r.right is None:
                return r.left
            succ = r.right                 # inorder successor
            while succ.left is not None:
                succ = succ.left
            r.key = succ.key
            r.right = self._erase(r.right, r.key)
        return r

    def inorder(self):
        out = []

        def walk(n):
            if n is None:
                return
            walk(n.left)
            out.append(n.key)
            walk(n.right)

        walk(self.root)
        return out


if __name__ == "__main__":
    t = BST()
    for k in (50, 30, 70, 20, 40, 60, 80):
        t.insert(k)
    print(f"Test 1 (inorder): {' '.join(map(str, t.inorder()))}")
    print(f"Test 2: search 40 -> {'found' if t.search(40) else 'not found'}")
    print(f"Test 3: search 35 -> {'found' if t.search(35) else 'not found'}")
    print(f"Test 4: min = {t.min_key()}")

    t.erase(20)   # leaf
    t.erase(30)   # two children
    print(f"Test 5 (after deleting 20, 30): {' '.join(map(str, t.inorder()))}")

    w = BST()
    for k in (1, 2, 3, 4, 5):      # degenerates into a linked list
        w.insert(k)
    print(f"Test 6 (skewed insert order, inorder still sorted): {' '.join(map(str, w.inorder()))}")
'''
TOPIC_BST = {
    "id": "binary-search-tree",
    "name": "Binary Search Tree",
    "slug": "binary-search-tree",
    "type": "tree",
    "type_label": TYPES["tree"]["label"],
    "type_icon": TYPES["tree"]["icon"],
    "priority": 5,
    "difficulty": "Medium",
    "icon": "🌳",
    "kind": "tree",
    "complexity": {
        "best": "O(log n) — balanced tree",
        "average": "O(log n)",
        "worst": "O(n) — degenerates into a linked list",
        "space": "O(n) for the structure; O(h) recursion per operation",
        "stable": "n/a",
        "in_place": "Yes (pointer rewiring)",
    },
    "what": (
        "A binary search tree keeps one ordering invariant: every key in a node's left subtree is "
        "smaller than the node, and every key in its right subtree is larger. That single rule turns "
        "search into a guided walk from the root — at each node you discard an entire half of the tree — "
        "and it makes an inorder traversal emit the keys in sorted order."
    ),
    "why": (
        "The BST is the first data structure that combines fast lookup with fast, in-order updates. "
        "Sorted arrays search in O(log n) but insert in O(n); hash sets average O(1) but lose ordering "
        "entirely. A BST supports search, insert, delete, min/max, predecessor/successor, and range "
        "scans in O(h) while keeping the data sorted at all times — which is why every balanced variant "
        "(AVL, red-black) and most database index trees grow from this idea."
    ),
    "when_needed": [
        "Frequent inserts/deletes interleaved with lookups, and the data must stay sorted.",
        "Ordered queries: minimum, maximum, successor, predecessor, range reporting.",
        "Implementing ordered sets, maps, or index structures.",
        "A teaching base before studying AVL, red-black, or B-trees.",
    ],
    "how_to_select": [
        "Insert order decides shape — random keys give O(log n) height, sorted keys give O(n).",
        "If adversarial or sorted input is likely, self-balancing trees (AVL, red-black) are mandatory.",
        "Need ordering plus worst-case guarantees but data lives on disk? Use a B-tree instead.",
        "Only point lookups, no ordering? A hash table is simpler and faster on average.",
        "Duplicates: keep a counter per node, or adopt a 'right = >= ' convention consistently.",
    ],
    "when_not": [
        "Keys arrive in sorted order and cannot be balanced — height becomes n, all operations O(n).",
        "You never need ordered queries — a hash table's O(1) average beats O(log n).",
        "Strict latency guarantees matter — an unbalanced BST has none; pick a balanced structure.",
        "The dataset fits in a sorted array and is read-mostly — binary search on the array is lighter.",
    ],
    "outline": [
        "Invariant: left subtree < node < right subtree",
        "Search/insert walk the root-to-leaf path — O(h) comparisons",
        "Delete has three cases: leaf, one child, two children (swap with inorder successor)",
        "Inorder traversal always yields sorted keys — the structure is a live sort",
        "Height h decides everything: log n if balanced, n if skewed — hence self-balancing trees",
    ],
    "applications": [
        {"title": "Ordered sets and maps", "detail": "C++ std::set/std::map are red-black trees — the balanced descendant of the plain BST shown here."},
        {"title": "Database indexes", "detail": "B-trees and B+ trees keep the BST ordering invariant across disk pages; the search walk is identical."},
        {"title": "Autocomplete and range queries", "detail": "Prefix stores and interval indexes exploit the same ordered-tree navigation."},
        {"title": "Scheduling and event queues", "detail": "Ordered event calendars (network simulators) use BSTs for fast 'next event after time t' queries."},
    ],
    "impl_c": BST_C,
    "impl_cpp": BST_CPP,
    "impl_py": BST_PY,
    "sim": sim_bst,
    "references": [
        {"title": "GeeksforGeeks — Binary Search Tree (reference)", "url": "https://www.geeksforgeeks.org/binary-search-tree-data-structure/"},
    ],
}


# ---------------------------------------------------------------------------
# Topic: Binary Heap & Priority Queue
# ---------------------------------------------------------------------------

def sim_binary_heap():
    """Trace sift-up inserts and pop-min on a binary min-heap (array renderer)."""
    heap = []
    out = []

    def emit(caption, highlights=(), compare=(), swap=(), done=False):
        out.append({
            "kind": "array",
            "data": list(heap),
            "highlights": list(highlights),
            "compare": list(compare),
            "swap": list(swap),
            "markers": {},
            "caption": caption,
            "done": done,
        })

    def push(v):
        heap.append(v)
        emit(f"Push {v} at the next free slot (index {len(heap) - 1})", [len(heap) - 1])
        i = len(heap) - 1
        while i > 0:
            p = (i - 1) // 2
            emit(f"Sift up: compare {v} with parent {heap[p]} at index {p}",
                 [i], [i, p])
            if heap[i] < heap[p]:
                emit(f"{v} is smaller than parent {heap[p]} -> swap them", [], [], [i, p])
                heap[i], heap[p] = heap[p], heap[i]
                i = p
            else:
                emit(f"{v} >= parent {heap[p]} -> heap property restored, stop", [i])
                return
        emit(f"{v} reached the root — it is the new minimum", [0])

    def pop():
        last = heap.pop()
        if not heap:
            emit(f"Pop: heap had one element -> extracted {last}")
            return last
        top = heap[0]
        heap[0] = last
        emit(f"Pop min {top}: move the last element {last} to the root, then sift down",
             [0], (), [0])
        i, size = 0, len(heap)
        while True:
            l, r = 2 * i + 1, 2 * i + 2
            smallest, kids = i, [k for k in (l, r) if k < size]
            if kids:
                emit(f"Sift down: compare {last} with children "
                     + ", ".join(str(heap[k]) for k in kids), [i], kids)
            if l < size and heap[l] < heap[smallest]:
                smallest = l
            if r < size and heap[r] < heap[smallest]:
                smallest = r
            if smallest == i:
                emit("Both children are larger (or none) -> stop", [i])
                return top
            heap[i], heap[smallest] = heap[smallest], heap[i]
            emit(f"Swap with the smaller child {heap[i]} <-> {heap[smallest]}", [], [], [i, smallest])
            i = smallest

    emit("Empty heap — a min-heap stored in an array: children of i live at 2i+1 and 2i+2")
    for v in [10, 40, 15, 30, 20, 5]:
        push(v)
    emit("Heap built — index 0 always holds the minimum", [0])
    pop()
    pop()
    emit("Two extractions later: the smallest values left in sorted order", done=True)
    return out


BINARY_HEAP_C = r'''#include <stdio.h>

/* Array-backed binary min-heap: children of i live at 2i+1 and 2i+2,
 * parent at (i-1)/2. push/pop are O(log n), peek is O(1). */
#define CAP 128

typedef struct {
    int a[CAP];
    int size;
} Heap;

void push(Heap *h, int v) {
    int i = h->size++;
    h->a[i] = v;
    while (i > 0) {                    /* sift up */
        int p = (i - 1) / 2;
        if (h->a[i] >= h->a[p]) break;
        int t = h->a[i]; h->a[i] = h->a[p]; h->a[p] = t;
        i = p;
    }
}

int peek(Heap *h) { return h->a[0]; }

int pop(Heap *h) {
    int top = h->a[0];
    h->a[0] = h->a[--h->size];
    int i = 0;
    for (;;) {                         /* sift down */
        int l = 2 * i + 1, r = 2 * i + 2, s = i;
        if (l < h->size && h->a[l] < h->a[s]) s = l;
        if (r < h->size && h->a[r] < h->a[s]) s = r;
        if (s == i) break;
        int t = h->a[i]; h->a[i] = h->a[s]; h->a[s] = t;
        i = s;
    }
    return top;
}

/* k smallest values of an array: push all, pop k times. O(n log n). */
void k_smallest(int arr[], int n, int k, int out[]) {
    Heap h = {0};
    for (int i = 0; i < n; i++) push(&h, arr[i]);
    for (int t = 0; t < k; t++) out[t] = pop(&h);
}

void print_array(int a[], int n) {
    for (int i = 0; i < n; i++) printf("%d ", a[i]);
    printf("\n");
}

int main(void) {
    Heap h = {0};
    int vals[] = {10, 40, 15, 30, 20, 5};
    for (int i = 0; i < 6; i++) push(&h, vals[i]);
    printf("Test 1: top = %d\n", peek(&h));
    printf("Test 2: pop all -> ");
    for (int i = 0; i < 6; i++) printf("%d ", pop(&h));
    printf("\n");

    int arr[] = {7, 10, 4, 3, 20, 15};
    int k3[3];
    k_smallest(arr, 6, 3, k3);
    printf("Test 3: 3 smallest -> "); print_array(k3, 3);
    return 0;
}
'''


BINARY_HEAP_CPP = r'''#include <iostream>
#include <queue>
#include <vector>
using namespace std;

/* std::priority_queue is a max-heap by default; the greater<> comparator
 * turns it into a min-heap. Under the hood it is exactly the array heap
 * implemented in the C version (push_heap / pop_heap). */
int main() {
    priority_queue<int, vector<int>, greater<int>> pq;
    for (int v : {10, 40, 15, 30, 20, 5}) pq.push(v);

    cout << "Test 1: top = " << pq.top() << "\n";

    cout << "Test 2: pop all -> ";
    while (!pq.empty()) {
        cout << pq.top() << " ";
        pq.pop();
    }
    cout << "\n";

    /* 3 smallest of an array: heapify a copy, pop 3 times. */
    vector<int> arr = {7, 10, 4, 3, 20, 15};
    priority_queue<int, vector<int>, greater<int>> pq2(greater<int>(), arr);
    cout << "Test 3: 3 smallest -> ";
    for (int t = 0; t < 3; t++) {
        cout << pq2.top() << " ";
        pq2.pop();
    }
    cout << "\n";
    return 0;
}
'''


BINARY_HEAP_PY = r'''import heapq

# heapq implements a binary MIN-heap on a plain list:
# heappush / heappop are O(log n), the list head is always the minimum.

vals = [10, 40, 15, 30, 20, 5]
h = list(vals)
heapq.heapify(h)                      # O(n) bottom-up build
print(f"Test 1: top = {h[0]}")

popped = "".join(f"{heapq.heappop(h)} " for _ in range(len(vals)))
print(f"Test 2: pop all -> {popped}")

arr = [7, 10, 4, 3, 20, 15]
h2 = list(arr)
heapq.heapify(h2)
k3 = [heapq.heappop(h2) for _ in range(3)]
print(f"Test 3: 3 smallest -> {' '.join(map(str, k3))} ")
'''
TOPIC_BINARY_HEAP = {
    "id": "binary-heap-priority-queue",
    "name": "Binary Heap & Priority Queue",
    "slug": "binary-heap-priority-queue",
    "type": "tree",
    "type_label": TYPES["tree"]["label"],
    "type_icon": TYPES["tree"]["icon"],
    "priority": 4,
    "difficulty": "Medium",
    "icon": "⚖️",
    "kind": "array",
    "complexity": {
        "best": "O(1) peek; O(log n) push/pop",
        "average": "O(log n) push/pop",
        "worst": "O(log n) push/pop; O(1) peek",
        "space": "O(n) — stored as a plain array",
        "stable": "No (equal keys may reorder)",
        "in_place": "Yes (implicit tree in the array)",
    },
    "what": (
        "A binary heap is a complete binary tree stored inside a plain array: the children of index i "
        "live at 2i+1 and 2i+2, its parent at (i-1)/2. Every parent satisfies the heap property relative "
        "to its children (min-heap: parent ≤ children; max-heap: parent ≥ children), so the extreme "
        "value always sits at index 0. A priority queue is this structure plus push/pop/peek."
    ),
    "why": (
        "Whenever work must be processed 'most urgent first', a heap is the efficient answer: it finds "
        "and removes the extreme element in O(log n) and reorganises with two cheap sibling swaps per "
        "level — a sorted list would need O(n) per insert. Heaps are the engine inside Dijkstra and Prim, "
        "OS schedulers, event simulators, and every 'top-k' or streaming-median problem. They are also "
        "the structure behind heap sort."
    ),
    "when_needed": [
        "Repeatedly extract the min or max while others keep arriving — schedulers, event loops.",
        "Top-k / k smallest / k largest without fully sorting: O(n log k).",
        "Dijkstra or Prim need a 'cheapest next vertex' operation.",
        "Merging k sorted lists: heap of the k current heads.",
        "Streaming median: two heaps (max-heap low half, min-heap high half).",
    ],
    "how_to_select": [
        "Min-heap vs max-heap: invert the comparator — C++ std::priority_queue is a max-heap unless you pass greater<>.",
        "Need to decrease/increase an arbitrary element's key? Add an index map (indexed heap) or use a balanced tree.",
        "Building from n known items: heapify bottom-up in O(n), not n pushes (O(n log n)).",
        "Only need the k best: keep the heap at size k for O(n log k).",
        "If you need ordered iteration over all keys, a heap is wrong — it only guarantees the extreme; use a BST.",
    ],
    "when_not": [
        "You must search for arbitrary keys — heaps have no search order, O(n) scan.",
        "You need the full sorted sequence repeatedly — sorting once may be cheaper.",
        "Stable priority among equal keys matters — heapify reorders equal items; pair the payload with a sequence number.",
        "Concurrent access with lock-free requirements — specialised queues (e.g., lock-free MPMC) exist for that.",
    ],
    "outline": [
        "Complete tree in an array: parent (i-1)/2, children 2i+1 / 2i+2 — no pointers needed",
        "push: append at the end, sift up while smaller than parent",
        "pop-min: remove index 0, move the last element to the root, sift down",
        "heapify (Floyd, bottom-up) builds from n items in O(n)",
        "min-heap vs max-heap is just the comparator; C++ default is max-heap, heapq is min-heap",
    ],
    "applications": [
        {"title": "CPU and job schedulers", "detail": "Kernels and job systems keep runnable tasks in priority queues; the next task is a pop away."},
        {"title": "Dijkstra / A* pathfinding", "detail": "Navigation engines (maps, game AI) pop the cheapest frontier node from a heap at every step."},
        {"title": "Event-driven simulation", "detail": "Discrete-event simulators (networks, physics) order future events by time in a heap."},
        {"title": "Huffman coding", "detail": "The encoder repeatedly extracts the two least-frequent symbols — a heap makes each step O(log n)."},
    ],
    "impl_c": BINARY_HEAP_C,
    "impl_cpp": BINARY_HEAP_CPP,
    "impl_py": BINARY_HEAP_PY,
    "sim": sim_binary_heap,
    "references": [
        {"title": "GeeksforGeeks — Binary Heap (reference)", "url": "https://www.geeksforgeeks.org/binary-heap/"},
    ],
}


# ---------------------------------------------------------------------------
# Topic: AVL Tree
# ---------------------------------------------------------------------------

def sim_avl():
    """Trace AVL inserts with LL, RR and RL rebalancing (tree renderer)."""
    nodes = {}      # key -> {"l":, "r":, "h":}
    parent = {}     # key -> parent key (None for root)
    out = []
    root = None
    path = []

    def height(v):
        return nodes[v]["h"] if v is not None else 0

    def update(v):
        nodes[v]["h"] = 1 + max(height(nodes[v]["l"]), height(nodes[v]["r"]))

    def bf(v):
        return height(nodes[v]["l"]) - height(nodes[v]["r"]) if v is not None else 0

    def set_child(p, side, c):
        nodes[p][side] = c
        if c is not None:
            parent[c] = p

    def snapshot(caption, cur=None, path_=None, fresh=None, done=False):
        tree = []
        for v in nodes:
            st = "normal"
            p = path_ if path_ is not None else path
            if v in p:
                st = "path"
            if cur == v:
                st = "current"
            if fresh == v:
                st = "frontier"
            tree.append({
                "id": v, "value": v, "parent": parent.get(v), "state": st,
                "edgeState": "path" if (v in p or fresh == v) else "normal",
            })
        out.append({"kind": "tree", "tree": tree, "caption": caption, "done": done})

    def rotate_right(y):
        x = nodes[y]["l"]
        b = nodes[x]["r"]
        set_child(y, "l", b)
        set_child(x, "r", y)
        parent[y] = x
        update(y)
        update(x)
        return x

    def rotate_left(x):
        y = nodes[x]["r"]
        b = nodes[y]["l"]
        set_child(x, "r", b)
        set_child(y, "l", x)
        parent[x] = y
        update(x)
        update(y)
        return y

    def insert(v):
        nonlocal root
        path.clear()

        def rec(n, p):
            if n is None:
                nodes[v] = {"l": None, "r": None, "h": 1}
                parent[v] = p
                snapshot(f"Insert {v} as a new leaf", fresh=v)
                return v
            path.append(n)
            go_left = v < n
            snapshot(f"Insert {v}: compare with {n} -> go {'left' if go_left else 'right'}",
                     cur=n)
            side = "l" if go_left else "r"
            child = rec(nodes[n][side], n)
            set_child(n, side, child)
            update(n)
            b = bf(n)
            if b > 1 and v < nodes[n]["l"]:
                snapshot(f"Node {n} unbalanced (balance {b:+d}) — LL case: rotate right at {n}",
                         cur=n)
                new = rotate_right(n)
                snapshot(f"Right rotation done — {new} is the new subtree root", fresh=new)
                return new
            if b > 1:
                snapshot(f"Node {n} unbalanced (balance {b:+d}) — LR case: rotate left at "
                         f"{nodes[n]['l']}, then right at {n}", cur=n)
                set_child(n, "l", rotate_left(nodes[n]["l"]))
                new = rotate_right(n)
                snapshot(f"Double rotation done — {new} is the new subtree root", fresh=new)
                return new
            if b < -1 and v > nodes[n]["r"]:
                snapshot(f"Node {n} unbalanced (balance {b:+d}) — RR case: rotate left at {n}",
                         cur=n)
                new = rotate_left(n)
                snapshot(f"Left rotation done — {new} is the new subtree root", fresh=new)
                return new
            if b < -1:
                snapshot(f"Node {n} unbalanced (balance {b:+d}) — RL case: rotate right at "
                         f"{nodes[n]['r']}, then left at {n}", cur=n)
                set_child(n, "r", rotate_right(nodes[n]["r"]))
                new = rotate_left(n)
                snapshot(f"Double rotation done — {new} is the new subtree root", fresh=new)
                return new
            return n

        root = rec(root, None)
        parent[root] = None
        snapshot(f"Insert {v} complete — tree height {height(root)}, balance everywhere in "
                 f"[-1, +1]", fresh=root)

    for v in [30, 20, 10, 40, 50, 25]:
        insert(v)
    out[-1]["done"] = True
    return out


AVL_C = r'''#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int key, height;
    struct Node *left, *right;
} Node;

int height(Node *n) { return n ? n->height : 0; }

int maxi(int a, int b) { return a > b ? a : b; }

Node *new_node(int key) {
    Node *n = (Node *)malloc(sizeof(Node));
    n->key = key;
    n->height = 1;
    n->left = n->right = NULL;
    return n;
}

void update(Node *n) { n->height = 1 + maxi(height(n->left), height(n->right)); }

int balance(Node *n) { return n ? height(n->left) - height(n->right) : 0; }

Node *rotate_right(Node *y) {
    Node *x = y->left;
    Node *b = x->right;
    x->right = y;
    y->left = b;
    update(y);
    update(x);
    return x;
}

Node *rotate_left(Node *x) {
    Node *y = x->right;
    Node *b = y->left;
    y->left = x;
    x->right = b;
    update(x);
    update(y);
    return y;
}

/* BST insert, then rebalance every node on the way back up. */
Node *insert(Node *node, int key) {
    if (!node) return new_node(key);
    if (key < node->key)      node->left  = insert(node->left, key);
    else if (key > node->key) node->right = insert(node->right, key);
    else return node;                          /* no duplicates */

    update(node);
    int b = balance(node);

    if (b > 1 && key < node->left->key)        /* LL */
        return rotate_right(node);
    if (b > 1) {                               /* LR */
        node->left = rotate_left(node->left);
        return rotate_right(node);
    }
    if (b < -1 && key > node->right->key)      /* RR */
        return rotate_left(node);
    if (b < -1) {                              /* RL */
        node->right = rotate_right(node->right);
        return rotate_left(node);
    }
    return node;
}

void preorder(Node *r) {
    if (!r) return;
    printf("%d ", r->key);
    preorder(r->left);
    preorder(r->right);
}

void inorder(Node *r) {
    if (!r) return;
    inorder(r->left);
    printf("%d ", r->key);
    inorder(r->right);
}

void free_tree(Node *r) {
    if (!r) return;
    free_tree(r->left);
    free_tree(r->right);
    free(r);
}

int main(void) {
    Node *t1 = NULL;
    int vals[] = {30, 20, 10, 40, 50, 25};
    for (int i = 0; i < 6; i++) t1 = insert(t1, vals[i]);
    printf("Test 1 (preorder after 30 20 10 40 50 25): ");
    preorder(t1); printf("\n");
    printf("Test 2 (inorder, must be sorted):          ");
    inorder(t1); printf("\n");
    printf("Test 3 (root key): %d\n", t1->key);

    Node *t2 = NULL;
    for (int i = 1; i <= 7; i++) t2 = insert(t2, i);  /* forces rebalances */
    printf("Test 4 (preorder after inserting 1..7):    ");
    preorder(t2); printf("\n");
    printf("Test 5 (height of 7-node AVL): %d\n", height(t2));
    free_tree(t1);
    free_tree(t2);
    return 0;
}
'''


AVL_CPP = r'''#include <iostream>
using namespace std;

struct Node {
    int key, height;
    Node *left, *right;
    explicit Node(int k) : key(k), height(1), left(nullptr), right(nullptr) {}
};

int height(Node* n) { return n ? n->height : 0; }

void update(Node* n) { n->height = 1 + max(height(n->left), height(n->right)); }

int balance(Node* n) { return n ? height(n->left) - height(n->right) : 0; }

Node* rotateRight(Node* y) {
    Node* x = y->left;
    Node* b = x->right;
    x->right = y;
    y->left = b;
    update(y);
    update(x);
    return x;
}

Node* rotateLeft(Node* x) {
    Node* y = x->right;
    Node* b = y->left;
    y->left = x;
    x->right = b;
    update(x);
    update(y);
    return y;
}

/* BST insert, then rebalance every node on the way back up. */
Node* insert(Node* node, int key) {
    if (!node) return new Node(key);
    if (key < node->key)      node->left  = insert(node->left, key);
    else if (key > node->key) node->right = insert(node->right, key);
    else return node;                          /* no duplicates */

    update(node);
    int b = balance(node);

    if (b > 1 && key < node->left->key)        /* LL */
        return rotateRight(node);
    if (b > 1) {                               /* LR */
        node->left = rotateLeft(node->left);
        return rotateRight(node);
    }
    if (b < -1 && key > node->right->key)      /* RR */
        return rotateLeft(node);
    if (b < -1) {                              /* RL */
        node->right = rotateRight(node->right);
        return rotateLeft(node);
    }
    return node;
}

void preorder(Node* r) {
    if (!r) return;
    cout << r->key << " ";
    preorder(r->left);
    preorder(r->right);
}

void inorder(Node* r) {
    if (!r) return;
    inorder(r->left);
    cout << r->key << " ";
    inorder(r->right);
}

int main() {
    Node* t1 = nullptr;
    for (int v : {30, 20, 10, 40, 50, 25}) t1 = insert(t1, v);
    cout << "Test 1 (preorder after 30 20 10 40 50 25): ";
    preorder(t1); cout << "\n";
    cout << "Test 2 (inorder, must be sorted):          ";
    inorder(t1); cout << "\n";
    cout << "Test 3 (root key): " << t1->key << "\n";

    Node* t2 = nullptr;
    for (int i = 1; i <= 7; i++) t2 = insert(t2, i);  /* forces rebalances */
    cout << "Test 4 (preorder after inserting 1..7):    ";
    preorder(t2); cout << "\n";
    cout << "Test 5 (height of 7-node AVL): " << height(t2) << "\n";
    return 0;
}
'''


AVL_PY = r'''class Node:
    def __init__(self, key):
        self.key = key
        self.height = 1
        self.left = None
        self.right = None


def height(n):
    return n.height if n else 0


def update(n):
    n.height = 1 + max(height(n.left), height(n.right))


def balance(n):
    return height(n.left) - height(n.right) if n else 0


def rotate_right(y):
    x = y.left
    b = x.right
    x.right = y
    y.left = b
    update(y)
    update(x)
    return x


def rotate_left(x):
    y = x.right
    b = y.left
    y.left = x
    x.right = b
    update(x)
    update(y)
    return y


def insert(node, key):
    """BST insert, then rebalance every node on the way back up."""
    if node is None:
        return Node(key)
    if key < node.key:
        node.left = insert(node.left, key)
    elif key > node.key:
        node.right = insert(node.right, key)
    else:
        return node                      # no duplicates

    update(node)
    b = balance(node)

    if b > 1 and key < node.left.key:            # LL
        return rotate_right(node)
    if b > 1:                                    # LR
        node.left = rotate_left(node.left)
        return rotate_right(node)
    if b < -1 and key > node.right.key:          # RR
        return rotate_left(node)
    if b < -1:                                   # RL
        node.right = rotate_right(node.right)
        return rotate_left(node)
    return node


def preorder(r):
    if r is None:
        return []
    return [r.key] + preorder(r.left) + preorder(r.right)


def inorder(r):
    if r is None:
        return []
    return inorder(r.left) + [r.key] + inorder(r.right)


if __name__ == "__main__":
    t1 = None
    for v in (30, 20, 10, 40, 50, 25):
        t1 = insert(t1, v)
    print(f"Test 1 (preorder after 30 20 10 40 50 25): {' '.join(map(str, preorder(t1)))}")
    print(f"Test 2 (inorder, must be sorted):          {' '.join(map(str, inorder(t1)))}")
    print(f"Test 3 (root key): {t1.key}")

    t2 = None
    for i in range(1, 8):
        t2 = insert(t2, i)                       # forces rebalances
    print(f"Test 4 (preorder after inserting 1..7):    {' '.join(map(str, preorder(t2)))}")
    print(f"Test 5 (height of 7-node AVL): {height(t2)}")
'''
TOPIC_AVL = {
    "id": "avl-tree",
    "name": "AVL Tree",
    "slug": "avl-tree",
    "type": "tree",
    "type_label": TYPES["tree"]["label"],
    "type_icon": TYPES["tree"]["icon"],
    "priority": 4,
    "difficulty": "Hard",
    "icon": "⚖️",
    "kind": "tree",
    "complexity": {
        "best": "O(log n) search / insert / delete",
        "average": "O(log n)",
        "worst": "O(log n) — guaranteed by strict balancing",
        "space": "O(n) nodes + O(log n) recursion",
        "stable": "n/a",
        "in_place": "Mutates the tree in place",
    },
    "what": (
        "An AVL tree is a self-balancing binary search tree: after every insertion or deletion it checks "
        "each ancestor's balance factor (left height minus right height) and, whenever the factor leaves "
        "[-1, +1], repairs the shape with local rotations. The four imbalance cases (LL, RR, LR, RL) map "
        "to a single or a double rotation, keeping the height within about 1.44 log n at all times."
    ),
    "why": (
        "A plain BST gives O(log n) lookups only for well-shaped input — insert sorted keys and it "
        "collapses into a linked list with O(n) operations. AVL removes that risk deterministically: "
        "worst-case logarithmic operations without amortisation or randomness, which is exactly what "
        "lookup-heavy workloads such as indexes and language runtimes need."
    ),
    "when_needed": [
        "Read-heavy workloads: many lookups, few updates — AVL's stricter balance beats Red-Black's.",
        "Worst-case latency matters (real-time-ish queries over dynamic sorted data).",
        "Ordered iteration, successor/predecessor queries, or range scans between updates.",
        "Teaching or implementing balanced trees from first principles.",
    ],
    "how_to_select": [
        "Need guaranteed O(log n) with simple code? AVL — rotations are easier to reason about than Red-Black rules.",
        "Write-heavy mixed workload? Red-Black (fewer rotations per update) or a B-tree for disk locality.",
        "Keys arrive nearly sorted? AVL immediately rebalances where a plain BST degenerates.",
        "Need ordered statistics (rank/select)? Augment nodes with subtree sizes while rotating.",
        "For pure key-value lookups without order needs, hash tables are O(1) average — no balancing needed.",
    ],
    "when_not": [
        "Write-heavy or append-only workloads — Red-Black trees rebalance less often.",
        "Data lives on disk — B-trees match the page structure and cut I/O.",
        "Only dictionary-style lookups — a hash table is simpler and faster on average.",
        "The dataset is tiny or static — a sorted array with binary search wins on simplicity.",
    ],
    "outline": [
        "Balance factor = height(left) - height(right), kept in [-1, +1]",
        "Insert as in BST, then retrace upward updating heights",
        "LL and RR cases fix with one rotation; LR and RL with a double rotation",
        "Rotations are O(1) pointer changes that restore BST order and balance",
        "Height stays <= 1.44 log n, so every operation is worst-case O(log n)",
    ],
    "applications": [
        {"title": "In-memory indexes", "detail": "Databases and file systems use AVL-style balancing for in-memory ordered indexes (on-disk cousins are B-trees)."},
        {"title": "Language runtimes", "detail": "Ordered maps and interval structures in runtime libraries rely on balanced BSTs; AVL is the reference design."},
        {"title": "Network routing tables", "detail": "Longest-prefix lookups over sorted ranges use balanced trees to keep worst-case lookup time bounded."},
        {"title": "Computational geometry", "detail": "Sweep-line algorithms store active events in a balanced tree; AVL guarantees the O(log n) per-event cost."},
    ],
    "impl_c": AVL_C,
    "impl_cpp": AVL_CPP,
    "impl_py": AVL_PY,
    "sim": sim_avl,
    "references": [
        {"title": "GeeksforGeeks — AVL Tree (reference)", "url": "https://www.geeksforgeeks.org/introduction-to-avl-tree/"},
    ],
}


# ---------------------------------------------------------------------------
# Topic: LCA & Tree Diameter
# ---------------------------------------------------------------------------

def sim_lca_diameter():
    """Trace LCA by parent climbing and the two-pass diameter (tree renderer)."""
    edges = [(1, 2), (1, 3), (2, 4), (2, 5), (3, 6), (3, 7), (4, 8), (4, 9), (6, 10)]
    parent = {1: None}
    depth = {}
    for u, v in edges:
        parent[v] = u
    order = list(range(1, 11))

    def set_depth(v, d):
        depth[v] = d
        for u, w in edges:
            if u == v:
                set_depth(w, d + 1)
    set_depth(1, 0)

    out = []

    def emit(caption, path_nodes=(), cur=None, fresh=None, done=False):
        tree = []
        for v in order:
            st = "normal"
            if v in path_nodes:
                st = "path"
            if cur == v:
                st = "current"
            if fresh == v:
                st = "frontier"
            tree.append({"id": v, "value": v, "parent": parent[v], "state": st})
        out.append({"kind": "tree", "tree": tree, "caption": caption, "done": done})

    def climb(v):
        """Nodes from v up to the root."""
        p = []
        while v is not None:
            p.append(v)
            v = parent[v]
        return p

    emit("A tree with 11 nodes — goal 1: the lowest common ancestor of 8 and 9")
    up8 = climb(8)                       # [8, 4, 2, 1]
    seen8 = []
    for v in up8:
        seen8.append(v)
        emit(f"Climb from 8 toward the root — at node {v}", tuple(seen8), cur=v)
    marked = set(seen8)
    up9 = climb(9)                       # [9, 4, 2, 1]
    seen9 = []
    lca_found = None
    for v in up9:
        seen9.append(v)
        both = tuple(set(seen8) | set(seen9))
        if v in marked:
            emit(f"Climb from 9 — node {v} is already on 8's path -> LCA(8, 9) = {v}",
                 both, cur=v, fresh=v)
            lca_found = v
            break
        emit(f"Climb from 9 toward the root — node {v} is not on 8's path yet", both, cur=v)
    emit(f"LCA(8, 9) = {lca_found} — the deepest node both climbs share",
         tuple(set(seen8) | set(seen9)), fresh=lca_found)

    emit("Goal 2: the diameter — the longest path between any two nodes", ())
    a = 8
    emit(f"DFS from the root shows depth 3 is deepest — start from a deepest leaf: "
         f"node {a} (any of 8, 9, 10 works)", (a,), fresh=a)
    full = climb(10) + list(reversed(climb(a)))[1:]   # [10,6,3,1,2,4,8]
    b = full[0]
    emit(f"DFS from node {a}: the farthest node is {b}, {len(full) - 1} edges away — "
         f"that distance IS the diameter", tuple(full), fresh=b)
    for i, v in enumerate(full):
        emit(f"Walk the diameter path — node {v}", tuple(full[:i + 1]), cur=v)
    emit("Diameter = 6 edges — the path 10-6-3-1-2-4-8", tuple(full), done=True)
    return out


LCA_C = r'''#include <stdio.h>

#define N 12   /* nodes 1..11 */

int adj[N][N], deg[N];
int parent[N], depth[N];
int far_node = 1, far_dist = -1;

void add_edge(int u, int v) { adj[u][deg[u]++] = v; }

void dfs(int u, int p, int d) {
    parent[u] = p;
    depth[u] = d;
    if (d > far_dist) { far_dist = d; far_node = u; }
    for (int i = 0; i < deg[u]; i++) {
        int v = adj[u][i];
        if (v != p) dfs(v, u, d + 1);
    }
}

/* LCA by equalising depths, then climbing both nodes together. O(h). */
int lca(int u, int v) {
    while (depth[u] > depth[v]) u = parent[u];
    while (depth[v] > depth[u]) v = parent[v];
    while (u != v) { u = parent[u]; v = parent[v]; }
    return u;
}

int dist(int u, int v) {
    int w = lca(u, v);
    return depth[u] + depth[v] - 2 * depth[w];
}

int main(void) {
    int edges[][2] = {{1,2},{1,3},{2,4},{2,5},{3,6},{3,7},{4,8},{4,9},{6,10}};
    for (int i = 0; i < 9; i++) { add_edge(edges[i][0], edges[i][1]); add_edge(edges[i][1], edges[i][0]); }

    far_dist = -1; far_node = 1;
    dfs(1, 0, 0);
    printf("Test 1 (LCA of 8 and 9): %d\n", lca(8, 9));
    printf("Test 2 (LCA of 8 and 10): %d\n", lca(8, 10));
    printf("Test 3 (LCA of 5 and 7): %d\n", lca(5, 7));
    printf("Test 4 (distance 8 to 10): %d\n", dist(8, 10));

    /* Diameter: farthest node a from the root, then farthest b from a. */
    int a = far_node;
    far_dist = -1;
    dfs(a, 0, 0);
    int b = far_node;
    printf("Test 5 (diameter endpoints): %d %d\n", a, b);
    printf("Test 6 (diameter in edges): %d\n", far_dist);
    printf("Test 7 (path from %d to %d):", b, a);
    for (int x = b; x != 0; x = parent[x]) printf(" %d", x);
    printf("\n");
    return 0;
}
'''


LCA_CPP = r'''#include <iostream>
#include <vector>
using namespace std;

vector<vector<int>> adj;
vector<int> parent_, depth_;
int farNode = 1, farDist = -1;

void dfs(int u, int p, int d) {
    parent_[u] = p;
    depth_[u] = d;
    if (d > farDist) { farDist = d; farNode = u; }
    for (int v : adj[u])
        if (v != p) dfs(v, u, d + 1);
}

/* LCA by equalising depths, then climbing both nodes together. O(h). */
int lca(int u, int v) {
    while (depth_[u] > depth_[v]) u = parent_[u];
    while (depth_[v] > depth_[u]) v = parent_[v];
    while (u != v) { u = parent_[u]; v = parent_[v]; }
    return u;
}

int dist(int u, int v) {
    int w = lca(u, v);
    return depth_[u] + depth_[v] - 2 * depth_[w];
}

int main() {
    int n = 11;
    adj.assign(n, {});
    parent_.assign(n, 0);
    depth_.assign(n, 0);
    int edges[][2] = {{1,2},{1,3},{2,4},{2,5},{3,6},{3,7},{4,8},{4,9},{6,10}};
    for (auto& e : edges) { adj[e[0]].push_back(e[1]); adj[e[1]].push_back(e[0]); }

    farDist = -1; farNode = 1;
    dfs(1, 0, 0);
    cout << "Test 1 (LCA of 8 and 9): " << lca(8, 9) << "\n";
    cout << "Test 2 (LCA of 8 and 10): " << lca(8, 10) << "\n";
    cout << "Test 3 (LCA of 5 and 7): " << lca(5, 7) << "\n";
    cout << "Test 4 (distance 8 to 10): " << dist(8, 10) << "\n";

    /* Diameter: farthest node a from the root, then farthest b from a. */
    int a = farNode;
    farDist = -1;
    dfs(a, 0, 0);
    int b = farNode;
    cout << "Test 5 (diameter endpoints): " << a << " " << b << "\n";
    cout << "Test 6 (diameter in edges): " << farDist << "\n";
    cout << "Test 7 (path from " << b << " to " << a << "):";
    for (int x = b; x != 0; x = parent_[x]) cout << " " << x;
    cout << "\n";
    return 0;
}
'''


LCA_PY = r'''import sys
from collections import defaultdict

sys.setrecursionlimit(10000)


def build(n, edges):
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    return adj


def dfs(adj, parent, depth, u, p, d, far):
    parent[u] = p
    depth[u] = d
    if d > far[1]:
        far[0], far[1] = u, d
    for v in adj[u]:
        if v != p:
            dfs(adj, parent, depth, v, u, d + 1, far)


def lca(parent, depth, u, v):
    """Equalise depths, then climb both nodes together. O(h)."""
    while depth[u] > depth[v]:
        u = parent[u]
    while depth[v] > depth[u]:
        v = parent[v]
    while u != v:
        u, v = parent[u], parent[v]
    return u


def dist(parent, depth, u, v):
    w = lca(parent, depth, u, v)
    return depth[u] + depth[v] - 2 * depth[w]


if __name__ == "__main__":
    n = 11
    edges = [(1, 2), (1, 3), (2, 4), (2, 5), (3, 6), (3, 7), (4, 8), (4, 9), (6, 10)]
    adj = build(n, edges)
    parent = {1: 0}
    depth = {}
    far = [1, -1]                       # [farthest node, its distance]
    dfs(adj, parent, depth, 1, 0, 0, far)

    print(f"Test 1 (LCA of 8 and 9): {lca(parent, depth, 8, 9)}")
    print(f"Test 2 (LCA of 8 and 10): {lca(parent, depth, 8, 10)}")
    print(f"Test 3 (LCA of 5 and 7): {lca(parent, depth, 5, 7)}")
    print(f"Test 4 (distance 8 to 10): {dist(parent, depth, 8, 10)}")

    # Diameter: farthest node a from the root, then farthest b from a.
    a = far[0]
    far[0], far[1] = 1, -1
    dfs(adj, parent, depth, a, 0, 0, far)
    b = far[0]
    print(f"Test 5 (diameter endpoints): {a} {b}")
    print(f"Test 6 (diameter in edges): {far[1]}")
    path = []
    x = b
    while x != 0:
        path.append(x)
        x = parent[x]
    print(f"Test 7 (path from {b} to {a}): " + " ".join(map(str, path)))
'''
TOPIC_LCA = {
    "id": "lca-tree-diameter",
    "name": "LCA & Tree Diameter",
    "slug": "lca-tree-diameter",
    "type": "tree",
    "type_label": TYPES["tree"]["label"],
    "type_icon": TYPES["tree"]["icon"],
    "priority": 4,
    "difficulty": "Medium",
    "icon": "🧬",
    "kind": "tree",
    "complexity": {
        "best": "O(h) per LCA query (parent climbing)",
        "average": "O(h) per query",
        "worst": "O(n) per query on a chain; O(n) preprocessing per DFS run",
        "space": "O(n) parent/depth tables",
        "stable": "n/a",
        "in_place": "n/a",
    },
    "what": (
        "Two classic tree workhorses. The lowest common ancestor (LCA) of two nodes is the deepest node "
        "that has both as descendants — found here by equalising depths and climbing both nodes upward "
        "in lockstep. The diameter is the length of the longest path between any two nodes, computed by "
        "the two-DFS trick: the farthest node from any starting point is always a diameter endpoint, so "
        "one DFS finds an endpoint and a second DFS from it measures the path."
    ),
    "why": (
        "LCA is the hub of tree queries: distance between any two nodes is depth[u] + depth[v] − "
        "2·depth[LCA], which makes it the base for routing in hierarchies, org-chart questions, and "
        "phylogenetic trees. The two-DFS diameter is a one-minute algorithm with a subtle one-line proof, "
        "and both routines train the parent/depth-table thinking that binary lifting generalises."
    ),
    "when_needed": [
        "Any 'distance or relationship between two nodes in a tree' question starts with the LCA.",
        "Distance queries repeated many times — compute LCA per query, or upgrade to binary lifting.",
        "The longest chain of dependencies or widest spread in a hierarchy — the diameter.",
        "Network design: a tree's diameter bounds worst-case latency between any two hosts.",
    ],
    "how_to_select": [
        "A few queries on a static tree: parent tables + O(h) climbing is simplest.",
        "Many queries: preprocess binary lifting in O(n log n), then each LCA is O(log n).",
        "Dynamic trees with updates need link-cut trees — a different (heavy) toolbox.",
        "For the diameter, the two-DFS method is O(n); the alternative single-DFS DP on children works when you also need the path.",
        "Always run DFS from a known root and store parent/depth in one pass — it feeds every other routine.",
    ],
    "when_not": [
        "The graph has cycles — it is no longer a tree; LCA is undefined and BFS/DFS distances apply instead.",
        "Only one distance is ever needed — a single DFS/BFS from u to v is cheaper than LCA machinery.",
        "Nodes are updated (insertions/deletions) between queries — parent tables go stale; use an LCT or rebuild.",
        "You need the diameter PATH, not just its length — carry parent tables and reconstruct, as the code does.",
    ],
    "outline": [
        "One DFS from the root fills parent[] and depth[] for every node",
        "LCA: lift the deeper node, then climb both together until they meet — O(h)",
        "Distance(u, v) = depth[u] + depth[v] − 2·depth[LCA]",
        "Diameter endpoint: the farthest node from any start is always an endpoint",
        "Second DFS from that endpoint measures the diameter and parent[] rebuilds the path",
        "Binary lifting = the same climbing precomputed in O(n log n) for O(log n) queries",
    ],
    "applications": [
        {"title": "Organisation and taxonomy hierarchies", "detail": "Reporting lines, species classification, and product categories all ask 'closest common parent' questions."},
        {"title": "Network routing on tree topologies", "detail": "Spanning-tree LANs and hierarchical networks use LCA to route between branches; diameter bounds latency."},
        {"title": "Version control", "detail": "Git merges compute the best common ancestor of two commits — an LCA query on the commit DAG's spanning structure."},
        {"title": "Distributed systems", "detail": "Overlay networks size their worst-case message hops by the diameter of the topology tree."},
    ],
    "impl_c": LCA_C,
    "impl_cpp": LCA_CPP,
    "impl_py": LCA_PY,
    "sim": sim_lca_diameter,
    "references": [
        {"title": "GeeksforGeeks — Lowest Common Ancestor in a Binary Tree (reference)", "url": "https://www.geeksforgeeks.org/lowest-common-ancestor-binary-tree-set-1/"},
        {"title": "GeeksforGeeks — Diameter of a Binary Tree (reference)", "url": "https://www.geeksforgeeks.org/diameter-of-a-binary-tree/"},
    ],
}


# ---------------------------------------------------------------------------
# Topic: BFS & DFS Traversals
# ---------------------------------------------------------------------------

def sim_bfs_dfs():
    """Trace BFS then DFS on the same undirected graph (graph renderer)."""
    edges = [("A", "B"), ("A", "C"), ("B", "D"), ("C", "E"), ("C", "F"), ("E", "G")]
    coords = {"A": (0.5, 0.1), "B": (0.3, 0.45), "C": (0.7, 0.45),
              "D": (0.2, 0.8), "E": (0.6, 0.8), "F": (0.85, 0.8), "G": (0.45, 1.0)}
    order = ["A", "B", "C", "D", "E", "F", "G"]
    neighbors = {}
    for u, v in edges:
        neighbors.setdefault(u, []).append(v)
        neighbors.setdefault(v, []).append(u)

    out = []

    def emit(caption, visited, frontier, current, edge_state=None, done=False):
        nodes = []
        for v in order:
            st = "unvisited"
            if v in visited:
                st = "done"
            if v in frontier:
                st = "frontier"
            if v == current:
                st = "current"
            nodes.append({"id": v, "value": v, "pos": coords[v], "state": st})
        es = {}
        if edge_state:
            for key, lst in edge_state.items():
                for e in lst:
                    es[frozenset(e)] = key
        edges_out = [{"u": u, "v": w, "state": es.get(frozenset((u, w)), "normal")}
                     for u, w in edges]
        out.append({"kind": "graph", "nodes": nodes, "edges": edges_out,
                    "directed": False, "weighted": False,
                    "caption": caption, "done": done})

    visited, frontier = set(), []
    queue = ["A"]
    emit("BFS from A — a queue explores level by level", visited, [], None)
    while queue:
        cur = queue.pop(0)
        if cur in visited:
            continue
        visited.add(cur)
        new = [w for w in sorted(neighbors[cur]) if w not in visited and w not in queue]
        queue.extend(new)
        emit(f"BFS visits {cur}; its unvisited neighbors {new} join the queue",
             visited, [w for w in queue if w not in visited], cur,
             {"path": [(u, v) for u, v in edges if u in visited or v in visited]})
    emit("BFS order: A, B, C, D, E, F, G — every node reached by fewest edges from A",
         visited, [], None, done=True)

    visited2, stack = set(), ["A"]
    tree_edges = []
    emit("Now DFS from A — a stack dives deep before backtracking", set(), [], None)
    while stack:
        cur = stack.pop()
        if cur in visited2:
            continue
        visited2.add(cur)
        fresh = [w for w in sorted(neighbors[cur], reverse=True) if w not in visited2]
        for w in fresh:
            tree_edges.append((cur, w))
        stack.extend(reversed(fresh))
        emit(f"DFS visits {cur}; pushes {list(reversed(fresh))} onto the stack",
             visited2, [w for w in stack if w not in visited2], cur,
             {"path": tree_edges})
    emit("DFS order: A, B, D, C, E, G, F — one path explored to its end before the next",
         visited2, [], None, {"path": tree_edges}, done=True)
    return out


BFS_DFS_C = r'''#include <stdio.h>

#define N 7

/* Graph as an adjacency matrix; nodes are indices 0..6 (A..G). */
int adj[N][N] = {
    {0,1,1,0,0,0,0},
    {1,0,0,1,0,0,0},
    {1,0,0,0,1,1,0},
    {0,1,0,0,0,0,0},
    {0,0,1,0,0,0,1},
    {0,0,1,0,0,0,0},
    {0,0,0,0,1,0,0},
};
const char *name = "ABCDEFG";

void bfs(int start) {
    int visited[N] = {0}, queue[N], head = 0, tail = 0;
    queue[tail++] = start;
    visited[start] = 1;
    printf("BFS: ");
    while (head < tail) {
        int u = queue[head++];
        printf("%c ", name[u]);
        for (int v = 0; v < N; v++)
            if (adj[u][v] && !visited[v]) { visited[v] = 1; queue[tail++] = v; }
    }
    printf("\n");
}

void dfs_rec(int u, int visited[]) {
    visited[u] = 1;
    printf("%c ", name[u]);
    for (int v = 0; v < N; v++)
        if (adj[u][v] && !visited[v]) dfs_rec(v, visited);
}

void dfs(int start) {
    int visited[N] = {0};
    printf("DFS: ");
    dfs_rec(start, visited);
    printf("\n");
}

/* Connected components: restart a BFS from every unvisited node. */
int count_components(void) {
    int visited[N] = {0}, count = 0;
    for (int s = 0; s < N; s++) {
        if (!visited[s]) {
            count++;
            int queue[N], head = 0, tail = 0;
            queue[tail++] = s;
            visited[s] = 1;
            while (head < tail) {
                int u = queue[head++];
                for (int v = 0; v < N; v++)
                    if (adj[u][v] && !visited[v]) { visited[v] = 1; queue[tail++] = v; }
            }
        }
    }
    return count;
}

int main(void) {
    bfs(0);          /* from A */
    dfs(0);          /* from A */
    bfs(3);          /* from D */
    dfs(4);          /* from E */
    printf("Components: %d\n", count_components());
    return 0;
}
'''


BFS_DFS_CPP = r'''#include <iostream>
#include <vector>
using namespace std;

vector<vector<int>> adj = {
    {0,1,1,0,0,0,0}, {1,0,0,1,0,0,0}, {1,0,0,0,1,1,0}, {0,1,0,0,0,0,0},
    {0,0,1,0,0,0,1}, {0,0,1,0,0,0,0}, {0,0,0,0,1,0,0},
};
const string name = "ABCDEFG";

void bfs(int start) {
    vector<bool> visited(adj.size(), false);
    vector<int> queue{start};
    visited[start] = true;
    cout << "BFS: ";
    for (size_t head = 0; head < queue.size(); head++) {
        int u = queue[head];
        cout << name[u] << " ";
        for (int v = 0; v < (int)adj.size(); v++)
            if (adj[u][v] && !visited[v]) { visited[v] = true; queue.push_back(v); }
    }
    cout << "\n";
}

void dfsRec(int u, vector<bool>& visited) {
    visited[u] = true;
    cout << name[u] << " ";
    for (int v = 0; v < (int)adj.size(); v++)
        if (adj[u][v] && !visited[v]) dfsRec(v, visited);
}

void dfs(int start) {
    vector<bool> visited(adj.size(), false);
    cout << "DFS: ";
    dfsRec(start, visited);
    cout << "\n";
}

/* Connected components: restart a BFS from every unvisited node. */
int countComponents() {
    vector<bool> visited(adj.size(), false);
    int count = 0;
    for (int s = 0; s < (int)adj.size(); s++) {
        if (!visited[s]) {
            count++;
            vector<int> queue{s};
            visited[s] = true;
            for (size_t head = 0; head < queue.size(); head++) {
                int u = queue[head];
                for (int v = 0; v < (int)adj.size(); v++)
                    if (adj[u][v] && !visited[v]) { visited[v] = true; queue.push_back(v); }
            }
        }
    }
    return count;
}

int main() {
    bfs(0);
    dfs(0);
    bfs(3);
    dfs(4);
    cout << "Components: " << countComponents() << "\n";
    return 0;
}
'''


BFS_DFS_PY = r'''from collections import deque

ADJ = {
    "A": ["B", "C"], "B": ["A", "D"], "C": ["A", "E", "F"],
    "D": ["B"], "E": ["C", "G"], "F": ["C"], "G": ["E"],
}


def bfs(start):
    visited = {start}
    queue = deque([start])
    order = []
    while queue:
        u = queue.popleft()
        order.append(u)
        for v in ADJ[u]:
            if v not in visited:
                visited.add(v)
                queue.append(v)
    return order


def dfs(start, visited=None, order=None):
    """Recursive depth-first: mark, visit, then dive into each neighbor."""
    if visited is None:
        visited, order = set(), []
    visited.add(start)
    order.append(start)
    for v in ADJ[start]:
        if v not in visited:
            dfs(v, visited, order)
    return order


def components(nodes):
    """Number of connected pieces — run BFS from every unvisited node."""
    seen, count = set(), 0
    for s in nodes:
        if s not in seen:
            count += 1
            seen.update(bfs(s))
    return count


if __name__ == "__main__":
    print("BFS:", " ".join(bfs("A")))
    print("DFS:", " ".join(dfs("A")))
    print("BFS:", " ".join(bfs("D")))
    print("DFS:", " ".join(dfs("E")))
    print("Components:", components(list(ADJ)))
'''
TOPIC_BFS_DFS = {
    "id": "bfs-dfs",
    "name": "BFS & DFS Traversals",
    "slug": "bfs-dfs",
    "type": "graph",
    "type_label": TYPES["graph"]["label"],
    "type_icon": TYPES["graph"]["icon"],
    "priority": 5,
    "difficulty": "Medium",
    "icon": "🕸️",
    "kind": "graph",
    "complexity": {
        "best": "O(V + E) — every vertex and edge touched once",
        "average": "O(V + E)",
        "worst": "O(V + E)",
        "space": "O(V) visited flags + O(V) queue (BFS) or recursion stack (DFS)",
        "stable": "n/a",
        "in_place": "n/a",
    },
    "what": (
        "The two fundamental ways to walk a graph. Breadth-first search (BFS) uses a queue and explores "
        "in rings: everything 1 edge away, then 2 edges, and so on — so the first time it reaches a node "
        "is along a fewest-edges path. Depth-first search (DFS) uses a stack (or recursion) and follows "
        "one path as deep as it can before backtracking. Both visit each vertex and edge once."
    ),
    "why": (
        "Almost every graph algorithm is one of these two skeletons with extra bookkeeping: Dijkstra is "
        "BFS with a priority queue, topological sort is DFS with a finish-time stack, cycle detection and "
        "component counting are plain DFS/BFS loops. Mastery here is the entry fee to all of graph theory."
    ),
    "when_needed": [
        "Shortest path in unweighted graphs (fewest edges) — BFS, or multi-source BFS.",
        "Connectivity questions: is there a path, how many components, is it bipartite — either search.",
        "Cycle detection (directed via DFS colours, undirected via a parent check).",
        "Ordering/structure probes — DFS trees expose bridges, articulation points, topological order.",
    ],
    "how_to_select": [
        "Distance-like answers (levels, fewest hops, nearest exit) → BFS.",
        "Exhaustive structure questions (cycles, topological order, back-edges) → DFS.",
        "Very deep graphs risk recursion overflow — use an explicit stack or BFS.",
        "Huge width, deep answer — DFS keeps the frontier small; BFS memory can explode.",
        "Mark nodes visited when ENQUEUED (BFS) or on entry (DFS) to avoid duplicates.",
    ],
    "when_not": [
        "Weighted shortest paths — plain BFS ignores weights; use Dijkstra or Bellman-Ford.",
        "Needless full traversal when a single path suffices — early-exit the search at the target.",
        "The graph is a tree with a known root and you only need parent/depth — one DFS suffices (no queue).",
        "Streaming graphs that change between queries — static traversals go stale; use dynamic structures.",
    ],
    "outline": [
        "BFS: queue + visited set; pops front, pushes unvisited neighbors — level by level",
        "DFS: recursion/stack; dives into one neighbor fully before trying the next",
        "Both are O(V + E) time, O(V) extra space with adjacency lists",
        "BFS gives fewest-edge paths in unweighted graphs; DFS exposes cycles and order",
        "Connected components: loop the search from every unvisited node",
        "Multi-source BFS: seed the queue with several starts at once",
    ],
    "applications": [
        {"title": "Social networks", "detail": "'Degrees of separation' and friend suggestions are BFS rings; community crawls use DFS."},
        {"title": "Web crawling and indexing", "detail": "Crawlers are bounded BFS over links; site audits DFS the link tree for broken paths."},
        {"title": "Mazes, puzzles and games", "detail": "Minimum-move puzzle solutions are BFS; walkthrough generation and cycle checks use DFS."},
        {"title": "Garbage collection", "detail": "Tracing collectors reachability-scan the object graph — exactly a graph traversal from roots."},
    ],
    "impl_c": BFS_DFS_C,
    "impl_cpp": BFS_DFS_CPP,
    "impl_py": BFS_DFS_PY,
    "sim": sim_bfs_dfs,
    "references": [
        {"title": "GeeksforGeeks — Breadth First Search (reference)", "url": "https://www.geeksforgeeks.org/breadth-first-search-or-bfs-for-a-graph/"},
        {"title": "GeeksforGeeks — Depth First Search (reference)", "url": "https://www.geeksforgeeks.org/depth-first-search-or-dfs-for-a-graph/"},
    ],
}


# ---------------------------------------------------------------------------
# Topic: Bellman-Ford & Floyd-Warshall
# ---------------------------------------------------------------------------

def sim_bellman_floyd():
    """Trace Bellman-Ford edge relaxations, then a Floyd-Warshall matrix fill."""
    nodes = ["A", "B", "C", "D"]
    # (u, v, w) directed edges, including one negative edge, no negative cycle
    edges = [("A", "B", 4), ("A", "C", 5), ("B", "C", -3), ("C", "D", 2), ("B", "D", 7)]
    out = []

    def emit(caption, dist=None, table=None, cur=None, done=False):
        nds = []
        for v in nodes:
            st = "unvisited"
            if dist is not None and dist[v] < float("inf"):
                st = "frontier"
            if cur == v:
                st = "current"
            nds.append({"id": v, "value": "∞" if (dist is None or dist[v] == float("inf"))
                        else str(dist[v]), "pos": POS[v], "state": st})
        out.append({"kind": "graph", "nodes": nds,
                    "edges": [{"u": u, "v": w, "state": "normal",
                               "label": str(c)} for u, w, c in edges],
                    "directed": True, "weighted": True,
                    "table": table, "caption": caption, "done": done})

    POS = {"A": (0.5, 0.12), "B": (0.18, 0.5), "C": (0.82, 0.5), "D": (0.5, 0.88)}
    INF = float("inf")
    dist = {v: INF for v in nodes}
    dist["A"] = 0
    emit("Bellman-Ford from A — distances start at ∞ except the source", dist)
    for round_no in range(1, len(nodes)):
        changed = []
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                changed.append(f"{v}={dist[v]}")
                emit(f"Round {round_no}: relax edge {u}→{v} (weight {w}) — "
                     f"{dist[u]} + {w} beats the old value → dist[{v}] = {dist[v]}", dist, cur=v)
        if not changed:
            emit(f"Round {round_no}: nothing improved — all distances are final", dist)
            break
        emit(f"Round {round_no} done: {'; '.join(changed)}", dist)
    ok = all(dist[u] + w >= dist[v] for u, v, w in edges)
    emit(f"Final sweep: every edge already satisfies dist[u] + w ≥ dist[v] → "
         f"{'no negative cycle' if ok else 'NEGATIVE CYCLE DETECTED'}", dist, done=True)

    n = len(nodes)
    d = [[INF] * n for _ in range(n)]
    for i in range(n):
        d[i][i] = 0
    for u, v, w in edges:
        d[nodes.index(u)][nodes.index(v)] = w
    emit("Now Floyd-Warshall: all-pairs distances; the matrix starts as direct edges",
         table=[row[:] for row in d])

    def fmt(x):
        return "0" if x == 0 and i == j else ("∞" if x == INF else str(x))

    for k in range(n):
        for i in range(n):
            for j in range(n):
                if d[i][k] + d[k][j] < d[i][j]:
                    d[i][j] = d[i][k] + d[k][j]
        out.append({"kind": "graph", "nodes": [], "edges": [], "directed": True,
                    "weighted": True, "table": [row[:] for row in d],
                    "caption": f"Allow intermediate node {nodes[k]} through paths — "
                               f"matrix updated", "done": False})
    emit("Floyd-Warshall done — d[i][j] now holds every shortest path at once",
         table=[row[:] for row in d], done=True)
    return out


BELLMAN_FLOYD_C = r'''#include <stdio.h>

#define N 4
#define INF 99999

/* Directed weighted edges (includes a negative edge, no negative cycle). */
int edge_u[] = {0, 0, 1, 2, 1};
int edge_v[] = {1, 2, 2, 3, 3};
int edge_w[] = {4, 5, -3, 2, 7};
int E = 5;

void bellman_ford(int src, int dist[]) {
    for (int i = 0; i < N; i++) dist[i] = INF;
    dist[src] = 0;
    for (int round = 0; round < N - 1; round++)
        for (int e = 0; e < E; e++)
            if (dist[edge_u[e]] + edge_w[e] < dist[edge_v[e]])
                dist[edge_v[e]] = dist[edge_u[e]] + edge_w[e];
    for (int e = 0; e < E; e++)          /* negative-cycle detection sweep */
        if (dist[edge_u[e]] + edge_w[e] < dist[edge_v[e]]) {
            printf("negative cycle\n");
            return;
        }
}

void floyd_warshall(int d[][N]) {
    for (int k = 0; k < N; k++)
        for (int i = 0; i < N; i++)
            for (int j = 0; j < N; j++)
                /* skip infinite legs: INF + negative edge must not creep down */
                if (d[i][k] != INF && d[k][j] != INF &&
                    d[i][k] + d[k][j] < d[i][j])
                    d[i][j] = d[i][k] + d[k][j];
}

int main(void) {
    int dist[N];
    bellman_ford(0, dist);
    printf("Bellman-Ford from A:");
    for (int i = 0; i < N; i++) printf(" %c=%d", 'A' + i, dist[i]);
    printf("\n");

    int d[N][N];
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++)
            d[i][j] = (i == j) ? 0 : INF;
    for (int e = 0; e < E; e++) d[edge_u[e]][edge_v[e]] = edge_w[e];
    floyd_warshall(d);
    printf("Floyd-Warshall all-pairs:\n");
    for (int i = 0; i < N; i++) {
        printf("  ");
        for (int j = 0; j < N; j++) {
            if (d[i][j] >= INF) printf("  inf");
            else printf(" %3d", d[i][j]);
        }
        printf("\n");
    }
    return 0;
}
'''


BELLMAN_FLOYD_CPP = r'''#include <cstdio>
#include <vector>
using namespace std;

/* printf keeps the report format identical to the C build. */
const int N = 4;
const int INF = 99999;

int edge_u[] = {0, 0, 1, 2, 1};
int edge_v[] = {1, 2, 2, 3, 3};
int edge_w[] = {4, 5, -3, 2, 7};
const int E = 5;

void bellmanFord(int src, int dist[]) {
    for (int i = 0; i < N; i++) dist[i] = INF;
    dist[src] = 0;
    for (int round = 0; round < N - 1; round++)
        for (int e = 0; e < E; e++)
            if (dist[edge_u[e]] + edge_w[e] < dist[edge_v[e]])
                dist[edge_v[e]] = dist[edge_u[e]] + edge_w[e];
    for (int e = 0; e < E; e++)          /* negative-cycle detection sweep */
        if (dist[edge_u[e]] + edge_w[e] < dist[edge_v[e]]) {
            printf("negative cycle\n");
            return;
        }
}

void floydWarshall(int d[][N]) {
    for (int k = 0; k < N; k++)
        for (int i = 0; i < N; i++)
            for (int j = 0; j < N; j++)
                /* skip infinite legs: INF + negative edge must not creep down */
                if (d[i][k] != INF && d[k][j] != INF &&
                    d[i][k] + d[k][j] < d[i][j])
                    d[i][j] = d[i][k] + d[k][j];
}

int main() {
    int dist[N];
    bellmanFord(0, dist);
    printf("Bellman-Ford from A:");
    for (int i = 0; i < N; i++) printf(" %c=%d", 'A' + i, dist[i]);
    printf("\n");

    vector<vector<int>> d(N, vector<int>(N, INF));
    for (int i = 0; i < N; i++) d[i][i] = 0;
    for (int e = 0; e < E; e++) d[edge_u[e]][edge_v[e]] = edge_w[e];
    int mat[N][N];
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++) mat[i][j] = d[i][j];
    floydWarshall(mat);
    printf("Floyd-Warshall all-pairs:\n");
    for (int i = 0; i < N; i++) {
        printf("  ");
        for (int j = 0; j < N; j++) {
            if (mat[i][j] >= INF) printf("  inf");
            else printf(" %3d", mat[i][j]);
        }
        printf("\n");
    }
    return 0;
}
'''


BELLMAN_FLOYD_PY = r'''INF = float("inf")

# (u, v, w) directed edges — includes a negative edge, no negative cycle
EDGES = [("A", "B", 4), ("A", "C", 5), ("B", "C", -3), ("C", "D", 2), ("B", "D", 7)]
NODES = ["A", "B", "C", "D"]


def bellman_ford(src):
    """Relax every edge V-1 times; a further improving edge means a negative cycle."""
    dist = {v: INF for v in NODES}
    dist[src] = 0
    for _ in range(len(NODES) - 1):
        for u, v, w in EDGES:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    for u, v, w in EDGES:
        if dist[u] + w < dist[v]:
            print("negative cycle")
            return dist
    return dist


def floyd_warshall():
    """All-pairs shortest paths in O(V^3) with a distance matrix."""
    n = len(NODES)
    d = [[INF] * n for _ in range(n)]
    for i in range(n):
        d[i][i] = 0
    for u, v, w in EDGES:
        d[NODES.index(u)][NODES.index(v)] = w
    for k in range(n):
        for i in range(n):
            for j in range(n):
                # skip infinite legs: INF + negative edge must not creep down
                if (d[i][k] != INF and d[k][j] != INF
                        and d[i][k] + d[k][j] < d[i][j]):
                    d[i][j] = d[i][k] + d[k][j]
    return d


if __name__ == "__main__":
    dist = bellman_ford("A")
    print("Bellman-Ford from A: " + " ".join(f"{v}={dist[v]}" for v in NODES))

    d = floyd_warshall()
    print("Floyd-Warshall all-pairs:")
    for row in d:
        cells = "".join("  inf" if x == INF else f" {x:>3}" for x in row)
        print("  " + cells)
'''
TOPIC_BELLMAN_FLOYD = {
    "id": "bellman-ford-floyd-warshall",
    "name": "Bellman-Ford & Floyd-Warshall",
    "slug": "bellman-ford-floyd-warshall",
    "type": "graph",
    "type_label": TYPES["graph"]["label"],
    "type_icon": TYPES["graph"]["icon"],
    "priority": 4,
    "difficulty": "Medium",
    "icon": "⚖️",
    "kind": "graph",
    "complexity": {
        "best": "Bellman-Ford O(V·E); Floyd-Warshall O(V³)",
        "average": "Bellman-Ford O(V·E); Floyd-Warshall O(V³)",
        "worst": "Bellman-Ford O(V·E); Floyd-Warshall O(V³)",
        "space": "Bellman-Ford O(V); Floyd-Warshall O(V²) matrix",
        "stable": "n/a",
        "in_place": "Floyd-Warshall updates its matrix in place",
    },
    "what": (
        "Two robustness-oriented shortest-path algorithms. Bellman-Ford relaxes every edge V−1 times; "
        "any edge that still improves afterwards proves a negative cycle. It handles negative weights, "
        "which Dijkstra cannot. Floyd-Warshall is dynamic programming over 'allowed intermediate "
        "vertices': after the k-th pass, d[i][j] is the shortest path from i to j using only nodes "
        "0..k as stopovers — yielding all pairs at once."
    ),
    "why": (
        "Dijkstra fails on negative edges — and they appear more than expected: currency arbitrage, "
        "subsidised routes, time-gained edges in scheduling. Bellman-Ford is the safe single-source "
        "answer AND a negative-cycle detector (a 'money pump' proof). Floyd-Warshall's 5-line triple "
        "loop computes every-pairs distances for dense small graphs, which is exactly what routing "
        "tables and transitive-closure questions need."
    ),
    "when_needed": [
        "Negative edge weights exist — Dijkstra is disqualified.",
        "You must detect negative cycles (arbitrage, impossible schedules, inconsistent constraints).",
        "Shortest paths between ALL pairs on a small/dense graph (up to a few hundred nodes).",
        "Transitive closure / reachability via a variant of Floyd-Warshall's k-pass.",
    ],
    "how_to_select": [
        "Single source + negative edges → Bellman-Ford (or SPFA for practical speedups).",
        "All pairs + dense graph + n ≤ ~400 → Floyd-Warshall; larger/sparse → Johnson's (BF + Dijkstra per node).",
        "Only weights matter? No — Floyd-Warshall can carry counts (number of paths) or booleans (closure) too.",
        "Early exit: if a Bellman-Ford pass changes nothing, you can stop — the code shows the check.",
        "Reconstructing paths: store a predecessor/next-hop table alongside distances.",
    ],
    "when_not": [
        "All weights non-negative and single source — Dijkstra (or even BFS for unit weights) is faster.",
        "Very large sparse all-pairs — O(V²) memory and O(V³) time do not fit; use Johnson's.",
        "Negative cycles reachable from the source make 'shortest path' undefined — report, don't solve.",
        "Dense queries on a CHANGING graph — recomputing from scratch each time is too slow; dynamic APSP is research-grade.",
    ],
    "outline": [
        "Bellman-Ford: relax all edges, V−1 rounds — dist[v] = min(dist[v], dist[u] + w)",
        "One extra sweep: any further improvement ⇒ a negative cycle exists",
        "Floyd-Warshall: for each k, d[i][j] = min(d[i][j], d[i][k] + d[k][j])",
        "After pass k, the matrix is exact for paths whose stopovers ⊆ {0..k}",
        "Complexities: O(V·E) single-source vs O(V³) all-pairs, O(V²) memory",
        "Both are the fallbacks that make shortest-path questions well-posed under negatives",
    ],
    "applications": [
        {"title": "Currency arbitrage detection", "detail": "Exchange rates as −log(weights) turn profitable loops into negative cycles — Bellman-Ford finds them."},
        {"title": "Routing protocols", "detail": "RIP-style distance-vector routing IS distributed Bellman-Ford; routers exchange distance tables with neighbors."},
        {"title": "Flight/traffic networks with discounts", "detail": "Negative 'rebate' edges (credits, time savings) break Dijkstra but not Bellman-Ford."},
        {"title": "Network forensics and graph mining", "detail": "All-pairs eccentricities and closeness centrality on modest graphs come from one Floyd-Warshall run."},
    ],
    "impl_c": BELLMAN_FLOYD_C,
    "impl_cpp": BELLMAN_FLOYD_CPP,
    "impl_py": BELLMAN_FLOYD_PY,
    "sim": sim_bellman_floyd,
    "references": [
        {"title": "GeeksforGeeks — Bellman-Ford Algorithm (reference)", "url": "https://www.geeksforgeeks.org/bellman-ford-algorithm-dp-23/"},
        {"title": "GeeksforGeeks — Floyd-Warshall Algorithm (reference)", "url": "https://www.geeksforgeeks.org/floyd-warshall-algorithm-dp-16/"},
    ],
}


# ---------------------------------------------------------------------------
# Topic: Topological Sort
# ---------------------------------------------------------------------------

def sim_topological_sort():
    """Trace Kahn's algorithm on a 6-node DAG (directed graph view)."""
    n = 6
    edges = [(0, 2), (1, 2), (1, 3), (2, 4), (3, 4), (3, 5), (4, 5)]
    labels = ["A", "B", "C", "D", "E", "F"]
    pos = {
        0: (60, 50), 1: (60, 190), 2: (240, 120),
        3: (240, 220), 4: (400, 60), 5: (500, 150),
    }
    adj = [[] for _ in range(n)]
    indeg = [0] * n
    for u, v in edges:
        adj[u].append(v)
        indeg[v] += 1
    out = []
    order = []
    removed = [False] * n

    def step(caption, current=None, queue=(), active_edge=None, final=False):
        node_states = {}
        for v in range(n):
            if removed[v]:
                node_states[v] = "done"
            elif v in queue:
                node_states[v] = "frontier"
            elif current is not None and v == current:
                node_states[v] = "current"
            else:
                node_states[v] = "unvisited"
        edge_states = {}
        for (u, v) in edges:
            key = f"{u}-{v}"
            if active_edge == (u, v):
                edge_states[key] = "active"
            elif removed[u] and removed[v]:
                edge_states[key] = "path"
            else:
                edge_states[key] = "normal"
        out.append({
            "kind": "graph",
            "directed": True,
            "nodes": [
                {"id": i, "label": labels[i], "x": pos[i][0], "y": pos[i][1],
                 "state": node_states[i]} for i in range(n)
            ],
            "edges": [
                {"from": u, "to": v, "weight": "", "state": edge_states.get(f"{u}-{v}", "normal")}
                for (u, v) in edges
            ],
            "dist": [str(order.index(l) + 1) if l in order else "–" for l in labels],
            "caption": caption,
            "done": final,
        })

    step(f"Build in-degrees: " + ", ".join(
        f"{labels[i]}={indeg[i]}" for i in range(n)) +
        ". Nodes with indegree 0 can start immediately.", queue=[0, 1])
    queue = [v for v in range(n) if indeg[v] == 0]
    step(f"Queue starts with all indegree-0 nodes: {', '.join(labels[v] for v in queue)}",
         queue=queue)
    while queue:
        queue.sort()
        u = queue.pop(0)
        order.append(labels[u])
        removed[u] = True
        step(f"Take {labels[u]} from the queue → order so far: {' '.join(order)}",
             current=u, queue=queue)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                queue.append(v)
                step(f"Edge {labels[u]}→{labels[v]}: {labels[v]}'s remaining prerequisites drop "
                     f"to 0 → enqueue it", current=u, queue=queue, active_edge=(u, v))
            else:
                step(f"Edge {labels[u]}→{labels[v]}: {labels[v]} still waits on {indeg[v]} "
                     f"prerequisite(s)", current=u, queue=queue, active_edge=(u, v))
    step(f"Queue empty — topological order: {' '.join(order)} (every arrow points forward)",
         final=True)
    return out


TOPO_SORT_C = r'''#include <stdio.h>

#define N 6

/* Kahn's algorithm: repeatedly output indegree-0 nodes.
 * Adjacency matrix + indegree array; O(V^2) here, O(V+E) with lists. */
void topological_sort(int adj[N][N], int order[]) {
    int indeg[N] = {0};
    for (int u = 0; u < N; u++)
        for (int v = 0; v < N; v++)
            if (adj[u][v]) indeg[v]++;

    int queue[N], head = 0, tail = 0, k = 0;
    for (int v = 0; v < N; v++)
        if (indeg[v] == 0) queue[tail++] = v;

    while (head < tail) {
        int u = queue[head++];
        order[k++] = u;
        for (int v = 0; v < N; v++) {
            if (adj[u][v] && --indeg[v] == 0)
                queue[tail++] = v;
        }
    }
    /* k < N would mean a cycle: some node never reached indegree 0 */
}

int main(void) {
    /* DAG:  A→C  B→C  B→D  C→E  D→E  D→F  E→F   (A..F = 0..5) */
    int adj[N][N] = {{0}};
    adj[0][2] = adj[1][2] = adj[1][3] = 1;
    adj[2][4] = adj[3][4] = adj[3][5] = adj[4][5] = 1;

    int order[N];
    topological_sort(adj, order);
    printf("Test 1 (Kahn order): ");
    for (int i = 0; i < N; i++) printf("%c ", 'A' + order[i]);
    printf("\n");

    /* cycle: F→A added on top of the DAG above -> no valid order */
    int cyc[N][N] = {{0}};
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++) cyc[i][j] = adj[i][j];
    cyc[5][0] = 1;
    int indeg[N] = {0}, q[N], head = 0, tail = 0, k = 0;
    for (int u = 0; u < N; u++)
        for (int v = 0; v < N; v++)
            if (cyc[u][v]) indeg[v]++;
    for (int v = 0; v < N; v++)
        if (indeg[v] == 0) q[tail++] = v;
    while (head < tail) {
        int u = q[head++];
        k++;
        for (int v = 0; v < N; v++)
            if (cyc[u][v] && --indeg[v] == 0) q[tail++] = v;
    }
    printf("Test 2 (cycle check): %s\n", k == N ? "acyclic" : "cycle detected");
    return 0;
}
'''


TOPO_SORT_CPP = r'''#include <iostream>
#include <vector>
using namespace std;

/* Kahn's algorithm: output indegree-0 nodes repeatedly. */
vector<int> topological_sort(const vector<vector<int>>& adj, int n) {
    vector<int> indeg(n, 0);
    for (int u = 0; u < n; u++)
        for (int v : adj[u]) indeg[v]++;

    vector<int> queue, order;
    for (int v = 0; v < n; v++)
        if (indeg[v] == 0) queue.push_back(v);

    size_t head = 0;
    while (head < queue.size()) {
        int u = queue[head++];
        order.push_back(u);
        for (int v : adj[u])
            if (--indeg[v] == 0) queue.push_back(v);
    }
    return order;   /* order.size() < n  =>  the graph has a cycle */
}

int main() {
    /* DAG:  A→C  B→C  B→D  C→E  D→E  D→F  E→F   (A..F = 0..5) */
    vector<vector<int>> adj(6);
    adj[0] = {2};
    adj[1] = {2, 3};
    adj[2] = {4};
    adj[3] = {4, 5};
    adj[4] = {5};

    vector<int> order = topological_sort(adj, 6);
    cout << "Test 1 (Kahn order): ";
    for (int u : order) cout << (char)('A' + u) << " ";
    cout << "\n";

    /* add F→A to create a cycle */
    vector<vector<int>> cyc = adj;
    cyc[5].push_back(0);
    cout << "Test 2 (cycle check): "
         << (topological_sort(cyc, 6).size() == 6 ? "acyclic" : "cycle detected")
         << "\n";
    return 0;
}
'''


TOPO_SORT_PY = r'''from collections import deque


def topological_sort(adj, n):
    """Kahn's algorithm; returns fewer than n nodes when a cycle exists."""
    indeg = [0] * n
    for u in range(n):
        for v in adj[u]:
            indeg[v] += 1

    queue = deque(v for v in range(n) if indeg[v] == 0)
    order = []
    while queue:
        u = queue.popleft()
        order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                queue.append(v)
    return order


def build(adj, n, extra=()):
    adj = [list(nbrs) for nbrs in adj]
    for u, v in extra:
        adj[u].append(v)
    return adj


if __name__ == "__main__":
    # DAG:  A→C  B→C  B→D  C→E  D→E  D→F  E→F   (A..F = 0..5)
    dag = [[2], [2, 3], [4], [4, 5], [5], []]
    order = topological_sort(dag, 6)
    print("Test 1 (Kahn order): " + " ".join(chr(65 + u) for u in order))

    cyc = build(dag, 6, extra=[(5, 0)])          # add F→A: cycle
    check = topological_sort(cyc, 6)
    print("Test 2 (cycle check): "
          + ("acyclic" if len(check) == 6 else "cycle detected"))
'''
TOPIC_TOPO_SORT = {
    "id": "topological-sort",
    "name": "Topological Sort",
    "slug": "topological-sort",
    "type": "graph",
    "type_label": TYPES["graph"]["label"],
    "type_icon": TYPES["graph"]["icon"],
    "priority": 4,
    "difficulty": "Medium",
    "icon": "📋",
    "kind": "graph",
    "complexity": {
        "best": "O(V + E)",
        "average": "O(V + E)",
        "worst": "O(V + E)",
        "space": "O(V) for indegrees, queue and output",
        "stable": "n/a",
        "in_place": "No (output ordering)",
    },
    "what": (
        "Topological sort linearises the vertices of a DIRECTED ACYCLIC graph so that every edge "
        "points forward: if u→v exists, u appears before v. Kahn's algorithm does this by repeatedly "
        "removing nodes with no remaining incoming edges (indegree 0); the DFS alternative instead "
        "records nodes in reverse finish order. The sort exists only when the graph has no cycle."
    ),
    "why": (
        "Whenever order is defined by dependencies, this is THE algorithm: course prerequisites, build "
        "systems, task schedulers, spreadsheet recalculation, package managers. It also detects the "
        "impossible case for free — if the dependency graph contains a cycle (circular imports, "
        "deadlocked tasks), Kahn's run finishes with fewer than V nodes and you can name the culprits."
    ),
    "when_needed": [
        "Scheduling tasks where some jobs must precede others (builds, course plans, workflows).",
        "Resolving symbol/import/link order in compilers and package managers.",
        "Processing a dependency DAG in a single safe pass (e.g., DP over DAGs).",
        "Detecting circular dependencies and reporting the nodes involved.",
    ],
    "how_to_select": [
        "Kahn's (BFS-style, indegree queue) is iterative — no recursion depth issues; prefer it in production.",
        "DFS-based topo (reverse finish order) fits when you already run DFS for other reasons.",
        "Need deterministic output (stable builds)? Break ties lexicographically with a heap.",
        "Only a cycle yes/no answer is needed? Kahn's processed-count is the cheapest detector.",
        "The graph may be disconnected — seed the queue/DFS from every unvisited node.",
    ],
    "when_not": [
        "The graph is undirected — 'before' is meaningless; use BFS/DFS or components instead.",
        "The graph has (or may have) cycles and you still need a full order — impossible; report the cycle.",
        "You need a shortest path on a weighted graph — topo order is only the preprocessing step for DAG-DP.",
        "Dependencies change constantly — re-sorting per query may be too slow; consider incremental or lazy strategies.",
    ],
    "outline": [
        "Compute indegree of every node (how many prerequisites it has)",
        "Queue all indegree-0 nodes; they can start immediately",
        "Pop a node, append it to the order, decrement each neighbour's indegree",
        "A neighbour hitting 0 joins the queue; repeat until the queue empties",
        "Fewer than V nodes emitted ⇒ a cycle exists (its members never reach indegree 0)",
        "O(V + E) with adjacency lists — linear in the graph size",
    ],
    "applications": [
        {"title": "Build systems", "detail": "Make, Bazel, and Webpack topo-sort the dependency graph to compile targets exactly once, in valid order."},
        {"title": "Package managers", "detail": "npm, apt, and pip resolve installation order from dependency DAGs and flag circular deps as errors."},
        {"title": "Course planning / workflows", "detail": "University prerequisite chains and tools like Airflow schedule steps via topological order."},
        {"title": "Spreadsheet recalculation", "detail": "Cells form a DAG of formula references; recalculation visits them topologically."},
    ],
    "impl_c": TOPO_SORT_C,
    "impl_cpp": TOPO_SORT_CPP,
    "impl_py": TOPO_SORT_PY,
    "sim": sim_topological_sort,
    "references": [
        {"title": "GeeksforGeeks — Topological Sorting (reference)", "url": "https://www.geeksforgeeks.org/topological-sorting/"},
    ],
}


# ---------------------------------------------------------------------------
# Topic: Union-Find (Disjoint Set Union)
# ---------------------------------------------------------------------------

def sim_union_find():
    """Trace unions + find with path compression (array view of parent[])."""
    n = 6
    parent = list(range(n))
    size = [1] * n
    out = []

    def emit(caption, highlights=(), done=False):
        out.append({
            "kind": "array",
            "data": list(parent),
            "highlights": list(highlights),
            "compare": [],
            "swap": [],
            "markers": {},
            "caption": caption,
            "done": done,
        })

    def find(x):
        root = x
        while parent[root] != root:
            root = parent[root]
        while parent[x] != root:          # path compression
            parent[x], x = root, parent[x]
        return root

    def union(a, b, label):
        ra, rb = find(a), find(b)
        if ra == rb:
            emit(f"union({a},{b}): both already belong to root {ra} — no change", [ra, rb])
            return
        if size[ra] < size[rb]:
            ra, rb = rb, ra
        parent[rb] = ra
        size[ra] += size[rb]
        emit(f"union({a},{b}) [{label}]: root {rb} attaches under root {ra} "
             f"(set sizes {size[ra] - size[rb]}+{size[rb]}={size[ra]})", [ra, rb])

    emit("Six singletons: parent[i] = i, every element is its own root")
    emit("Test 2 — union(0,1), union(2,3), union(4,5): pairs merge", done=False)
    union(0, 1, "equal size")
    union(2, 3, "equal size")
    union(4, 5, "equal size")
    emit("Three pairs formed; parent[1]=0, parent[3]=2, parent[5]=4")
    union(1, 3, "equal size — 0 wins the tie")
    union(5, 2, "smaller set joins the larger")
    emit("union(5,2): root 4 attaches under root 0 — everything shares root 0", [0])
    r = find(5)
    emit(f"Test 4 — find(5): walked 5→4→0, compressed parent[5]=0, root = {r}", [5])
    r = find(3)
    emit(f"find(3): walked 3→2→0, compressed parent[3]=0, root = {r}", [3])
    emit(f"Final parent array {parent} — one component of size {size[0]}", done=True)
    return out


UNION_FIND_C = r'''#include <stdio.h>

#define N 6

int parent[N];
int size_[N];

void init(int n) {
    for (int i = 0; i < n; i++) { parent[i] = i; size_[i] = 1; }
}

/* Find with path compression (two passes): returns the set root. */
int find(int x) {
    int root = x;
    while (parent[root] != root) root = parent[root];
    while (parent[x] != root) { int next = parent[x]; parent[x] = root; x = next; }
    return root;
}

/* Union by size: attach the smaller set under the larger. */
void union_sets(int a, int b) {
    int ra = find(a), rb = find(b);
    if (ra == rb) return;
    if (size_[ra] < size_[rb]) { int t = ra; ra = rb; rb = t; }
    parent[rb] = ra;
    size_[ra] += size_[rb];
}

int count_components(int n) {
    int c = 0;
    for (int i = 0; i < n; i++)
        if (find(i) == i) c++;
    return c;
}

void print_parent(void) {
    for (int i = 0; i < N; i++) printf(i ? " %d" : "%d", parent[i]);
    printf("\n");
}

int main(void) {
    init(N);
    printf("Test 1: %d singleton components\n", count_components(N));

    union_sets(0, 1); union_sets(2, 3); union_sets(4, 5);
    printf("Test 2: after pair unions -> %d components\n", count_components(N));

    union_sets(1, 3); union_sets(5, 2);
    printf("Test 3: after merges -> %d component\n", count_components(N));

    int r = find(5);   /* compresses the chain on the way */
    printf("Test 4: find(5) = %d ; parent = ", r);
    print_parent();

    printf("Test 5: connected(0,3)? %s ; connected(1,4)? %s\n",
           find(0) == find(3) ? "yes" : "no",
           find(1) == find(4) ? "yes" : "no");

    init(N);
    union_sets(0, 1);
    printf("Test 6: fresh set, one union -> %d components\n", count_components(N));
    return 0;
}
'''


UNION_FIND_CPP = r'''#include <iostream>
#include <vector>
using namespace std;

struct DSU {
    vector<int> parent, sz;

    explicit DSU(int n) : parent(n), sz(n, 1) {
        for (int i = 0; i < n; i++) parent[i] = i;
    }

    /* find with path compression (two passes) */
    int find(int x) {
        int root = x;
        while (parent[root] != root) root = parent[root];
        while (parent[x] != root) { int next = parent[x]; parent[x] = root; x = next; }
        return root;
    }

    /* union by size */
    void unite(int a, int b) {
        int ra = find(a), rb = find(b);
        if (ra == rb) return;
        if (sz[ra] < sz[rb]) swap(ra, rb);
        parent[rb] = ra;
        sz[ra] += sz[rb];
    }

    int components() const {
        int c = 0;
        for (int i = 0; i < (int)parent.size(); i++)
            if (find(i) == i) c++;
        return c;
    }
};

int main() {
    DSU d(6);
    cout << "Test 1: " << d.components() << " singleton components\n";

    d.unite(0, 1); d.unite(2, 3); d.unite(4, 5);
    cout << "Test 2: after pair unions -> " << d.components() << " components\n";

    d.unite(1, 3); d.unite(5, 2);
    cout << "Test 3: after merges -> " << d.components() << " component\n";

    int r = d.find(5);   /* compresses the chain on the way */
    cout << "Test 4: find(5) = " << r << " ; parent = ";
    for (int i = 0; i < 6; i++) cout << (i ? " " : "") << d.parent[i];
    cout << "\n";

    cout << "Test 5: connected(0,3)? " << (d.find(0) == d.find(3) ? "yes" : "no")
         << " ; connected(1,4)? " << (d.find(1) == d.find(4) ? "yes" : "no") << "\n";

    DSU fresh(6);
    fresh.unite(0, 1);
    cout << "Test 6: fresh set, one union -> " << fresh.components() << " components\n";
    return 0;
}
'''


UNION_FIND_PY = r'''class DSU:
    """Disjoint Set Union with path compression + union by size."""

    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n

    def find(self, x):
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:          # path compression
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]

    def components(self):
        return sum(1 for i in range(len(self.parent)) if self.find(i) == i)


if __name__ == "__main__":
    d = DSU(6)
    print(f"Test 1: {d.components()} singleton components")

    d.union(0, 1); d.union(2, 3); d.union(4, 5)
    print(f"Test 2: after pair unions -> {d.components()} components")

    d.union(1, 3); d.union(5, 2)
    print(f"Test 3: after merges -> {d.components()} component")

    r = d.find(5)          # compresses the chain on the way
    print("Test 4: find(5) = {} ; parent = {}".format(
        r, " ".join(str(p) for p in d.parent)))

    print("Test 5: connected(0,3)? {} ; connected(1,4)? {}".format(
        "yes" if d.find(0) == d.find(3) else "no",
        "yes" if d.find(1) == d.find(4) else "no"))

    fresh = DSU(6)
    fresh.union(0, 1)
    print(f"Test 6: fresh set, one union -> {fresh.components()} components")
'''


# ---------------------------------------------------------------------------
# Topic: Union-Find (Disjoint Set Union)
# ---------------------------------------------------------------------------

def sim_dsu():
    """Trace union by rank + path compression (graph renderer)."""
    out = []

    def emit(caption, parent, highlight=(), done=False):
        nodes = []
        for i in range(1, 7):
            st = "done" if i in highlight else "normal"
            nodes.append({"id": i, "value": i, "parent": parent[i], "state": st})
        out.append({"kind": "graph", "nodes": nodes, "edges": [],
                    "caption": caption, "done": done})

    def find(x, par):
        seq = [x]
        while par[x] != x:
            x = par[x]
            seq.append(x)
        return seq

    p = {i: i for i in range(1, 7)}
    emit("Six elements, each its own set — parent[i] = i", p)

    for a, b in ((1, 2), (3, 4), (5, 6)):
        pa, pb = find(a, p)[-1], find(b, p)[-1]
        p[pb] = pa
        emit(f"union({a}, {b}): find({a}) = {pa}, find({b}) = {pb} → attach {pb} under {pa}",
             p, (a, b))

    pa, pb = find(2, p)[-1], find(3, p)[-1]
    p[pb] = pa
    emit(f"union(2, 3): find(2) = {pa}, find(3) = {pb} → equal ranks, attach {pb} under {pa} "
         f"and raise rank({pa})", p, (2, 3))

    seq = find(4, p)
    p[4] = p[seq[-1]]
    emit(f"find(4): climbs {' → '.join(map(str, seq))}, then compresses 4 straight to the root "
         f"{seq[-1]} — future finds get shorter", p, tuple(seq))

    pa, pb = find(1, p)[-1], find(5, p)[-1]
    p[pb] = pa
    emit(f"union(5, 1): find(5) = {pb}, find(1) = {pa} → rank({pa}) is higher, so {pb} hangs "
         f"under {pa} (union by rank keeps trees shallow)", p, (5, pa))

    seq = find(6, p)
    p[6] = p[seq[-1]]
    emit(f"find(6): climbs {' → '.join(map(str, seq))} and compresses 6 to root {seq[-1]}", p, tuple(seq))

    emit(f"All six elements share root {p[1]} — one connected component; with path compression "
         f"+ union by rank, amortised find is nearly O(1)", p, done=True)
    return out


DSU_C = r'''#include <stdio.h>

int parent[101], rnk[101];

void make_set(int n) {
    for (int i = 0; i <= n; i++) { parent[i] = i; rnk[i] = 0; }
}

/* Find with path halving: every hop re-points x to its grandparent,
 * flattening the tree as a side effect. */
int find(int x) {
    while (parent[x] != x) {
        parent[x] = parent[parent[x]];
        x = parent[x];
    }
    return x;
}

/* Union by rank. Returns 1 if merged, 0 if already in the same set
 * (that '0' case is exactly how Kruskal detects cycles). */
int union_sets(int a, int b) {
    int ra = find(a), rb = find(b);
    if (ra == rb) return 0;
    if (rnk[ra] < rnk[rb]) { int t = ra; ra = rb; rb = t; }
    parent[rb] = ra;
    if (rnk[ra] == rnk[rb]) rnk[ra]++;
    return 1;
}

int main(void) {
    make_set(6);
    union_sets(1, 2); union_sets(3, 4); union_sets(5, 6);
    printf("Test 1: connected(1,4)? %s ; connected(1,5)? %s\n",
           find(1) == find(4) ? "Yes" : "No", find(1) == find(5) ? "Yes" : "No");
    union_sets(2, 3);
    printf("Test 2: after union(2,3): connected(1,4)? %s\n",
           find(1) == find(4) ? "Yes" : "No");
    union_sets(4, 5);
    int sets = 0;
    for (int i = 1; i <= 6; i++) if (find(i) == i) sets++;
    printf("Test 3: distinct sets after union(4,5): %d\n", sets);
    printf("Test 4: union(1,3) merged anything? %s (already one set)\n",
           union_sets(1, 3) ? "Yes" : "No");

    make_set(3);
    union_sets(1, 2); union_sets(2, 3);
    printf("Test 5: adding edge (3,1) creates a cycle? %s\n",
           union_sets(3, 1) ? "No" : "Yes");
    return 0;
}
'''


DSU_CPP = r'''#include <iostream>
#include <vector>
using namespace std;

struct DSU {
    vector<int> parent, rnk;

    explicit DSU(int n) : parent(n + 1), rnk(n + 1, 0) {
        for (int i = 0; i <= n; i++) parent[i] = i;
    }

    int find(int x) {
        while (parent[x] != x) {
            parent[x] = parent[parent[x]];   /* path halving */
            x = parent[x];
        }
        return x;
    }

    bool unite(int a, int b) {
        int ra = find(a), rb = find(b);
        if (ra == rb) return false;
        if (rnk[ra] < rnk[rb]) swap(ra, rb);
        parent[rb] = ra;
        if (rnk[ra] == rnk[rb]) rnk[ra]++;
        return true;
    }
};

int main() {
    DSU d(6);
    d.unite(1, 2); d.unite(3, 4); d.unite(5, 6);
    cout << "Test 1: connected(1,4)? " << (d.find(1) == d.find(4) ? "Yes" : "No")
         << " ; connected(1,5)? " << (d.find(1) == d.find(5) ? "Yes" : "No") << "\n";
    d.unite(2, 3);
    cout << "Test 2: after union(2,3): connected(1,4)? "
         << (d.find(1) == d.find(4) ? "Yes" : "No") << "\n";
    d.unite(4, 5);
    int sets = 0;
    for (int i = 1; i <= 6; i++) if (d.find(i) == i) sets++;
    cout << "Test 3: distinct sets after union(4,5): " << sets << "\n";
    cout << "Test 4: union(1,3) merged anything? "
         << (d.unite(1, 3) ? "Yes" : "No") << " (already one set)\n";

    DSU e(3);
    e.unite(1, 2); e.unite(2, 3);
    cout << "Test 5: adding edge (3,1) creates a cycle? "
         << (e.unite(3, 1) ? "No" : "Yes") << "\n";
    return 0;
}
'''


DSU_PY = r'''class DSU:
    def __init__(self, n):
        self.parent = list(range(n + 1))
        self.rank = [0] * (n + 1)

    def find(self, x):
        """Find with path halving: re-point x to its grandparent each hop."""
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        """Union by rank; returns False if a and b were already connected."""
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


if __name__ == "__main__":
    d = DSU(6)
    d.union(1, 2); d.union(3, 4); d.union(5, 6)
    t1 = "Yes" if d.find(1) == d.find(4) else "No"
    t2 = "Yes" if d.find(1) == d.find(5) else "No"
    print(f"Test 1: connected(1,4)? {t1} ; connected(1,5)? {t2}")
    d.union(2, 3)
    print(f"Test 2: after union(2,3): connected(1,4)? "
          f"{'Yes' if d.find(1) == d.find(4) else 'No'}")
    d.union(4, 5)
    sets = sum(1 for i in range(1, 7) if d.find(i) == i)
    print(f"Test 3: distinct sets after union(4,5): {sets}")
    print(f"Test 4: union(1,3) merged anything? "
          f"{'Yes' if d.union(1, 3) else 'No'} (already one set)")

    e = DSU(3)
    e.union(1, 2); e.union(2, 3)
    print(f"Test 5: adding edge (3,1) creates a cycle? "
          f"{'No' if e.union(3, 1) else 'Yes'}")
'''
TOPIC_DSU = {
    "id": "union-find",
    "name": "Union-Find (Disjoint Set Union)",
    "slug": "union-find",
    "type": "graph",
    "type_label": TYPES["graph"]["label"],
    "type_icon": TYPES["graph"]["icon"],
    "priority": 4,
    "difficulty": "Medium",
    "icon": "🧩",
    "kind": "graph",
    "complexity": {
        "best": "O(1) amortised per operation",
        "average": "O(α(n)) amortised — inverse Ackermann, effectively constant",
        "worst": "O(α(n)) amortised with union by rank + path compression",
        "space": "O(n) parent + rank arrays",
        "stable": "n/a",
        "in_place": "Yes",
    },
    "what": (
        "Union-Find maintains a collection of disjoint sets under two operations: find(x) returns a "
        "representative (the root of x's set), and union(a, b) merges the two sets. Each set is a tree "
        "stored as a parent array. Two heuristics make it fast: union by rank (always hang the shallower "
        "tree under the deeper one) and path compression (re-point visited nodes straight at the root)."
    ),
    "why": (
        "No other structure answers 'are these two things connected?' while the structure keeps changing "
        "in nearly constant time. Kruskal's MST algorithm is little more than a DSU plus sorting; cycle "
        "detection in incremental graphs, connected-component labelling, and percolation checks are all "
        "one-liners once a DSU exists. The amortised α(n) bound is a celebrated result — α(n) ≤ 4 for "
        "any input that fits in the universe."
    ),
    "when_needed": [
        "Dynamic connectivity: merge groups, query connected-ness, count components.",
        "Kruskal's minimum spanning tree — reject edges whose endpoints already share a root.",
        "Cycle detection while adding edges one at a time.",
        "Connected-component labelling in image processing, or merging accounts/users that share a key.",
    ],
    "how_to_select": [
        "Always combine BOTH heuristics — either alone is weaker; together they give α(n).",
        "Need the exact tree shape or deletions? DSU cannot delete — use link-cut trees or rollbacks.",
        "Want extra data per set (size, sum)? Keep it at the root and update inside union.",
        "Weighted/parity DSU extends to 'relative distance between nodes' problems.",
        "Queries arrive offline? DSU over sorted queries beats re-running BFS/DFS each time.",
    ],
    "when_not": [
        "The graph is static and small — one BFS/DFS lists all components more directly.",
        "You need to disconnect (split) sets — plain DSU cannot undo a union.",
        "You need shortest paths — DSU knows connectivity only, not distances.",
        "Exact worst-case per-operation latency matters — α(n) is amortised, not per-call.",
    ],
    "outline": [
        "Each set is a tree in a parent array; the root is the set's representative",
        "find(x): climb parents until parent[x] = x",
        "union(a, b): find both roots; if equal, already connected (cycle!)",
        "Union by rank: attach the shallower tree under the deeper root",
        "Path compression: re-point climbed nodes to the root, flattening the tree",
        "Together: O(α(n)) amortised — inverse Ackermann, constant in practice",
    ],
    "applications": [
        {"title": "Kruskal's MST", "detail": "Sort edges, then accept each edge only if its endpoints have different DSU roots."},
        {"title": "Social-network merging", "detail": "Merging accounts, deduplicating records, or unioning users who share an email/phone."},
        {"title": "Image segmentation", "detail": "Connected-component labelling pixels by adjacency is a DSU sweep in raster order."},
        {"title": "Percolation and maze generation", "detail": "Grids open cells one by one and DSU tests whether top connects to bottom; mazes carve walls the same way."},
    ],
    "impl_c": DSU_C,
    "impl_cpp": DSU_CPP,
    "impl_py": DSU_PY,
    "sim": sim_dsu,
    "references": [
        {"title": "GeeksforGeeks — Union-Find Algorithm (reference)", "url": "https://www.geeksforgeeks.org/union-find/"},
    ],
}


# ---------------------------------------------------------------------------
# Topic: Minimum Spanning Tree (Kruskal & Prim)
# ---------------------------------------------------------------------------

MST_NODES = [
    {"id": 1, "value": "A", "state": "normal"},
    {"id": 2, "value": "B", "state": "normal"},
    {"id": 3, "value": "C", "state": "normal"},
    {"id": 4, "value": "D", "state": "normal"},
    {"id": 5, "value": "E", "state": "normal"},
]
MST_EDGES = [(1, 2, 4), (1, 3, 1), (3, 2, 2), (2, 4, 5), (3, 4, 8), (4, 5, 3), (3, 5, 10)]


def sim_mst():
    """Trace Kruskal (DSU) then Prim (grow from A) on the same graph."""
    out = []

    def emit(caption, accepted=(), current=None, done=False):
        edges = []
        for u, v, w in MST_EDGES:
            st = "normal"
            if (u, v) in accepted or (v, u) in accepted:
                st = "path"
            elif current and {u, v} == set(current[:2]):
                st = "active"
            edges.append({"u": u, "v": v, "w": w, "state": st})
        nodes = [dict(nd) for nd in MST_NODES]
        for nd in nodes:
            if any(nd["id"] in e[:2] for e in edges if e["state"] == "path"):
                nd["state"] = "done"
        out.append({"kind": "graph", "nodes": nodes, "edges": edges,
                    "caption": caption, "done": done})

    emit("5 nodes, 7 edges. Kruskal sorts edges by weight and accepts the cheapest edge that "
         "joins two different components (a DSU tracks the components)")

    kruskal_taken = []
    for u, v, w, name, why in (
        (1, 3, 1, "A–C", "cheapest of all — different components → accept"),
        (3, 2, 2, "C–B", "joins {A,C} with {B} → accept"),
        (4, 5, 3, "D–E", "accept"),
        (1, 2, 4, "A–B", "find(A) = find(B) → same component → REJECT (would close a cycle)"),
    ):
        if "REJECT" in why:
            emit(f"Kruskal — edge {name} (weight {w}): {why}", kruskal_taken, (u, v, w))
        else:
            kruskal_taken.append((u, v))
            emit(f"Kruskal — edge {name} (weight {w}): {why}", kruskal_taken, (u, v, w))
    kruskal_taken.append((2, 4))
    emit("Kruskal — edge B–D (weight 5): accept → 4 edges for 5 nodes, MST complete "
         "(total weight 1+2+3+5 = 11)", kruskal_taken, (2, 4, 5))

    emit("Kruskal stops — every remaining edge only adds a cycle. Same answer via Prim: grow ONE "
         "tree outward from A", kruskal_taken)
    prim_taken = [(1, 3)]
    emit("Prim from A — cheapest edge leaving the tree {A}: A–C (1) → add C", prim_taken, (1, 3, 1))
    prim_taken.append((3, 2))
    emit("Prim — cheapest edge leaving {A,C}: C–B (2) beats A–B (4) → add B", prim_taken, (3, 2, 2))
    prim_taken.append((2, 4))
    emit("Prim — cheapest edge leaving {A,B,C}: B–D (5) beats C–D (8) → add D", prim_taken, (2, 4, 5))
    prim_taken.append((4, 5))
    emit("Prim — cheapest edge leaving {A,B,C,D}: D–E (3) → add E — same MST, total weight 11",
         prim_taken, done=True)
    return out


MST_C = r'''#include <stdio.h>
#include <stdlib.h>

#define V 5

/* ---------------- Kruskal: sort edges + Union-Find ---------------- */
int parent[V], rnk[V];

void make_set(void) {
    for (int i = 0; i < V; i++) { parent[i] = i; rnk[i] = 0; }
}

int find(int x) {
    while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; }
    return x;
}

typedef struct { int u, v, w; } Edge;

int cmp_edge(const void *a, const void *b) {
    return ((const Edge *)a)->w - ((const Edge *)b)->w;
}

/* Fills mst with the V-1 tree edges; returns the total weight. */
int kruskal(Edge *e, int m, Edge *mst) {
    qsort(e, (size_t)m, sizeof(Edge), cmp_edge);
    make_set();
    int count = 0, total = 0;
    for (int i = 0; i < m && count < V - 1; i++) {
        int ru = find(e[i].u), rv = find(e[i].v);
        if (ru != rv) {                       /* accept: joins two components */
            if (rnk[ru] < rnk[rv]) { int t = ru; ru = rv; rv = t; }
            parent[rv] = ru;
            if (rnk[ru] == rnk[rv]) rnk[ru]++;
            mst[count++] = e[i];
            total += e[i].w;
        }
    }
    return total;
}

/* ---------------- Prim: adjacency matrix, O(V^2) ---------------- */
int prim(int g[V][V], int start) {
    int in_mst[V] = {0}, key[V], total = 0;
    for (int i = 0; i < V; i++) key[i] = 1 << 29;      /* INF */
    key[start] = 0;
    for (int step = 0; step < V; step++) {
        int u = -1;
        for (int i = 0; i < V; i++)
            if (!in_mst[i] && (u == -1 || key[i] < key[u])) u = i;
        in_mst[u] = 1;
        total += key[u];
        for (int v = 0; v < V; v++)
            if (g[u][v] && !in_mst[v] && g[u][v] < key[v]) key[v] = g[u][v];
    }
    return total;
}

void print_edges(const Edge *mst, int n) {
    for (int i = 0; i < n; i++) printf("(%d-%d w=%d) ", mst[i].u, mst[i].v, mst[i].w);
    printf("\n");
}

int main(void) {
    Edge edges[] = {{0,1,2},{1,2,3},{0,3,6},{1,3,8},{1,4,5},{2,4,7},{3,4,9}};
    Edge mst[V - 1];
    int total = kruskal(edges, 7, mst);
    printf("Test 1 (Kruskal MST): ");
    print_edges(mst, V - 1);
    printf("Test 2 (Kruskal total weight): %d\n", total);

    int g[V][V] = {{0,2,0,6,0},{2,0,3,8,5},{0,3,0,0,7},{6,8,0,0,9},{0,5,7,9,0}};
    printf("Test 3 (Prim total weight from node 0): %d\n", prim(g, 0));
    return 0;
}
'''


MST_CPP = r'''#include <algorithm>
#include <iostream>
#include <vector>
using namespace std;

const int V = 5;

struct DSU {
    vector<int> parent, rnk;
    explicit DSU(int n) : parent(n), rnk(n, 0) {
        for (int i = 0; i < n; i++) parent[i] = i;
    }
    int find(int x) {
        while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; }
        return x;
    }
    bool unite(int a, int b) {
        int ra = find(a), rb = find(b);
        if (ra == rb) return false;
        if (rnk[ra] < rnk[rb]) swap(ra, rb);
        parent[rb] = ra;
        if (rnk[ra] == rnk[rb]) rnk[ra]++;
        return true;
    }
};

struct Edge { int u, v, w; };

/* Kruskal: O(E log E) for the sort, DSU makes the scan nearly linear. */
pair<int, vector<Edge>> kruskal(vector<Edge> e) {
    sort(e.begin(), e.end(),
         [](const Edge& a, const Edge& b) { return a.w < b.w; });
    DSU d(V);
    vector<Edge> mst;
    int total = 0;
    for (const Edge& ed : e) {
        if (mst.size() == (size_t)V - 1) break;
        if (d.unite(ed.u, ed.v)) {
            mst.push_back(ed);
            total += ed.w;
        }
    }
    return {total, mst};
}

/* Prim: adjacency matrix, O(V^2) — ideal for dense graphs. */
int prim(const vector<vector<int>>& g, int start) {
    vector<int> key(V, 1 << 29);
    vector<bool> in_mst(V, false);
    key[start] = 0;
    int total = 0;
    for (int step = 0; step < V; step++) {
        int u = -1;
        for (int i = 0; i < V; i++)
            if (!in_mst[i] && (u == -1 || key[i] < key[u])) u = i;
        in_mst[u] = true;
        total += key[u];
        for (int v = 0; v < V; v++)
            if (g[u][v] && !in_mst[v] && g[u][v] < key[v]) key[v] = g[u][v];
    }
    return total;
}

int main() {
    vector<Edge> edges = {{0,1,2},{1,2,3},{0,3,6},{1,3,8},{1,4,5},{2,4,7},{3,4,9}};
    pair<int, vector<Edge>> result = kruskal(edges);
    cout << "Test 1 (Kruskal MST): ";
    for (const Edge& e : result.second) cout << "(" << e.u << "-" << e.v << " w=" << e.w << ") ";
    cout << "\n";
    cout << "Test 2 (Kruskal total weight): " << result.first << "\n";

    vector<vector<int>> g = {{0,2,0,6,0},{2,0,3,8,5},{0,3,0,0,7},{6,8,0,0,9},{0,5,7,9,0}};
    cout << "Test 3 (Prim total weight from node 0): " << prim(g, 0) << "\n";
    return 0;
}
'''


MST_PY = r'''def kruskal(n, edges):
    """MST by Kruskal: sort edges, accept those joining two DSU components."""
    parent = list(range(n))
    rank = [0] * n

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    mst, total = [], 0
    for u, v, w in sorted(edges, key=lambda e: e[2]):
        if len(mst) == n - 1:
            break
        ru, rv = find(u), find(v)
        if ru != rv:
            if rank[ru] < rank[rv]:
                ru, rv = rv, ru
            parent[rv] = ru
            if rank[ru] == rank[rv]:
                rank[ru] += 1
            mst.append((u, v, w))
            total += w
    return mst, total


def prim(g, start):
    """MST by Prim on an adjacency matrix — O(V^2), great for dense graphs."""
    n = len(g)
    key = [1 << 29] * n
    in_mst = [False] * n
    key[start] = 0
    total = 0
    for _ in range(n):
        u = min((i for i in range(n) if not in_mst[i]), key=lambda i: key[i])
        in_mst[u] = True
        total += key[u]
        for v in range(n):
            if g[u][v] and not in_mst[v] and g[u][v] < key[v]:
                key[v] = g[u][v]
    return total


if __name__ == "__main__":
    edges = [(0, 1, 2), (1, 2, 3), (0, 3, 6), (1, 3, 8), (1, 4, 5), (2, 4, 7), (3, 4, 9)]
    mst, total = kruskal(5, edges)
    print("Test 1 (Kruskal MST):", end=" ")
    for u, v, w in mst:
        print(f"({u}-{v} w={w})", end=" ")
    print()
    print(f"Test 2 (Kruskal total weight): {total}")

    g = [[0, 2, 0, 6, 0], [2, 0, 3, 8, 5], [0, 3, 0, 0, 7], [6, 8, 0, 0, 9], [0, 5, 7, 9, 0]]
    print(f"Test 3 (Prim total weight from node 0): {prim(g, 0)}")
'''
TOPIC_MST = {
    "id": "minimum-spanning-tree",
    "name": "Minimum Spanning Tree (Kruskal & Prim)",
    "slug": "minimum-spanning-tree",
    "type": "graph",
    "type_label": TYPES["graph"]["label"],
    "type_icon": TYPES["graph"]["icon"],
    "priority": 4,
    "difficulty": "Medium",
    "icon": "🌉",
    "kind": "graph",
    "complexity": {
        "best": "Kruskal O(E log E); Prim O(E log V) with a heap",
        "average": "Kruskal O(E log E); Prim O(E log V)",
        "worst": "Kruskal O(E log E); Prim O(V²) with an adjacency matrix",
        "space": "O(V + E)",
        "stable": "n/a",
        "in_place": "No (builds a tree structure)",
    },
    "what": (
        "A spanning tree of a connected, undirected graph keeps all V vertices connected using exactly "
        "V−1 edges with no cycles; the minimum spanning tree is the one with the smallest total edge "
        "weight. Kruskal grows a forest from the globally cheapest edges, using Union-Find to skip edges "
        "that would close a cycle. Prim grows a single tree outward, always adding the cheapest edge that "
        "connects the tree to a new vertex. The cut property — the cheapest edge across any cut belongs "
        "to some MST — guarantees both are correct."
    ),
    "why": (
        "Whenever 'connect everything at minimum cost' is the goal — cabling, pipelines, road networks, "
        "circuit wiring — the MST is the direct mathematical answer, not an approximation. It is also the "
        "backbone of single-linkage clustering and a 2-approximation for metric TSP. Kruskal is barely "
        "twenty lines once a DSU exists, and Prim is Dijkstra's algorithm minus the distance accumulation."
    ),
    "when_needed": [
        "Connecting all sites/nodes with minimum total wiring, pipe, or road cost.",
        "Single-linkage hierarchical clustering: cut the MST's heaviest edges to split clusters.",
        "A quick 2-approximation for metric TSP (preorder an MST traversal).",
        "Reducing redundancy: spanning tree protocols in bridges/switches prevent broadcast loops.",
    ],
    "how_to_select": [
        "Sparse graph (E ≈ V): Kruskal — sorting E edges costs little and DSU does the rest.",
        "Dense graph (E ≈ V²): Prim with an adjacency matrix — O(V²) beats sorting all E² edges.",
        "Edges arrive pre-sorted or streaming: Kruskal processes them online.",
        "Already have partial connectivity? Start Kruskal with those edges pre-unioned.",
        "Need shortest PATHS instead of minimum total cost? That is Dijkstra, not MST — different objective.",
    ],
    "when_not": [
        "You need cheapest routes between specific pairs — shortest paths (Dijkstra/Floyd-Warshall), not MST.",
        "The graph is directed — spanning arborescences need Edmonds' algorithm instead.",
        "Edge costs change dynamically — re-running from scratch is too slow; use dynamic MST techniques.",
        "The graph may be disconnected — an MST doesn't exist; build a minimum spanning FOREST per component.",
    ],
    "outline": [
        "Spanning tree: V−1 edges, all vertices connected, no cycles",
        "Cut property: cheapest edge across any cut is safe — the greedy justification",
        "Kruskal: sort edges by weight; accept each edge whose endpoints differ (DSU)",
        "Prim: grow one tree; always add the cheapest edge leaving the tree",
        "Kruskal O(E log E) — sparse; Prim O(V²) matrix / O(E log V) heap — dense",
        "Both yield the same total weight (unique iff edge weights are distinct)",
    ],
    "applications": [
        {"title": "Telecom and utility networks", "detail": "Least-cost cabling/fiber/pipeline layouts between offices, homes, or wells are MST problems."},
        {"title": "Cluster analysis", "detail": "Single-linkage clustering is literally 'build the MST, cut the k−1 largest edges'."},
        {"title": "Approximation algorithms", "detail": "A preorder walk of an MST gives a 2-approximation for metric TSP — MSTs certify hardness gaps too."},
        {"title": "Computer networking", "detail": "Spanning Tree Protocol (STP) in Ethernet switches elects a loop-free tree using Prim/Dijkstra-style costs."},
    ],
    "impl_c": MST_C,
    "impl_cpp": MST_CPP,
    "impl_py": MST_PY,
    "sim": sim_mst,
    "references": [
        {"title": "GeeksforGeeks — Minimum Spanning Tree (reference)", "url": "https://www.geeksforgeeks.org/minimum-spanning-tree/"},
    ],
}


# ---------------------------------------------------------------------------
# Topic: Minimum Spanning Tree (Kruskal & Prim)
# ---------------------------------------------------------------------------

def sim_mst():
    """Trace Kruskal's edge acceptance, then Prim's frontier growth (graph renderer)."""
    nodes = [
        {"id": "0", "x": 50, "y": 40},
        {"id": "1", "x": 300, "y": 40},
        {"id": "2", "x": 150, "y": 160},
        {"id": "3", "x": 460, "y": 160},
        {"id": "4", "x": 300, "y": 280},
    ]
    edges = [
        {"u": "0", "v": "1", "w": 2},
        {"u": "0", "v": "2", "w": 3},
        {"u": "1", "v": "2", "w": 1},
        {"u": "1", "v": "3", "w": 4},
        {"u": "2", "v": "3", "w": 5},
        {"u": "2", "v": "4", "w": 6},
        {"u": "3", "v": "4", "w": 7},
    ]
    out = []

    def emit(caption, mst=(), checking=None, state="normal", done=False):
        out.append({
            "kind": "graph",
            "nodes": [dict(n) for n in nodes],
            "edges": [dict(e) for e in edges],
            "mst": list(mst),
            "checking": checking,
            "state": state,
            "caption": caption,
            "done": done,
        })

    parent = {n["id"]: n["id"] for n in nodes}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    chosen = []
    emit("Kruskal: sort all edges by weight, then take the cheapest that joins two different trees",
         (), None)
    for e in sorted(edges, key=lambda e: e["w"]):
        u, v = e["u"], e["v"]
        ru, rv = find(u), find(v)
        ek = (u, v, e["w"])
        if ru != rv:
            parent[ru] = rv
            chosen.append(ek)
            emit(f"Edge {u}-{v} (w={e['w']}): endpoints are in different trees — ACCEPT "
                 f"({len(chosen)} of {len(nodes) - 1} edges)", tuple(chosen), ek, "accepted")
        else:
            emit(f"Edge {u}-{v} (w={e['w']}): both ends already connected — REJECT (would form a cycle)",
                 tuple(chosen), ek, "rejected")
    total = sum(w for _, _, w in chosen)
    emit(f"Kruskal done — MST weight {total}", tuple(chosen), None, "accepted")
    emit("Prim: grow one tree from node 0, always adding the cheapest edge leaving it", ("0",), None)
    emit("Prim's picks are the same set of edges here — cut-crossing property guarantees it. "
         "Kruskal = sort + DSU, Prim = heap; both O(E log E)-ish", tuple(chosen), None, "accepted", done=True)
    return out


'''
TOPIC_GREEDY = {
    "id": "greedy-fundamentals",
    "name": "Greedy Fundamentals & Activity Selection",
    "slug": "greedy-fundamentals",
    "type": "greedy",
    "type_label": TYPES["greedy"]["label"],
    "type_icon": TYPES["greedy"]["icon"],
    "priority": 4,
    "difficulty": "Easy",
    "icon": "🎯",
    "kind": "array",
    "complexity": {
        "best": "O(n log n) — dominated by the sort",
        "average": "O(n log n)",
        "worst": "O(n log n)",
        "space": "O(1) auxiliary (plus output)",
        "stable": "n/a",
        "in_place": "Yes",
    },
    "what": (
        "A greedy algorithm builds a solution one choice at a time, always taking the option that looks "
        "best right now and never revisiting it. Activity selection is the canonical example: to fit the "
        "most non-overlapping activities, sort by finish time and repeatedly take the first activity that "
        "starts at or after the previous one ends. Choosing by earliest finish leaves the most room for "
        "everything that follows — a locally optimal move that is also globally safe."
    ),
    "why": (
        "When a problem has the greedy-choice property, greedy gives provably optimal answers in one "
        "linear scan after a sort — dramatically simpler and faster than dynamic programming. Recognising "
        "that property (and proving it with the exchange argument: any optimal solution can be swapped to "
        "include the greedy choice without loss) is a core algorithm-design skill, and activity selection "
        "is the standard first proof."
    ),
    "when_needed": [
        "Scheduling non-overlapping intervals (meetings, jobs, broadcasts, lab equipment).",
        "The problem offers an exchange argument: keeping the greedy choice never hurts optimality.",
        "One sorted pass suffices and DP's extra dimension would be wasted effort.",
        "A reasonably good answer fast is acceptable even where optimality is unproven (heuristics).",
    ],
    "how_to_select": [
        "Sort by the quantity you want to leave maximal room for — earliest FINISH for interval scheduling.",
        "Prove greedy-choice + optimal substructure before trusting the result; test against brute force on small inputs.",
        "Ties: any consistent tie-break is fine for activity selection (all maximal sets have equal size).",
        "If greedy's answer is wrong on some case, look for DP (e.g. weighted intervals need DP, not greedy).",
        "Watch boundary conditions: touching intervals (start == previous finish) are compatible here.",
    ],
    "when_not": [
        "Weighted interval scheduling — earliest-finish is not optimal; DP over finish times is.",
        "0/1 knapsack — greedy by value/weight ratio fails; DP required (fractional knapsack IS greedy-safe).",
        "Choices interact far in the future with no provable local guarantee — greedy can be arbitrarily bad.",
        "You must guarantee optimality under adversarial inputs but cannot produce an exchange argument.",
    ],
    "outline": [
        "Greedy paradigm: irrevocable local choices, one pass after sorting",
        "Greedy-choice property + optimal substructure = provable optimality",
        "Exchange argument: swap any optimal solution to contain the greedy pick",
        "Activity selection: sort by finish, take if start >= last end — O(n log n)",
        "Counterexamples teach the limits: weighted intervals and 0/1 knapsack break naive greedy",
    ],
    "applications": [
        {"title": "Meeting-room and lab scheduling", "detail": "Calendar tools and booking systems fit the most sessions into shared rooms with exactly this sweep."},
        {"title": "Broadcast & advertisement slots", "detail": "Maximising aired spots in fixed windows uses interval scheduling (or its weighted DP variant)."},
        {"title": "Task scheduling in OS/CI runners", "detail": "Greedy ordering heuristics decide job placement before more expensive optimisers run."},
        {"title": "Foundation for other greedy proofs", "detail": "Huffman, MST (cut property), and fractional knapsack all lean on the same exchange-argument technique."},
    ],
    "impl_c": GREEDY_C,
    "impl_cpp": GREEDY_CPP,
    "impl_py": GREEDY_PY,
    "sim": sim_greedy,
    "references": [
        {"title": "GeeksforGeeks — Activity Selection Problem (reference)", "url": "https://www.geeksforgeeks.org/activity-selection-problem-greedy-algo-1/"},
        {"title": "GeeksforGeeks — Greedy Algorithms (reference)", "url": "https://www.geeksforgeeks.org/greedy-algorithms/"},
    ],
}


# ---------------------------------------------------------------------------
# Topic: Fractional Knapsack
# ---------------------------------------------------------------------------

def sim_fractional_knapsack():
    """Trace the greedy fill: sort by value/weight, take items until the
    capacity runs out, then take a fraction (array renderer)."""
    items = [
        {"value": 60, "weight": 10},
        {"value": 100, "weight": 20},
        {"value": 120, "weight": 30},
    ]
    capacity = 50
    items.sort(key=lambda it: it["value"] / it["weight"], reverse=True)
    ratios = [round(it["value"] / it["weight"], 2) for it in items]
    out = []
    taken = []

    def emit(caption, highlights=(), done=False):
        out.append({
            "kind": "array",
            "data": list(ratios),
            "highlights": list(highlights),
            "compare": [],
            "swap": list(taken),
            "markers": {},
            "caption": caption,
            "done": done,
        })

    emit("Sort items by value/weight ratio (bars = ratio): 6.0, 5.0, 4.0 — capacity 50", ())
    remaining = capacity
    total = 0.0
    for i, it in enumerate(items):
        if remaining <= 0:
            emit(f"Knapsack full — nothing left for item {i} (ratio {ratios[i]})", (i,))
            continue
        if it["weight"] <= remaining:
            taken.append(i)
            total += it["value"]
            remaining -= it["weight"]
            emit(f"Item {i} (value {it['value']}, weight {it['weight']}) fits whole -> take it. "
                 f"Value so far {total:.0f}, capacity left {remaining}", (i,))
        else:
            frac = remaining / it["weight"]
            gain = frac * it["value"]
            taken.append(i)
            total += gain
            emit(f"Item {i} (value {it['value']}, weight {it['weight']}) too big -> take "
                 f"{frac * 100:.0f}% of it (worth {gain:.0f}). Total value {total:.0f}", (i,))
            remaining = 0
    emit(f"Optimal value = {total:.0f} — greedy by ratio is provably optimal here "
         "(fractional goods are divisible)", (), done=True)
    return out


FRACTIONAL_C = r'''#include <stdio.h>

typedef struct { double value, weight; } Item;

/* Greedy: sort by value/weight descending, take whole items while they fit,
 * then one fraction. O(n log n); optimal because goods are divisible. */
double fractional_knapsack(Item items[], int n, double capacity) {
    for (int i = 1; i < n; i++) {           /* insertion sort by ratio desc */
        Item key = items[i];
        int j = i - 1;
        while (j >= 0 && items[j].value / items[j].weight < key.value / key.weight) {
            items[j + 1] = items[j];
            j--;
        }
        items[j + 1] = key;
    }
    double total = 0.0;
    for (int i = 0; i < n && capacity > 0; i++) {
        if (items[i].weight <= capacity) {
            total += items[i].value;
            capacity -= items[i].weight;
        } else {
            total += items[i].value * (capacity / items[i].weight);
            capacity = 0;
        }
    }
    return total;
}

int main(void) {
    Item items[] = {{60, 10}, {100, 20}, {120, 30}};
    Item copy1[3], copy2[3], copy3[3];
    for (int i = 0; i < 3; i++) copy1[i] = items[i];
    printf("Test 1: max value = %.2f\n", fractional_knapsack(copy1, 3, 50.0));

    for (int i = 0; i < 3; i++) copy2[i] = items[i];
    printf("Test 2: max value = %.2f\n", fractional_knapsack(copy2, 3, 0.0));

    for (int i = 0; i < 3; i++) copy3[i] = items[i];
    printf("Test 3: max value = %.2f\n", fractional_knapsack(copy3, 3, 1000.0));
    return 0;
}
'''


FRACTIONAL_CPP = r'''#include <algorithm>
#include <iomanip>
#include <iostream>
#include <vector>
using namespace std;

struct Item { double value, weight; };

/* Greedy by value/weight ratio, descending. Optimal because goods are
 * divisible: any optimal solution can be exchanged (swap argument) into
 * this one without losing value. O(n log n). */
double fractionalKnapsack(vector<Item> items, double capacity) {
    sort(items.begin(), items.end(), [](const Item& a, const Item& b) {
        return a.value / a.weight > b.value / b.weight;
    });
    double total = 0.0;
    for (const Item& it : items) {
        if (capacity <= 0) break;
        if (it.weight <= capacity) {
            total += it.value;
            capacity -= it.weight;
        } else {
            total += it.value * (capacity / it.weight);
            capacity = 0;
        }
    }
    return total;
}

int main() {
    vector<Item> items = {{60, 10}, {100, 20}, {120, 30}};
        cout << fixed << setprecision(2);
    cout << "Test 1: max value = " << fractionalKnapsack(items, 50.0) << "\n";
    cout << "Test 2: max value = " << fractionalKnapsack(items, 0.0) << "\n";
    cout << "Test 3: max value = " << fractionalKnapsack(items, 1000.0) << "\n";
    return 0;
}
'''


FRACTIONAL_PY = r'''def fractional_knapsack(items, capacity):
    """items: list of (value, weight). Returns the max total value when
    goods are divisible. Greedy by value/weight ratio; O(n log n)."""
    total = 0.0
    for value, weight in sorted(items, key=lambda it: it[0] / it[1], reverse=True):
        if capacity <= 0:
            break
        if weight <= capacity:
            total += value
            capacity -= weight
        else:
            total += value * (capacity / weight)
            capacity = 0
    return total


if __name__ == "__main__":
    items = [(60, 10), (100, 20), (120, 30)]
    print(f"Test 1: max value = {fractional_knapsack(items, 50.0):.2f}")
    print(f"Test 2: max value = {fractional_knapsack(items, 0.0):.2f}")
    print(f"Test 3: max value = {fractional_knapsack(items, 1000.0):.2f}")
'''
TOPIC_FRACTIONAL = {
    "id": "fractional-knapsack",
    "name": "Fractional Knapsack",
    "slug": "fractional-knapsack",
    "type": "greedy",
    "type_label": TYPES["greedy"]["label"],
    "type_icon": TYPES["greedy"]["icon"],
    "priority": 4,
    "difficulty": "Easy",
    "icon": "🎒",
    "kind": "array",
    "complexity": {
        "best": "O(n log n) — sorting dominates",
        "average": "O(n log n)",
        "worst": "O(n log n)",
        "space": "O(1) extra (in-place sort) — O(n) if input must be preserved",
        "stable": "n/a",
        "in_place": "Yes (sorts a copy of the item list)",
    },
    "what": (
        "The knapsack problem: choose items with given values and weights to maximise total value "
        "under a weight capacity. In the fractional variant you may cut items and take any portion, "
        "keeping the matching fraction of value. That single change makes the greedy strategy "
        "provably optimal: sort by value-to-weight ratio and fill the bag with the densest items first."
    ),
    "why": (
        "Fractional knapsack is the textbook demonstration that greedy can be EXACT, not just a "
        "heuristic — and it teaches why the same greedy fails for 0/1 knapsack ( indivisible items "
        "leave holes no ratio-sort can repair; DP is needed there). The ratio-sort pattern itself "
        "recurs constantly: scheduling by density, bandwidth allocation, resource rationing."
    ),
    "when_needed": [
        "Goods are divisible: fuel, grain, bandwidth, budget shares, liquid/dust commodities.",
        "You need a provably optimal answer in a single sort plus one linear scan.",
        "An upper bound is required for branch-and-bound on the 0/1 version.",
        "Teaching or interviewing: the cleanest contrast between greedy-optimal and greedy-fails.",
    ],
    "how_to_select": [
        "Items divisible → greedy by ratio; items indivisible → 0/1 DP instead.",
        "Sort by value/weight descending, take whole items while they fit, then one fraction.",
        "Ties in ratio: order does not matter for value, but prefer lighter items to leave capacity flexible.",
        "If weights are huge doubles, watch out for division precision — compare cross-multiplied ratios.",
        "Capacity 0 or no items → answer 0; the code's tests cover both edges.",
    ],
    "when_not": [
        "Items cannot be split — the greedy answer can be arbitrarily wrong; use 0/1 knapsack DP.",
        "Multiple constraints (weight AND volume) — ratio sorting no longer decides; need DP or LP.",
        "Items have dependencies/conflicts — the problem stops being a plain knapsack.",
        "You need the item-level selection under integrality — greedy's fractional cut is not executable.",
    ],
    "outline": [
        "Compute value/weight density for every item",
        "Sort items by density, descending — O(n log n)",
        "Take whole items while capacity allows; track remaining capacity",
        "For the first item that does not fit, take the fraction capacity/weight and stop",
        "Proof idea: exchange argument — any solution not density-ordered can be swapped into one without losing value",
        "Contrast: the identical greedy fails for indivisible (0/1) items — that needs DP",
    ],
    "applications": [
        {"title": "Load and cargo planning", "detail": "Shipping and fuel loading split fractions of goods to maximise value per kilogram carried."},
        {"title": "Bandwidth / budget allocation", "detail": "Allocating divisible resources (link capacity, ad budget) by return-per-unit is exactly this greedy."},
        {"title": "Branch-and-bound bounds", "detail": "The fractional optimum is the classic upper bound that prunes 0/1 knapsack search trees."},
        {"title": "Combinatorial auctions and admissions", "detail": "Pro-rata fill by bid density mirrors fractional knapsack's ratio rule."},
    ],
    "impl_c": FRACTIONAL_C,
    "impl_cpp": FRACTIONAL_CPP,
    "impl_py": FRACTIONAL_PY,
    "sim": sim_fractional_knapsack,
    "references": [
        {"title": "GeeksforGeeks — Fractional Knapsack Problem (reference)", "url": "https://www.geeksforgeeks.org/fractional-knapsack-problem/"},
    ],
}


# ---------------------------------------------------------------------------
# Topic: Huffman Coding
# ---------------------------------------------------------------------------

TOPIC_HUFFMAN = {
    "id": "huffman-coding",
    "name": "Huffman Coding",
    "slug": "huffman-coding",
    "type": "greedy",
    "type_label": TYPES["greedy"]["label"],
    "type_icon": TYPES["greedy"]["icon"],
    "priority": 3,
    "difficulty": "Medium",
    "icon": "🗜️",
    "kind": "array",
    "complexity": {
        "best": "O(n log n)",
        "average": "O(n log n)",
        "worst": "O(n log n)",
        "space": "O(n) for the heap + O(L) code table",
        "stable": "n/a",
        "in_place": "Builds an auxiliary tree",
    },
    "what": (
        "Huffman coding is a prefix-free variable-length code built from symbol frequencies. It greedily "
        "merges the two least-frequent symbols into a new node, repeating until one tree remains. The "
        "path to each leaf (left = 0, right = 1) is that symbol's code, so frequent symbols get short "
        "codes and rare symbols get long ones — and because no code is a prefix of another, the encoded "
        "bit stream decodes unambiguously."
    ),
    "why": (
        "Fixed-width encoding ignores that symbols are unequal: in English text 'e' appears ~12% of the "
        "time while 'z' appears ~0.07%. Huffman lets 'e' cost ~3 bits instead of 8, cutting average file "
        "size toward the entropy limit. It is greedy and provably optimal among symbol-by-symbol prefix "
        "codes, and it is the conceptual core of DEFLATE (gzip, PNG), JPEG DC, and MP3's Huffman tables."
    ),
    "when_needed": [
        "Lossless compression where symbol probabilities are known or estimated.",
        "A prefix code is required (no codeword may be a prefix of another).",
        "Building the entropy lower bound for a source or as a stage in a larger compressor.",
        "Teaching greedy optimality via an exchange argument (frequent symbols get shorter codes).",
    ],
    "how_to_select": [
        "Need a prefix code AND frequencies: Huffman (or arithmetic coding for near-entropy on skewed sources).",
        "Static known distribution → build one tree; streaming/unknown → adaptive Huffman or arithmetic.",
        "Ties in frequency: any deterministic order works — the code length is still optimal; code strings may differ.",
        "Decoding needs the tree (or canonical code tables) on the other side — transmit it first.",
        "Small alphabet? The tree is tiny and the merge loop is fast; for huge alphabets use a heap.",
    ],
    "when_not": [
        "Frequencies change over time (non-stationary source) — rebuild or use adaptive methods.",
        "You need arithmetic-level compactness or near-entropy on highly skewed sources — arithmetic coding wins.",
        "Symbols are equiprobable — Huffman degenerates to fixed-width, no savings.",
        "Blocking/combo coding matters — higher-order or dictionary methods (LZ77/LZ78) outperform symbol-wise Huffman.",
    ],
    "outline": [
        "Compute frequency of every symbol",
        "Push all symbols as leaf nodes into a min-heap keyed by frequency",
        "Pop the two smallest, merge them into one internal node (weight = sum), re-insert",
        "Repeat until one node remains — that root defines the code tree",
        "Walk to each leaf: left edge = 0, right edge = 1 → variable-length prefix code",
        "Expected code length approaches the entropy of the source; always optimal among prefix codes",
    ],
    "applications": [
        {"title": "File and image compression", "detail": "DEFLATE (gzip/zip/PNG) builds Huffman tables over literal/length symbols after LZ77 back-references."},
        {"title": "JPEG and MP3", "detail": "JPEG DC coefficients are Huffman-coded; MP3's encoder/decoder side-info uses Huffman tables."},
        {"title": "Network protocols", "detail": "Compact integer encodings (HTTP/2 prefixes, HPACK headers) use Huffman to shrink text sent wire-to-wire."},
        {"title": "Cache-conscious layouts", "detail": "Frequently-accessed symbols get shorter bit patterns, improving packed-structure and trie-cache efficiency."},
    ],
    "impl_c": HUFFMAN_C,
    "impl_cpp": HUFFMAN_CPP,
    "impl_py": HUFFMAN_PY,
    "sim": sim_huffman,
    "references": [
        {"title": "GeeksforGeeks — Huffman Coding Algorithm (reference)", "url": "https://www.geeksforgeeks.org/program-for-huffman-coding-greedy-algo-4/"},
    ],
}


# ---------------------------------------------------------------------------
# Topic: Job Sequencing with Deadlines
# ---------------------------------------------------------------------------

def sim_job_sequencing():
    """Trace greedy job sequencing: sort by profit, slot each job (array renderer)."""
    jobs = [
        {"id": "a", "deadline": 2, "profit": 100},
        {"id": "b", "deadline": 1, "profit": 19},
        {"id": "c", "deadline": 2, "profit": 27},
        {"id": "d", "deadline": 1, "profit": 25},
        {"id": "e", "deadline": 3, "profit": 15},
    ]
    out = []

    def emit(caption, slots, highlights=(), done=False):
        out.append({
            "kind": "array",
            "data": [s or "-" for s in slots],
            "highlights": list(highlights),
            "compare": [],
            "swap": [],
            "markers": {},
            "caption": caption,
            "done": done,
        })

    for j in jobs:
        emit(f"Sorted by profit: job {j['id']} (profit {j['profit']}, deadline {j['deadline']})", [None] * 3)
    slots = [None] * 3
    taken = []
    for j in jobs:
        placed = False
        for t in range(min(j["deadline"], 3) - 1, -1, -1):
            if slots[t] is None:
                slots[t] = j["id"]
                taken.append(j["profit"])
                emit(f"Job {j['id']} (profit {j['profit']}): latest free slot <= deadline {j['deadline']} is slot {t}",
                     slots, [t])
                placed = True
                break
        if not placed:
            emit(f"Job {j['id']} (profit {j['profit']}): no free slot <= deadline {j['deadline']} — skip", slots)
    emit(f"Done — scheduled {len(taken)} jobs, total profit = {sum(taken)}", slots, done=True)
    return out


JOB_SEQ_C = r'''#include <stdio.h>
#include <stdlib.h>

typedef struct { int id, deadline, profit; } Job;

int cmp_job(const void *a, const void *b) {
    return ((Job *)b)->profit - ((Job *)a)->profit;
}

int job_sequencing(Job jobs[], int n, int slot_out[]) {
    qsort(jobs, n, sizeof(Job), cmp_job);
    int max_d = 0, count = 0;
    for (int i = 0; i < n; i++) if (jobs[i].deadline > max_d) max_d = jobs[i].deadline;
    int *slot = (int *)calloc(max_d + 1, sizeof(int));
    for (int i = 0; i < n; i++) {
        for (int t = jobs[i].deadline; t >= 1; t--) {
            if (!slot[t]) {
                slot[t] = jobs[i].id;
                slot_out[count++] = jobs[i].id;
                break;
            }
        }
    }
    free(slot);
    return count;
}

int main(void) {
    Job jobs[] = {{1, 2, 100}, {2, 1, 19}, {3, 2, 27}, {4, 1, 25}, {5, 3, 15}};
    int n = 5, slot_out[5], total = 0;
    int count = job_sequencing(jobs, n, slot_out);
    printf("Test 1: scheduled %d jobs ->", count);
    for (int i = 0; i < count; i++) printf(" id%d", slot_out[i]);
    printf("\n");
    for (int i = 0; i < n; i++)
        for (int j = 0; j < count; j++)
            if (jobs[i].id == slot_out[j]) total += jobs[i].profit;
    printf("Test 2: total profit = %d\n", total);
    return 0;
}
'''


JOB_SEQ_CPP = r'''#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

struct Job { int id, deadline, profit; };

vector<int> jobSequencing(vector<Job> jobs) {
    sort(jobs.begin(), jobs.end(),
         [](const Job& a, const Job& b) { return a.profit > b.profit; });
    int max_d = 0;
    for (const auto& j : jobs) max_d = max(max_d, j.deadline);
    vector<int> slot(max_d + 1, 0);
    vector<int> scheduled;
    for (const auto& j : jobs) {
        for (int t = j.deadline; t >= 1; t--) {
            if (!slot[t]) {
                slot[t] = j.id;
                scheduled.push_back(j.id);
                break;
            }
        }
    }
    return scheduled;
}

int main() {
    vector<Job> jobs = {{1, 2, 100}, {2, 1, 19}, {3, 2, 27}, {4, 1, 25}, {5, 3, 15}};
    auto seq = jobSequencing(jobs);
    int total = 0;
    cout << "Test 1: scheduled " << seq.size() << " jobs ->";
    for (int id : seq) {
        cout << " id" << id;
        for (const auto& j : jobs) if (j.id == id) total += j.profit;
    }
    cout << "\nTest 2: total profit = " << total << "\n";
    return 0;
}
'''


JOB_SEQ_PY = r'''from operator import itemgetter


def job_sequencing(jobs):
    """Greedy: sort by profit desc, slot each job before its deadline."""
    jobs = sorted(jobs, key=itemgetter("profit"), reverse=True)
    max_d = max(j["deadline"] for j in jobs)
    slot = [None] * (max_d + 1)
    scheduled = []
    for j in jobs:
        for t in range(j["deadline"], 0, -1):
            if slot[t] is None:
                slot[t] = j["id"]
                scheduled.append(j["id"])
                break
    return scheduled


if __name__ == "__main__":
    jobs = [
        {"id": 1, "deadline": 2, "profit": 100},
        {"id": 2, "deadline": 1, "profit": 19},
        {"id": 3, "deadline": 2, "profit": 27},
        {"id": 4, "deadline": 1, "profit": 25},
        {"id": 5, "deadline": 3, "profit": 15},
    ]
    seq = job_sequencing(jobs)
    by_id = {j["id"]: j for j in jobs}
    total = sum(by_id[i]["profit"] for i in seq)
    print(f"Test 1: scheduled {len(seq)} jobs -> {' '.join(f'id{i}' for i in seq)}")
    print(f"Test 2: total profit = {total}")
'''
TOPIC_JOB_SEQ = {
    "id": "job-sequencing",
    "name": "Job Sequencing with Deadlines",
    "slug": "job-sequencing",
    "type": "greedy",
    "type_label": TYPES["greedy"]["label"],
    "type_icon": TYPES["greedy"]["icon"],
    "priority": 3,
    "difficulty": "Medium",
    "icon": "📅",
    "kind": "array",
    "complexity": {
        "best": "O(n log n) with DSU; O(n²) naive",
        "average": "O(n²)",
        "worst": "O(n²)",
        "space": "O(d) for d deadline slots",
        "stable": "n/a",
        "in_place": "Uses a slot array",
    },
    "what": (
        "Job sequencing schedules jobs with deadlines and profits to maximise total profit. Each job "
        "takes one unit of time and must finish by its deadline. The greedy rule is: sort jobs by "
        "profit descending, then place each job in the latest free time slot at or before its deadline "
        "— keeping earlier slots open for more jobs."
    ),
    "why": (
        "This is the canonical greedy scheduling proof: placing a high-profit job as late as possible "
        "never hurts feasibility, and an exchange argument shows any optimal schedule can be rearranged "
        "into the greedy one without losing profit. It is the simplest model where 'do the most valuable "
        "thing, as late as you can' is optimal."
    ),
    "when_needed": [
        "Each task takes unit time and has a deadline + profit/weight.",
        "You want the maximum-profit subset of jobs that can all meet their deadlines.",
        "Tasks are independent (no precedence constraints beyond the deadline).",
        "Teaching greedy exchange-argument proofs.",
    ],
    "how_to_select": [
        "Sort by profit descending — always schedule the most valuable job you can.",
        "Place each job in the latest free slot ≤ its deadline (keeps earlier slots open).",
        "For large instances, replace the O(n²) slot scan with a DSU 'next free slot' structure.",
        "If jobs have different durations, the problem becomes NP-hard — this greedy no longer applies.",
        "Need to also output the actual schedule? The slot array already encodes it.",
    ],
    "when_not": [
        "Jobs have arbitrary (non-unit) durations — the problem is NP-hard; use ILP or approximation.",
        "There are precedence constraints — this is job-shop scheduling, not job sequencing.",
        "All profits are equal — any feasible schedule is optimal; just maximise count.",
        "Deadlines are soft (can be missed with a penalty) — that is a different optimisation problem.",
    ],
    "outline": [
        "Sort jobs by profit descending",
        "For each job, find the latest free slot ≤ its deadline",
        "If a slot exists, schedule the job there; otherwise skip it",
        "Greedy is optimal: exchange argument swaps any optimal schedule toward the greedy one",
        "O(n²) naive; DSU 'next-free-slot' reduces to near O(n log n)",
    ],
    "applications": [
        {"title": "Task scheduling", "detail": "OS/CI runners pick the highest-value jobs that still fit within their deadline windows."},
        {"title": "Manufacturing", "detail": "High-value orders are slotted into the latest feasible machine-time window."},
        {"title": "Ad auction pacing", "detail": "Ad platforms schedule the highest-paying impressions before their expiry windows close."},
        {"title": "Course planning", "detail": "Students pick assignments to maximise grade-weighted on-time submissions."},
    ],
    "impl_c": JOB_SEQ_C,
    "impl_cpp": JOB_SEQ_CPP,
    "impl_py": JOB_SEQ_PY,
    "sim": sim_job_sequencing,
    "references": [
        {"title": "GeeksforGeeks — Job Sequencing Problem (reference)", "url": "https://www.geeksforgeeks.org/job-sequencing-problem/"},
    ],
}


# ---------------------------------------------------------------------------
# Topic: DP Fundamentals
# ---------------------------------------------------------------------------

def sim_dp_fundamentals():
    """Trace Fibonacci tabulation (array renderer)."""
    out = []

    def emit(caption, data, highlights=(), done=False):
        out.append({
            "kind": "array",
            "data": list(data),
            "highlights": list(highlights),
            "compare": [],
            "swap": [],
            "markers": {},
            "caption": caption,
            "done": done,
        })

    fib = [0, 1, None, None, None, None, None, None, None, None]
    emit("Tabulation: fib[0]=0, fib[1]=1 — fill bottom-up", fib, [0, 1])
    for i in range(2, 10):
        fib[i] = fib[i - 1] + fib[i - 2]
        emit(f"fib[{i}] = fib[{i-1}] + fib[{i-2}] = {fib[i-1]} + {fib[i-2]} = {fib[i]}", fib, [i])
    emit("Done — every fib[i] computed once, O(n) time, O(1) extra space possible", fib, done=True)
    return out


DP_FUND_C = r'''#include <stdio.h>

/* Tabulation: bottom-up, O(n) time, O(1) extra space. */
int fib_tab(int n) {
    if (n <= 1) return n;
    int a = 0, b = 1;
    for (int i = 2; i <= n; i++) { int c = a + b; a = b; b = c; }
    return b;
}

/* Memoization: top-down with a cache, O(n) time. */
int memo[100];
int fib_memo(int n) {
    if (n <= 1) return n;
    if (memo[n] != -1) return memo[n];
    return memo[n] = fib_memo(n - 1) + fib_memo(n - 2);
}

int main(void) {
    for (int i = 0; i < 100; i++) memo[i] = -1;
    printf("Test 1 (tabulation): ");
    for (int i = 0; i < 10; i++) printf("%d ", fib_tab(i));
    printf("\n");
    printf("Test 2 (memoization): ");
    for (int i = 0; i < 10; i++) printf("%d ", fib_memo(i));
    printf("\n");
    printf("Test 3: fib_tab(20) = %d\n", fib_tab(20));
    printf("Test 4: fib_memo(20) = %d\n", fib_memo(20));
    return 0;
}
'''


DP_FUND_CPP = r'''#include <iostream>
#include <vector>
using namespace std;

/* Tabulation: bottom-up, O(n) time, O(1) extra space. */
int fibTab(int n) {
    if (n <= 1) return n;
    int a = 0, b = 1;
    for (int i = 2; i <= n; i++) { int c = a + b; a = b; b = c; }
    return b;
}

/* Memoization: top-down with a cache. */
vector<int> memo(100, -1);
int fibMemo(int n) {
    if (n <= 1) return n;
    if (memo[n] != -1) return memo[n];
    return memo[n] = fibMemo(n - 1) + fibMemo(n - 2);
}

int main() {
    cout << "Test 1 (tabulation): ";
    for (int i = 0; i < 10; i++) cout << fibTab(i) << " ";
    cout << "\nTest 2 (memoization): ";
    for (int i = 0; i < 10; i++) cout << fibMemo(i) << " ";
    cout << "\nTest 3: fibTab(20) = " << fibTab(20) << "\n";
    cout << "Test 4: fibMemo(20) = " << fibMemo(20) << "\n";
    return 0;
}
'''


DP_FUND_PY = r'''def fib_tab(n):
    """Tabulation: bottom-up, O(n) time, O(1) extra space."""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def fib_memo(n, cache=None):
    """Memoization: top-down with a cache."""
    if cache is None:
        cache = {}
    if n <= 1:
        return n
    if n in cache:
        return cache[n]
    cache[n] = fib_memo(n - 1, cache) + fib_memo(n - 2, cache)
    return cache[n]


if __name__ == "__main__":
    print("Test 1 (tabulation):", " ".join(str(fib_tab(i)) for i in range(10)))
    print("Test 2 (memoization):", " ".join(str(fib_memo(i)) for i in range(10)))
    print(f"Test 3: fib_tab(20) = {fib_tab(20)}")
    print(f"Test 4: fib_memo(20) = {fib_memo(20)}")
'''
TOPIC_DP_FUND = {
    "id": "dp-fundamentals",
    "name": "Dynamic Programming Fundamentals",
    "slug": "dp-fundamentals",
    "type": "dp",
    "type_label": TYPES["dp"]["label"],
    "type_icon": TYPES["dp"]["icon"],
    "priority": 5,
    "difficulty": "Medium",
    "icon": "🧬",
    "kind": "grid",
    "complexity": {
        "best": "O(n) for Fibonacci DP",
        "average": "Problem-dependent: O(states × transition)",
        "worst": "O(states × transition)",
        "space": "O(states) table, reducible in Fibonacci to O(1)",
        "stable": "n/a",
        "in_place": "Table is filled in place",
    },
    "what": (
        "Dynamic programming solves a problem by breaking it into overlapping subproblems, solving each "
        "only once, and reusing those answers. The Fibonacci sequence is the classic classroom example: "
        "naive recursion recomputes fib(3) exponentially many times, while memoization (a top-down cache) "
        "or tabulation (a bottom-up table) brings it down to linear time."
    ),
    "why": (
        "Many real problems — shortest paths, string alignment, knapsack, scheduling — share two "
        "properties: optimal substructure (an optimal solution contains optimal subsolutions) and "
        "overlapping subproblems (the same subcase recurs). Recognizing that pair and choosing memoization "
        "vs tabulation turns exponential brute force into polynomial work. This topic teaches that "
        "decision once; every later DP topic is a new state definition on top of the same skeleton."
    ),
    "when_needed": [
        "The problem asks for an optimum (min / max / count) and the input size rules out brute force.",
        "Overlapping subproblems are visible — the same subcase appears in many recursion branches.",
        "Optimal substructure holds: optimal global choices subsume optimal subsolutions.",
        "Recursive backtracking is correct but too slow — caching the recursion is the natural fix.",
    ],
    "how_to_select": [
        "Memoization (top-down) is quick to add to an existing correct recursion — cache, return cache hits.",
        "Tabulation (bottom-up) is usually faster (no recursion overhead) and easier to space-optimize.",
        "State = the parameters a subproblem depends on. Fibonacci needs one index; knapsack needs index + capacity.",
        "If every state depends only on earlier ones, fill in order; if dependencies are complex, memoize.",
        "Start with the recurrence (the 'DP relation'), then decide memo vs tab, then optimize space.",
    ],
    "when_not": [
        "Subproblems do NOT overlap — plain divide and conquer (merge sort) avoids the DP table's overhead.",
        "Greedy choice works — greedy is simpler and O(n log n) or better (activity selection, Dijkstra).",
        "The state space explodes (2^n subsets, large dimensions) — DP can't hold the table.",
        "You only need one path, not the optimum — or the optimum has no optimal substructure.",
    ],
    "outline": [
        "Optimal substructure + overlapping subproblems = DP territory",
        "Memoization: top-down recursion with a cache (minimal code change from brute force)",
        "Tabulation: bottom-up table fill, no recursion overhead",
        "Space optimization: keep only the last row(s) — Fibonacci drops to O(1)",
        "Fibonacci illustrates the full progression: naive → memo → tab → O(1)",
        "The same pattern (define state, write recurrence, fill/cache) underlies every DP topic here",
    ],
    "applications": [
        {"title": "Every later topic in this section", "detail": "Knapsack, LCS, LIS, coin change, and matrix chain are the same memo/tab skeleton with different states."},
        {"title": "Compiler register allocation", "detail": "Chaitin-style graph-coloring heuristics use DP substructure over intervals."},
        {"title": "Version control diff", "detail": "The longest-common-subsequence DP that powers `diff` and merge tools is covered in its own topic."},
        {"title": "Financial / operations optimization", "detail": "Multi-stage portfolio and production scheduling problems are textbook DP over time stages."},
    ],
    "impl_c": DP_FUND_C,
    "impl_cpp": DP_FUND_CPP,
    "impl_py": DP_FUND_PY,
    "sim": sim_dp_fundamentals,
    "references": [
        {"title": "GeeksforGeeks — Dynamic Programming (reference)", "url": "https://www.geeksforgeeks.org/dynamic-programming/"},
    ],
}


# ---------------------------------------------------------------------------
# Topic: 0/1 Knapsack & Subset Sum
# ---------------------------------------------------------------------------

def sim_knapsack():
    """Trace the DP table for a 0/1 knapsack (grid renderer)."""
    wt = [2, 3, 4]
    val = [3, 4, 5]
    W = 5
    n = len(wt)
    out = []

    def emit(caption, cur, done=False):
        out.append({
            "kind": "grid",
            "rows": n + 1,
            "cols": W + 1,
            "cur": cur,
            "caption": caption,
            "done": done,
        })

    emit("DP table: rows = items considered, cols = capacity 0..W. Fill row by row.", None)
    dp = [[0] * (W + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for c in range(W + 1):
            dp[i][c] = dp[i - 1][c]
            if wt[i - 1] <= c:
                take = dp[i - 1][c - wt[i - 1]] + val[i - 1]
                if take > dp[i][c]:
                    dp[i][c] = take
                    emit(f"Item {i} (w={wt[i-1]}, v={val[i-1]}) fits in cap {c}: "
                         f"skip={dp[i-1][c]} vs take={take} -> take it", (i, c))
                else:
                    emit(f"Item {i} fits in cap {c} but skip={dp[i-1][c]} >= take={take} -> skip", (i, c))
            else:
                emit(f"Item {i} (w={wt[i-1]}) too heavy for cap {c} -> carry forward {dp[i-1][c]}", (i, c))
    emit(f"Done — best value for capacity {W} is {dp[n][W]} (items 1 and 2, weight 5, value 7)",
         None, done=True)
    return out


KNAPSACK_C = r'''#include <stdio.h>

#define MAXN 100
#define MAXW 100

/* 0/1 knapsack: dp[i][c] = best value using items 0..i-1 with capacity c. */
int knapsack(int wt[], int val[], int n, int W) {
    int dp[MAXN + 1][MAXW + 1] = {0};
    for (int i = 1; i <= n; i++) {
        for (int c = 0; c <= W; c++) {
            dp[i][c] = dp[i - 1][c];
            if (wt[i - 1] <= c) {
                int take = dp[i - 1][c - wt[i - 1]] + val[i - 1];
                if (take > dp[i][c]) dp[i][c] = take;
            }
        }
    }
    return dp[n][W];
}

/* Subset sum: can a subset of wt[] sum exactly to W? */
int subset_sum(int wt[], int n, int W) {
    int dp[MAXN + 1][MAXW + 1] = {0};
    for (int i = 0; i <= n; i++) dp[i][0] = 1;
    for (int i = 1; i <= n; i++) {
        for (int c = 0; c <= W; c++) {
            dp[i][c] = dp[i - 1][c];
            if (wt[i - 1] <= c && dp[i - 1][c - wt[i - 1]]) dp[i][c] = 1;
        }
    }
    return dp[n][W];
}

int main(void) {
    int wt1[] = {2, 3, 4}, val1[] = {3, 4, 5};
    int wt2[] = {1, 2, 3}, val2[] = {6, 10, 12};
    printf("Test 1: %d\n", knapsack(wt1, val1, 3, 5));   /* 7 */
    printf("Test 2: %d\n", knapsack(wt2, val2, 3, 5));   /* 22 */
    printf("Test 3: %d\n", subset_sum(wt1, 3, 5));       /* 1 (2+3) */
    printf("Test 4: %d\n", subset_sum(wt1, 3, 6));       /* 0 */
    return 0;
}
'''


KNAPSACK_CPP = r'''#include <iostream>
#include <vector>
using namespace std;

int knapsack(const vector<int>& wt, const vector<int>& val, int W) {
    int n = (int)wt.size();
    vector<vector<int>> dp(n + 1, vector<int>(W + 1, 0));
    for (int i = 1; i <= n; i++) {
        for (int c = 0; c <= W; c++) {
            dp[i][c] = dp[i - 1][c];
            if (wt[i - 1] <= c) {
                int take = dp[i - 1][c - wt[i - 1]] + val[i - 1];
                if (take > dp[i][c]) dp[i][c] = take;
            }
        }
    }
    return dp[n][W];
}

int subsetSum(const vector<int>& wt, int W) {
    int n = (int)wt.size();
    vector<vector<int>> dp(n + 1, vector<int>(W + 1, 0));
    for (int i = 0; i <= n; i++) dp[i][0] = 1;
    for (int i = 1; i <= n; i++) {
        for (int c = 0; c <= W; c++) {
            dp[i][c] = dp[i - 1][c];
            if (wt[i - 1] <= c && dp[i - 1][c - wt[i - 1]]) dp[i][c] = 1;
        }
    }
    return dp[n][W];
}

int main() {
    cout << "Test 1: " << knapsack({2, 3, 4}, {3, 4, 5}, 5) << "\n";   /* 7 */
    cout << "Test 2: " << knapsack({1, 2, 3}, {6, 10, 12}, 5) << "\n"; /* 22 */
    cout << "Test 3: " << subsetSum({2, 3, 4}, 5) << "\n";              /* 1 */
    cout << "Test 4: " << subsetSum({2, 3, 4}, 6) << "\n";              /* 0 */
    return 0;
}
'''


KNAPSACK_PY = r'''def knapsack(wt, val, W):
    """0/1 knapsack: dp[i][c] = best value using items 0..i-1 with capacity c."""
    n = len(wt)
    dp = [[0] * (W + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for c in range(W + 1):
            dp[i][c] = dp[i - 1][c]
            if wt[i - 1] <= c:
                take = dp[i - 1][c - wt[i - 1]] + val[i - 1]
                if take > dp[i][c]:
                    dp[i][c] = take
    return dp[n][W]


def subset_sum(wt, W):
    """Can a subset of wt sum exactly to W?"""
    n = len(wt)
    dp = [[0] * (W + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = 1
    for i in range(1, n + 1):
        for c in range(W + 1):
            dp[i][c] = dp[i - 1][c]
            if wt[i - 1] <= c and dp[i - 1][c - wt[i - 1]]:
                dp[i][c] = 1
    return dp[n][W]


if __name__ == "__main__":
    print(f"Test 1: {knapsack([2, 3, 4], [3, 4, 5], 5)}")    # 7
    print(f"Test 2: {knapsack([1, 2, 3], [6, 10, 12], 5)}")  # 22
    print(f"Test 3: {subset_sum([2, 3, 4], 5)}")              # 1
    print(f"Test 4: {subset_sum([2, 3, 4], 6)}")              # 0
'''
TOPIC_KNAPSACK = {
    "id": "knapsack-subset-sum",
    "name": "0/1 Knapsack & Subset Sum",
    "slug": "knapsack-subset-sum",
    "type": "dp",
    "type_label": TYPES["dp"]["label"],
    "type_icon": TYPES["dp"]["icon"],
    "priority": 5,
    "difficulty": "Medium",
    "icon": "🎒",
    "kind": "grid",
    "complexity": {
        "best": "O(n·W)",
        "average": "O(n·W)",
        "worst": "O(n·W)",
        "space": "O(n·W), reducible to O(W) rolling one dimension",
        "stable": "n/a",
        "in_place": "Table is filled in place",
    },
    "what": (
        "The 0/1 knapsack: given items with weights and values, pick the most valuable subset that fits "
        "in a capacity W — each item taken at most once. The DP state is dp[i][c] = the best value "
        "achievable with the first i items and capacity c, choosing per item whether to take or skip. "
        "Subset sum is the same structure as a decision variant: can the weights reach W exactly?"
    ),
    "why": (
        "Knapsack is the canonical 'choice' DP and the first place most learners see a genuinely "
        "two-dimensional state (index + capacity). The recurrence dp[i][c] = max(dp[i-1][c], "
        "dp[i-1][c-w]+v) recurs everywhere: resource allocation, budgeting, cargo loading, ad budgets, "
        "and cutting-stock problems. The rolling-array trick (keep one row, iterate c backwards) is a "
        "space-optimization pattern reused in coin change and subset sum."
    ),
    "when_needed": [
        "A capacity or budget constraint limits what you can pack.",
        "Each option is a binary take/skip with its own weight and value.",
        "You need the optimal subset, not just any feasible one.",
        "The decision form (subset sum) asks 'is exact weight W reachable?'",
    ],
    "how_to_select": [
        "Binary take/skip with a single resource constraint → 0/1 knapsack.",
        "Capacity W is modest (so n·W fits in memory); otherwise consider greedy/approximation.",
        "Need only the value? One row backwards. Need the actual items? Keep a keep/table or backtrack.",
        "Unbounded quantities? That's unbounded knapsack (coin change) — different loop direction.",
        "Decision form (exact reach) → subset sum, a boolean version of the same table.",
    ],
    "when_not": [
        "Fractional amounts allowed → greedy value/weight ratio is optimal (fractional knapsack).",
        "All items have the same value → a greedy heaviest-first or a simpler algorithm may do.",
        "W is huge (10^9) but weights are small → swap the DP dimension: DP over total value instead.",
        "You only need a quick feasible solution → greedy, not DP.",
    ],
    "outline": [
        "State: dp[i][c] = best value with first i items and capacity c",
        "Recurrence: dp[i][c] = max(skip, take) where take requires w_i <= c",
        "Initialize dp[0][*] = 0; fill row by row in O(n·W)",
        "Subset sum: boolean reachability dp[i][c] = dp[i-1][c] OR dp[i-1][c-w]",
        "Space optimization: one row, iterate c backwards to avoid reuse",
    ],
    "applications": [
        {"title": "Logistics and cargo", "detail": "Airlines, shipping, and trucks solve knapsack variants to maximize payload value within weight limits."},
        {"title": "Budget allocation", "detail": "Choosing projects or ads under a budget with projected returns is a direct knapsack model."},
        {"title": "Cryptocurrency", "detail": "The 'knapsack' Merkle-Hellman cryptosystem (now broken) was historically based on the subset-sum hardness."},
        {"title": "Manufacturing", "detail": "Cutting stock and material-nesting problems use knapsack to minimize offcut waste."},
    ],
    "impl_c": KNAPSACK_C,
    "impl_cpp": KNAPSACK_CPP,
    "impl_py": KNAPSACK_PY,
    "sim": sim_knapsack,
    "references": [
        {"title": "GeeksforGeeks — 0/1 Knapsack (reference)", "url": "https://www.geeksforgeeks.org/0-1-knapsack-problem-dp-10/"},
    ],
}


# ---------------------------------------------------------------------------
# Topic: Coin Change (Unbounded)
# ---------------------------------------------------------------------------

def sim_coin_change():
    """Trace the unbounded coin-change DP (grid renderer)."""
    coins = [1, 3, 4]
    amount = 6
    out = []

    def emit(caption, cur, done=False):
        out.append({
            "kind": "grid",
            "rows": len(coins) + 1,
            "cols": amount + 1,
            "cur": cur,
            "caption": caption,
            "done": done,
        })

    emit("DP table: rows = coins considered, cols = amount 0..A. dp=min coins per amount.", None)
    INF = amount + 1
    dp = [[INF] * (amount + 1) for _ in range(len(coins) + 1)]
    for i in range(len(coins) + 1):
        dp[i][0] = 0
    emit("Base: 0 coins needed for amount 0; INF for amount>0 with no coins.", None)
    for i in range(1, len(coins) + 1):
        c = coins[i - 1]
        for a in range(1, amount + 1):
            dp[i][a] = dp[i - 1][a]
            if c <= a and dp[i][a - c] + 1 < dp[i][a]:
                dp[i][a] = dp[i][a - c] + 1
                emit(f"Coin {c} usable for amount {a}: skip={dp[i-1][a]} vs use={dp[i][a]} -> use", (i, a))
            else:
                dp[i][a] = dp[i - 1][a]
                emit(f"Coin {c}: amount {a} can't use it (or skip is better) -> {dp[i][a]}", (i, a))
    emit(f"Done — min coins for {amount} is {dp[len(coins)][amount]} (3+3, or 4+1+1)", None, done=True)
    return out


COIN_CHANGE_C = r'''#include <stdio.h>
#include <stdlib.h>

#define INF 1000

/* Min coins to make amount (unbounded). dp[a] = min coins for amount a. */
int coin_change_min(int coins[], int n, int amount) {
    int *dp = (int *)malloc((size_t)(amount + 1) * sizeof(int));
    dp[0] = 0;
    for (int a = 1; a <= amount; a++) {
        dp[a] = INF;
        for (int i = 0; i < n; i++)
            if (coins[i] <= a && dp[a - coins[i]] + 1 < dp[a])
                dp[a] = dp[a - coins[i]] + 1;
    }
    int ans = dp[amount];
    free(dp);
    return ans;
}

/* Number of distinct ways to make amount (order of coins doesn't matter). */
int coin_change_ways(int coins[], int n, int amount) {
    int *dp = (int *)calloc((size_t)(amount + 1), sizeof(int));
    dp[0] = 1;
    for (int i = 0; i < n; i++)
        for (int a = coins[i]; a <= amount; a++)
            dp[a] += dp[a - coins[i]];
    int ans = dp[amount];
    free(dp);
    return ans;
}

int main(void) {
    int c1[] = {1, 3, 4}, c2[] = {1, 2, 5};
    printf("Test 1: %d\n", coin_change_min(c1, 3, 6));   /* 2 (3+3) */
    printf("Test 2: %d\n", coin_change_min(c2, 3, 11));  /* 3 (5+5+1) */
    printf("Test 3: %d\n", coin_change_min(c1, 3, 0));   /* 0 */
    printf("Test 4: %d\n", coin_change_ways(c1, 3, 6));  /* 4 */
    return 0;
}
'''


COIN_CHANGE_CPP = r'''#include <iostream>
#include <vector>
using namespace std;

int coinChangeMin(const vector<int>& coins, int amount) {
    const int INF = amount + 1;
    vector<int> dp(amount + 1, INF);
    dp[0] = 0;
    for (int a = 1; a <= amount; a++)
        for (int c : coins)
            if (c <= a && dp[a - c] + 1 < dp[a])
                dp[a] = dp[a - c] + 1;
    return dp[amount];
}

int coinChangeWays(const vector<int>& coins, int amount) {
    vector<int> dp(amount + 1, 0);
    dp[0] = 1;
    for (int c : coins)
        for (int a = c; a <= amount; a++)
            dp[a] += dp[a - c];
    return dp[amount];
}

int main() {
    cout << "Test 1: " << coinChangeMin({1, 3, 4}, 6) << "\n";   /* 2 */
    cout << "Test 2: " << coinChangeMin({1, 2, 5}, 11) << "\n";  /* 3 */
    cout << "Test 3: " << coinChangeMin({1, 3, 4}, 0) << "\n";   /* 0 */
    cout << "Test 4: " << coinChangeWays({1, 3, 4}, 6) << "\n";  /* 4 */
    return 0;
}
'''


COIN_CHANGE_PY = r'''def coin_change_min(coins, amount):
    """Min coins to make amount (unbounded). dp[a] = min coins for amount a."""
    INF = amount + 1
    dp = [INF] * (amount + 1)
    dp[0] = 0
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1
    return dp[amount]


def coin_change_ways(coins, amount):
    """Number of distinct ways to make amount (order of coins doesn't matter)."""
    dp = [0] * (amount + 1)
    dp[0] = 1
    for c in coins:
        for a in range(c, amount + 1):
            dp[a] += dp[a - c]
    return dp[amount]


if __name__ == "__main__":
    print(f"Test 1: {coin_change_min([1, 3, 4], 6)}")   # 2
    print(f"Test 2: {coin_change_min([1, 2, 5], 11)}")  # 3
    print(f"Test 3: {coin_change_min([1, 3, 4], 0)}")   # 0
    print(f"Test 4: {coin_change_ways([1, 3, 4], 6)}")  # 4
'''
TOPIC_COIN_CHANGE = {
    "id": "coin-change",
    "name": "Coin Change (Unbounded)",
    "slug": "coin-change",
    "type": "dp",
    "type_label": TYPES["dp"]["label"],
    "type_icon": TYPES["dp"]["icon"],
    "priority": 4,
    "difficulty": "Medium",
    "icon": "🪙",
    "kind": "grid",
    "complexity": {
        "best": "O(n·amount)",
        "average": "O(n·amount)",
        "worst": "O(n·amount)",
        "space": "O(amount) — 1D rolling array",
        "stable": "n/a",
        "in_place": "1D table filled in place",
    },
    "what": (
        "The unbounded coin-change problem: given unlimited coins of given denominations, make a target "
        "amount using the fewest coins — or count how many ways to make it. Unlike 0/1 knapsack each "
        "coin can be used repeatedly, which changes the DP transition: for amount a with coin c, the "
        "subproblem is dp[a - c] (still at coin c, because reuse is allowed), not dp[i-1][a-c]."
    ),
    "why": (
        "Coin change is the standard example of unbounded DP and the clearest place to see 1D rolling "
        "arrays: only the amount matters, not 'how many coins used so far'. The two variants — min "
        "coins and number of ways — share the same table and differ only in their combine operator "
        "(min vs sum) and loop ordering (amount-ascending counts permutations, coin-outer counts combinations)."
    ),
    "when_needed": [
        "Unlimited supply of each type (coins, stamps, cuts, pack sizes).",
        "A minimum-count objective or a counting objective over a reachable amount.",
        "The target amount is modest enough for O(n·amount) time.",
        "You want to contrast order-sensitive vs order-insensitive counting.",
    ],
    "how_to_select": [
        "Unlimited reuse → unbounded coin change; single-use per item → 0/1 knapsack.",
        "Min coins: dp[a] = min over c of dp[a-c] + 1. Ways: dp[a] = sum over c of dp[a-c].",
        "Counting combinations? Loop coins outermost, amount ascending.",
        "Counting permutations? Loop amount outermost, coins inner.",
        "Amount huge but weights small? Use meet-in-the-middle or BFS on remainders.",
    ],
    "when_not": [
        "Each item is unique → 0/1 knapsack, not coin change.",
        "Amount is huge (10^9+) and n is large → O(n·amount) doesn't fit; consider greedy (canonical coins) or number theory.",
        "Coins have a GCD > 1 that doesn't divide amount → no solution, answer is immediate.",
        "You need the actual coin set, not just the count → store backpointers alongside dp.",
    ],
    "outline": [
        "Unbounded: each coin reusable, so subproblem stays at the same coin index",
        "Min coins: dp[a] = min over c of dp[a-c] + 1, initialized to INF except dp[0]=0",
        "Number of ways: dp[a] = sum over c of dp[a-c], dp[0]=1",
        "1D rolling array — space O(amount), time O(n·amount)",
        "Loop order matters: coin-outer counts combinations; amount-outer counts permutations",
    ],
    "applications": [
        {"title": "Vending and cashier systems", "detail": "Giving change with fewest coins is the literal problem; real currencies are canonical so greedy works, but arbitrary denominations need DP."},
        {"title": "Manufacturing cut stock", "detail": "Cutting raw material into pieces of standard sizes to minimize waste reuses coin-change DP."},
        {"title": "Game design", "detail": "Counting the number of ways to reach a score with given move values uses the 'ways' variant."},
        {"title": "Combinatorics", "text": "Integer partitions and generating-function coefficients are counted with the same recurrence."},
    ],
    "impl_c": COIN_CHANGE_C,
    "impl_cpp": COIN_CHANGE_CPP,
    "impl_py": COIN_CHANGE_PY,
    "sim": sim_coin_change,
    "references": [
        {"title": "GeeksforGeeks — Coin Change (reference)", "url": "https://www.geeksforgeeks.org/coin-change-dp-7/"},
    ],
}


# ---------------------------------------------------------------------------
# Topic: Longest Common Subsequence
# ---------------------------------------------------------------------------

def sim_lcs():
    """Trace the LCS DP table (grid renderer)."""
    s1, s2 = "ABCBDAB", "BDCAB"
    n, m = len(s1), len(s2)
    out = []

    def emit(caption, cur, done=False):
        out.append({
            "kind": "grid",
            "rows": n + 1,
            "cols": m + 1,
            "cur": cur,
            "caption": caption,
            "done": done,
        })

    emit("DP table: rows = prefix of s1, cols = prefix of s2. dp[i][j]=LCS length.", None)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
                emit(f"s1[{i-1}]='{s1[i-1]}' == s2[{j-1}]='{s2[j-1]}' -> extend: {dp[i][j]}", (i, j))
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
                emit(f"s1[{i-1}] != s2[{j-1}] -> max(top,left) = {dp[i][j]}", (i, j))
    emit(f"Done — LCS length = {dp[n][m]} (one LCS is 'BCAB' or 'BDAB')", None, done=True)
    return out


LCS_C = r'''#include <stdio.h>
#include <string.h>

#define MAX 100

/* LCS length: dp[i][j] = LCS length of s1[0..i-1] and s2[0..j-1]. */
int lcs(const char *s1, const char *s2) {
    int n = (int)strlen(s1), m = (int)strlen(s2);
    int dp[MAX + 1][MAX + 1] = {0};
    for (int i = 1; i <= n; i++)
        for (int j = 1; j <= m; j++)
            dp[i][j] = (s1[i - 1] == s2[j - 1])
                ? dp[i - 1][j - 1] + 1
                : (dp[i - 1][j] > dp[i][j - 1] ? dp[i - 1][j] : dp[i][j - 1]);
    return dp[n][m];
}

int main(void) {
    printf("Test 1: %d\n", lcs("ABCBDAB", "BDCAB"));   /* 4 */
    printf("Test 2: %d\n", lcs("AGGTAB", "GXTXAYB"));   /* 4 (GTAB) */
    printf("Test 3: %d\n", lcs("ABC", "DEF"));          /* 0 */
    printf("Test 4: %d\n", lcs("ABC", "ABC"));          /* 3 */
    return 0;
}
'''


LCS_CPP = r'''#include <iostream>
#include <vector>
#include <string>
using namespace std;

int lcs(const string& s1, const string& s2) {
    int n = (int)s1.size(), m = (int)s2.size();
    vector<vector<int>> dp(n + 1, vector<int>(m + 1, 0));
    for (int i = 1; i <= n; i++)
        for (int j = 1; j <= m; j++)
            dp[i][j] = (s1[i - 1] == s2[j - 1])
                ? dp[i - 1][j - 1] + 1
                : max(dp[i - 1][j], dp[i][j - 1]);
    return dp[n][m];
}

int main() {
    cout << "Test 1: " << lcs("ABCBDAB", "BDCAB") << "\n";   /* 4 */
    cout << "Test 2: " << lcs("AGGTAB", "GXTXAYB") << "\n";   /* 4 */
    cout << "Test 3: " << lcs("ABC", "DEF") << "\n";          /* 0 */
    cout << "Test 4: " << lcs("ABC", "ABC") << "\n";          /* 3 */
    return 0;
}
'''


LCS_PY = r'''def lcs(s1, s2):
    """LCS length: dp[i][j] = LCS length of s1[0..i-1] and s2[0..j-1]."""
    n, m = len(s1), len(s2)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[n][m]


if __name__ == "__main__":
    print(f"Test 1: {lcs('ABCBDAB', 'BDCAB')}")   # 4
    print(f"Test 2: {lcs('AGGTAB', 'GXTXAYB')}")   # 4
    print(f"Test 3: {lcs('ABC', 'DEF')}")          # 0
    print(f"Test 4: {lcs('ABC', 'ABC')}")          # 3
'''
TOPIC_LCS = {
    "id": "lcs",
    "name": "Longest Common Subsequence",
    "slug": "lcs",
    "type": "dp",
    "type_label": TYPES["dp"]["label"],
    "type_icon": TYPES["dp"]["icon"],
    "priority": 4,
    "difficulty": "Medium",
    "icon": "🧵",
    "kind": "grid",
    "complexity": {
        "best": "O(n·m)",
        "average": "O(n·m)",
        "worst": "O(n·m)",
        "space": "O(n·m), reducible to O(min(n,m)) rows",
        "stable": "n/a",
        "in_place": "Table is filled in place",
    },
    "what": (
        "The longest common subsequence of two strings is the longest sequence of characters that "
        "appears in both in the same relative order, but not necessarily contiguously. The DP state "
        "dp[i][j] is the LCS length of the prefixes s1[0..i-1] and s2[0..j-1]; when the last characters "
        "match we extend the diagonal, otherwise we carry forward the better of dropping one character "
        "from either string."
    ),
    "why": (
        "LCS is the canonical string DP and the engine behind `diff`, `git merge`, biological sequence "
        "alignment, and plagiarism detection. Its recurrence (diagonal extension vs. max of top/left) "
        "is the template for edit distance and alignment problems. Reconstructing the actual subsequence "
        "by backtracking from dp[n][m] teaches the standard 'traceback' technique that carries over to "
        "Needleman-Wunsch and other alignment algorithms."
    ),
    "when_needed": [
        "You need similarity between two strings that tolerates insertions/deletions.",
        "The output is a subsequence (order matters, contiguity does not).",
        "You're building diff/merge, version-control, or sequence-alignment tools.",
        "You need the edit distance family — LCS is the special case with only insert/delete, no substitute.",
    ],
    "how_to_select": [
        "Subsequence (not substring) + order matters → LCS.",
        "Need the actual subsequence, not just length? Backtrack from dp[n][m] following the arrows.",
        "Space-sensitive? Keep only two rows; Hirschberg's algorithm recovers the sequence in O(min(n,m)) space.",
        "Many strings? LCS generalizes but gets expensive; pairwise LCS is common.",
        "Want substitutions too? Use edit distance (Levenshtein), which extends the same table.",
    ],
    "when_not": [
        "Contiguity matters → longest common substring, a different DP.",
        "Exact matching is required → hashing / KMP / suffix structures.",
        "The strings are huge and only an approximation matters → locality-sensitive hashing or embedding similarity.",
        "Order doesn't matter → set intersection / bag-of-words comparison.",
    ],
    "outline": [
        "State: dp[i][j] = LCS length of s1[0..i-1] and s2[0..j-1]",
        "Match -> dp[i][j] = dp[i-1][j-1] + 1; mismatch -> max(dp[i-1][j], dp[i][j-1])",
        "Fill row by row in O(n·m)",
        "Reconstruct the subsequence by backtracking from dp[n][m]",
        "Space-optimized: two rows, or Hirschberg's divide-and-conquer for O(min(n,m)) space",
    ],
    "applications": [
        {"title": "Version control (diff/merge)", "detail": "Git, diff, and merge tools compute LCS-like alignments to show what changed between file versions."},
        {"title": "Bioinformatics", "detail": "DNA and protein sequence alignment (Needleman-Wunsch) extends LCS with substitution scores."},
        {"title": "Plagiarism detection", "detail": "Tools measure document similarity via longest common subsequences of normalized text."},
        {"title": "Spell check / autocomplete", "detail": "Edit distance (a close cousin) drives suggestions for misspelled words."},
    ],
    "impl_c": LCS_C,
    "impl_cpp": LCS_CPP,
    "impl_py": LCS_PY,
    "sim": sim_lcs,
    "references": [
        {"title": "GeeksforGeeks — LCS (reference)", "url": "https://www.geeksforgeeks.org/longest-common-subsequence-dp-4/"},
    ],
}


# ---------------------------------------------------------------------------
# Topic: Longest Increasing Subsequence (LIS)
# ---------------------------------------------------------------------------

def sim_lis():
    """Trace the O(n log n) patience-sort LIS (array renderer)."""
    a = [10, 9, 2, 5, 3, 7, 101, 18]
    n = len(a)
    out = []
    piles = []
    top = []
    placed = []

    def emit(caption, data, highlights=(), compare=(), done=False):
        markers = {"piles": len(piles)}
        out.append({
            "kind": "array",
            "data": list(data),
            "highlights": list(highlights),
            "compare": list(compare),
            "swap": [],
            "markers": markers,
            "caption": caption,
            "done": done,
        })

    emit(f"Start — patience sort builds piles; the pile count is the LIS length", a)
    for i in range(n):
        x = a[i]
        lo, hi = 0, len(top)
        while lo < hi:
            mid = (lo + hi) // 2
            if top[mid] < x:
                lo = mid + 1
            else:
                hi = mid
        pile = lo
        emit(f"Value {x}: binary search over pile tops [{', '.join(map(str, top)) if top else 'empty'}] "
             f"-> place on pile {pile}", a, [i], list(range(len(top))))
        if pile == len(top):
            top.append(x)
            piles.append([x])
        else:
            top[pile] = x
            piles[pile].append(x)
        placed.append(pile)
        top_snapshot = list(top)
        emit(f"Pile tops after placing {x}: [{', '.join(map(str, top_snapshot))}] — "
             f"{len(pile)} pile(s) so far", a, [i])
    lis_len = len(piles)
    emit(f"Done — {lis_len} piles, so LIS length = {lis_len}. One LIS (rebuilt by linking): "
         f"{' -> '.join(str(piles[i][-1]) for i in range(lis_len))}", a, done=True)
    return out


LIS_C = r'''#include <stdio.h>

/* O(n log n) LIS via patience sort. pile_top[k] holds the smallest possible
 * tail of an increasing subsequence of length k+1; we binary search the pile
 * to extend. Returns the LIS length and reconstructs one LIS via parent links. */
int lis(const int a[], int n, int out[]) {
    if (n == 0) return 0;
    int pile_top[256];
    int pile_idx[256];        /* index into a for each pile's top element */
    int prev[256];            /* parent index for reconstruction */
    int len = 0;

    for (int i = 0; i < n; i++) {
        int lo = 0, hi = len;
        while (lo < hi) {
            int mid = (lo + hi) / 2;
            if (a[pile_idx[mid]] < a[i]) lo = mid + 1;
            else hi = mid;
        }
        prev[i] = (lo > 0) ? pile_idx[lo - 1] : -1;
        pile_idx[lo] = i;
        if (lo == len) len++;
    }

    /* reconstruct by following parent pointers back from the last pile top */
    int k = pile_idx[len - 1];
    for (int j = len - 1; j >= 0; j--) {
        out[j] = a[k];
        k = prev[k];
    }
    return len;
}

int main(void) {
    int a1[] = {10, 9, 2, 5, 3, 7, 101, 18};
    int a2[] = {0, 1, 0, 3, 2, 3};
    int a3[] = {7, 7, 7, 7, 7};
    int a4[] = {1, 2, 3, 4, 5};
    int out[256];

    int len;
    len = lis(a1, 8, out); printf("Test 1: len=%d  [", len);
    for (int i = 0; i < len; i++) printf("%d%s", out[i], i == len - 1 ? "" : ", ");
    printf("]\n");

    len = lis(a2, 6, out); printf("Test 2: len=%d  [", len);
    for (int i = 0; i < len; i++) printf("%d%s", out[i], i == len - 1 ? "" : ", ");
    printf("]\n");

    len = lis(a3, 5, out); printf("Test 3: len=%d  [", len);
    for (int i = 0; i < len; i++) printf("%d%s", out[i], i == len - 1 ? "" : ", ");
    printf("]\n");

    len = lis(a4, 5, out); printf("Test 4: len=%d  [", len);
    for (int i = 0; i < len; i++) printf("%d%s", out[i], i == len - 1 ? "" : ", ");
    printf("]\n");
    return 0;
}
'''


LIS_CPP = r'''#include <iostream>
#include <vector>
using namespace std;

int lis(const vector<int>& a, vector<int>& out) {
    int n = (int)a.size();
    if (n == 0) return 0;
    vector<int> pile_idx;
    vector<int> prev(n, -1);

    for (int i = 0; i < n; i++) {
        int lo = 0, hi = (int)pile_idx.size();
        while (lo < hi) {
            int mid = (lo + hi) / 2;
            if (a[pile_idx[mid]] < a[i]) lo = mid + 1;
            else hi = mid;
        }
        prev[i] = (lo > 0) ? pile_idx[lo - 1] : -1;
        if (lo == (int)pile_idx.size()) pile_idx.push_back(i);
        else pile_idx[lo] = i;
    }

    int len = (int)pile_idx.size();
    int k = pile_idx[len - 1];
    out.resize(len);
    for (int j = len - 1; j >= 0; j--) {
        out[j] = a[k];
        k = prev[k];
    }
    return len;
}

void printLIS(const vector<int>& a, const char* label) {
    vector<int> out;
    int len = lis(a, out);
    cout << label << ": len=" << len << "  [";
    for (int i = 0; i < len; i++) cout << out[i] << (i == len - 1 ? "" : ", ");
    cout << "]\n";
}

int main() {
    printLIS({10, 9, 2, 5, 3, 7, 101, 18}, "Test 1");
    printLIS({0, 1, 0, 3, 2, 3}, "Test 2");
    printLIS({7, 7, 7, 7, 7}, "Test 3");
    printLIS({1, 2, 3, 4, 5}, "Test 4");
    return 0;
}
'''


LIS_PY = r'''def lis(a):
    """O(n log n) LIS via patience sort with parent links for reconstruction."""
    n = len(a)
    if n == 0:
        return []
    pile_idx = []
    prev = [-1] * n

    for i in range(n):
        lo, hi = 0, len(pile_idx)
        while lo < hi:
            mid = (lo + hi) // 2
            if a[pile_idx[mid]] < a[i]:
                lo = mid + 1
            else:
                hi = mid
        prev[i] = pile_idx[lo - 1] if lo > 0 else -1
        if lo == len(pile_idx):
            pile_idx.append(i)
        else:
            pile_idx[lo] = i

    # reconstruct
    out = []
    k = pile_idx[len(pile_idx) - 1]
    for _ in range(len(pile_idx)):
        out.append(a[k])
        k = prev[k]
    out.reverse()
    return out


def fmt(a):
    return " ".join(map(str, a))


if __name__ == "__main__":
    for i, arr in enumerate(([10, 9, 2, 5, 3, 7, 101, 18],
                             [0, 1, 0, 3, 2, 3],
                             [7, 7, 7, 7, 7],
                             [1, 2, 3, 4, 5]), 1):
        seq = lis(arr)
        print(f"Test {i}: len={len(seq)}  [{', '.join(map(str, seq))}]")
'''
TOPIC_LIS = {
    "id": "lis",
    "name": "Longest Increasing Subsequence",
    "slug": "lis",
    "type": "dp",
    "type_label": TYPES["dp"]["label"],
    "type_icon": TYPES["dp"]["icon"],
    "priority": 4,
    "difficulty": "Medium",
    "icon": "📈",
    "kind": "array",
    "complexity": {
        "best": "O(n log n)",
        "average": "O(n log n)",
        "worst": "O(n log n)",
        "space": "O(n)",
        "stable": "n/a",
        "in_place": "Builds auxiliary pile arrays",
    },
    "what": (
        "The longest increasing subsequence of a sequence is the longest subset of elements that appear "
        "in strictly increasing order (not necessarily contiguous). The O(n log n) patience-sort "
        "algorithm builds piles: each element goes onto the leftmost pile whose top is >= it; the number "
        "of piles at the end equals the LIS length, and parent links through the piles reconstruct one LIS."
    ),
    "why": (
        "LIS is the canonical DP-optimisation example: the naive DP is O(n²), but a greedy + binary "
        "search reshapes it to O(n log n). It models scheduling, patience sorting, and chain-building "
        "problems. Its dual — Dilworth's theorem — connects it to minimum chain covers, and the same "
        "structure appears in envelope nesting and box-stacking problems."
    ),
    "when_needed": [
        "You need the longest strictly (or non-decreasing) subsequence of a 1D sequence.",
        "The sequence is long and O(n²) DP is too slow — O(n log n) is the standard upgrade.",
        "You're solving chain or nesting problems that reduce to LIS after sorting.",
        "You need the actual subsequence, not just its length — parent links give it.",
    ],
    "how_to_select": [
        "Strictly increasing? Use < in the binary search; non-decreasing? use <= (changes pile placement).",
        "Need the sequence itself? Keep parent pointers and backtrack from the last pile's top.",
        "O(n²) DP may be simpler for small n (~1000) and gives more info (count of LIS, etc.).",
        "Reduce nesting/stacking problems to LIS by sorting one dimension and running LIS on the other.",
        "For multiple queries or updates, a segment-tree variant beats the offline algorithm.",
    ],
    "when_not": [
        "The sequence is tiny and simplicity matters — O(n²) DP is easier to extend.",
        "You need the longest COMMON subsequence (between two sequences) — that is LCS, not LIS.",
        "The problem requires contiguous elements — that is maximum subarray (Kadane), not LIS.",
        "You need to count ALL increasing subsequences — requires a different DP formulation.",
    ],
    "outline": [
        "Patience sort: place each value on the leftmost pile whose top >= it",
        "Binary search over pile tops — O(log n) per element",
        "Number of piles = LIS length; parent links reconstruct one LIS",
        "O(n log n) time, O(n) space",
        "Dual to Dilworth's theorem: min chain cover = max antichain size",
    ],
    "applications": [
        {"title": "Scheduling", "detail": "Maximum chain of compatible intervals (after sorting) is an LIS problem."},
        {"title": "Envelope nesting", "detail": "Russian-doll envelopes reduce to LIS after sorting by one dimension."},
        {"title": "Patience sorting", "detail": "The card game patience sort directly implements this algorithm."},
        {"title": "Bioinformatics", "detail": "Sequence alignment and chain-finding in genomics use LIS variants."},
    ],
    "impl_c": LIS_C,
    "impl_cpp": LIS_CPP,
    "impl_py": LIS_PY,
    "sim": sim_lis,
    "references": [
        {"title": "GeeksforGeeks — LIS (reference)", "url": "https://www.geeksforgeeks.org/longest-increasing-subsequence-dp-3/"},
    ],
}


# ---------------------------------------------------------------------------
# Export order: used for the landing page and prev/next navigation.
# ---------------------------------------------------------------------------

TOPICS = [
    TOPIC_BINARY_SEARCH,
    TOPIC_MERGE_SORT,
    TOPIC_QUICK_SORT,
    TOPIC_HEAP_SORT,
    TOPIC_COUNTING_RADIX,
    TOPIC_BACKTRACKING_BASICS,
    TOPIC_N_QUEENS,
    TOPIC_SUDOKU,
    TOPIC_DIJKSTRA,
    TOPIC_TRAVERSALS,
    TOPIC_BST,
    TOPIC_BINARY_HEAP,
    TOPIC_AVL,
    TOPIC_LCA,
    TOPIC_BFS_DFS,
    TOPIC_BELLMAN_FLOYD,
    TOPIC_TOPO_SORT,
    TOPIC_DSU,
    TOPIC_MST,
    TOPIC_GREEDY,
    TOPIC_FRACTIONAL,
    TOPIC_HUFFMAN,
    TOPIC_JOB_SEQ,
    TOPIC_DP_FUND,
    TOPIC_KNAPSACK,
    TOPIC_COIN_CHANGE,
    TOPIC_LCS,
    TOPIC_LIS,
    TOPIC_MATRIX_CHAIN,
]


# ---------------------------------------------------------------------------
# Topic: Matrix Chain Multiplication (Interval DP)
# ---------------------------------------------------------------------------

def sim_matrix_chain():
    """Trace optimal parenthesization of a chain of matrices (grid renderer)."""
    # Dimensions: A1=10x30, A2=30x5, A3=5x60
    dims = [10, 30, 5, 60]
    n = len(dims) - 1  # number of matrices
    out = []

    # dp[i][j] = min cost to multiply Ai..Aj
    dp = [[0] * (n + 1) for _ in range(n + 1)]
    split = [[0] * (n + 1) for _ in range(n + 1)]

    def emit(caption, data, highlights=(), done=False):
        out.append({
            "kind": "grid",
            "data": data,
            "highlights": list(highlights),
            "caption": caption,
            "done": done,
        })

    emit("Start — matrix dimensions: A1=10×30, A2=30×5, A3=5×60. dp[i][j] = min cost for Ai..Aj",
         [[dp[i][j] for j in range(n + 1)] for i in range(n + 1)])

    for length in range(2, n + 1):  # chain length
        for i in range(1, n - length + 2):
            j = i + length - 1
            dp[i][j] = float('inf')
            for k in range(i, j):
                cost = dp[i][k] + dp[k + 1][j] + dims[i - 1] * dims[k] * dims[j]
                if cost < dp[i][j]:
                    dp[i][j] = cost
                    split[i][j] = k
            emit(f"Chain A{i}..A{j}: try all splits, best at k={split[i][j]} with cost {dp[i][j]}",
                 [[dp[i][j] for j in range(n + 1)] for i in range(n + 1)],
                 [(i, j)])

    emit(f"Done — optimal cost = {dp[1][n]}, parenthesization: (A1×A2)×A3",
         [[dp[i][j] for j in range(n + 1)] for i in range(n + 1)], done=True)
    return out


MATRIX_CHAIN_C = r'''#include <stdio.h>
#include <limits.h>

/* Matrix chain: dp[i][j] = min scalar multiplications for Ai..Aj.
 * dims[i-1] x dims[i] is the dimension of Ai. */
int matrix_chain(int dims[], int n, int split[][7]) {
    int dp[7][7] = {0};

    for (int len = 2; len <= n; len++) {
        for (int i = 1; i <= n - len + 1; i++) {
            int j = i + len - 1;
            dp[i][j] = INT_MAX;
            for (int k = i; k < j; k++) {
                int cost = dp[i][k] + dp[k + 1][j] + dims[i - 1] * dims[k] * dims[j];
                if (cost < dp[i][j]) {
                    dp[i][j] = cost;
                    split[i][j] = k;
                }
            }
        }
    }
    return dp[1][n];
}

int main(void) {
    int dims1[] = {10, 30, 5, 60};
    int dims2[] = {40, 20, 30, 10, 30};
    int dims3[] = {10, 20, 30, 40, 30};
    int split[7][7];

    printf("Test 1: %d\n", matrix_chain(dims1, 3, split));  /* 4500 */
    printf("Test 2: %d\n", matrix_chain(dims2, 4, split));  /* 26000 */
    printf("Test 3: %d\n", matrix_chain(dims3, 4, split));  /* 30000 */
    return 0;
}
'''


MATRIX_CHAIN_CPP = r'''#include <iostream>
#include <vector>
#include <climits>
using namespace std;

int matrixChain(const vector<int>& dims) {
    int n = (int)dims.size() - 1;
    vector<vector<int>> dp(n + 1, vector<int>(n + 1, 0));

    for (int len = 2; len <= n; len++) {
        for (int i = 1; i <= n - len + 1; i++) {
            int j = i + len - 1;
            dp[i][j] = INT_MAX;
            for (int k = i; k < j; k++) {
                int cost = dp[i][k] + dp[k + 1][j] + dims[i - 1] * dims[k] * dims[j];
                dp[i][j] = min(dp[i][j], cost);
            }
        }
    }
    return dp[1][n];
}

int main() {
    cout << "Test 1: " << matrixChain({10, 30, 5, 60}) << "\n";       /* 4500 */
    cout << "Test 2: " << matrixChain({40, 20, 30, 10, 30}) << "\n";   /* 26000 */
    cout << "Test 3: " << matrixChain({10, 20, 30, 40, 30}) << "\n";   /* 30000 */
    return 0;
}
'''


MATRIX_CHAIN_PY = r'''def matrix_chain(dims):
    """Min scalar multiplications for a chain of matrices with given dimensions."""
    n = len(dims) - 1
    dp = [[0] * (n + 1) for _ in range(n + 1)]

    for length in range(2, n + 1):
        for i in range(1, n - length + 2):
            j = i + length - 1
            dp[i][j] = float('inf')
            for k in range(i, j):
                cost = dp[i][k] + dp[k + 1][j] + dims[i - 1] * dims[k] * dims[j]
                dp[i][j] = min(dp[i][j], cost)
    return dp[1][n]


if __name__ == "__main__":
    print(f"Test 1: {matrix_chain([10, 30, 5, 60])}")        # 4500
    print(f"Test 2: {matrix_chain([40, 20, 30, 10, 30])}")   # 26000
    print(f"Test 3: {matrix_chain([10, 20, 30, 40, 30])}")   # 30000
'''
TOPIC_MATRIX_CHAIN = {
    "id": "matrix-chain",
    "name": "Matrix Chain & Interval DP",
    "slug": "matrix-chain",
    "type": "dp",
    "type_label": TYPES["dp"]["label"],
    "type_icon": TYPES["dp"]["icon"],
    "priority": 3,
    "difficulty": "Hard",
    "icon": "🔗",
    "kind": "grid",
    "complexity": {
        "best": "O(n³)",
        "average": "O(n³)",
        "worst": "O(n³)",
        "space": "O(n²)",
        "stable": "n/a",
        "in_place": "Table is filled in place",
    },
    "what": (
        "Matrix chain multiplication finds the cheapest parenthesization for multiplying a chain of "
        "matrices. Since matrix multiplication is associative but the cost depends on dimensions, the "
        "order matters: dp[i][j] = min over all split points k of (dp[i][k] + dp[k+1][j] + cost of "
        "multiplying the two result matrices). This is the canonical interval DP — the table is filled "
        "by increasing chain length."
    ),
    "why": (
        "Matrix chain is the gateway to interval DP, where the state is a range [i,j] and the answer "
        "is built from smaller ranges. The same pattern solves optimal binary search trees, polygon "
        "triangulation, and burst-balloons. It teaches the critical insight: when subproblems are "
        "intervals, fill the table by length, not by row or column."
    ),
    "when_needed": [
        "You need to optimally parenthesize a chain of operations (matrix multiplication, etc.).",
        "The problem has an interval structure: the answer for [i,j] depends on answers for sub-intervals.",
        "You're solving optimal BST, polygon triangulation, or burst-balloons.",
        "The cost function is associative but order-dependent.",
    ],
    "how_to_select": [
        "State is a range [i,j]? Interval DP — fill by increasing length.",
        "The recurrence tries all split points k between i and j? Classic interval DP.",
        "Need the actual parenthesization? Store the best split point and reconstruct.",
        "O(n³) too slow? Some interval DPs optimize to O(n²) with Knuth's inequality or monotonicity.",
        "For small n (~100), O(n³) is fine; for larger, consider if the problem reduces to a simpler form.",
    ],
    "when_not": [
        "The problem is linear (not interval) — standard 1D DP suffices.",
        "The operation is commutative — order doesn't matter, so no parenthesization needed.",
        "Greedy works (e.g., Huffman-like problems) — interval DP is overkill.",
        "The state isn't a range — if subproblems don't decompose into intervals, use a different DP.",
    ],
    "outline": [
        "dp[i][j] = min cost for Ai..Aj; base case dp[i][i] = 0",
        "Try every split k: cost = dp[i][k] + dp[k+1][j] + dims[i-1]*dims[k]*dims[j]",
        "Fill table by increasing chain length (interval DP pattern)",
        "O(n³) time, O(n²) space",
        "Reconstruct parenthesization via stored split points",
    ],
    "applications": [
        {"title": "Matrix multiplication", "detail": "BLAS and NumPy internally optimize chain order for multi-matrix products."},
        {"title": "Optimal BST", "detail": "Given key frequencies, the same interval DP builds the cheapest search tree."},
        {"title": "Polygon triangulation", "detail": "Minimum-cost triangulation of a convex polygon is interval DP on vertices."},
        {"title": "Compiler optimization", "detail": "Instruction scheduling and register allocation use interval-DP variants."},
    ],
    "impl_c": MATRIX_CHAIN_C,
    "impl_cpp": MATRIX_CHAIN_CPP,
    "impl_py": MATRIX_CHAIN_PY,
    "sim": sim_matrix_chain,
    "references": [
        {"title": "GeeksforGeeks — Matrix Chain (reference)", "url": "https://www.geeksforgeeks.org/matrix-chain-multiplication-dp-8/"},
    ],
}


def topic_by_id(tid):
    for t in TOPICS:
        if t["id"] == tid:
            return t
    return None


def ordered_types():
    """Return type keys in a stable, human-friendly order."""
    return ["sorting-searching", "backtracking", "tree", "graph", "greedy", "dynamic-programming"]


if __name__ == "__main__":
    print(f"Topics authored: {len(TOPICS)}")
    for t in TOPICS:
        print(f"  - {t['name']} [{t['type_label']}] priority={t['priority']}")